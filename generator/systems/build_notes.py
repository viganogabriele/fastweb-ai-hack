"""Merge generator/systems/notes/*.md into generated/ground_truth/answer_keys/systems_notes.md"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

parts = [p.read_text(encoding="utf-8").strip() for p in sorted(C.NOTES.glob("*.md"))]
(C.GT / "answer_keys" / "systems_notes.md").write_text("\n\n".join(parts) + "\n", encoding="utf-8")
print("written", C.GT / "answer_keys" / "systems_notes.md", sum(len(p) for p in parts), "chars")
