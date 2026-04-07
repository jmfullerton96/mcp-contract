# MCP Contract

Specification for composable AI workflow bundles with typed contracts between layers.

## Project Structure

- `SPEC.md` — The full specification (v0.1.0-draft). Source of truth for all conventions.
- `schema/mcp-contract.schema.json` — JSON Schema for validating `mcp-contract.json` manifests.
- `cli/` — The `mcpc` CLI (Python, stdlib only, no external deps). Commands: `validate`, `init`, `pack`, `unpack`, `test`.
- `examples/` — Example bundles. `due-diligence/` is full (all layers), `code-review/` is minimal (prompts-only), `security-review/` demonstrates cross-author composition via `extends`.

## Key Concepts

A bundle has up to 5 layers: Prompts, Tools, Apps, Skills, and the Compiler (the LLM itself). Layers are wired through **contracts** — `provides`/`consumes` declarations backed by JSON Schema. Every `consumes` must be satisfied by a `provides` from another layer.

## Working With Bundles

```sh
# Validate a bundle
PYTHONPATH=cli python3 -m mcpc validate path/to/bundle

# Scaffold a new bundle
PYTHONPATH=cli python3 -m mcpc init my-bundle --template full
PYTHONPATH=cli python3 -m mcpc init my-bundle --template prompts-only

# Pack a bundle into a .mcpc archive
PYTHONPATH=cli python3 -m mcpc pack path/to/bundle
PYTHONPATH=cli python3 -m mcpc pack path/to/bundle -o output.mcpc
```

After `pip install -e cli/`, use `mcpc` directly instead of the `PYTHONPATH` prefix.

## Conventions

- JSON Schema: draft 2020-12, include `$id` and `description` on all schemas
- Prompts: Markdown with YAML frontmatter (`name`, `version`, `description`, `provides`)
- Prompts must not reference tool names — use capability descriptions instead
- CLI: Python standard library only, no external dependencies
- License: Apache-2.0

## Reference Implementation

The [Synth Ops](../synthops/) repo (sibling directory) is the reference implementation — a working MCP Contract bundle for infrastructure operations.
