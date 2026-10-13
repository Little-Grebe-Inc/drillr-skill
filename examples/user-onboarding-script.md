# User onboarding

## Install or connect drillr MCP

Read the [official installation guide](https://drillr.ai/developer/mcp-install.md)
for the user's target app. Keep client-specific steps, response language, OAuth,
and connection verification in that guide instead of copying them here.

The user can paste this into their agent:

```text
Please connect drillr MCP in this app using this installation guide: https://drillr.ai/developer/mcp-install.md. Walk me through sign-in and verify the connection.
```

A phone or chat interface alone does not determine whether its runtime supports
OAuth. Use the guide's matching client section before choosing an API-key fallback.

## REST API access

Use this flow when the user requests REST API access. For MCP without OAuth,
use the fallback in the installation guide.

> Open https://drillr.ai/account/api-keys and sign in. Create an external API key,
> then save it in your runtime's secret manager or set `DRILLR_API_KEY` locally.
> Do not paste the key into this conversation. Tell me when it is configured.

Use the configured key without displaying it. Verify REST access as described in
`SKILL.md`. Confirm success only after that request succeeds.

If the request returns 401, ask the user to check or replace the key in the same
secure storage. Do not ask them to send the key in chat.
