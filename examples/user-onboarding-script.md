# User-onboarding script templates

Copy-paste-able prompts the agent can send to the user during key
onboarding. Adapt freely; they're written to be polite, brief, and
IM-friendly (short paragraphs, numbered steps).

---

## Path A — Indirect (IM / web chat / phone user)

### First-time key request

> To use Drillr I need an API key. From any browser (your phone is
> fine):
>
> 1. Open https://drillr.ai/account/api-keys
> 2. Sign in — **Google sign-in is the quickest**; email/password
>    also works
> 3. Tap "Create API key" → name it (e.g. "my-agent") → copy the
>    `drl_...` string
> 4. Paste it back to me here. The key is shown only once.
>
> After I confirm it works, you can delete your message.

### Confirmation after storing (mask the key!)

> Stored `drl_xxxxxxxx_...e9f2`. You can safely delete your message
> now.

### When the pasted key fails validation (401)

> That key didn't work — I got a 401 from Drillr. It may have a
> typo, or it may have already been revoked. Could you go back to
> https://drillr.ai/account/api-keys, create a fresh one, and paste
> it again?

### When the key is revoked mid-session

> Your Drillr API key was just revoked. To keep going, please
> create a new one at https://drillr.ai/account/api-keys and paste
> it here.

---

## Path B — Direct (terminal co-located with user)

### Claude Code MCP setup (browser sign-in, no key)

> 1. Run `claude mcp add --scope user --transport http drillr-data https://gateway.drillr.ai/mcp/data`, or add this to `~/.claude.json` (or merge it into your existing
>    `mcpServers` object):
>
>    ```json
>    {
>      "mcpServers": {
>        "drillr-data": {
>          "type": "http",
>          "url": "https://gateway.drillr.ai/mcp/data"
>        }
>      }
>    }
>    ```
>
> 2. Restart Claude Code, run `/mcp`, pick `drillr-data` → Authenticate,
>    and approve **drillr Data** in the browser.

### REST / env-var setup

> ```
> export DRILLR_API_KEY=drl_...
> ```
>
> Then any HTTP call carries the header
> `Authorization: Bearer $DRILLR_API_KEY` (or `X-API-KEY`).
> Base URL for typed data: https://gateway.drillr.ai/api/v2 — see https://drillr.ai/docs/api
