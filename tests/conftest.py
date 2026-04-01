"""Shared fixtures for blogger tests."""

import subprocess
import shutil
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def hugo_bin():
    """Return path to hugo binary, skip if not installed."""
    hugo = shutil.which("hugo")
    if hugo is None:
        pytest.skip("hugo not installed")
    return hugo


@pytest.fixture(scope="session")
def hugo_build(hugo_bin, tmp_path_factory):
    """Run hugo build once per session and return the public/ directory."""
    dest = tmp_path_factory.mktemp("public")
    result = subprocess.run(
        [hugo_bin, "build", "-d", str(dest)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "public_dir": dest,
    }
