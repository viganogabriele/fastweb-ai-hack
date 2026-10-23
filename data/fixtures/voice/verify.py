"""Verify DATA-03 fixtures, or record/replay src.voice into an isolated evidence DB.

Run from the repository root with backend/.venv/bin/python. No provider call is made
unless --mode record is explicitly selected. Evidence and cache remain gitignored.
"""

import argparse
import hashlib
import json
import socket
import wave
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from tessera.core.config import REPO_ROOT, MissingApiKey, Settings
from tessera.core.contracts import ModuleSnapshot, RunSpec, Segment, SourceDocument
from tessera.core.db import connect
from tessera.core.llm import LLMClient
from tessera.core.orchestrator import run
from tessera.core.registry import RegisteredModule, Registry
from tessera.core.run_repo import repo_session
from tessera.modules.sources import voice

AS_OF = "2026-10-22T20:00:00+00:00"
ROOT = Path(__file__).resolve().parent


def no_network(*args, **kwargs):
    raise RuntimeError("network forbidden during offline replay")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", choices=("check", "record", "replay"), default="check"
    )
    parser.add_argument(
        "--env-file", type=Path, help="load existing config through Settings"
    )
    args = parser.parse_args()
    settings = Settings(**({"_env_file": args.env_file} if args.env_file else {}))
    # Cache/evidence belong to this checkout, even if config is reused from another one.
    settings = settings.model_copy(
        update={
            "data_dir": REPO_ROOT / "data",
            "llm_mode": args.mode if args.mode != "check" else "replay",
        }
    )
    notes = [voice.read_sidecar(p.parent) for p in sorted(ROOT.glob("*/note.json"))]
    if len(notes) != 3:
        raise ValueError("expected exactly the three DATA-03 notes")
    evidence = {"as_of": AS_OF, "mode": args.mode, "notes": []}
    for note in notes:
        audio = voice.load_audio(note)
        manual = voice.manual_transcript(note)
        with wave.open(str(audio.path)) as wav:
            duration = wav.getnframes() / wav.getframerate()
            if wav.getnchannels() != 1 or wav.getframerate() != 16000:
                raise ValueError(f"{note.slug}: expected mono 16 kHz audio")
        if abs(duration - note.sidecar.duration_s) > 0.1:
            raise ValueError(f"{note.slug}: duration disagrees with sidecar")
        if note.sidecar.sent_at > datetime.fromisoformat(AS_OF):
            raise ValueError(f"{note.slug}: note is unavailable at verification as_of")
        document, segments = voice.declared_document(note, audio)
        for segment in segments:
            segment.validate_against(document)
            if segment.t_start_s is not None or segment.t_end_s is not None:
                raise ValueError("manual fallback must have no timestamps")
        evidence["notes"].append(
            {
                "note_id": note.slug,
                "store_id": note.sidecar.store_id,
                "fixture_kind": note.sidecar.fixture_kind,
                "sent_at": note.sidecar.sent_at.isoformat(),
                "audio_sha256": audio.sha256,
                "duration_s": duration,
                "manual_transcript_sha256": document.meta["manual_transcript_sha256"],
                "manual_text": manual,
            }
        )
    if args.mode == "check":
        print(json.dumps(evidence, ensure_ascii=False, indent=2))
        return 0
    if args.mode == "record":
        try:
            settings.asr_key()
        except MissingApiKey:
            print(
                "BLOCKED: Settings.asr_key() has no ASR credential; no recording attempted"
            )
            return 2
    else:
        # A cached response must suffice: deny socket connections, including accidental ones.
        socket.socket.connect = no_network
        socket.create_connection = no_network
    output = settings.data_dir / "voice_verification"
    output.mkdir(parents=True, exist_ok=True)
    spec = RunSpec(
        run_id=f"ing03b-{args.mode}-{uuid4()}",
        scenario_id="data03-synthetic-voice-verification",
        as_of=AS_OF,
        stores=("MIL01", "MIL02"),
        source_manifest_hash=hashlib.sha256(
            "".join((n.directory / "note.json").read_text() for n in notes).encode()
        ).hexdigest(),
        config_hash="ing03b-voice-only-v1",
        code_version="src.voice-v1",
        mode="live" if args.mode == "record" else "recorded",
        modules=(ModuleSnapshot(manifest=voice.MANIFEST, params={"mode": "recorded"}),),
        prompt_versions={},
        model_versions={"asr": settings.asr_model},
        authorized_fixture_refs=(),
    )
    client = LLMClient(settings)
    engine = connect(f"sqlite:///{output / 'runs.db'}")
    registry = Registry(
        (RegisteredModule(voice.MANIFEST, lambda ctx: voice.run(ctx, voice_dir=ROOT)),)
    )
    (status,) = run(
        spec, engine=engine, registry=registry, clients={"llm": client.for_run(spec)}
    )
    with repo_session(engine, spec) as repo:
        documents = repo.list(SourceDocument)
        segments = repo.list(Segment)
    evidence.update(
        spec=spec.model_dump(mode="json"),
        module=status.model_dump(mode="json"),
        documents=[d.model_dump(mode="json") for d in documents],
        segments=[s.model_dump(mode="json") for s in segments],
        traces=client.traces,
    )
    evidence_path = output / f"{spec.run_id}.json"
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    print(f"Published evidence: {evidence_path}")
    print(f"Cache: {client.cache.directory}")
    # An unusable real response may explicitly fall back, but a missing response cannot pass.
    calls = client.traces
    result = status.result
    if (
        result is None
        or result.errors
        or len(documents) != len(notes)
        or len(calls) != len(notes)
        or any(not (t.get("cache_hit") or t.get("status") == 200) for t in calls)
        or any("UnusableTranscript" not in reason for reason in result.abstentions)
    ):
        print("INCOMPLETE: inspect evidence for explicit ASR fallback reasons")
        return 1
    by_id = {d.id: d for d in documents}
    for segment in segments:
        segment.validate_against(by_id[segment.document_id])
        if by_id[segment.document_id].meta["transcript_mode"] == "fixture":
            if segment.t_start_s is not None or segment.t_end_s is not None:
                raise ValueError("manual fallback must have no timestamps")
            if not any(
                by_id[segment.document_id].uri in reason
                for reason in result.abstentions
            ):
                raise ValueError("manual fallback must have an explicit reason")
            continue
        duration = next(
            n["duration_s"]
            for n in evidence["notes"]
            if f"doc-voice-{n['note_id']}" == segment.document_id
        )
        if not (0 <= segment.t_start_s < segment.t_end_s <= duration):
            print("INCOMPLETE: ASR interval is unusable; inspect evidence")
            return 1
    print(
        f"Verified {len(calls)} cached ASR responses: "
        f"{result.counts['recorded']} recorded notes, "
        f"{result.counts['declared']} explicit interval fallbacks; compare evidence manually"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
