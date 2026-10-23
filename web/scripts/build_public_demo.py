"""Build an allowlisted public demo projection; never publish original DTOs or media."""

import argparse
import hashlib
import hmac
import json
import math
import os
import re
import shutil
import unicodedata
from pathlib import Path

import yaml

KINDS = ("SourceDocument", "Segment", "Observation", "Case", "Report")
NOTICE = "Synthetic example; names substituted. No real replay, ROI or causal result is certified."
PRIVATE = re.compile(
    r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\b[A-Za-z][A-Za-z0-9+.-]*://\S+|\bwww\.\S+"
    r"|(?<!\w)/(?:[\w.-]+/)+[\w.-]+|[A-Za-z]:\\\S+|(?:^|[\s(])\.{1,2}/\S+"
    r"|\b[\w.-]+\.(?:eml|msg|pdf|xlsx?|csv|docx?|pptx?|rtf|odt|ods|txt|json|zip|7z|rar|gz|tar"
    r"|wav|mp3|mp4|m4a|ogg|opus|webm|png|jpe?g|gif|webp|heic|heif|tiff?)\b"
    r"|\\\\[\w.$-]+\\|(?:^|[\s(])~/\S*"
    r"|\b(?:[a-z0-9-]+\.)+(?:com|net|org|it|fr|de|ch|uk|es|nl|dk|jp|kr|cn|hk|tw|sg|au|ae|io"
    r"|local|internal|corp|lan|example)\b"
    r"|\bAKIA[0-9A-Z]{16}\b"
    # Header lines of forwarded/quoted mail, in the dataset's languages. Ambiguous short words
    # ("Da:", "Data:", "A:") are left out: names and addresses are caught separately.
    r"|^\s*(?:from|to|cc|bcc|subject|date|sent|received|reply-to|message-id|return-path"
    r"|oggetto|inviato|von|gesendet|betreff|objet|envoyé|asunto|enviado|onderwerp|verzonden"
    r"|emne|sendt|发件人|收件人|主题|發件人|寄件者|收件者|主旨|差出人|宛先|件名|送信日時"
    r"|보낸 사람|받는 사람|제목|보낸 날짜)\s*[:：]"
    r"|</?[A-Za-z][^>]*>|\[[^\]]*\]\([^)]*\)"
    r"|\bsk-[A-Za-z0-9_-]{8,}|\bBearer\s+\S+|\b(?:api[_ -]?key|password|token)\s*[:=]\s*\S+",
    re.I | re.M,
)


class Excluded(ValueError):
    pass


_STORE_ID = re.compile(r"\b[A-Z]{3}\d{2}\b")


def folded(text):
    """Compatibility-normalized, case-folded text without invisible characters."""
    return "".join(
        c for c in unicodedata.normalize("NFKC", text) if unicodedata.category(c) != "Cf"
    ).casefold()


def squeezed(text):
    """Only letters and digits: a name split by hyphens, spaces or line breaks still matches."""
    return "".join(c for c in folded(text) if c.isalnum())


def encoded(value):
    return (
        json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    ).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


