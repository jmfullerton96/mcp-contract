"""Unpack a .mcpc archive into a bundle directory.

Extracts the archive, verifies it contains a valid mcp-contract.json
at the root, and optionally validates the extracted bundle.
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path


_BOLD = "\033[1m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"
_RESET = "\033[0m"


def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _fmt(code: str, text: str) -> str:
    return f"{code}{text}{_RESET}" if _supports_color() else text


def _error(msg: str) -> str:
    return _fmt(_RED, f"  error: {msg}")


def _info(msg: str) -> str:
    return _fmt(_CYAN, f"  info:  {msg}")


def _ok(msg: str) -> str:
    return _fmt(_GREEN, f"  ok:    {msg}")


def unpack_bundle(archive: str, output: str | None = None, quiet: bool = False) -> bool:
    """Unpack a .mcpc archive. Returns True on success."""
    archive_path = Path(archive).resolve()

    if not archive_path.exists():
        print(_error(f"file not found: {archive_path}"))
        return False

    if not zipfile.is_zipfile(archive_path):
        print(_error(f"not a valid zip archive: {archive_path}"))
        return False

    if not quiet:
        print(f"\n{_fmt(_BOLD, 'mcpc unpack')} {archive_path}\n")

    # Determine output directory
    if output is not None:
        out_dir = Path(output).resolve()
    else:
        # Strip -version.mcpc to get a clean directory name
        stem = archive_path.stem  # e.g. "due-diligence-0.1.0"
        out_dir = Path.cwd() / stem

    if out_dir.exists():
        print(_error(f"output directory already exists: {out_dir}"))
        return False

    # Verify archive contains mcp-contract.json at root
    with zipfile.ZipFile(archive_path, "r") as zf:
        names = zf.namelist()

        if "mcp-contract.json" not in names:
            print(_error("archive does not contain mcp-contract.json at root"))
            return False

        # Check archive integrity
        bad = zf.testzip()
        if bad is not None:
            print(_error(f"corrupt file in archive: {bad}"))
            return False

        # Read manifest for summary
        manifest_data = zf.read("mcp-contract.json")
        try:
            manifest = json.loads(manifest_data)
        except json.JSONDecodeError:
            print(_error("mcp-contract.json in archive is not valid JSON"))
            return False

        # Extract
        zf.extractall(out_dir)

    name = manifest.get("name", "?")
    version = manifest.get("version", "?")
    file_count = len(names)

    if not quiet:
        print(_ok(f"unpacked {name}@{version} ({file_count} files)"))
        print(_info(f"path: {out_dir}"))
        print()

    return True
