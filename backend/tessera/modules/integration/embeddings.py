"""Opt-in embedding retrieval: rank fusion, never cosine-to-fuzzy score comparison.

The caller supplies its time-filtered catalog and source-derived descriptions.
Vectors are cached through the existing LLM client, with a content fingerprint.
Semantic retrieval alone does not establish product identity.
"""

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from threading import Lock
from typing import Any

from tessera.modules.integration.candidates import (
    BLOCKING_FLAGS,
    Candidate,
    Catalog,
    LinkParams,
    LinkResult,
    link_mention,
)


class InvalidEmbedding(ValueError):
    """An unusable provider vector; retain the deterministic candidates."""


class EmbeddingRetriever:
    def __init__(self, client: Any, dimensions: int = 512):
        if dimensions not in (512, 2048):
            raise ValueError("embedding dimensions must be 512 or 2048")
        self.client = client
        self.dimensions = dimensions
        self.indexes: dict[str, list[list[float]]] = {}
        self._index_lock = Lock()

    def retrieve(
        self,
        mention: str,
        catalog: Catalog,
        *,
        params: LinkParams,
        size: str | None = None,
        store_skus: frozenset[str] | None = None,
        descriptions: Mapping[str, str] | None = None,
    ) -> LinkResult:
        fuzzy = link_mention(mention, catalog, size, store_skus, params)
        if (
            fuzzy.status == "linked"
            or not mention.strip()
            or any(set(c.flags) & BLOCKING_FLAGS for c in fuzzy.candidates)
        ):
            return fuzzy
        entries = []
        for style in sorted(catalog.styles.values(), key=lambda s: s.code):
            for colour in sorted(style.colours):
                sku = f"{style.code}-{colour}"
                text = " ".join(
                    (
                        style.name,
                        *catalog.style_aliases.get(style.code, ()),
                        *catalog.colour_names.get(colour, ()),
                        (descriptions or {}).get(sku, ""),
                    )
                )
                entries.append((sku, style, text))
        if store_skus is not None:
            local = [e for e in entries if e[0] in store_skus]
            entries = local or entries
        if not entries:
            return fuzzy
        texts = [e[2] for e in entries]
        fingerprint = hashlib.sha256(
            json.dumps(
                [(e[0], e[2]) for e in entries],
                ensure_ascii=False,
            ).encode()
        ).hexdigest()
        context = {"catalog_version": fingerprint, "retrieval_version": "rrf-v1"}
        # int.link shares this retriever across concurrent observation decisions.
        # Build each index once, while leaving query calls free to run in parallel.
        with self._index_lock:
            if fingerprint not in self.indexes:
                vectors = self.client.embed(texts, self.dimensions, cache_context=context)
                _validate(vectors, len(entries), self.dimensions)
                self.indexes[fingerprint] = vectors
        queries = self.client.embed([mention], self.dimensions, cache_context=context)
        _validate(queries, 1, self.dimensions)
        query = queries[0]
        scored = []
        for (sku, style, text), vector in zip(entries, self.indexes[fingerprint], strict=True):
            similarity = _cosine(query, vector)
            if similarity <= 0:
                continue
            flags = () if size is None or size.upper() in style.sizes else ("size_not_in_size_run",)
            target = f"{sku}-{size.upper()}" if size and not flags else sku
            level = "sku_size" if size and not flags else "sku"
            scored.append(
                (
                    similarity,
                    Candidate(
                        target,
                        level,
                        similarity,
                        "embedding",
                        text,
                        flags,
                        None if store_skus is None else sku in store_skus,
                    ),
                )
            )
        semantic = [c for _, c in sorted(scored, key=lambda p: (-p[0], p[1].target_id))]
        candidates = fuse_ranks(fuzzy.candidates, semantic[: params.top_k], params.top_k)
        return LinkResult(
            "ambiguous" if candidates else "unlinked",
            None,
            None,
            candidates,
            (*fuzzy.reasons, "semantic_retrieval_requires_confirmation"),
        )


