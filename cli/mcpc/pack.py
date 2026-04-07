"""Pack an MCP Contract bundle into a .mcpc archive.

Validates the bundle first, then creates a zip archive with the .mcpc
extension containing all bundle files. The archive preserves the
directory structure relative to the bundle root.
"""

from __future__ import annotations

import json
import os
import sys
import zipfile
from pathlib import Path

from mcpc.validate import validate_bundle


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


# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------

# Files/directories to always exclude from the archive
EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".mypy_cache"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db"}


def _collect_files(bundle_dir: Path) -> list[Path]:
    """Collect all files in the bundle directory, excluding common junk."""
    files: list[Path] = []
    for root, dirs, filenames in os.walk(bundle_dir):
        # Prune excluded directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for name in filenames:
            if name in EXCLUDE_FILES:
                continue
            files.append(Path(root) / name)
    return sorted(files)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def pack_bundle(path: str, output: str | None = None, quiet: bool = False) -> bool:
    """Pack an MCP Contract bundle into a .mcpc archive. Returns True on success."""
    bundle_dir = Path(path).resolve()

    if not quiet:
        print(f"\n{_fmt(_BOLD, 'mcpc pack')} {bundle_dir}\n")

    # Step 1: Validate
    if not quiet:
        print(_info("validating bundle..."))

    valid = validate_bundle(str(bundle_dir), quiet=True)
    if not valid:
        print(_error("bundle validation failed — run 'mcpc validate' for details"))
        return False

    if not quiet:
        print(_ok("validation passed"))

    # Step 2: Determine output path
    manifest_path = bundle_dir / "mcp-contract.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    name = manifest.get("name", "bundle")
    version = manifest.get("version", "0.0.0")

    if output is not None:
        out_path = Path(output).resolve()
    else:
        out_path = bundle_dir.parent / f"{name}-{version}.mcpc"

    # Step 3: Collect files
    files = _collect_files(bundle_dir)

    if not quiet:
        print(_info(f"packing {len(files)} files..."))

    # Step 4: Create archive
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            arcname = file_path.relative_to(bundle_dir)
            zf.write(file_path, arcname)

    size_kb = out_path.stat().st_size / 1024

    if not quiet:
        print()
        print(_ok(f"created {out_path.name} ({size_kb:.1f} KB)"))
        print(_info(f"path: {out_path}"))
        print()

    return True