class Builder:
    def __init__(self, manifest, dev_stores):
        if manifest.get("version") != 1 or manifest.get("approved") is not True:
            raise ValueError("An explicitly approved version-1 manifest is required")
        stores = manifest.get("stores", [])
        if manifest.get("split") != "dev" or not stores or not set(stores) <= set(dev_stores):
            raise ValueError("Only explicitly selected dev stores are supported")
        key = manifest.get("reference_key", "")
        if not isinstance(key, str) or len(key) < 32:
            raise ValueError("Provide a private reference_key of at least 32 characters")
        self.key = key.encode()
        self.replacements = manifest.get("replacements", {})
        if not self.replacements or any(
            not isinstance(k, str) or not k or not isinstance(v, str)
            for k, v in self.replacements.items()
        ):
            raise ValueError("Provide explicit sensitive-to-fictional text replacements")
        self.stores = set(stores)
        self.residuals = [(folded(k), squeezed(k)) for k in self.replacements]
        self.pattern = re.compile(
            "|".join(re.escape(k) for k in sorted(self.replacements, key=lambda s: (-len(s), s)))
        )
        self.raw, self.public, self.documents, self.segments = {}, {}, {}, {}
        self.malformed = set()
        self.excluded, self.mapping = [], []
        self.identifiers = {}
        for item in manifest["artifacts"]:
            kind, payload = item["kind"], item["payload"]
            identity = (kind, payload["id"], payload["version"])
            if not all(isinstance(part, str) and part for part in identity) or identity in self.raw:
                raise ValueError("Artifact identities must be nonempty and unique")
            meta, scope = payload.get("meta", {}), payload.get("scope", {})
            store_ids = payload.get("store_ids", [])
            if (
                not isinstance(meta, dict)
                or not isinstance(scope, dict)
                or not isinstance(store_ids, list)
                or any(not isinstance(value, str) for value in store_ids)
            ):
                self.malformed.add(identity)
            else:
                declared = [payload.get("store_id"), meta.get("store_id"), scope.get("store_id")]
                declared = [value for value in declared if value is not None] + store_ids
                if any(not isinstance(value, str) for value in declared):
                    self.malformed.add(identity)
                elif not set(declared) <= self.stores:
                    raise ValueError("Artifact is outside the approved dev stores")
            self.raw[identity] = payload
            self.mapping.append(
                {
                    "original": list(identity),
                    "public": self.ref(identity),
                    "input_sha256": digest(encoded(payload)),
                }
            )

    def opaque(self, namespace, value):
        token = hmac.new(self.key, encoded([namespace, value]), hashlib.sha256).hexdigest()[:32]
        self.identifiers[token] = {"namespace": namespace, "original": value, "public": token}
        return token

    def ref(self, identity):
        return {
            "kind": identity[0] if identity[0] in KINDS else "unsupported",
            "id": self.opaque("artifact", identity),
            "version": "public-v1",
        }

    def text(self, value):
        if not isinstance(value, str):
            raise Excluded("invalid_text")
        out, boundaries, cursor, length = [], {0: 0}, 0, 0
        for match in self.pattern.finditer(value):
            before = value[cursor : match.start()]
            out.append(before)
            for index in range(cursor, match.start() + 1):
                boundaries[index] = length + index - cursor
            length += len(before)
            replacement = self.replacements[match.group()]
            out.append(replacement)
            length += len(replacement)
            boundaries[match.end()] = length
            cursor = match.end()
        out.append(value[cursor:])
        for index in range(cursor, len(value) + 1):
            boundaries[index] = length + index - cursor
        text = "".join(out)
        normal, compact = folded(text), squeezed(text)
        if PRIVATE.search(text) or PRIVATE.search(normal):
            raise Excluded("unresolved_sensitive_text")
        if any(
            key in normal or (len(short) >= 4 and short in compact) for key, short in self.residuals
        ):
            raise Excluded("unresolved_sensitive_text")
        if set(_STORE_ID.findall(normal.upper())) - self.stores:
            raise Excluded("store_outside_approved_split")
        return text, boundaries

    def scrub(self, value):
        return self.text(value)[0]

    def resolve(self, ref):
        identity = (ref["kind"], ref["id"], ref["version"])
        if identity not in self.public:
            raise Excluded("dangling_or_excluded_reference")
        return self.ref(identity)

    def span(self, document, start, end, text):
        raw, public, boundaries = self.documents[document]
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(raw):
            raise Excluded("invalid_source_offsets")
        if raw[start:end] != text:
            raise Excluded("source_quote_mismatch")
        if start not in boundaries or end not in boundaries or boundaries[start] == boundaries[end]:
            raise Excluded("boundary_inside_replacement")
        a, b = boundaries[start], boundaries[end]
        return a, b, public[a:b]

    def document_for_segment(self, payload):
        found = [
            identity
            for identity, source in self.raw.items()
            if identity[0] == "SourceDocument"
            and identity[1] == payload["document_id"]
            and identity in self.documents
            and source["text_version"] == payload["text_version"]
        ]
        if len(found) != 1:
            raise Excluded("ambiguous_or_excluded_document")
        return found[0]

    def project(self, identity, p):
        kind = identity[0]
        result = {"id": self.ref(identity)["id"], "version": "public-v1"}
        if kind == "SourceDocument":
            if not isinstance(p.get("text_version"), str) or not p["text_version"]:
                raise Excluded("malformed_artifact")
            store = p.get("meta", {}).get("store_id")
            if not store:
                raise Excluded("missing_dev_store")
            if p.get("source_type") not in {
                "email",
                "chat_message",
                "report",
                "external_feed",
                "clarification_reply",
            }:
                raise Excluded("unsupported_media")
            text, boundaries = self.text(p["text"])
            result.update(
                text=text,
                text_version=digest(text.encode())[:24],
                store_ref=self.opaque("store", store),
                source_type=p["source_type"],
            )
            self.documents[identity] = (p["text"], text, boundaries)
        elif kind == "Segment":
            doc = self.document_for_segment(p)
            a, b, text = self.span(doc, p["char_start"], p["char_end"], p["text"])
            result.update(
                document_ref=self.ref(doc),
                text_version=self.public[doc]["text_version"],
                text=text,
                char_start=a,
                char_end=b,
            )
            self.segments[identity] = (doc, a, b)
        elif kind == "Observation":
            evidence = []
            for e in p["evidence"]:
                doc = ("SourceDocument", e["document_id"], e["document_version"])
                segment = [
                    i
                    for i in self.segments
                    if i[1] == e["segment_id"] and self.segments[i][0] == doc
                ]
                if (
                    doc not in self.documents
                    or len(segment) != 1
                    or e["document_id"] != p["document_id"]
                ):
                    raise Excluded("dangling_or_excluded_evidence")
                a, b, quote = self.span(doc, e["char_start"], e["char_end"], e["quote"])
                _, start, end = self.segments[segment[0]]
                if not start <= a < b <= end:
                    raise Excluded("evidence_outside_segment")
                evidence.append(
                    {
                        "document_ref": self.ref(doc),
                        "segment_ref": self.ref(segment[0]),
                        "char_start": a,
                        "char_end": b,
                        "quote": quote,
                    }
                )
            if not evidence:
                raise Excluded("missing_public_evidence")
            result.update(observation_type=self.scrub(p["kind"]), evidence=evidence)
            for field in ("product_mention", "reason_text", "time_text"):
                if p.get(field) is not None:
                    result[field] = self.scrub(p[field])
            # Only already structured quantities; no totals, conversion or inference.
            quantity = p.get("quantity", {})
            if quantity:
                q = {}
                for field in ("kind", "unit", "currency", "raw"):
                    if quantity.get(field) is not None:
                        q[field] = self.scrub(quantity[field])
                for field in ("value", "low", "high"):
                    value = quantity.get(field)
                    if value is not None:
                        if (
                            isinstance(value, bool)
                            or not isinstance(value, (int, float))
                            or not math.isfinite(value)
                        ):
                            raise Excluded("invalid_quantity")
                        q[field] = value
                result["quantity"] = q
        elif kind == "Case":
            result.update(
                {
                    field: self.scrub(p[field])
                    for field in ("case_type", "status", "priority", "priority_reason")
                }
            )
            result["owner_ref"] = self.opaque("owner", p["owner"])
            for field in ("supporting", "contradicting", "context_refs"):
                result[field] = [self.resolve(ref) for ref in p.get(field, [])]
        elif kind == "Report":
            citations = []
            for citation in p["citations"]:
                scope = (citation.get("scope") or {}).get("store_id")
                if scope is not None and scope not in self.stores:
                    raise Excluded("store_outside_approved_split")
                ref = self.resolve(citation["ref"])
                item = {"ref": ref}
                field = citation.get("field")
                if field:
                    public = self.public[
                        (citation["ref"]["kind"], citation["ref"]["id"], citation["ref"]["version"])
                    ]
                    for part in field.split("."):
                        if not isinstance(public, dict) or part not in public:
                            raise Excluded("excluded_citation_field")
                        public = public[part]
                    item["field"] = field
                citations.append(item)
            if not citations:
                raise Excluded("missing_public_citations")
            markdown = self.scrub(p["markdown"])
            if any(not 1 <= int(n) <= len(citations) for n in re.findall(r"\[(\d+)\]", markdown)):
                raise Excluded("dangling_citation_number")
            result.update(markdown=markdown, citations=citations)
        return result

    def build(self):
        pending = sorted(
            self.raw, key=lambda i: (KINDS.index(i[0]) if i[0] in KINDS else len(KINDS), i)
        )
        # Cases and reports may cite each other: retry until no new artifact resolves, so the
        # result does not depend on the order of their ids.
        while True:
            failed = {}
            for identity in pending:
                try:
                    if identity in self.malformed:
                        raise Excluded("malformed_artifact")
                    if identity[0] not in KINDS:
                        raise Excluded("unsupported_artifact")
                    self.public[identity] = self.project(identity, self.raw[identity])
                except Excluded as error:
                    failed[identity] = str(error)
                except (KeyError, TypeError, AttributeError, ValueError):
                    failed[identity] = "malformed_artifact"
            if len(failed) == len(pending):
                break
            pending = list(failed)
        for identity, reason in failed.items():
            exclusion = {**self.ref(identity), "reason": reason}
            self.excluded.append({**exclusion, "descriptor_sha256": digest(encoded(exclusion))})
        artifacts = [{"kind": i[0], "payload": self.public[i]} for i in sorted(self.public)]
        public = encoded(artifacts)
        manifest = encoded(
            {
                "version": 1,
                "synthetic": True,
                "notice": NOTICE,
                "files": [{"path": "artifacts.json", "sha256": digest(public)}],
                "included": [
                    {**self.ref(i), "sha256": digest(encoded(self.public[i]))}
                    for i in sorted(self.public)
                ],
                "excluded": self.excluded,
                "projection_policy": "Documented fields only; other metadata and media omitted.",
            }
        )
        return {"artifacts.json": public, "manifest.json": manifest}, encoded(
            {
                "mapping": self.mapping,
                "replacements": self.replacements,
                "identifiers": [self.identifiers[key] for key in sorted(self.identifiers)],
            }
        )


