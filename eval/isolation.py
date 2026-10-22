"""Linux Landlock read allowlist, applied before starting the product process.

Restrictions are inherited across exec, including by native libraries and children.
Fail closed on unsupported hosts; this is file isolation, not a network sandbox.
"""

import ctypes
import os
import platform
import subprocess
from pathlib import Path

EXECUTE, READ_FILE, READ_DIR = 1, 4, 8
READ_ACCESS = EXECUTE | READ_FILE | READ_DIR


class _Ruleset(ctypes.Structure):
    _fields_ = [("handled_access_fs", ctypes.c_uint64)]


class _PathRule(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("allowed_access", ctypes.c_uint64), ("parent_fd", ctypes.c_int32)]


def restrict_reads(allowed: list[Path]) -> None:
    """Irreversibly restrict this process and its descendants to allowed paths."""
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "aarch64"}:
        raise RuntimeError("Product isolation requires Linux Landlock (x86_64/aarch64)")
    libc = ctypes.CDLL(None, use_errno=True)

    def checked(result: int) -> int:
        if result < 0:
            errno = ctypes.get_errno()
            raise OSError(errno, os.strerror(errno))
        return result

    ruleset = _Ruleset(READ_ACCESS)
    fd = checked(libc.syscall(444, ctypes.byref(ruleset), ctypes.sizeof(ruleset), 0))
    try:
        for path in allowed:
            resolved = path.resolve(strict=True)
            path_fd = os.open(resolved, os.O_PATH | os.O_CLOEXEC)
            try:
                access = READ_ACCESS if resolved.is_dir() else EXECUTE | READ_FILE
                rule = _PathRule(access, path_fd)
                checked(libc.syscall(445, fd, 1, ctypes.byref(rule), 0))
            finally:
                os.close(path_fd)
        checked(libc.prctl(38, 1, 0, 0, 0))  # PR_SET_NO_NEW_PRIVS
        checked(libc.syscall(446, fd, 0))
    finally:
        os.close(fd)


def run_product(root: Path, arguments: list[str]) -> int:
    """Run the backend interpreter with source/runtime inputs only."""
    root = root.resolve(strict=True)
    python = root / "backend/.venv/bin/python"
    # The uv interpreter can live outside both the repository and /usr.
    runtime = python.resolve(strict=True).parent.parent
    allowed = [runtime, root / "backend", root / "generated/sources"]
    for path in ["/usr", "/lib", "/lib64", "/bin", "/etc", "/dev"]:
        if Path(path).exists():
            allowed.append(Path(path))
    for relative in ["config", "data", ".env"]:
        path = root / relative
        if path.exists():
            allowed.append(path)
    # Run this CLI in a single-threaded process: preexec_fn installs the kernel
    # policy in the child before any product code or Python startup hooks run.
    return subprocess.run(
        [str(python), *arguments],
        cwd=root / "backend",
        env={**os.environ, "PYTHONPATH": str(root / "backend")},
        preexec_fn=lambda: restrict_reads(allowed),
        check=False,
    ).returncode
