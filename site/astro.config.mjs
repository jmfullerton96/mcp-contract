import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

export default defineConfig({
  site: "https://mcpcontracts.com",
  integrations: [
    starlight({
      title: "MCP Contract",
      description:
        "An open specification for composable AI workflow bundles with typed contracts between layers.",
      defaultLocale: "root",
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/jmfullerton96/mcp-contract",
        },
      ],
      customCss: ["./src/styles/custom.css"],
      sidebar: [
        {
          label: "Getting Started",
          items: [
            { label: "Introduction", slug: "index" },
            { label: "Quick Start", slug: "quickstart" },
          ],
        },
        {
          label: "Specification",
          items: [
            { label: "Overview", slug: "specification" },
          ],
        },
        {
          label: "CLI Reference",
          items: [
            { label: "Overview", slug: "cli" },
          ],
        },
        {
          label: "Examples",
          items: [
            { label: "Overview", slug: "examples" },
          ],
        },
      ],
    }),
  ],
});
