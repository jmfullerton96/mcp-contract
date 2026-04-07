# Due Diligence — MCP Contract Example

A complete example bundle demonstrating the MCP Contract specification. This bundle models a financial due diligence workflow with SEC filing analysis and comparable company modeling.

## Structure

```
due-diligence/
├── mcp-contract.json              # Manifest — layers, contracts, composition
├── schemas/
│   ├── analysis-request.json      # Prompt output shape (provided by prompts)
│   ├── sec-filings.json           # SEC filing data (provided by tools)
│   └── comps-table.json           # Comparable company data (provided by tools)
├── prompts/
│   ├── main.md                    # Primary analysis methodology
│   ├── risk-framework.md          # Risk assessment framework
│   └── output-format.md           # Memo output structure
├── tools/
│   └── server.py                  # MCP tool server (stub)
├── apps/
│   └── memo.html                  # Investment memo renderer (stub)
└── skills/
    └── claude.md                  # Claude platform adaptation
```

## Contract Graph

```
Prompts ──provides──▶ analysis-request
Tools   ──provides──▶ sec-filings, comps-table
Apps    ──consumes──▶ comps-table, analysis-request
```

Every `consumes` entry is satisfied by a `provides` entry from another layer. The `sec-filings` schema is provided but not consumed by apps — it flows through the prompt layer's reasoning rather than being rendered directly.

## What's Real vs. Stub

| Layer | Status | Notes |
|---|---|---|
| **Schemas** | Complete | Fully specified JSON Schema contracts |
| **Prompts** | Complete | Functional reasoning prompts with frontmatter |
| **Skills** | Complete | Claude platform adaptation |
| **Tools** | Stub | Placeholder — see [Synth Ops](https://github.com/jmfullerton96/synthops) for a working tool server |
| **Apps** | Stub | Placeholder — see [Synth Ops](https://github.com/jmfullerton96/synthops) for working MCP Apps |

## Key Spec Concepts Demonstrated

- **Typed contracts** — `provides`/`consumes` declarations backed by JSON Schema (`schemas/`)
- **Prompt layer independence** — Prompts reference capabilities, not tool names ("retrieve the company's public filings" not "call `sec_edgar_search()`")
- **Graceful degradation** — The `compose.fallback` is `prompts-only`, and the main prompt explicitly handles the no-tools case
- **Platform adaptation** — The `skills/claude.md` adapts for Claude without modifying core layers
- **Compiler agnosticism** — `compiler_compatibility` lists Claude, GPT, and Gemini
