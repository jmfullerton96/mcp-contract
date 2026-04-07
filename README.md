# MCP Contract

[![Spec](https://img.shields.io/badge/spec-v0.1.0--draft-blue)](SPEC.md)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)
[![JSON Schema](https://img.shields.io/badge/JSON%20Schema-draft%202020--12-orange)](schema/mcp-contract.schema.json)
[![Website](https://img.shields.io/badge/web-mcpcontracts.com-purple)](https://mcpcontracts.com)

A specification for composable AI workflow bundles with typed contracts between layers.

## The Problem

MCP servers are monoliths. If you want to use one server's reasoning prompts with another server's tools and a third server's UI, you fork all three. MCP Contract fixes this by separating bundles into independently authored, versioned, and composable layers.

## The Layers

| Layer | Role | Analogy |
|---|---|---|
| **Prompts** | Reasoning logic | Source code |
| **Tools** | State + execution | Runtime libraries |
| **Apps** | Interactive views | UI framework |
| **Skills** | Platform adaptation | Compiler flags |
| **Compiler** | The LLM | gcc, clang, rustc |

Layers are wired together through **contracts** — typed `provides`/`consumes` declarations backed by JSON Schema. A prompt layer provides an output shape. A tool layer provides data schemas. An app layer consumes both.

## Quick Start

```
my-workflow/
├── mcp-contract.json      # Manifest
├── prompts/               # Markdown reasoning
├── tools/                 # MCP server
├── apps/                  # Interactive UIs
├── schemas/               # JSON Schema contracts
└── skills/                # Platform hints
```

See [SPEC.md](SPEC.md) for the full specification.

## Reference Implementation

[Synth Ops](https://github.com/jmfullerton96/synthops) — intelligent infrastructure operations built as an MCP Contract bundle.

## Manifest Schema

The JSON Schema for validating `mcp-contract.json` manifests is at [`schema/mcp-contract.schema.json`](schema/mcp-contract.schema.json).

Reference it in your manifest:

```json
{
  "$schema": "https://mcpcontracts.com/schema/0.1.0.json",
  "name": "my-workflow",
  "version": "0.1.0",
  "layers": { ... }
}
```

## Status

**v0.1.0-draft** — Spec, manifest schema, CLI (`mcpc validate`, `init`, `pack`, `test`), and one reference implementation.

## License

Apache-2.0
