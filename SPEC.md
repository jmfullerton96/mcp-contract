# MCP Contract Specification

**Version:** 0.1.0-draft
**Author:** Joe Fullerton
**Date:** April 2026
**Status:** Draft

---

## Abstract

MCP Contract is a specification for decomposing AI workflow bundles into independently authored, versioned, and composable layers with typed contracts between them. It introduces a manifest format (`mcp-contract.json`) that declares the boundaries between reasoning logic (Prompts), execution bindings (Tools), rendering targets (Apps), and platform-specific adaptation (Skills), enabling mix-and-match composition across authors, runtimes, and LLM compilers.

This specification does not define a package manager, a runtime, or a marketplace. It defines the contract format that makes all of those possible.

---

## 1. Problem Statement

### 1.1 The Monolith Problem

The current MCP ecosystem packages servers as monolithic units. An MCP server bundles its prompts, tool definitions, resource handlers, and (where applicable) UI rendering into a single artifact. The MCPB format (`.mcpb`) standardizes *packaging* — zip archives with a `manifest.json` — but does not standardize *decomposition*.

This creates three concrete problems:

**Non-composability.** If a developer wants to use Server A's reasoning prompts with Server B's data tools and Server C's UI, they must fork all three and manually wire them together. There is no contract surface that enables this composition without full reimplementation.

**Coarse-grained forking.** To change one layer — say, adapting prompts for a different analytical framework — a developer must fork the entire server. Version control, attribution, and upstream merges become intractable. The modification surface is the entire package rather than the specific layer that changed.

**Platform coupling.** A bundle built for Claude Desktop may not function in Cursor, VS Code, or a custom agent runtime. Platform-specific adaptation is embedded in the server code rather than isolated in a separable layer, requiring reimplementation per platform rather than thin adaptation.

### 1.2 The Compiler Analogy

The relationship between an LLM and its MCP integrations is structurally identical to the relationship between a compiler and its build inputs:

| Concept | Traditional Build | MCP Contract |
|---|---|---|
| Source code | `.c`, `.rs`, `.ts` files | MCP Prompts (reasoning logic) |
| Runtime libraries | `libc`, `stdlib`, npm packages | MCP Tools (state + execution) |
| UI framework | React, Qt, GTK | MCP Apps (interactive views) |
| Compiler flags | `-O2`, `--target=arm64` | Platform Skills (per-platform wrappers) |
| Compiler | `gcc`, `clang`, `rustc` | Claude, GPT, Gemini, Llama |

This analogy is not decorative. It has structural consequences:

- Source code (Prompts) should compile on any compiler. Well-written prompts degrade gracefully across LLMs, just as well-written C compiles on both gcc and clang.
- Runtime libraries (Tools) are linked at compile time. The compiler resolves tool bindings based on declared schemas, not hardcoded references.
- Compiler flags (Skills) adapt the build for a specific target without modifying source or libraries.
- The build graph (composition order, dependency resolution, caching) is a separate concern from any individual layer.

### 1.3 What Exists Today

| Project | What it does | What it doesn't do |
|---|---|---|
| MCPB (.mcpb) | Packages servers as portable zip archives with manifest | No layer separation; server is atomic |
| Microsoft APM | Agent package manager with dependency resolution | Bundles instructions + skills + plugins as one manifest; no typed contracts between layers |
| MCP.bar | Registry of 1500+ MCP servers | Directory only; no composition, no versioning contracts |
| NimbleBrain MCPB | Production-grade bundle format with cold-start optimization | Focused on DevOps (deployment, version drift); no architectural decomposition |
| install-mcp | Meta-server for agent self-management | Manages servers, not layers within servers |

The gap is consistent: **no existing format treats Prompts, Tools, and Apps as separate composable layers with typed contracts between them.**

---

## 2. Architecture

### 2.1 The Five Layers

MCP Contract defines five layers. Each layer has a distinct role, a distinct authorship boundary, and a distinct versioning lifecycle.

**Layer 1: Prompts** — Operational reasoning logic. Prompts define *what* to think about, *how* to structure analysis, and *what output shape* to produce. They are pure declarative intent. Prompts must not reference specific tools by name or assume a particular UI rendering target. A well-written prompt layer compiles on any LLM that supports the relevant context window and instruction-following capabilities.

**Layer 2: Tools** — Runtime execution bindings. Tools provide stateful access to external systems: APIs, databases, file systems, computation engines. Each tool declares a typed input/output schema. Tools are the contract surface — the boundary where reasoning meets execution. Tools must not embed reasoning logic or UI assumptions.