def build_bundle(root, source, output, private_map):
    root, source = root.resolve(), source.resolve(strict=True)
    output, private_map = output.resolve(), private_map.resolve()
    if any(not p.is_relative_to(root / "data") for p in (source, output, private_map)):
        raise ValueError("Manifest, derived output and private map must be under data/")
    if source.is_relative_to(output) or private_map.is_relative_to(output) or source == private_map:
        raise ValueError("Original inputs and private mapping must stay outside public output")
    ignore = root / ".gitignore"
    versioned = [
        (root / line[1:].strip().rstrip("/")).resolve()
        for line in (ignore.read_text().splitlines() if ignore.exists() else [])
        if line.startswith("!data/")
    ]
    if any(p.is_relative_to(v) for p in (output, private_map) for v in versioned):
        raise ValueError("Output and private map must not be under a versioned data/ folder")
    data = json.loads(source.read_bytes())
    dev = yaml.safe_load((root / "config/eval_split.yaml").read_text())["dev"]
    files, mapping = Builder(data, dev).build()
    output.parent.mkdir(parents=True, exist_ok=True)
    private_map.parent.mkdir(parents=True, exist_ok=True)
    created = False
    with open(
        private_map, "x", encoding="utf-8", opener=lambda p, f: os.open(p, f, 0o600)
    ) as stream:
        try:
            output.mkdir()
            created = True
            for name, content in files.items():
                (output / name).write_bytes(content)
            stream.write(mapping.decode())
        except BaseException:
            if created:
                shutil.rmtree(output)
            private_map.unlink()
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--private-map", type=Path, required=True)
    args = parser.parse_args()
    build_bundle(Path(__file__).resolve().parents[2], args.manifest, args.output, args.private_map)
