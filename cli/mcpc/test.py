"""Run structural tests on MCP Contract bundle layers.

Tests go beyond validation to check layer content quality:
  - Prompt tests: YAML frontmatter, required fields, no tool name references
  - Tool tests: server entry point is syntactically valid Python/JS
  - Schema tests: schemas are well-formed with $id and description
  - App tests: entry point files are non-empty
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


_BOLD = "\033[1m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"
_RESET = "\033[0m"


def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _fmt(code: str, text: str) -> str:
    return f"{code}{text}{_RESET}" if _supports_color() else text


def _error(msg: str) -> str:
    return _fmt(_RED, f"  FAIL:  {msg}")


def _warn(msg: str) -> str:
    return _fmt(_YELLOW, f"  warn:  {msg}")


def _ok(msg: str) -> str:
    return _fmt(_GREEN, f"  pass:  {msg}")


def _info(msg: str) -> str:
    return _fmt(_CYAN, f"  info:  {msg}")


# ---------------------------------------------------------------------------
# Frontmatter parsing (stdlib only, no pyyaml)
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_YAML_KV_RE = re.compile(r"^(\w[\w-]*):\s*(.+)$", re.MULTILINE)


def _parse_frontmatter(text: str) -> dict[str, str] | None:
    """Parse simple YAML frontmatter (key: value pairs only)."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return None
    block = match.group(1)
    return dict(_YAML_KV_RE.findall(block))


# ---------------------------------------------------------------------------
# Layer tests
# ---------------------------------------------------------------------------

def _test_prompts(manifest: dict, bundle_dir: Path) -> tuple[list[str], list[str], int]:
    """Test prompt layer quality. Returns (failures, warnings, test_count)."""
    failures: list[str] = []
    warnings: list[str] = []
    tests = 0
    layers = manifest.get("layers", {})
    prompts = layers.get("prompts")
    if not prompts:
        return failures, warnings, tests

    # Collect all prompt files
    prompt_files = []
    if "entry" in prompts:
        prompt_files.append(prompts["entry"])
    for mod in prompts.get("modules", []):
        prompt_files.append(mod)

    for rel_path in prompt_files:
        full_path = bundle_dir / rel_path
        if not full_path.exists():
            continue  # File existence is checked by validate

        text = full_path.read_text(encoding="utf-8", errors="replace")

        # Test: has frontmatter
        tests += 1
        fm = _parse_frontmatter(text)
        if fm is None:
            failures.append(f"{rel_path}: missing YAML frontmatter")
            continue
        else:
            # Test: frontmatter has required fields
            tests += 1
            missing = [f for f in ("name", "version") if f not in fm]
            if missing:
                failures.append(f"{rel_path}: frontmatter missing fields: {', '.join(missing)}")

            # Test: has description
            tests += 1
            if "description" not in fm:
                warnings.append(f"{rel_path}: frontmatter missing 'description' (recommended)")

        # Test: no tool name references (function call patterns)
        tests += 1
        tool_refs = re.findall(r"\b\w+_\w+\(\)", text)
        if tool_refs:
            failures.append(
                f"{rel_path}: references tool names directly: {', '.join(tool_refs[:3])} "
                f"— prompts should use capability descriptions instead"
            )

        # Test: non-trivial content (beyond frontmatter)
        tests += 1
        body = _FRONTMATTER_RE.sub("", text).strip()
        if len(body) < 50:
            warnings.append(f"{rel_path}: prompt body is very short ({len(body)} chars)")

    return failures, warnings, tests


def _test_schemas(manifest: dict, bundle_dir: Path) -> tuple[list[str], list[str], int]:
    """Test schema quality. Returns (failures, warnings, test_count)."""
    failures: list[str] = []
    warnings: list[str] = []
    tests = 0
    layers = manifest.get("layers", {})

    # Collect all schema paths
    schema_paths: set[str] = set()
    for layer_name in ("prompts", "tools"):
        layer = layers.get(layer_name, {})
        for entry in layer.get("provides", []):
            if "schema" in entry:
                schema_paths.add(entry["schema"])
    apps = layers.get("apps", {})
    for entry in apps.get("consumes", []):
        if "schema" in entry:
            schema_paths.add(entry["schema"])

    for rel_path in sorted(schema_paths):
        full_path = bundle_dir / rel_path
        if not full_path.exists():
            continue  # Checked by validate

        try:
            with open(full_path) as f:
                schema = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue  # Checked by validate

        # Test: has $id
        tests += 1
        if "$id" not in schema:
            failures.append(f"{rel_path}: missing '$id' field (required by convention)")

        # Test: has description
        tests += 1
        if "description" not in schema:
            warnings.append(f"{rel_path}: missing 'description' field (recommended)")

        # Test: uses draft 2020-12
        tests += 1
        meta_schema = schema.get("$schema", "")
        if meta_schema and "2020-12" not in meta_schema:
            warnings.append(f"{rel_path}: uses '{meta_schema}' — convention is draft 2020-12")

        # Test: has type
        tests += 1
        if "type" not in schema:
            warnings.append(f"{rel_path}: missing top-level 'type' field")

    return failures, warnings, tests