**Layer 3: Apps** — Interactive rendering targets. Apps consume tool output schemas and prompt output shapes to produce user-facing views: dashboards, reports, forms, interactive artifacts. Apps declare which schemas they consume. They do not execute logic or access external systems directly.

**Layer 4: Skills** — Platform-specific adaptation. Skills are thin wrappers that adapt a bundle to a specific LLM platform (Claude, GPT, Cursor, etc.) without modifying the core layers. Skills may include platform-specific system prompt formatting, tool registration syntax, context window optimization hints, or UI rendering directives. Skills are optional — a bundle without skills should still compile, albeit without platform-specific optimization.

**Layer 5: The Compiler** — The LLM itself (Claude, GPT, Gemini, Llama, etc.). The compiler reads the manifest, links the layers, resolves contracts, and executes the composed workflow at runtime. The compiler is not part of the bundle. The bundle is compiler-agnostic by design.

### 2.2 Layer Independence

Each layer is:

- **Independently authored.** Different developers can write the prompts, tools, and apps for a single composed workflow.
- **Independently versioned.** Updating the tool layer from v1.2 to v1.3 does not require updating the prompt or app layers, provided the tool's output schema remains backward-compatible.
- **Independently forkable.** A developer can fork only the prompt layer to adapt reasoning for a different domain, while consuming the same tools and apps.
- **Independently testable.** Prompts can be evaluated against reference outputs without running tools. Tools can be integration-tested without prompt logic. Apps can be rendered with mock data without either.

### 2.3 The Contract Mechanism

Layers are wired together through **contracts**: typed declarations of what each layer provides and what it consumes.

```
┌──────────────────────────────────────────────────────┐
│                   mcp-contract.json                   │
│                                                      │
│   Prompts ──provides──▶ ["analysis-request"]         │
│                              │                       │
│   Tools ──provides──▶ ["sec-filings", "comps-table"] │
│                              │                       │
│   Apps ──consumes──▶ ["comps-table",                 │
│                       "analysis-request"]            │
│                                                      │
│   Skills ──targets──▶ ["claude", "gpt"]              │
└──────────────────────────────────────────────────────┘
```

A `provides` declaration publishes a named schema. A `consumes` declaration depends on a named schema. The compiler resolves these at runtime, ensuring that every consumed schema has a corresponding provider.

This is dependency resolution for AI workflows.

---

## 3. Bundle Format

### 3.1 Directory Structure

A compliant MCP Contract bundle is a directory or archive with the following structure:

```
my-workflow/
├── mcp-contract.json          # Required. Manifest declaring layers and contracts.
├── prompts/                   # Required. Reasoning logic.
│   ├── main.md                # Primary prompt entry point.
│   └── *.md                   # Additional prompt modules.
├── tools/                     # Required. Runtime execution bindings.
│   ├── server.py|server.ts    # MCP server implementation.
│   └── schemas/               # Typed input/output schemas.
│       └── *.json             # JSON Schema definitions.
├── apps/                      # Optional. Rendering targets.
│   └── *.html|*.jsx|*.svelte  # UI components.
└── skills/                    # Optional. Platform-specific adaptation.
    ├── claude.md              # Claude-specific hints.
    ├── gpt.md                 # GPT-specific hints.
    └── cursor.md              # Cursor-specific hints.
```

### 3.2 Manifest Schema (`mcp-contract.json`)

```json
{
  "$schema": "https://mcp-contract.dev/schema/0.1.0.json",
  "name": "due-diligence",
  "version": "0.1.0",
  "description": "Financial due diligence workflow with SEC filing analysis and comparable company modeling.",
  "author": {
    "name": "Builder Name",
    "url": "https://example.com"
  },
  "license": "MIT",

  "layers": {
    "prompts": {
      "entry": "prompts/main.md",
      "modules": ["prompts/risk-framework.md", "prompts/output-format.md"],
      "provides": [
        {
          "name": "analysis-request",
          "schema": "schemas/analysis-request.json",
          "description": "Structured analysis request with company identifier, analysis type, and output preferences."
        }
      ]
    },

    "tools": {
      "entry": "tools/server.py",
      "runtime": "python",
      "dependencies": "tools/requirements.txt",
      "provides": [
        {
          "name": "sec-filings",
          "schema": "schemas/sec-filings.json",
          "description": "Retrieves and parses SEC EDGAR filings by CIK or ticker."
        },
        {
          "name": "comps-table",
          "schema": "schemas/comps-table.json",
          "description": "Generates comparable company analysis with configurable multiples."
        }
      ]
    },

    "apps": {
      "entry": "apps/memo.jsx",
      "consumes": [
        {
          "name": "comps-table",
          "schema": "schemas/comps-table.json"
        },
        {
          "name": "analysis-request",
          "schema": "schemas/analysis-request.json"
        }
      ]
    },

    "skills": {
      "targets": {
        "claude": "skills/claude.md",
        "gpt": "skills/gpt.md",
        "cursor": "skills/cursor.md"
      }
    }
  },

  "compiler_compatibility": ["claude", "gpt", "gemini", "llama"],

  "compose": {
    "chain": ["prompts", "tools", "apps"],
    "fallback": "prompts-only"
  }
}
```

