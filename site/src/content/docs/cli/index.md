---
title: CLI Reference
description: Reference for the mcpc command-line tool.
---

The `mcpc` CLI is a Python tool (standard library only, no external dependencies) for working with MCP Contract bundles.

## Installation

```bash
pip install mcpc-cli
```

## Commands

### `mcpc validate`

Validate a bundle's manifest, schemas, and contract wiring.

```bash
mcpc validate path/to/bundle
```

### `mcpc init`

Scaffold a new bundle from a template.

```bash
mcpc init my-bundle --template full
mcpc init my-bundle --template prompts-only
```

### `mcpc pack`

Pack a bundle into a `.mcpc` archive for distribution.

```bash
mcpc pack path/to/bundle
mcpc pack path/to/bundle -o output.mcpc
```

### `mcpc unpack`

Extract a `.mcpc` archive.

```bash
mcpc unpack bundle.mcpc
mcpc unpack bundle.mcpc -o target-directory
```

### `mcpc test`

Run contract tests against a bundle.

```bash
mcpc test path/to/bundle
```