def _test_tools(manifest: dict, bundle_dir: Path) -> tuple[list[str], list[str], int]:
    """Test tool layer quality. Returns (failures, warnings, test_count)."""
    failures: list[str] = []
    warnings: list[str] = []
    tests = 0
    layers = manifest.get("layers", {})
    tools = layers.get("tools")
    if not tools:
        return failures, warnings, tests

    entry = tools.get("entry")
    if not entry:
        return failures, warnings, tests

    full_path = bundle_dir / entry
    if not full_path.exists():
        return failures, warnings, tests

    # Test: Python files are syntactically valid
    if full_path.suffix == ".py":
        tests += 1
        source = full_path.read_text(encoding="utf-8", errors="replace")
        try:
            compile(source, str(full_path), "exec")
        except SyntaxError as e:
            failures.append(f"{entry}: Python syntax error at line {e.lineno}: {e.msg}")

    # Test: entry point is non-empty
    tests += 1
    if full_path.stat().st_size == 0:
        failures.append(f"{entry}: tool server entry point is empty")

    return failures, warnings, tests


def _test_apps(manifest: dict, bundle_dir: Path) -> tuple[list[str], list[str], int]:
    """Test app layer quality. Returns (failures, warnings, test_count)."""
    failures: list[str] = []
    warnings: list[str] = []
    tests = 0
    layers = manifest.get("layers", {})
    apps = layers.get("apps")
    if not apps:
        return failures, warnings, tests

    entry = apps.get("entry")
    if not entry:
        return failures, warnings, tests

    full_path = bundle_dir / entry
    if not full_path.exists():
        return failures, warnings, tests

    # Test: entry point is non-empty
    tests += 1
    if full_path.stat().st_size == 0:
        failures.append(f"{entry}: app entry point is empty")

    return failures, warnings, tests


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def test_bundle(path: str, layer: str | None = None, quiet: bool = False) -> bool:
    """Run structural tests on an MCP Contract bundle. Returns True if all pass."""
    bundle_dir = Path(path).resolve()
    manifest_path = bundle_dir / "mcp-contract.json"

    if not manifest_path.exists():
        print(_error(f"no mcp-contract.json found in {bundle_dir}"))
        return False

    if not quiet:
        print(f"\n{_fmt(_BOLD, 'mcpc test')} {bundle_dir}\n")

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        print(_error(f"mcp-contract.json is not valid JSON: {e}"))
        return False

    all_failures: list[str] = []
    all_warnings: list[str] = []
    total_tests = 0

    # Run layer tests
    test_runners = {
        "prompts": _test_prompts,
        "schemas": _test_schemas,
        "tools": _test_tools,
        "apps": _test_apps,
    }

    for name, runner in test_runners.items():
        if layer and name != layer:
            continue
        failures, warnings, count = runner(manifest, bundle_dir)
        all_failures.extend(failures)
        all_warnings.extend(warnings)
        total_tests += count

        if not quiet and count > 0:
            status = _fmt(_GREEN, "pass") if not failures else _fmt(_RED, "FAIL")
            print(f"  {name}: {count} tests — {status}")

    # Report
    print()
    for f in all_failures:
        print(_error(f))
    for w in all_warnings:
        print(_warn(w))

    if not quiet:
        print()
        passed = total_tests - len(all_failures)
        if all_failures:
            print(_fmt(_RED, f"  {passed}/{total_tests} passed, {len(all_failures)} failed"))
        else:
            print(_ok(f"{total_tests}/{total_tests} passed"))
        if all_warnings:
            print(_info(f"{len(all_warnings)} warning(s)"))
        print()

    return len(all_failures) == 0
