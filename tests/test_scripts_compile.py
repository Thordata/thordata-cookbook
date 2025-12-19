from __future__ import annotations

import os
import py_compile
from pathlib import Path


def test_scripts_compile() -> None:
    """
    Ensure all Python scripts compile.

    This is a safe CI check for cookbook-style repos: it catches syntax errors
    without executing scripts (no network calls, no side effects).
    """
    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"

    if not scripts_dir.exists():
        # Cookbook might not have scripts; if so, keep this test non-blocking.
        return

    py_files = sorted(scripts_dir.rglob("*.py"))
    assert py_files, "No Python files found under scripts/"

    # Avoid environment-dependent failures in CI.
    os.environ.setdefault("PYTHONUTF8", "1")

    for f in py_files:
        py_compile.compile(str(f), doraise=True)
