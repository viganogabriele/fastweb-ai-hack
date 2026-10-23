"""Synthetic vectors prove retrieval math and isolation, not model quality."""

import math
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from tesseract.core.cache import ReplayMiss
from tesseract.modules.integration.candidates import Candidate, Catalog, LinkParams, Style
from tesseract.modules.integration.embeddings import (
    EmbeddingRetriever,
    InvalidEmbedding,
    RetrievalQuery,
    compare_dimensions,
    fuse_ranks,
)


@pytest.fixture
def catalog():
    return Catalog(
        styles={
            "A": Style("A", "ALPHA", ("999",), ("S", "M")),
            "B": Style("B", "BETA", ("999",), ("M", "L")),
        },
        colour_names={"999": ("black", "nero")},
    )


class Embeddings:
    def __init__(self):
        self.calls = []

    def embed(self, texts, dimensions, *, cache_context):
        self.calls.append((list(texts), dimensions, cache_context))
        return [
            [1.0, 0.0] + [0.0] * (dimensions - 2)
            if "ALPHA" in text or "long" in text
            else [0.0, 1.0] + [0.0] * (dimensions - 2)
            for text in texts
        ]


def test_rank_fusion_uses_positions_not_incomparable_scores_and_keeps_flags():
    a = Candidate("A-999", "sku", 99, "fuzzy", "a")
    b = Candidate("B-999", "sku", 0.1, "embedding", "b", ("size_not_in_size_run",))
    first = fuse_ranks([a, b], [b, a], 2)
    second = fuse_ranks([a.__class__(**(a.__dict__ | {"score": -999})), b], [b, a], 2)
    assert [c.target_id for c in first] == ["A-999", "B-999"]
    assert [c.score for c in first] == [c.score for c in second]
    assert first[1].flags == ("size_not_in_size_run",)
    assert all(c.method == "rrf" and 0 < c.score <= 100 for c in first)
    assert fuse_ranks([a, a], [], 2)[0].score == fuse_ranks([a], [], 2)[0].score


@pytest.mark.parametrize("dimension", [512, 2048])
def test_semantic_only_retrieval_stays_ambiguous_and_index_is_reused(catalog, dimension):
    client = Embeddings()
    retriever = EmbeddingRetriever(client, dimension)
    result = retriever.retrieve("the long black one", catalog, params=LinkParams(top_k=1))
    assert result.status == "ambiguous" and result.target_id is None
    assert [c.target_id for c in result.candidates] == ["A-999"]
    retriever.retrieve("another long coat", catalog, params=LinkParams(top_k=1))
    assert len(client.calls) == 3  # catalog once, two queries
    assert all(call[1] == dimension for call in client.calls)
    assert len({call[2]["catalog_version"] for call in client.calls}) == 1


def test_time_filtered_catalog_and_assortment_bound_semantic_candidates(catalog):
    client = Embeddings()
    retriever = EmbeddingRetriever(client)
    restricted = Catalog(styles={"A": catalog.styles["A"]}, colour_names=catalog.colour_names)
    retriever.retrieve("long", restricted, params=LinkParams())
    assert all("BETA" not in text for text in client.calls[0][0])
    retriever.retrieve("long", catalog, params=LinkParams(), store_skus=frozenset({"B-999"}))
    assert all("ALPHA" not in text for text in client.calls[2][0])
    assert client.calls[0][2] != client.calls[2][2]


def test_catalog_description_changes_invalidate_index(catalog):
    client = Embeddings()
    retriever = EmbeddingRetriever(client)
    for text in ("short coat", "long coat"):
        retriever.retrieve("long", catalog, params=LinkParams(), descriptions={"A-999": text})
    assert len(client.calls) == 4
    assert client.calls[0][2] != client.calls[2][2]


def test_exact_links_and_blocking_colour_size_flags_do_not_call_embeddings(catalog):
    client = Embeddings()
    retriever = EmbeddingRetriever(client)
    assert retriever.retrieve("ALPHA black", catalog, params=LinkParams()).status == "linked"
    flagged = retriever.retrieve("ALPHA black", catalog, size="XXL", params=LinkParams())
    assert any("size_not_in_size_run" in c.flags for c in flagged.candidates)
    assert client.calls == []


@pytest.mark.parametrize("bad", [[], [[0.0] * 512], [[math.nan] * 512], [[1.0]], [[1e308] * 512]])
def test_bad_vectors_fail_explicitly(catalog, bad):
    class Broken:
        def embed(self, *args, **kwargs):
            return bad

    with pytest.raises(InvalidEmbedding):
        EmbeddingRetriever(Broken()).retrieve("long", catalog, params=LinkParams())


def test_semantic_size_candidate_is_not_coerced_to_another_size(catalog):
    result = EmbeddingRetriever(Embeddings()).retrieve(
        "long coat",
        catalog,
        size="XS",
        params=LinkParams(),
    )
    assert result.status == "ambiguous"
    assert result.candidates[0].target_id == "A-999"
    assert "size_not_in_size_run" in result.candidates[0].flags


def test_comparison_uses_same_k_and_labels_with_negative_abstentions(catalog):
    client = Embeddings()
    result = compare_dimensions(
        [
            RetrievalQuery("the long one", ("A-999",)),
            RetrievalQuery("alien", ()),
        ],
        catalog,
        client,
        top_k=1,
    )
    assert result["top_k"] == 1
    assert result["results"]["fuzzy"]["recall_at_k"] == 0
    for dimension in ("512", "2048"):
        metrics = result["results"][dimension]
        assert metrics["positive_n"] == 1 and metrics["negative_n"] == 1
        assert metrics["recall_at_k"] == 1 and metrics["abstentions"] == 2
        assert metrics["incorrect_accepted"] == 0
    assert {call[1] for call in client.calls} == {512, 2048}


def test_replay_miss_propagates_from_comparison_instead_of_fabricating_metrics(catalog):
    class Offline:
        def embed(self, *args, **kwargs):
            raise ReplayMiss("missing")

    with pytest.raises(ReplayMiss):
        compare_dimensions([RetrievalQuery("long", ("A-999",))], catalog, Offline())


def test_empty_positive_universe_has_no_invented_recall(catalog):
    result = compare_dimensions([RetrievalQuery("alien", ())], catalog, Embeddings())
    assert all(m["recall_at_k"] is None for m in result["results"].values())


@pytest.mark.parametrize("value", [0, 21])
def test_invalid_k_rejected(catalog, value):
    with pytest.raises(ValueError):
        compare_dimensions([RetrievalQuery("long", ())], catalog, Embeddings(), top_k=value)


def test_concurrent_observations_build_catalog_index_once(catalog):
    ready = threading.Barrier(4)

    class SlowEmbeddings(Embeddings):
        def embed(self, texts, dimensions, *, cache_context):
            if len(texts) > 1:
                time.sleep(0.05)  # expose overlapping index builds without synchronization
            return super().embed(texts, dimensions, cache_context=cache_context)

    client = SlowEmbeddings()
    retriever = EmbeddingRetriever(client)

    def retrieve(_):
        ready.wait(timeout=5)
        return retriever.retrieve("long", catalog, params=LinkParams())

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(retrieve, range(4)))
    assert all(result == results[0] for result in results)
    assert sum(len(texts) > 1 for texts, _, _ in client.calls) == 1
    assert len(client.calls) == 5  # one shared index and four query calls