### 3.3 Schema Definitions

Each `provides` and `consumes` entry references a JSON Schema file that defines the typed contract. Schemas use standard JSON Schema (draft 2020-12) with the following conventions:

```json
{
  "$id": "https://mcp-contract.dev/schemas/comps-table/0.1.0",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CompsTable",
  "description": "Comparable company analysis output.",
  "type": "object",
  "required": ["companies", "multiples", "generated_at"],
  "properties": {
    "companies": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["ticker", "name", "market_cap"],
        "properties": {
          "ticker": { "type": "string" },
          "name": { "type": "string" },
          "market_cap": { "type": "number" },
          "ev_ebitda": { "type": "number" },
          "pe_ratio": { "type": "number" },
          "revenue_growth": { "type": "number" }
        }
      }
    },
    "multiples": {
      "type": "object",
      "properties": {
        "median_ev_ebitda": { "type": "number" },
        "median_pe": { "type": "number" }
      }
    },
    "generated_at": { "type": "string", "format": "date-time" }
  }
}
```

### 3.4 Prompt Layer Conventions

Prompt files are Markdown with optional YAML frontmatter for metadata:

```markdown
---
name: due-diligence-analysis
version: 0.1.0
provides: analysis-request
output_format: structured
---

# Due Diligence Analysis

You are conducting financial due diligence on a target company.
Your analysis should be structured, evidence-based, and suitable
for investment committee review.

## Analysis Framework

1. **Business Overview** — Describe the company's core business,
   market position, and competitive dynamics.
2. **Financial Analysis** — Evaluate revenue trends, margins,
   capital structure, and cash flow quality.
3. **Risk Assessment** — Identify material risks including
   regulatory, competitive, technological, and execution risks.
4. **Valuation Context** — Situate the company relative to
   comparable public companies and precedent transactions.

## Output Shape

Produce a structured analysis with the following sections...
```

Prompt layer rules:

- Prompts must not reference specific tool names or function signatures. Use capability descriptions instead (e.g., "retrieve the company's public filings" not "call sec_edgar_search()").
- Prompts must not assume a specific UI rendering target. Describe output *shape* (structured sections, tables, key-value pairs) not output *format* (HTML, JSX, specific CSS classes).
- Prompts should degrade gracefully. If tools are unavailable, the prompt should still produce useful reasoning from the LLM's training data, albeit without live data enrichment.

### 3.5 Tool Layer Conventions

Tool servers implement the standard MCP server protocol. MCP Contract adds one requirement: **every tool must declare typed input and output schemas in the `schemas/` directory**, referenced by the manifest.

Tool layer rules:

- Tools must not embed reasoning logic. A tool retrieves, transforms, or computes data. It does not decide *what* to analyze or *how* to interpret results.
- Tools must not assume a specific prompt or app layer. A tool's interface is its schema, not its caller.
- Tool schemas must be backward-compatible within a major version. Adding optional fields is non-breaking. Removing required fields or changing types is breaking.

**Resources.** MCP defines Resources as read-only data sources (files, database records, API responses) distinct from invocable Tools. In MCP Contract, Resources are modeled as `provides` entries on the Tool layer — not as a separate layer. Resources and Tools share the same MCP server, the same authorship boundary, and the same versioning lifecycle. A resource's read-only schema is declared as a contract entry like any tool output. Consumers (apps, prompts) reference resources by contract name without needing to know whether the provider is a tool invocation or a resource read.

### 3.6 App Layer Conventions

Apps are UI components that consume tool output schemas and/or prompt output shapes to render user-facing views.

App layer rules:

- Apps must declare every schema they consume in the manifest's `consumes` array.
- Apps must not call external APIs or access data directly. All data flows through the tool layer.
- Apps should be renderable with mock data conforming to the consumed schemas, enabling independent development and testing.

### 3.7 Skill Layer Conventions

Skills are Markdown files containing platform-specific instructions that the compiler uses to optimize its interaction with the prompt, tool, and app layers.

