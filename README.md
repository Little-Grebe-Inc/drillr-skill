# drillr-skill

The agent skill for [drillr](https://drillr.ai) — financial research data for
AI agents: read-only SQL over 90+ standardized tables, paragraph-cited search
across company filings, semantic news and event search, and natural-language
company discovery, for US, Japan, Hong Kong and China A-share equities.

`SKILL.md` teaches an agent how to onboard the user (browser sign-in for MCP
clients, or an API key for relayed chats), connect the drillr MCP server or
REST API, and use the nine data tools well. Any runtime that reads
[Agent Skills](https://agentskills.io) can use it; nothing to build or run.

## Install

```bash
# skills CLI (Claude Code, Codex, Cursor, Copilot, Gemini CLI, OpenClaw, …)
npx skills add Little-Grebe-Inc/drillr-skill

# Claude Code, as a plugin
/plugin marketplace add Little-Grebe-Inc/drillr-skill
/plugin install drillr

# ClawHub / OpenClaw
clawhub install drillr

# Hermes Agent
hermes skills tap add Little-Grebe-Inc/drillr-skill

# by hand
git clone https://github.com/Little-Grebe-Inc/drillr-skill ~/.claude/skills/drillr
```

Listings: [skills.sh](https://www.skills.sh/little-grebe-inc/drillr-skill/drillr) ·
[Smithery](https://smithery.ai/skills/drillr/drillr) · [ClawHub](https://clawhub.ai/skills/drillr)

## What the skill connects to

| Channel | Address | Auth |
|---|---|---|
| MCP (Streamable HTTP) | `https://gateway.drillr.ai/mcp/data` | browser OAuth; API key for non-OAuth clients |
| REST, Public Data API v2 | `https://gateway.drillr.ai/api/v2` · [OpenAPI](https://gateway.drillr.ai/api/v2/openapi.json) | `X-API-KEY` |
| REST, tool mirrors | `https://gateway.drillr.ai/api/v1/data/<tool>` | `Authorization: Bearer drl_…` |

The MCP server itself is documented at
[Little-Grebe-Inc/drillr-mcp-server](https://github.com/Little-Grebe-Inc/drillr-mcp-server).
Keys: <https://drillr.ai/account/api-keys>. Pricing: <https://drillr.ai/pricing>.

## What's inside

```
drillr-skill/
├── SKILL.md                          # the skill
├── .claude-plugin/marketplace.json   # lets the repo act as a Claude Code plugin marketplace
├── examples/
│   ├── claude-code-mcp-config.json   # OAuth entry for Claude Code / Cursor / Desktop
│   ├── openclaw-mcp-config.json      # API-key entry for OpenClaw
│   ├── hermes-mcp-config.yaml        # API-key entry for Hermes
│   └── user-onboarding-script.md     # copy-paste onboarding prompts
├── CHANGELOG.md
└── README.md
```

## License

MIT — see `LICENSE`.
