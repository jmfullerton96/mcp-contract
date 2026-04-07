---
target: claude
version: 0.1.0
---

# Claude Platform Skill

## System Prompt Wrapper

When executing this workflow on Claude, the prompt layer's Markdown files are loaded directly into the system context. Claude processes Markdown natively — no additional formatting or escaping is required.

## Tool Registration

Claude uses MCP native tool registration via the stdio transport. Register the tool server as a standard MCP server in your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "due-diligence-tools": {
      "command": "python",
      "args": ["tools/server.py"]
    }
  }
}
```

## Context Window

This workflow's full prompt chain (main + risk-framework + output-format) is approximately 2,500 tokens. Claude Opus supports 200k context. No chunking or summarization is required.

SEC filing data can be large. For companies with extensive filing histories, limit retrieval to the most recent 8 quarterly and 2 annual filings to stay within context budget while covering the standard analysis window.

## App Rendering

Claude supports interactive artifacts natively. The app layer's components can be rendered in Claude's artifact system. The comps table renders as a sortable data table; the memo renders as structured Markdown within an artifact.

## Graceful Degradation

If the MCP tool server is unavailable (e.g., running in a context without MCP client support), Claude should proceed with analysis using training data. The prompt layer is designed for this — it instructs the model to flag sections that would benefit from live data enrichment.