```markdown
---
target: claude
version: 0.1.0
---

# Claude Platform Skill

## System Prompt Wrapper
When executing this workflow on Claude, prepend the following
system context...

## Tool Registration
Claude uses MCP native tool registration. Register tools via
the standard MCP client protocol. No additional configuration
required.

## Context Window Optimization
This workflow's full prompt chain is approximately 4,000 tokens.
Claude Opus supports 200k context. No chunking required.

## App Rendering
Claude supports React artifacts natively. The app layer's JSX
components can be rendered directly in Claude's artifact system.
```

Skill layer rules:

- Skills must not modify the semantics of the prompt, tool, or app layers. They adapt *how* the compiler processes those layers, not *what* those layers contain.
- Skills are optional. A bundle without skills must still be compilable by any supported LLM, producing a functional (if unoptimized) result.
- Skills are keyed to specific compiler targets. A skill for Claude must not contain GPT-specific instructions.

---

## 4. Composition

### 4.1 Single-Author Composition

The simplest case: one developer writes all layers and ships a complete bundle.

```
due-diligence/
├── mcp-contract.json
├── prompts/main.md
├── tools/server.py
├── apps/memo.jsx
└── skills/claude.md
```

The manifest declares all layers, their contracts, and the composition chain. The compiler reads the manifest and links everything at runtime.

### 4.2 Cross-Author Composition

The power case: layers from different authors are composed into a single workflow.

```json
{
  "name": "custom-diligence",
  "version": "0.1.0",
  "extends": [
    { "package": "@alice/diligence-prompts", "version": "^1.0.0", "layer": "prompts" },
    { "package": "@bob/sec-tools", "version": "^2.1.0", "layer": "tools" },
    { "package": "@carol/finance-dashboard", "version": "^1.0.0", "layer": "apps" }
  ],
  "skills": {
    "targets": {
      "claude": "skills/claude.md"
    }
  }
}
```

In this model, the manifest acts as a `package.json` — declaring dependencies on external layers by reference. A package manager (not defined by this spec) resolves these references, downloads the layers, and validates that all `consumes` declarations are satisfied by corresponding `provides` declarations.

### 4.3 Layer Override

A developer can override a single layer while inheriting the rest:

```json
{
  "name": "healthcare-diligence",
  "version": "0.1.0",
  "extends": [
    { "package": "@alice/diligence-prompts", "version": "^1.0.0", "layer": "prompts" }
  ],
  "layers": {
    "prompts": {
      "entry": "prompts/healthcare-specific.md",
      "provides": [
        {
          "name": "analysis-request",
          "schema": "schemas/analysis-request.json"
        }
      ]
    }
  }
}
```

