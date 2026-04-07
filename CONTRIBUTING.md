# Contributing to MCP Contract

MCP Contract is in **v0.1.0-draft** status. Contributions that shape the specification, improve the reference tooling, or add examples are welcome.

## Open Questions

The spec ([SPEC.md Section 9](SPEC.md#9-open-questions)) identifies five unresolved design questions. These are the highest-value areas for community input:

1. **Resource layer** — Should MCP Resources be a distinct layer, or a subset of the Tool layer's `provides` contracts?
2. **Multi-step orchestration** — How should the spec handle iterative loops, conditional branching, or parallel tool invocation beyond the linear `compose.chain`?
3. **Auth propagation** — When composing layers from different authors, how should authentication credentials propagate across layer boundaries?
4. **Streaming contracts** — Should the spec support streaming output schemas for real-time tool output and progressive app rendering?
5. **Bundle signing** — Should the spec define cryptographic signing for bundles and individual layers?

If you have experience or opinions on any of these, open an issue with the relevant question number (e.g., "Q3: Auth propagation for OAuth-based tool layers").

## What to Contribute

**Spec feedback** — Open an issue describing the problem, your proposed change, and why. Reference specific sections of SPEC.md.

**Examples** — Add a new bundle under `examples/`. Use `mcpc init` to scaffold, then flesh out the prompts and schemas with real content. Run `mcpc validate` before submitting.

```
cd examples
mcpc init my-workflow --template full
# or: mcpc init my-workflow --template prompts-only
mcpc validate my-workflow
```

**CLI tooling** — The `mcpc` CLI lives in `cli/`. It uses Python with no external dependencies. To develop locally:

```
cd cli
pip install -e .
mcpc --version
```

**Schema improvements** — The manifest schema is at `schema/mcp-contract.schema.json`. Changes here should be reflected in SPEC.md and tested against existing examples.

## How to Submit

1. Fork the repository
2. Create a branch (`git checkout -b my-contribution`)
3. Make your changes
4. Validate any bundles you've touched (`mcpc validate path/to/bundle`)
5. Open a pull request with a clear description of what changed and why

## Code Style

- Python: standard library only, no external dependencies for the CLI
- JSON Schema: draft 2020-12, include `$id` and `description` on all schemas
- Markdown prompts: YAML frontmatter with `name`, `version`, `description`, and `provides` where applicable

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 license.
