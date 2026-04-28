# drillr-skill

Agent-readable skill for [Drillr](https://drillr.ai) — financial
research, signals, articles, and watchlists, available over **MCP**,
**REST**, and a **CLI**.

This repository is the distribution point for the Drillr agent skill.
Drop it into any Claude Agent Skills-compatible runtime and your
agent will be able to onboard a user, collect an API key, and start
pulling financial data — whether the user is sitting at a terminal or
chatting from their phone.

## Install

### Claude Code / Claude Agent SDK

```bash
git clone https://github.com/Little-Grebe-Inc/drillr-skill ~/.claude/skills/drillr
```

Restart Claude Code. The skill auto-loads based on the `description`
field in `SKILL.md`, so Claude will invoke it when the user asks
about stocks, earnings, signals, etc.

### Smithery (one-line install for any Smithery-compatible client)

```bash
npx -y @smithery/cli install drillr/drillr --client claude
```

Wires Drillr's MCP server into your client via Smithery's gateway —
authorization goes through Drillr OAuth, no API key paste required.

Browse the listings:

- MCP server: <https://smithery.ai/servers/drillr/drillr>
- Skill: <https://smithery.ai/skills/drillr/drillr>

### Clawhub / OpenClaw

The frontmatter in `SKILL.md` includes the `metadata.openclaw.*`
fields required by the [clawhub skill format](https://clawhub.ai).
Install via your clawhub client, or clone into your OpenClaw skills
directory.

### Hermes Agent

```bash
git clone https://github.com/Little-Grebe-Inc/drillr-skill ~/.hermes/skills/drillr
```

Or, to make it discoverable to anyone who has Hermes:

```bash
hermes skills tap add Little-Grebe-Inc/drillr-skill
```

Restart Hermes — the skill will appear in `/skills browse` and
auto-register as a slash command.

### Other agent runtimes

The skill is a single `SKILL.md` with YAML frontmatter and Markdown
body — no executables, no helper scripts, no MCP bundle required.
Any runtime that can read [Agent Skills](https://agentskills.io)
files should work; the install path is typically the runtime's
`skills/` directory (e.g. `~/.claude/skills/`, `~/.hermes/skills/`,
`~/.config/<runtime>/skills/`).

## What's inside

```
drillr-skill/
├── SKILL.md                           # the skill itself
├── README.md                          # this file
├── CHANGELOG.md                       # version history pinned to API version
└── examples/
    ├── claude-code-mcp-config.json    # drop-in MCP config for Claude Code
    ├── openclaw-mcp-config.json       # drop-in MCP config for OpenClaw
    ├── hermes-mcp-config.yaml         # drop-in MCP config for Hermes
    └── user-onboarding-script.md      # copy-paste-able onboarding prompts
```

## Prerequisites for use

- A Drillr account (free): <https://drillr.ai>
- An `external` scope API key: <https://drillr.ai/developer/keys>

The skill itself handles teaching the agent how to onboard the
user and collect the key — you don't need to do anything special
beyond dropping the skill in.

## License

MIT — see `LICENSE`.

## Links

- Drillr: <https://drillr.ai>
- API reference: <https://drillr.ai/developer/docs>
- Issues / feedback: <https://github.com/Little-Grebe-Inc/drillr-skill/issues>
