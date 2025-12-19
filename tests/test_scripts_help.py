import subprocess
import sys
from pathlib import Path


def _run_help(script: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    assert result.returncode == 0, (result.stdout or "") + "\n" + (result.stderr or "")


def test_rag_data_pipeline_help() -> None:
    script = Path("scripts/rag_data_pipeline.py")
    if script.exists():
        _run_help(script)


def test_mcp_server_help() -> None:
    script = Path("scripts/mcp_server.py")
    if script.exists():
        _run_help(script)