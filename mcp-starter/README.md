# MCP Starter — your Week 1 server

A complete, working MCP server built with **FastMCP**. Build it this afternoon,
see it run in the Inspector, then connect it to Claude Desktop and watch Claude
call *your* tools.

It exposes all three MCP primitives:
- **tools** — `add`, `get_weather` (the weather tool wraps a real external API — the money skill)
- **resource** — `about`
- **prompt** — `outdoor_check`

---

## Prerequisites
- **Python 3.10+** — check with `python --version` (or `python3 --version`)
- **Claude Desktop** (free) — https://claude.ai/download
- _Optional but recommended:_ **uv** (fast Python runner) — https://docs.astral.sh/uv/

---

## Step 1 — Install dependencies
From inside this `mcp-starter/` folder:

```bash
pip install -r requirements.txt
```

(or with uv: `uv pip install -r requirements.txt`)

---

## Step 2 — See it work IMMEDIATELY (no Claude needed yet)
Launch the **MCP Inspector** — a browser UI to test your tools directly:

```bash
fastmcp dev server.py
```

It prints a local URL. Open it, find the **Tools** tab, click `get_weather`,
type a city (e.g. `Tokyo`), and hit run. You just called your own MCP server. 🎉
Try `add` and the `about` resource too.

> If `fastmcp dev` isn't found, run `fastmcp --help` to see the exact subcommand
> name for your version, or `python server.py` (it'll wait silently on stdio — that's
> correct; Ctrl+C to quit).

---

## Step 3 — Connect it to Claude Desktop

**Easy button** (FastMCP writes the config for you):
```bash
fastmcp install claude-desktop server.py
```

**Manual** (if you prefer, or the CLI differs): edit Claude Desktop's config file:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "demo": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/mcp-starter/server.py"]
    }
  }
}
```
Use the **absolute** path, and make sure `python` is the same interpreter where you
installed the dependencies (on macOS it may be `python3`). Cleaner cross-env option:
```json
{
  "command": "uv",
  "args": ["run", "--with", "fastmcp", "--with", "httpx",
           "fastmcp", "run", "/ABSOLUTE/PATH/TO/mcp-starter/server.py"]
}
```

---

## Step 4 — Restart Claude Desktop and try it
Fully quit and reopen Claude Desktop. Click the **tools** icon (slider/hammer) in the
chat box — you should see `add`, `get_weather`. Then ask:

> *"What's the weather in Tokyo right now?"*

Watch Claude call your `get_weather` tool and answer with live data. **That's an MCP
server doing real work.** You're now ahead of 99% of "AI freelancers."

---

## Troubleshooting
- **Tools don't appear** → you didn't fully quit Claude Desktop (use Quit, not just close the window); or the path/interpreter in the config is wrong.
- **`fastmcp: command not found`** → `pip install fastmcp` didn't land on your PATH; try `python -m fastmcp dev server.py`.
- **Weather errors** → check internet; the API is keyless and free, so it's almost always a typo'd city.

---

## What to build next (Week 2 → 3)
1. **Swap the API.** Replace Open-Meteo with an API *a business actually pays for* —
   their CRM, a Google Sheet, Airtable, Notion, Postgres. Same pattern: a `@mcp.tool`
   that calls the API and returns the result.
2. **Add a write tool** (create a record, send a message) — read-only is cheap, write
   actions are what clients pay for.
3. **Go remote.** Switch `mcp.run()` → `mcp.run(transport="http")` to serve it over
   Streamable HTTP, deploy to Railway/Render, add auth. That's your $300–$600 tier.

This file is the seed of your first **$100–$150 gig deliverable**.
