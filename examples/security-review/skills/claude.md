---
target: claude
version: 0.1.0
---

# Claude Platform Skill — Security Review

## System Prompt Wrapper
When executing this workflow on Claude, emphasize security-first analysis. Prioritize critical and high severity findings. Cross-reference code review findings with vulnerability scan results to identify patterns.

## Tool Registration
Register the vulnerability-scan tool via standard MCP client protocol. The tool expects a repository identifier and git ref as input.

## Context Window
This workflow combines code-review prompts (~2,000 tokens) with vulnerability scan results (variable). For large repositories, scope scans to changed files using the `paths` field in the scan target.

## Composition Note
This bundle extends @mcpc/code-review for its prompt layer. Claude should apply the code review methodology first, then augment findings with vulnerability scan data. The app layer merges both outputs into a unified security report.
