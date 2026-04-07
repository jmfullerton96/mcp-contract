# Security Review — Cross-Author Composition Example

This example demonstrates **cross-author composition** using the `extends` field. It pulls its prompt layer from an external package (`@mcpc/code-review`) and adds local tool, app, and skill layers.

## Composition

```
@mcpc/code-review (external)     security-review (local)
┌─────────────────────┐          ┌─────────────────────┐
│  Prompts layer      │─extends──│  (inherited)        │
│  - code review      │          │                     │
│    methodology      │          │  Tools layer        │
│  - provides:        │          │  - vulnerability    │
│    code-review-     │          │    scanner          │
│    output           │          │  - provides:        │
└─────────────────────┘          │    vulnerability-   │
                                 │    scan             │
                                 │                     │
                                 │  Apps layer         │
                                 │  - consumes:        │
                                 │    code-review-     │
                                 │    output,          │
                                 │    vulnerability-   │
                                 │    scan             │
                                 │                     │
                                 │  Skills layer       │
                                 │  - claude           │
                                 └─────────────────────┘
```

## Key Points

- The prompt layer is not local — it comes from `@mcpc/code-review ^0.1.0`
- The app layer consumes schemas from **both** the extended prompt layer and the local tool layer
- A copy of `code-review-output.json` is included in `schemas/` for validation; in production, a package manager would resolve this from the dependency
- The `compose.fallback: "prompts-only"` setting means the bundle degrades gracefully if tools are unavailable

## Validation

```sh
PYTHONPATH=cli python3 -m mcpc validate examples/security-review
```

Note: The validator checks local contract coverage. Since the prompt layer is external (via `extends`), the `code-review-output` schema consumed by the app layer is satisfied by the local copy in `schemas/`. A future package manager would resolve this from the dependency graph.
