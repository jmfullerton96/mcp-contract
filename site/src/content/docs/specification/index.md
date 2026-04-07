---
title: Specification
description: The MCP Contract specification — composable AI workflow bundles with typed contracts between layers.
---

The full MCP Contract specification defines how bundles are structured, how layers interact through typed contracts, and how cross-author composition works.

**Current version: v0.1.0-draft**

## Key Concepts

### Layers

A bundle has up to five layers:

| Layer | Role | Analogy |
|---|---|---|
| **Prompts** | Reasoning logic | Source code |
| **Tools** | State + execution | Runtime libraries |
| **Apps** | Interactive views | UI framework |
| **Skills** | Platform adaptation | Compiler flags |
| **Compiler** | The LLM itself | gcc, clang, rustc |

### Contracts

Layers are wired through **contracts** — `provides`/`consumes` declarations backed by JSON Schema. Every `consumes` entry must be satisfied by a `provides` from another layer.

### Composition

Bundles can extend other bundles using the `extends` field in the manifest. This enables cross-author composition: use one author's prompts with another's tools without forking either.

---

*Full specification content will be ported from [SPEC.md](https://github.com/jmfullerton96/mcp-contract/blob/main/SPEC.md).*
