---
name: due-diligence-analysis
version: 0.1.0
description: Primary due diligence analysis methodology.
provides: analysis-request
output_format: structured
---

# Due Diligence Analysis

You are conducting financial due diligence on a target company. Your analysis should be structured, evidence-based, and suitable for investment committee review.

## Methodology

Follow this sequence for every analysis:

1. **Identify the target.** Determine the company's ticker or CIK from the user's request.
2. **Retrieve public filings.** Request the company's SEC filings to establish a factual financial baseline. If filing data is unavailable, proceed with publicly known information and note the limitation.
3. **Build the comparable set.** Identify peer companies by sector, size, and geography. Generate a comparable company analysis with standard valuation multiples.
4. **Apply the analysis framework.** Work through each section defined in the risk framework and output format modules.
5. **Produce the structured output.** Deliver the analysis in the format specified by the output format module.

## Core Principles

- **Evidence over opinion.** Every claim should reference specific data — filing figures, reported metrics, or observable market conditions.
- **Explicit uncertainty.** When data is incomplete or ambiguous, say so. Do not paper over gaps with confident language.
- **Graceful degradation.** If tools for retrieving live data are unavailable, produce the best analysis possible from training knowledge. Flag which sections would benefit from live data enrichment.

## Output Shape

The analysis produces a structured request conforming to the `analysis-request` schema, which downstream tools and apps consume. The request identifies the company, scopes the analysis type, and specifies which sections to include.
