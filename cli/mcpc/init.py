"""Scaffold a new MCP Contract bundle."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


_BOLD = "\033[1m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"
_RESET = "\033[0m"


def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _fmt(code: str, text: str) -> str:
    return f"{code}{text}{_RESET}" if _supports_color() else text


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

TEMPLATES = {
    "full": {
        "description": "Complete bundle with all layers (prompts, tools, apps, skills)",
        "layers": ["prompts", "tools", "apps", "skills", "schemas"],
    },
    "prompts-only": {
        "description": "Minimal bundle with prompts layer only — no tools, apps, or skills",
        "layers": ["prompts", "schemas"],
    },
}


def _make_manifest(name: str, template: str) -> dict:
    manifest: dict = {
        "$schema": "https://mcp-contract.dev/schema/0.1.0.json",
        "name": name,
        "version": "0.1.0",
        "description": "",
        "author": {"name": ""},
        "license": "Apache-2.0",
        "layers": {},
    }

    layers = manifest["layers"]

    if template in ("full", "prompts-only"):
        layers["prompts"] = {
            "entry": "prompts/main.md",
            "provides": [
                {
                    "name": f"{name}-output",
                    "schema": f"schemas/{name}-output.json",
                    "description": f"Output shape for {name} workflow.",
                }
            ],
        }

    if template == "full":
        layers["tools"] = {
            "entry": "tools/server.py",
            "runtime": "python",
            "provides": [
                {
                    "name": f"{name}-data",
                    "schema": f"schemas/{name}-data.json",
                    "description": f"Data provided by {name} tool server.",
                }
            ],
        }
        layers["apps"] = {
            "entry": "apps/main.html",
            "consumes": [
                {
                    "name": f"{name}-data",
                    "schema": f"schemas/{name}-data.json",
                },
                {
                    "name": f"{name}-output",
                    "schema": f"schemas/{name}-output.json",
                },
            ],
        }
        layers["skills"] = {
            "targets": {
                "claude": "skills/claude.md",
            }
        }
        manifest["compiler_compatibility"] = ["claude"]
        manifest["compose"] = {
            "chain": ["prompts", "tools", "apps"],
            "fallback": "prompts-only",
        }
    else:
        manifest["compiler_compatibility"] = ["claude", "gpt", "gemini"]
        manifest["compose"] = {
            "chain": ["prompts"],
            "fallback": "prompts-only",
        }

    return manifest


def _make_schema(name: str, title: str, description: str) -> dict:
    return {
        "$id": f"https://mcp-contract.dev/schemas/{name}/0.1.0",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": title,
        "description": description,
        "type": "object",
        "required": [],
        "properties": {},
    }


def _make_prompt(bundle_name: str, provides_name: str) -> str:
    return f"""---
name: {bundle_name}
version: 0.1.0
description: Primary methodology for {bundle_name}.
provides: {provides_name}
---

# {bundle_name.replace('-', ' ').title()}

Describe your workflow's reasoning methodology here.

## Methodology

1. **Step one** — What to analyze first.
2. **Step two** — How to structure the analysis.
3. **Step three** — What output to produce.

## Output Shape

The analysis produces structured output conforming to the
`{provides_name}` schema.
"""


def _make_tool_stub(bundle_name: str) -> str:
    return f'''"""
{bundle_name} MCP Tool Server (Stub)

Implement your MCP tools here. Each tool should:
  - Declare typed input/output schemas in schemas/
  - Not embed reasoning logic (that belongs in prompts/)
  - Not assume a specific prompt or app layer
"""
'''


def _make_app_stub(bundle_name: str) -> str:
    return f"""<!--
  {bundle_name} App (Stub)

  Implement your interactive view here. The app should:
    - Declare every schema it consumes in the manifest
    - Not call external APIs directly (data flows through tools)
    - Be renderable with mock data for independent testing
-->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{bundle_name.replace('-', ' ').title()}</title>
</head>
<body>
  <h1>{bundle_name.replace('-', ' ').title()}</h1>
</body>
</html>
"""


def _make_skill(bundle_name: str) -> str:
    return f"""---
target: claude
version: 0.1.0
---

# Claude Platform Skill

Platform-specific adaptation for running {bundle_name} on Claude.

## Tool Registration

Register the tool server via MCP stdio transport in Claude Desktop config.

## Context Window

Estimate your prompt chain token count here. Claude Opus supports 200k context.

## Graceful Degradation

If the tool server is unavailable, the prompt layer should still produce
useful output from the LLM's training data.
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def init_bundle(name: str, path: str, template: str) -> bool:
    """Scaffold a new MCP Contract bundle. Returns True on success."""
    bundle_dir = Path(path).resolve() / name

    if bundle_dir.exists():
        print(f"  error: {bundle_dir} already exists", file=sys.stderr)
        return False

    tmpl = TEMPLATES[template]
    manifest = _make_manifest(name, template)

    print(f"\n{_fmt(_BOLD, 'mcpc init')} {name} ({tmpl['description']})\n")

    # Create directories
    dirs = [bundle_dir / layer for layer in tmpl["layers"]]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    created: list[str] = []

    # Write manifest
    manifest_path = bundle_dir / "mcp-contract.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    created.append("mcp-contract.json")

    # Write prompt
    prompt_path = bundle_dir / "prompts" / "main.md"
    with open(prompt_path, "w") as f:
        f.write(_make_prompt(name, f"{name}-output"))
    created.append("prompts/main.md")

    # Write output schema
    schema_path = bundle_dir / "schemas" / f"{name}-output.json"
    with open(schema_path, "w") as f:
        json.dump(
            _make_schema(
                f"{name}-output",
                f"{name.replace('-', ' ').title()} Output",
                f"Output shape for {name} workflow.",
            ),
            f,
            indent=2,
        )
        f.write("\n")
    created.append(f"schemas/{name}-output.json")

    if template == "full":
        # Data schema
        data_schema_path = bundle_dir / "schemas" / f"{name}-data.json"
        with open(data_schema_path, "w") as f:
            json.dump(
                _make_schema(
                    f"{name}-data",
                    f"{name.replace('-', ' ').title()} Data",
                    f"Data provided by {name} tool server.",
                ),
                f,
                indent=2,
            )
            f.write("\n")
        created.append(f"schemas/{name}-data.json")

        # Tool stub
        tool_path = bundle_dir / "tools" / "server.py"
        with open(tool_path, "w") as f:
            f.write(_make_tool_stub(name))
        created.append("tools/server.py")

        # App stub
        app_path = bundle_dir / "apps" / "main.html"
        with open(app_path, "w") as f:
            f.write(_make_app_stub(name))
        created.append("apps/main.html")

        # Skill
        skill_path = bundle_dir / "skills" / "claude.md"
        with open(skill_path, "w") as f:
            f.write(_make_skill(name))
        created.append("skills/claude.md")

    # Report
    for f in created:
        print(f"  {_fmt(_GREEN, '+')} {f}")

    print(f"\n{_fmt(_CYAN, '  info:')}  created {len(created)} files in {bundle_dir}")
    print(f"{_fmt(_CYAN, '  info:')}  run {_fmt(_BOLD, f'mcpc validate {name}')} to check\n")

    return True
