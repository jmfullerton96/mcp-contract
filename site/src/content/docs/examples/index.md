---
title: Examples
description: Example MCP Contract bundles demonstrating different patterns.
---

The repository includes several example bundles that demonstrate different patterns and complexity levels.

## Due Diligence

**Full bundle** — All five layers working together for an infrastructure due-diligence workflow. Demonstrates the complete layer stack with prompts, tools, apps, skills, and contract wiring between them.

[View on GitHub](https://github.com/jmfullerton96/mcp-contract/tree/main/examples/due-diligence)

## Code Review

**Prompts-only bundle** — A minimal bundle with just a prompts layer. Shows that you don't need all five layers; a single layer with typed contracts is still useful.

[View on GitHub](https://github.com/jmfullerton96/mcp-contract/tree/main/examples/code-review)

## Security Review

**Cross-author composition** — Demonstrates the `extends` mechanism. This bundle extends another bundle's prompts and tools, adding its own security-focused reasoning without forking the original.

[View on GitHub](https://github.com/jmfullerton96/mcp-contract/tree/main/examples/security-review)
