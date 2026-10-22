"""Real child processes, fake secret files: no hidden dataset content is accessed."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from eval.isolation import restrict_reads, run_product


class IsolationTests(unittest.TestCase):
    def test_unsupported_platform_fails_closed(self):
        with patch("eval.isolation.platform.system", return_value="Darwin"):
            with self.assertRaisesRegex(RuntimeError, "requires Linux Landlock"):
                restrict_reads([])

    def test_native_reads_symlinks_and_descendants_are_denied(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "generated/sources"
            source.mkdir(parents=True)
            (source / "ok.txt").write_text("permitted")
            denied = []
            for relative in ["generated/ground_truth/key", "generator/answers", "eval/key"]:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("hidden test sentinel")
                denied.append(str(path))
            (source / "link").symlink_to(denied[0])
            denied.append(str(source / "link"))
            runtime = Path(sys.executable).resolve().parent.parent
            allowed = [source, runtime]
            allowed.extend(Path(p) for p in ["/usr", "/lib", "/lib64"] if Path(p).exists())
            code = """
import ctypes, os, pathlib, subprocess, sys
assert pathlib.Path(sys.argv[1], "ok.txt").read_text() == "permitted"
libc = ctypes.CDLL(None, use_errno=True)
for name in sys.argv[2:]:
    for reader in (lambda p: open(p).read(), pathlib.Path.read_text, os.open):
        try:
            if reader is os.open:
                reader(name, os.O_RDONLY)
            elif reader is pathlib.Path.read_text:
                reader(pathlib.Path(name))
            else:
                reader(name)
        except PermissionError:
            pass
        else:
            raise AssertionError("Readable: " + name)
    assert libc.open(name.encode(), 0) == -1
    assert ctypes.get_errno() == 13
child = subprocess.run([sys.executable, "-c",
    "import pathlib,sys; pathlib.Path(sys.argv[1]).read_text()", sys.argv[2]],
    capture_output=True, text=True)
assert child.returncode != 0 and "PermissionError" in child.stderr
"""
            result = subprocess.run(
                [sys.executable, "-S", "-c", code, str(source), *denied],
                preexec_fn=lambda: restrict_reads(allowed),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_product_starts_and_cannot_import_eval(self):
        root = Path(__file__).resolve().parents[2]
        code = """
from tessera.api.main import app
assert app is not None
try:
    open("../eval/harness.py")
except PermissionError:
    pass
else:
    raise AssertionError("Product can open eval code")
"""
        self.assertEqual(run_product(root, ["-c", code]), 0)
