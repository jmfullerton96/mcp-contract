<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/logo-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="docs/logo-light.png">
    <img src="docs/logo-light.png" alt="MCP Contract" width="500">
  </picture>
</p>

[![CI](https://github.com/jmfullerton96/mcp-contract/actions/workflows/ci.yml/badge.svg)](https://github.com/jmfullerton96/mcp-contract/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/mcpc-cli)](https://pypi.org/project/mcpc-cli/)
[![Spec](https://img.shields.io/badge/spec-v0.1.0--draft-blue)](SPEC.md)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)
[![JSON Schema](https://img.shields.io/badge/JSON%20Schema-draft%202020--12-orange)](schema/mcp-contract.schema.json)
[![Website](https://img.shields.io/badge/web-mcpcontracts.com-purple)](https://mcpcontracts.com)

A project structure for Claude extensions that have outgrown a single file. Built on the [Model Context Protocol](https://modelcontextprotocol.io), an open standard originally developed by Anthropic. MCP Contract is an independent open-source project.

## The problem

A small Claude extension is a single prompt file. Anything useful grows past that — an MCP tool server, an interactive UI, a couple of schemas, some platform-specific hints. Somewhere in that growth the layers start bleeding into each other:

- The prompt that decides *what to do* starts naming tools directly, so swapping a tool means editing the reasoning.
- The MCP tool server grows reasoning into it — retry heuristics, ranking logic, "should we even do this" checks — because it is the only layer with state.
- UI cards render fields the tool no longer returns, and nobody notices until a user sees a blank panel.
- Platform-specific bits (Claude Desktop artifact hints, Code CLI skill files) end up wherever you happened to be working.
- Schemas exist in multiple places and agree in none.

None of this is novel. It's the tangle any application gets when it has no enforced seams. But MCP extensions don't have a conventional project layout, so every builder invents one, and every invented one drifts toward the same mess.

MCP Contract is a layout that stops the drift. Four layers with explicit boundaries — **Prompts** (reasoning), **Tools** (state and execution), **Apps** (rendering), **Skills** (platform adaptation) — and a manifest that declares what each layer publishes and consumes as typed JSON Schema. A small CLI validates it.

That's the whole idea. It's `create-react-app` for Claude extensions, not a standards pitch.

## Who this is for

People building a Claude extension that has grown past a single file and is starting to feel unmaintainable. If your prompt knows the name of your tool, or your UI renders fields you removed from your schema two weeks ago, this might save you some pain.

It's not aimed at the MCP ecosystem as a whole, at teams composing multi-server workflows, or at anyone looking for a marketplace. It's a skeleton.

## The layers

| Layer | Role | Analogy |
|---|---|---|
| **Prompts** | Reasoning logic | Source code |
| **Tools** | State + execution | Runtime libraries |
| **Apps** | Interactive views | UI framework |
| **Skills** | Platform adaptation | Compiler flags |
| **Compiler** | The LLM | gcc, clang, rustc |

The separation is the point. Prompts don't reference tool names, tools don't embed reasoning, apps don't call APIs, skills don't change semantics. When you keep those rules, the thing stays legible as it grows.

## Quick start

```
my-workflow/
├── mcp-contract.json      # Manifest
├── prompts/               # Markdown reasoning
├── tools/                 # MCP server
├── apps/                  # Interactive UIs
├── schemas/               # JSON Schema contracts
└── skills/                # Platform hints
```

Scaffold a new bundle:

```sh
pip install mcpc-cli
mcpc init my-workflow --template full
mcpc validate my-workflow
```

See [SPEC.md](SPEC.md) for the full specification.

## Why contracts between layers

Each layer declares what it `provides` and what it `consumes`, backed by JSON Schema. The prompt layer publishes the shape of the reasoning output. The tool layer publishes the shape of its data. The app layer declares what schemas it expects to consume. `mcpc validate` checks that every consumed schema has a provider and flags drift between them.

Day-to-day, this catches the failure mode in the problem list above: a schema changes on one side and the other side keeps rendering stale fields until a user notices. The validator catches it before the user does.

Downstream, if enough extensions share this skeleton, the same contracts that keep a single project honest start to make cross-project composition possible — Alice's prompts with Bob's tools and Carol's UI, wired by matching `provides` to `consumes`. That's the long-term bet, and the spec is shaped to permit it. But it is not the reason to adopt this today. The reason to adopt this today is that your one extension gets easier to maintain.

## Reference implementation

[Synth Ops](https://github.com/jmfullerton96/synthops) — an intelligent infrastructure operations system built as an MCP Contract bundle. It's the bundle the spec was extracted from, and the only one that exercises all four layers end-to-end.

## Manifest schema

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

**v0.1.0-draft.** One author, one reference implementation (Synth Ops), no external adopters yet. The spec, the manifest schema, and the CLI (`mcpc validate`, `init`, `pack`, `unpack`, `test`) all work. Interfaces may change before 1.0 based on what breaks when someone else tries it.

If you pick it up and something doesn't fit, open an issue — the shape of the spec is still negotiable.

## License

Apache-2.0
