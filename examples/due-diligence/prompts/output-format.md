---
name: output-format
version: 0.1.0
description: Defines the output structure for due diligence analysis memos.
---

# Output Format

Structure every due diligence analysis as a memo with the following sections. Each section maps to a component of the `analysis-request` schema.

## Section Definitions

### 1. Business Overview
- Company description and history
- Core products/services and revenue model
- Market position and competitive landscape
- Key customers, suppliers, and partners

### 2. Financial Analysis
- Revenue trends (3-5 year view where available)
- Margin analysis (gross, operating, net)
- Capital structure and leverage metrics
- Cash flow quality and working capital dynamics
- Comparison to peer metrics from the comparable company set

### 3. Risk Assessment
- Apply the risk framework module
- Present risks by category with severity ratings
- Highlight risk interactions and cumulative exposure

### 4. Valuation Context
- Relative valuation using comparable company multiples
- Key multiples: EV/EBITDA, P/E, revenue growth-adjusted metrics
- Implied valuation range based on peer set
- Premium/discount factors specific to the target

## Formatting Guidelines

- Lead each section with a one-sentence summary before detail
- Use tables for quantitative comparisons
- Flag data gaps explicitly rather than omitting sections
- Keep the total memo under 3,000 words for standard detail level