def _validate(vectors: Sequence[Sequence[float]], count: int, dimensions: int) -> None:
    if len(vectors) != count or any(
        len(v) != dimensions
        or not all(math.isfinite(x) for x in v)
        or not 0 < math.hypot(*v) < math.inf
        for v in vectors
    ):
        raise InvalidEmbedding("invalid embedding count, dimensions, finite values or zero norm")


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    # Normalize first: bounded provider values are not an assumption of the helper.
    ln, rn = math.hypot(*left), math.hypot(*right)
    return math.fsum((a / ln) * (b / rn) for a, b in zip(left, right, strict=True))


def fuse_ranks(
    fuzzy: Sequence[Candidate],
    semantic: Sequence[Candidate],
    top_k: int,
) -> tuple[Candidate, ...]:
    """Equal-weight reciprocal rank fusion, c=60; result is a rank score, not confidence."""
    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20")
    ranks: dict[tuple[str, str], float] = {}
    records: dict[tuple[str, str], Candidate] = {}
    for ranking in (fuzzy, semantic):
        seen = set()
        for rank, candidate in enumerate(ranking, 1):
            key = candidate.target_id, candidate.level
            if key in seen:
                continue
            seen.add(key)
            ranks[key] = ranks.get(key, 0.0) + 1 / (60 + rank)
            records.setdefault(key, candidate)
    result = []
    for key in sorted(ranks, key=lambda k: (-ranks[k], k))[:top_k]:
        candidate = records[key]
        flags = tuple(
            sorted(
                {
                    flag
                    for ranking in (fuzzy, semantic)
                    for c in ranking
                    if (c.target_id, c.level) == key
                    for flag in c.flags
                }
            )
        )
        result.append(
            Candidate(
                candidate.target_id,
                candidate.level,
                ranks[key] * 61 / 2 * 100,
                "rrf",
                candidate.matched,
                flags,
                candidate.in_assortment,
            )
        )
    return tuple(result)


@dataclass(frozen=True)
class RetrievalQuery:
    mention: str
    expected_ids: tuple[str, ...]
    size: str | None = None
    store_skus: frozenset[str] | None = None


def compare_dimensions(
    queries: Sequence[RetrievalQuery],
    catalog: Catalog,
    client: Any,
    *,
    top_k: int = 8,
    descriptions: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Same queries/catalog/k for fuzzy, 512 and 2048. Labels are caller-supplied dev labels.

    Empty expected_ids is a negative. Recall is macro hit@k over positives;
    negative examples stay in the abstention and incorrect-acceptance counts.
    Errors (including replay misses) propagate; no fabricated metrics on failure.
    """
    if not queries:
        raise ValueError("comparison requires at least one query")
    params = LinkParams(top_k=top_k)
    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20")
    positives = sum(bool(q.expected_ids) for q in queries)
    output = {}
    for dimension in (None, 512, 2048):
        retriever = EmbeddingRetriever(client, dimension) if dimension else None
        hits = abstentions = incorrect = 0
        for query in queries:
            result = (
                retriever.retrieve(
                    query.mention,
                    catalog,
                    params=params,
                    size=query.size,
                    store_skus=query.store_skus,
                    descriptions=descriptions,
                )
                if retriever
                else link_mention(
                    query.mention,
                    catalog,
                    query.size,
                    query.store_skus,
                    params,
                )
            )
            hits += bool(set(query.expected_ids) & {c.target_id for c in result.candidates})
            abstentions += result.status != "linked"
            incorrect += result.status == "linked" and result.target_id not in query.expected_ids
        output[str(dimension) if dimension else "fuzzy"] = {
            "n": len(queries),
            "positive_n": positives,
            "negative_n": len(queries) - positives,
            "hits_at_k": hits,
            "recall_at_k": hits / positives if positives else None,
            "abstentions": abstentions,
            "abstention_rate": abstentions / len(queries),
            "incorrect_accepted": incorrect,
        }
    return {"top_k": top_k, "rank_fusion": "rrf-c60", "results": output}
