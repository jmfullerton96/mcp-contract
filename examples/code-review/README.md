# Code Review — MCP Contract Minimal Example

The simplest possible MCP Contract bundle: a single prompt layer with a typed output schema. No tools, no apps, no skills.

## Structure

```
code-review/
├── mcp-contract.json              # Manifest
├── prompts/
│   └── main.md                    # Review methodology
└── schemas/
    └── code-review-output.json    # Output shape contract
```

## Why This Matters

This bundle demonstrates that MCP Contract works without any MCP server infrastructure. The prompt layer defines a structured methodology and a typed output schema. Any LLM that can follow instructions produces output conforming to the schema — no tools required.

This is the `compose.fallback: "prompts-only"` mode that every full bundle should degrade to gracefully.

## Contract Graph

```
Prompts ──provides──▶ code-review-output
```

No layer consumes the output — it flows directly through the LLM's response to the user. A tool or app layer could be added later to consume `code-review-output` without modifying the prompt layer.

## Scaffolded With

```
mcpc init code-review --template prompts-only
```
