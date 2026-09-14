# OSS and market references

LIQA does not ship customers’ UAT through these clouds. We study lawful public repos and public docs.

## Clone (permissive)

| Repo | License | Why |
|---|---|---|
| https://github.com/steel-dev/steel-browser | Apache-2.0 | Headful session + live view ideas |
| https://github.com/web-infra-dev/midscene | See repo | GUI agent E2E |
| https://github.com/zavora-ai/computer-use-mcp | MIT | Win32 screenshot/mouse MCP |
| https://github.com/browser-use/browser-use | MIT | Agent loop (docs/code study) |
| https://github.com/browserbase/stagehand | MIT | act/extract/observe — not our headed core |

Shallow clone into `vendor/oss/` (gitignored):

```powershell
.\scripts\clone-oss.ps1
```

## Docs only (no scrape of private apps)

- https://www.askui.com/blog-posts/3-layer-architecture-demo-trap-enterprise-agents
- https://karatelabs.io/blog/enterprise-computer-use-on-premises
- https://docs.steel.dev/overview/sessions-api/embed-sessions/live-sessions
- https://www.browserstack.com/docs/local-testing/how-local-testing-works
