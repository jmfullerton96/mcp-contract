---
name: code-review
version: 0.1.0
description: Structured code review methodology.
provides: code-review-output
---

# Code Review

Review the provided code changes and produce structured findings. Each finding should be actionable and categorized.

## Review Checklist

Work through these categories in order. Skip categories with no findings.

1. **Correctness** — Logic errors, off-by-one, null handling, race conditions, unhandled edge cases.
2. **Security** — Injection vectors, auth gaps, secret exposure, unsafe deserialization, OWASP Top 10 patterns.
3. **Performance** — N+1 queries, unnecessary allocations, missing indexes, blocking calls in hot paths.
4. **Maintainability** — Naming clarity, function length, coupling, missing abstractions, dead code.
5. **Testing** — Missing test coverage for new logic, brittle assertions, test isolation.

## Severity Ratings

| Level | Definition |
|---|---|
| **Critical** | Must fix before merge — correctness bug, security vulnerability, or data loss risk. |
| **Warning** | Should fix — performance issue, maintainability concern, or missing test. |
| **Suggestion** | Optional improvement — style, naming, or minor simplification. |

## Output Shape

Produce findings conforming to the `code-review-output` schema:
- Group findings by category
- Rate each by severity
- Include the specific file and line range
- Provide a concrete recommendation (not just "fix this")
- End with a summary verdict: approve, request changes, or needs discussion