Here, the developer overrides only the prompt layer with healthcare-specific reasoning while inheriting Alice's tools and Carol's apps (assuming they were part of Alice's base bundle). The override must satisfy the same `provides` contracts as the layer it replaces.

### 4.4 Contract Validation

Before compilation, the manifest must pass contract validation:

1. **Coverage.** Every `consumes` entry must have a corresponding `provides` entry with the same `name` across all layers (local or extended).
2. **Schema compatibility.** The schema referenced by a `consumes` entry must be a subset of (or identical to) the schema referenced by the corresponding `provides` entry. Subset compatibility means the consumer can handle any output the provider produces.
3. **No circular dependencies.** The composition chain must be a directed acyclic graph.
4. **Compiler compatibility.** If the manifest declares `compiler_compatibility`, the target compiler must be listed.

A validation tool (not defined by this spec, but expected as reference tooling) should produce clear error messages:

```
ERROR: Contract violation in healthcare-diligence@0.1.0
  App layer consumes "comps-table" but no layer provides it.
  Did you forget to extend a tools package?

WARNING: Schema drift in @bob/sec-tools@2.1.0
  Provider schema for "sec-filings" adds optional field "filing_amendments"
  not present in consumer schema. Consumer will ignore this field.
```

---

## 5. Versioning

### 5.1 Bundle Versioning

Bundles follow Semantic Versioning 2.0.0:

- **Major** — Breaking changes to any contract schema (removed fields, changed types, renamed provides/consumes names).
- **Minor** — New capabilities that don't break existing contracts (new optional fields, additional provides entries, new skill targets).
- **Patch** — Bug fixes, documentation updates, prompt refinements that don't change output shape.

### 5.2 Layer Versioning

Individual layers within a bundle may have their own version numbers in their frontmatter or module metadata. These are informational. The bundle version is the authoritative version for dependency resolution.

### 5.3 Schema Evolution

Schemas evolve under these rules:

- **Non-breaking:** Adding optional properties, adding new enum values, relaxing constraints (e.g., removing `required` from a field).
- **Breaking:** Removing properties, adding required properties, changing property types, renaming properties, tightening constraints.

Breaking schema changes require a major version bump on the bundle.

---

## 6. Relationship to Existing Standards

### 6.1 MCP Protocol

MCP Contract is additive to the MCP protocol. It does not modify the MCP server protocol, transport layer, or client-server communication model. A tool layer in an MCP Contract bundle is a standard MCP server. The contribution is the manifest layer that sits *above* the server, declaring how it composes with prompts and apps.

### 6.2 MCPB Format

MCPB (`.mcpb`) bundles can be consumed as tool layers within MCP Contract. An existing `.mcpb` server can be referenced in an MCP Contract manifest without modification. MCP Contract adds layer separation and contracts on top of what MCPB provides for packaging.

### 6.3 Microsoft APM

APM's manifest format overlaps with MCP Contract in declaring instructions, skills, and plugins. MCP Contract differs in enforcing typed contracts between layers and treating each layer as independently versionable. The two formats could converge if APM adopted the provides/consumes contract mechanism.

### 6.4 JSON Schema

MCP Contract uses JSON Schema (draft 2020-12) for all contract definitions. No custom schema language is introduced.

---

## 7. Design Decisions

### 7.1 Why Markdown for Prompts?

Markdown is the lingua franca of LLM interaction. Every major LLM processes Markdown natively. Prompts stored as Markdown are readable by humans, parseable by machines, diffable in version control, and renderable in documentation. No custom DSL is necessary.

### 7.2 Why JSON Schema for Contracts?

JSON Schema is the most widely adopted schema language for HTTP APIs, OpenAPI specifications, and tool definitions. Using it for MCP Contract contracts means existing validation libraries, editor tooling, and developer knowledge transfer directly. Inventing a custom schema language would create adoption friction without corresponding benefit.

### 7.3 Why Not a Single Manifest for Everything?

A single manifest that inlines all prompts, tool definitions, and UI components would be simpler but would sacrifice the core value proposition: independent authorship and versioning. The file-based layer structure enables git-based collaboration patterns that developers already use.

### 7.4 Why Skills Are Optional

Requiring platform-specific skills would undermine compiler agnosticism. A bundle should compile on any LLM. Skills optimize that compilation for a specific platform but are never required for basic functionality.

---

## 8. Reference Implementation

The reference implementation is [Synth Ops](https://github.com/jmfullerton96/synthops) — an intelligent infrastructure operations system built as an MCP Contract bundle.

Synth demonstrates:
- Standalone Markdown prompts for operational reasoning (deploy, investigate, maintain, query)
- A Node.js MCP tool server with typed JSON Schema contracts
- Interactive MCP Apps (dashboard, plan review) that consume tool output schemas
- A Claude Desktop platform skill

---

## 9. Open Questions

The following questions are unresolved in this draft and invite community input:

1. **Multi-step orchestration.** The `compose.chain` field implies linear execution (prompts → tools → apps). How should the spec handle iterative loops, conditional branching, or parallel tool invocation?

2. **Auth propagation.** When composing layers from different authors, how should authentication credentials propagate? Should the manifest declare auth requirements per layer?

3. **Streaming contracts.** Current schemas define request/response shapes. Should the spec support streaming output schemas for real-time tool output and progressive app rendering?

4. **Bundle signing.** Should the spec define a mechanism for cryptographic signing of bundles and individual layers to establish authorship and integrity?

### 9.1 Resolved

- **Resource layer** (resolved in v0.1.0-draft) — Resources are modeled as `provides` entries on the Tool layer, not as a separate layer. See §3.5.

---

## 10. Conclusion

MCP Contract proposes that the atomic unit of AI workflow distribution should not be the server but the *layer*. By separating reasoning (Prompts), execution (Tools), rendering (Apps), and platform adaptation (Skills) into independently authored, versioned, and composable layers with typed contracts between them, MCP Contract enables a software engineering model for AI workflows that mirrors the composability, reusability, and collaboration patterns that made traditional software ecosystems productive.

The specification is intentionally minimal. It defines the manifest format, the contract mechanism, and the layer conventions. Everything else — package managers, registries, runtimes, marketplaces — is downstream. The bet is that if the contract format is right, the ecosystem builds itself.

---

*MCP Contract is an independent specification. It is not affiliated with Anthropic, the Model Context Protocol project, or the Linux Foundation. It is additive to the MCP ecosystem and designed for compatibility with existing MCP tooling.*
