# drillr-skill

Agent Skill for [Drillr](https://drillr.ai) — financial-research data
for US and Japan public equities, exposed to any SKILL.md-compatible
agent runtime.

This is the small thing you give a user so their agent can:

- Resolve tickers, fetch standardized financial statements / ratios /
  prices, search SEC filings paragraph-by-paragraph, surface curated
  market signals, and explore AI value-chain alt-data
- Onboard a first-time user (walk them through API key creation), then
  remember the key locally for future sessions

The skill ships with a small Python dispatcher
(`scripts/drillr.py`) that wraps the Drillr REST API — stdlib only,
no `pip install` required. The agent invokes the dispatcher; the
dispatcher handles auth, errors, and credit accounting in one place.

> For agent runtimes that **don't** support skills (raw MCP clients,
> ChatGPT MCP, etc.), use [drillr-mcp-server](https://github.com/Little-Grebe-Inc/drillr-mcp-server)
> instead — it exposes the same data as a standard MCP server.

## Install

### OpenClaw

Once published to ClawHub:

```bash
openclaw skills install drillr
```

Or clone manually into the OpenClaw skills directory:

```bash
# user-global — available to every workspace (recommended)
git clone https://github.com/Little-Grebe-Inc/drillr-skill ~/.openclaw/skills/drillr

# OR workspace-local — only the current workspace sees it
git clone https://github.com/Little-Grebe-Inc/drillr-skill ~/.openclaw/workspace/skills/drillr
```

When you tell the OpenClaw agent to install it from a URL (the
"prompt-as-installer" flow), it will typically place the skill in the
**workspace-local** path — that's also fine, both paths are
discovered by `openclaw skills check`.

### Hermes Agent

```bash
hermes skills install drillr
```

Or clone manually:

```bash
git clone https://github.com/Little-Grebe-Inc/drillr-skill ~/.hermes/skills/drillr
```

### Claude Code / Claude Agent SDK

```bash
git clone https://github.com/Little-Grebe-Inc/drillr-skill ~/.claude/skills/drillr
```

Restart Claude Code. The skill auto-loads on relevant questions (the
`description` field is matched by Claude against the user's question).

### Other agent runtimes

The skill follows the open [agentskills.io](https://agentskills.io)
SKILL.md format — adopted by 40+ products. Most runtimes' install
path is `~/.<runtime>/skills/<slug>/`. Clone there and you're done.

## First run

After install, ask the agent any drillr-relevant question, e.g.:

> *"What's NVDA's gross margin trend over the last 4 quarters?"*

The skill detects the missing API key and walks the user through:

1. Open <https://drillr.ai/developer/keys> in any browser
2. Sign in (Google sign-in is fastest)
3. Click "Create API key", copy the string
4. Paste it back to the agent

The agent then runs `python scripts/drillr.py setup-key <key>` —
the key is stored at `~/.drillr/config.json` (mode `0600`) as the
single source of truth.

## Verify

```bash
python ~/.openclaw/skills/drillr/scripts/drillr.py probe
```

(Adjust the path for your runtime.) Expect a JSON output with
`"ok": true` and a credit-balance summary.

## What's inside

```
drillr-skill/
├── SKILL.md              # what the agent reads — overview, decision tree, onboarding
├── README.md             # this file
├── CHANGELOG.md          # version history
├── LICENSE
├── scripts/
│   └── drillr.py         # unified dispatcher (Python 3 stdlib, no deps)
└── references/
    ├── tools.md          # exact parameter schemas per tool — loaded on demand
    ├── sql_schemas.md    # SQL table discovery guide
    └── workflows.md      # multi-tool research templates
```

## Prerequisites

- A free [drillr.ai](https://drillr.ai) account
- An API key from <https://drillr.ai/developer/keys>
- Python 3 (preinstalled on macOS and most Linux distros)

## License

MIT — see [`LICENSE`](./LICENSE).

## Links

- Drillr: <https://drillr.ai>
- Developer docs: <https://drillr.ai/developer/docs>
- API keys: <https://drillr.ai/developer/keys>
- MCP server (for non-skill runtimes): <https://github.com/Little-Grebe-Inc/drillr-mcp-server>
- Issues: <https://github.com/Little-Grebe-Inc/drillr-skill/issues>
