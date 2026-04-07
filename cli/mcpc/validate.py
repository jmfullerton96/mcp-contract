"""MCP Contract bundle validation.

Validates a bundle directory against the MCP Contract specification:
  1. Manifest structure — required fields, types, patterns, enums
  2. Contract coverage — every consumes has a matching provides
  3. File integrity — all referenced paths exist and parse correctly
  4. Schema validity — referenced JSON Schema files are valid JSON
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

_BOLD = "\033[1m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"
_RESET = "\033[0m"


def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _fmt(code: str, text: str) -> str:
    if _supports_color():
        return f"{code}{text}{_RESET}"
    return text


def _error(msg: str) -> str:
    return _fmt(_RED, f"  error: {msg}")


def _warn(msg: str) -> str:
    return _fmt(_YELLOW, f"  warn:  {msg}")


def _info(msg: str) -> str:
    return _fmt(_CYAN, f"  info:  {msg}")


def _ok(msg: str) -> str:
    return _fmt(_GREEN, f"  ok:    {msg}")


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------

VALID_LAYERS = {"prompts", "tools", "apps", "skills"}
VALID_RUNTIMES = {"node", "python", "go", "rust"}
VALID_CHAIN_ITEMS = {"prompts", "tools", "apps"}
NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+")


def _check_type(value, expected_type: type, path: str, errors: list) -> bool:
    if not isinstance(value, expected_type):
        errors.append(f"{path}: expected {expected_type.__name__}, got {type(value).__name__}")
        return False
    return True


def _validate_contract_entries(entries, label: str, errors: list) -> list[dict]:
    """Validate provides/consumes contract entries. Returns valid entries."""
    valid = []
    if not isinstance(entries, list):
        errors.append(f"{label}: expected array")
        return valid
    for i, entry in enumerate(entries):
        entry_path = f"{label}[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{entry_path}: expected object")
            continue
        if "name" not in entry:
            errors.append(f"{entry_path}: missing required field 'name'")
        elif not isinstance(entry["name"], str):
            errors.append(f"{entry_path}.name: expected string")
        if "schema" not in entry:
            errors.append(f"{entry_path}: missing required field 'schema'")
        elif not isinstance(entry["schema"], str):
            errors.append(f"{entry_path}.schema: expected string")
        valid.append(entry)
    return valid


def _validate_manifest_structure(manifest: dict) -> tuple[list[str], list[str]]:
    """Validate manifest against the schema structurally. Returns (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    # --- Required top-level fields ---
    for field in ("name", "version", "layers"):
        if field not in manifest:
            errors.append(f"missing required field '{field}'")

    # --- name ---
    name = manifest.get("name")
    if isinstance(name, str) and not NAME_PATTERN.match(name):
        errors.append(f"name '{name}' must be lowercase alphanumeric with hyphens only")

    # --- version ---
    version = manifest.get("version")
    if isinstance(version, str) and not VERSION_PATTERN.match(version):
        errors.append(f"version '{version}' must follow semver (MAJOR.MINOR.PATCH)")

    # --- author ---
    author = manifest.get("author")
    if author is not None:
        if _check_type(author, dict, "author", errors):
            if "name" not in author:
                errors.append("author: missing required field 'name'")

    # --- layers ---
    layers = manifest.get("layers")
    if not isinstance(layers, dict):
        return errors, warnings

    unknown_layers = set(layers.keys()) - VALID_LAYERS
    for layer in unknown_layers:
        errors.append(f"layers: unknown layer '{layer}'")

    # --- prompts layer ---
    prompts = layers.get("prompts")
    if prompts is not None:
        if _check_type(prompts, dict, "layers.prompts", errors):
            if "entry" not in prompts:
                errors.append("layers.prompts: missing required field 'entry'")
            modules = prompts.get("modules")
            if modules is not None and not isinstance(modules, list):
                errors.append("layers.prompts.modules: expected array")
            if "provides" in prompts:
                _validate_contract_entries(prompts["provides"], "layers.prompts.provides", errors)

    # --- tools layer ---
    tools = layers.get("tools")
    if tools is not None:
        if _check_type(tools, dict, "layers.tools", errors):
            if "entry" not in tools:
                errors.append("layers.tools: missing required field 'entry'")
            runtime = tools.get("runtime")
            if runtime is not None and runtime not in VALID_RUNTIMES:
                errors.append(
                    f"layers.tools.runtime: '{runtime}' not in {sorted(VALID_RUNTIMES)}"
                )
            if "provides" in tools:
                _validate_contract_entries(tools["provides"], "layers.tools.provides", errors)

    # --- apps layer ---
    apps = layers.get("apps")
    if apps is not None:
        if _check_type(apps, dict, "layers.apps", errors):
            if "entry" not in apps:
                errors.append("layers.apps: missing required field 'entry'")
            if "consumes" in apps:
                _validate_contract_entries(apps["consumes"], "layers.apps.consumes", errors)

    # --- skills layer ---
    skills = layers.get("skills")
    if skills is not None:
        if _check_type(skills, dict, "layers.skills", errors):
            if "targets" not in skills:
                errors.append("layers.skills: missing required field 'targets'")
            elif not isinstance(skills["targets"], dict):
                errors.append("layers.skills.targets: expected object")

    # --- compose ---
    compose = manifest.get("compose")
    if compose is not None and isinstance(compose, dict):
        chain = compose.get("chain")
        if chain is not None:
            if isinstance(chain, list):
                for item in chain:
                    if item not in VALID_CHAIN_ITEMS:
                        errors.append(f"compose.chain: '{item}' not in {sorted(VALID_CHAIN_ITEMS)}")
            else:
                errors.append("compose.chain: expected array")

    # --- extends ---
    extends = manifest.get("extends")
    if extends is not None:
        if isinstance(extends, list):
            for i, ext in enumerate(extends):
                ext_path = f"extends[{i}]"
                if isinstance(ext, dict):
                    for field in ("package", "version", "layer"):
                        if field not in ext:
                            errors.append(f"{ext_path}: missing required field '{field}'")
                    layer = ext.get("layer")
                    if isinstance(layer, str) and layer not in VALID_LAYERS:
                        errors.append(f"{ext_path}.layer: '{layer}' not in {sorted(VALID_LAYERS)}")
                else:
                    errors.append(f"{ext_path}: expected object")
        else:
            errors.append("extends: expected array")

    return errors, warnings


def _validate_contracts(manifest: dict) -> tuple[list[str], list[str]]:
    """Check that every consumes entry has a matching provides entry."""
    errors: list[str] = []
    warnings: list[str] = []
    layers = manifest.get("layers", {})

    provided: dict[str, str] = {}  # name -> providing layer
    consumed: dict[str, str] = {}  # name -> consuming layer

    for layer_name in ("prompts", "tools"):
        layer = layers.get(layer_name, {})
        for entry in layer.get("provides", []):
            name = entry.get("name")
            if name:
                if name in provided:
                    warnings.append(
                        f"contract '{name}' provided by both "
                        f"'{provided[name]}' and '{layer_name}'"
                    )
                provided[name] = layer_name

    apps = layers.get("apps", {})
    for entry in apps.get("consumes", []):
        name = entry.get("name")
        if name:
            consumed[name] = "apps"

    # Check which layers are covered by extends
    extended_layers: set[str] = set()
    for ext in manifest.get("extends", []):
        layer = ext.get("layer")
        if layer:
            extended_layers.add(layer)

    for name, consumer in consumed.items():
        if name not in provided:
            if extended_layers & {"prompts", "tools"}:
                warnings.append(
                    f"{consumer} consumes '{name}' — expected from extended package "
                    f"(not locally provided)"
                )
            else:
                errors.append(
                    f"{consumer} consumes '{name}' but no layer provides it"
                )

    # Warn about provided-but-not-consumed (informational, not an error)
    for name, provider in provided.items():
        if name not in consumed:
            warnings.append(
                f"'{provider}' provides '{name}' but no layer consumes it "
                f"(may flow through prompt reasoning)"
            )

    return errors, warnings


def _load_schema(bundle_dir: Path, rel_path: str) -> dict | None:
    """Load and parse a JSON Schema file. Returns None on failure."""
    full_path = bundle_dir / rel_path
    if not full_path.exists():
        return None
    try:
        with open(full_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _check_schema_compatibility(
    provider_schema: dict,
    consumer_schema: dict,
    path: str = "",
) -> list[str]:
    """Check that a consumer schema is satisfiable by a provider schema.

    Returns a list of incompatibility descriptions. An empty list means
    the schemas are compatible.

    Compatibility means: any data valid under the provider schema can be
    consumed by the consumer schema. Concretely:
      - Every required field in the consumer must exist in the provider
      - Field types must match
      - Nested objects are checked recursively
      - Enum values in the consumer must be a subset of the provider's
    """
    issues: list[str] = []
    prefix = f"{path}." if path else ""

    # Type compatibility
    p_type = provider_schema.get("type")
    c_type = consumer_schema.get("type")
    if p_type and c_type and p_type != c_type:
        issues.append(f"{prefix}type: provider is '{p_type}', consumer expects '{c_type}'")
        return issues  # No point checking deeper if types differ

    # Enum compatibility — consumer values must be subset of provider
    p_enum = provider_schema.get("enum")
    c_enum = consumer_schema.get("enum")
    if c_enum and p_enum:
        extra = set(c_enum) - set(p_enum)
        if extra:
            issues.append(f"{prefix}enum: consumer expects values {sorted(extra)} not in provider")

    # Object property compatibility
    if c_type == "object" or (not c_type and "properties" in consumer_schema):
        c_props = consumer_schema.get("properties", {})
        p_props = provider_schema.get("properties", {})
        c_required = set(consumer_schema.get("required", []))

        # Every required field in consumer must exist in provider
        for field in c_required:
            if field not in p_props:
                issues.append(f"{prefix}{field}: required by consumer but not in provider schema")

        # Recursively check shared properties
        for field, c_field_schema in c_props.items():
            if field in p_props:
                issues.extend(
                    _check_schema_compatibility(p_props[field], c_field_schema, f"{prefix}{field}")
                )

    # Array item compatibility
    if c_type == "array" or (not c_type and "items" in consumer_schema):
        c_items = consumer_schema.get("items")
        p_items = provider_schema.get("items")
        if c_items and p_items and isinstance(c_items, dict) and isinstance(p_items, dict):
            issues.extend(
                _check_schema_compatibility(p_items, c_items, f"{prefix}items")
            )

    return issues


def _validate_schema_compatibility(
    manifest: dict, bundle_dir: Path
) -> tuple[list[str], list[str]]:
    """Check structural compatibility between matched provides/consumes schemas."""
    errors: list[str] = []
    warnings: list[str] = []
    layers = manifest.get("layers", {})

    # Build provides map: name -> (layer, schema_path)
    provides_map: dict[str, tuple[str, str]] = {}
    for layer_name in ("prompts", "tools"):
        layer = layers.get(layer_name, {})
        for entry in layer.get("provides", []):
            name = entry.get("name")
            schema = entry.get("schema")
            if name and schema:
                provides_map[name] = (layer_name, schema)

    # Check each consumes entry against its provider
    apps = layers.get("apps", {})
    for entry in apps.get("consumes", []):
        name = entry.get("name")
        c_schema_path = entry.get("schema")
        if not name or not c_schema_path or name not in provides_map:
            continue

        p_layer, p_schema_path = provides_map[name]
        p_schema = _load_schema(bundle_dir, p_schema_path)
        c_schema = _load_schema(bundle_dir, c_schema_path)

        if p_schema is None or c_schema is None:
            continue  # File errors caught by _validate_files

        issues = _check_schema_compatibility(p_schema, c_schema)
        for issue in issues:
            errors.append(f"schema incompatibility for '{name}' ({p_layer} → apps): {issue}")

    return errors, warnings


def _validate_files(manifest: dict, bundle_dir: Path) -> tuple[list[str], list[str]]:
    """Check that all referenced files exist and JSON files parse."""
    errors: list[str] = []
    warnings: list[str] = []
    layers = manifest.get("layers", {})

    files_to_check: list[tuple[str, str]] = []  # (path, label)

    # Prompt layer
    prompts = layers.get("prompts", {})
    if "entry" in prompts:
        files_to_check.append((prompts["entry"], "layers.prompts.entry"))
    for mod in prompts.get("modules", []):
        files_to_check.append((mod, "layers.prompts.modules"))

    # Tool layer
    tools = layers.get("tools", {})
    if "entry" in tools:
        files_to_check.append((tools["entry"], "layers.tools.entry"))
    if "dependencies" in tools:
        files_to_check.append((tools["dependencies"], "layers.tools.dependencies"))

    # App layer
    apps = layers.get("apps", {})
    if "entry" in apps:
        files_to_check.append((apps["entry"], "layers.apps.entry"))
    for mod in apps.get("modules", []):
        files_to_check.append((mod, "layers.apps.modules"))

    # Skill layer
    skills = layers.get("skills", {})
    for target, path in skills.get("targets", {}).items():
        files_to_check.append((path, f"layers.skills.targets.{target}"))

    # Schema files from contracts
    schema_files: list[tuple[str, str]] = []
    for entry in prompts.get("provides", []):
        if "schema" in entry:
            schema_files.append((entry["schema"], f"prompts.provides[{entry.get('name', '?')}].schema"))
    for entry in tools.get("provides", []):
        if "schema" in entry:
            schema_files.append((entry["schema"], f"tools.provides[{entry.get('name', '?')}].schema"))
    for entry in apps.get("consumes", []):
        if "schema" in entry:
            schema_files.append((entry["schema"], f"apps.consumes[{entry.get('name', '?')}].schema"))

    # Check existence
    for rel_path, label in files_to_check:
        full_path = bundle_dir / rel_path
        if not full_path.exists():
            errors.append(f"file not found: {rel_path} (referenced by {label})")

    # Check schema files exist and are valid JSON
    seen_schemas: set[str] = set()
    for rel_path, label in schema_files:
        full_path = bundle_dir / rel_path
        if not full_path.exists():
            errors.append(f"schema not found: {rel_path} (referenced by {label})")
        elif rel_path not in seen_schemas:
            seen_schemas.add(rel_path)
            try:
                with open(full_path) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                errors.append(f"invalid JSON in {rel_path}: {e}")

    return errors, warnings


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_bundle(path: str, quiet: bool = False) -> bool:
    """Validate an MCP Contract bundle. Returns True if valid."""
    bundle_dir = Path(path).resolve()
    manifest_path = bundle_dir / "mcp-contract.json"

    if not manifest_path.exists():
        print(_error(f"no mcp-contract.json found in {bundle_dir}"))
        return False

    if not quiet:
        print(f"\n{_fmt(_BOLD, 'mcpc validate')} {bundle_dir}\n")

    # Parse manifest
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        print(_error(f"mcp-contract.json is not valid JSON: {e}"))
        return False

    all_errors: list[str] = []
    all_warnings: list[str] = []

    # 1. Structural validation
    errors, warnings = _validate_manifest_structure(manifest)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # 2. Contract coverage (only if structure is sound enough)
    if "layers" in manifest and isinstance(manifest["layers"], dict):
        errors, warnings = _validate_contracts(manifest)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    # 3. File integrity
    if "layers" in manifest and isinstance(manifest["layers"], dict):
        errors, warnings = _validate_files(manifest, bundle_dir)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    # 4. Schema compatibility
    if "layers" in manifest and isinstance(manifest["layers"], dict):
        errors, warnings = _validate_schema_compatibility(manifest, bundle_dir)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    # Report
    for e in all_errors:
        print(_error(e))
    for w in all_warnings:
        print(_warn(w))

    if not quiet:
        # Summary
        name = manifest.get("name", "?")
        version = manifest.get("version", "?")
        layers = manifest.get("layers", {})
        provided = set()
        consumed = set()
        for layer in ("prompts", "tools"):
            for entry in layers.get(layer, {}).get("provides", []):
                provided.add(entry.get("name", "?"))
        for entry in layers.get("apps", {}).get("consumes", []):
            consumed.add(entry.get("name", "?"))

        print()
        if not all_errors:
            print(_ok(f"{name}@{version} is valid"))
            print(_info(f"provides: {', '.join(sorted(provided))}"))
            print(_info(f"consumes: {', '.join(sorted(consumed)) or '(none)'}"))
            active_layers = [l for l in ("prompts", "tools", "apps", "skills") if l in layers]
            print(_info(f"layers:   {', '.join(active_layers)}"))
        else:
            print(_fmt(_RED, f"  {name}@{version} has {len(all_errors)} error(s)"))

        if all_warnings:
            print(_info(f"{len(all_warnings)} warning(s)"))
        print()

    return len(all_errors) == 0
