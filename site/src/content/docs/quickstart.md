---
title: Quick Start
description: Get up and running with MCP Contract in minutes.
---

## Install the CLI

```bash
pip install mcpc-cli
```

Or run from source (no install needed):

```bash
git clone https://github.com/jmfullerton96/mcp-contract.git
cd mcp-contract
PYTHONPATH=cli python3 -m mcpc --help
```

## Bundle Structure

Every MCP Contract bundle follows this layout:

```
my-workflow/
├── mcp-contract.json      # Manifest
├── prompts/               # Markdown reasoning
├── tools/                 # MCP server
├── apps/                  # Interactive UIs
├── schemas/               # JSON Schema contracts
└── skills/                # Platform hints
```

## Scaffold a Bundle

```bash
mcpc init my-bundle --template full
```

Or for a prompts-only bundle:

```bash
mcpc init my-bundle --template prompts-only
```

## Validate

```bash
mcpc validate path/to/bundle
```

## Pack and Share

```bash
mcpc pack path/to/bundle
mcpc pack path/to/bundle -o my-bundle.mcpc
```

## Manifest Schema

Reference the JSON Schema in your manifest:

```json
{
  "$schema": "https://mcpcontracts.com/schema/0.1.0.json",
  "name": "my-workflow",
  "version": "0.1.0",
  "layers": { }
}
```

## Next Steps

- Read the full [Specification](/specification/) for all the details
- Explore the [Examples](/examples/) to see real bundles
- Check the [CLI Reference](/cli/) for all available commands
