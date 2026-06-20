# Fiverr / Freelance Gig Research Playbook

_Last updated: 2026-06-20_

This is the saved trail of a full gig-research session: the methodology, what got
ruled out and why, and two fully-mapped paths to commit to. Built on **live mid-2026
market data**, not recycled listicles.

---

## 0. The methodology (your permanent edge)

Most people pick a niche off a "Top 10 Fiverr gigs 2026" blog. That's how you land in
a graveyard. The whole game is the overlap of **real buyer demand × low/accessible
competition**.

### The velocity + accessibility test (run on any niche, ~5 min, logged in)

1. **Search the exact keyword** → note total results.
   `<500` great · `500–1,500` workable with SEO + a few reviews · `>1,500` secondary tag only.
2. **Open the top 8–10 gigs** and read:
   - **"Orders in Queue"** → want several with live queues.
   - **Newest review _date_** → within ~2 weeks = alive; _months_ old = morgue 🪦.
   - **Review velocity** → 30 reviews all from the last 6 weeks beats 300 where the newest is 4 months old.
3. **The accessibility check (the decisive one):** does page 1 have any **New Seller /
   sub-20-review** gigs ranking? Some newcomers = you can break in. **All 500+ review
   veterans = locked, walk away.**
4. **Cross-check Google Trends** on the term — rising, not flat.
5. **PASS only if BOTH are green:** recent reviews/active queues **AND** newcomers on page 1.
   - High demand + locked page 1 = trap (the voice-agent problem).
   - Open page 1 + no demand = dead (the Notion problem).

### Rules learned this session

- **Fiverr's level system structurally rewards incumbents.** A niche older than ~12 months
  is usually locked for new accounts no matter how "in demand" it is. Win by **(1) entering
  during a niche's pre-saturation window, or (2) selling where seller-levels don't gate you.**
- **Tool-name keywords are a beginner trap.** `make.com automation` (11k+ results),
  `zapier automation` (6.5k+), `make com` (3.3k+) are wall-to-wall specialists. Rank on the
  lower-competition **outcome** term; deliver _with_ the saturated tools.
- **"Novel + uncontested" and "fastest + easiest to earn" pull in opposite directions.**
  Every still-open niche is open because of a moat: skill, audience-building, or craft.
  Pick which goal leads — eyes open.

---

## 1. What got ruled out (and why)

| Niche | Verdict | Why |
|---|---|---|
| Notion setup / dashboards / templates | ❌ Graveyard | Real keyword competition (`notion setup` 547, `notion crm` 620) but **order velocity dead** — most gigs' newest delivery was 3–4 months old. Supply without buyers. |
| AI voice agents (Vapi/Retell) | ⚠️ Not for new accounts | Genuine velocity, but leveled sellers vacuum the demand; new gigs starve on page 7. Mentor-confirmed. |
| MSFS liveries / VRChat avatars | ⚠️ Wrong lane | Real, low-competition passion subcultures — but design/3D craft skills and low ticket ($5–$45 liveries). Not an automation lane. |
| ComfyUI / Flux LoRA | ⚠️ Filling fast | Still younger than voice agents, but already entering the blog phase; big chunk is the AI-influencer/NSFW economy. Fresh corners only (product photography, consistent-character storybooks). |
| Generic writing / translation | ❌ Declining | Down ~28% / ~22% — AI ate it. |

**Profile that drove the final picks:** tech/automation lane · wants fastest path to first
dollar · likely real-estate domain knowledge.

---

## 2. PATH A — MCP servers (highest ceiling, thinnest competition)

### What it is (for selling)
**Model Context Protocol (MCP)** is the open standard — created by Anthropic, **donated to
the Linux Foundation's Agentic AI Foundation in Dec 2025** — that lets AI assistants (Claude,
Cursor, Copilot, etc.) plug into external tools, data, and systems through one uniform
interface. Businesses pay you to build an **MCP server** that exposes _their_ data/API/tools
so their team (or their customers) can use it inside AI clients — replacing brittle one-off
integrations.

### Why it's the bet
- **Thin competition _because_ it's hard** — the skill gate is the moat.
- **Real, high-ticket demand:** live Fiverr gigs from **$100 → $3,000**; active Upwork
  enterprise jobs (MCP gateways with routing/JWT/rate-limiting/multi-tenant); a Freelancer
  category; 13,000+ MCP servers on GitHub; 97M+ SDK downloads.
- **Pre-saturation window**, and dead-on your automation/technical lane.

### Exact skills (in dependency order)
1. **A language — Python (recommended) or TypeScript.** Python via **FastMCP 3.0** (released
   Jan 2026) is the fastest on-ramp: you decorate Python functions as MCP "tools." No coding
   yet? Week 1 = Python basics (functions, async, JSON, calling REST APIs with `httpx`).
2. **REST APIs / JSON / auth basics** — most MCP servers _wrap an existing API_ (a CRM,
   database, internal service). Direct extension of the no-code "connect app A to app B" instinct.
3. **MCP core concepts** — the three primitives a server exposes: **tools** (actions the AI
   can call), **resources** (data it can read), **prompts** (reusable templates); plus the
   client/server model.
4. **The SDK** — **FastMCP** (Python) or **`@modelcontextprotocol/sdk` + Zod** (TypeScript).
   SDKs also exist for Java, Kotlin, C#, Go.
5. **Transports** — **stdio** (local, simplest) vs **Streamable HTTP** (remote, hosted,
   multi-user). Start stdio, graduate to Streamable HTTP.
6. **OAuth for remote servers** — the multi-tenant/enterprise tier (JWT, auth). This is the
   $1k–$3k differentiator.
7. **Deploy/host** — Docker on Railway / Render / Fly.io / Cloudflare Workers.
8. **Distribution + credibility** — publish public servers to **GitHub** and the **Smithery**
   registry. Public servers = portfolio + inbound leads.

### 3–4 week ramp
- **Week 1 — Foundations.** Python basics (skip if you code). Build & call a REST API. Read the
  MCP intro docs. Install Claude Desktop / Cursor as your test client.
- **Week 2 — First local server.** With FastMCP, build a **stdio** server wrapping one public
  API (weather, GitHub, a Google Sheet). Connect it to Claude Desktop, watch Claude call your
  tools. First portfolio piece.
- **Week 3 — Real, niche server + remote.** Build something a business would pay for: "MCP
  server that lets Claude query your Postgres / Airtable / Notion / CRM." Convert to
  **Streamable HTTP**, deploy to Railway/Render (live URL), add basic auth.
- **Week 4 — Productize + ship.** Add OAuth for the multi-tenant story, clean README, publish
  1–2 servers to GitHub + Smithery, record a 2-min Loom demo, create the gig.

### The $100 → $1,000+ gig ladder (one productized gig, tiered)
| Tier | Price | Scope |
|---|---|---|
| **Basic** | **$100–$150** | One stdio (local) server wrapping a single API/data source, ~3–5 tools, delivered as code + setup guide. (Matches the live $100 gig.) |
| **Standard** | **$300–$600** | Remote (Streamable HTTP) server, hosted/deployed, with auth, connecting one business system (CRM/DB/Notion). Tools + resources + Loom walkthrough. |
| **Premium** | **$1,000–$3,000** | Multi-tenant MCP gateway: OAuth, multiple data sources, rate-limiting, deploy to their cloud, full docs. (Matches the live $3,000 enterprise gig.) |
| **Retainer** | recurring | Maintenance + adding tools as their needs grow. |

**Gig title direction:** _"I will build a custom MCP server to connect [your data/tools] to
Claude / AI assistants."_ Niche by source system (Notion / Airtable / Postgres / your SaaS) or
by vertical.

---

## 3. PATH B — Productized automation templates (ungated, passive)

### What to build
Sharp, single-problem **n8n / Make workflow templates** (optionally **GoHighLevel snapshots**).
Not generic mega-bundles (those race to the bottom) — outcome-named templates:
- "Auto-qualify inbound leads → enrich → push to CRM → Slack alert"
- "Form submission → generate invoice → email + log to Sheet"
- "AI content factory: idea → draft → schedule across socials"
- Vertical-specific (real estate / agency / ecom): "New lead → SMS follow-up sequence → book showing"

### Where to sell
- **Gumroad** — primary storefront (no upfront cost, handles checkout/delivery).
- **n8n creator marketplace** — 8,300+ templates and growing; n8n is building a creator
  program + affiliate. Native buyer intent.
- **Make / Zapier template galleries** for reach; **Whop** to bundle into a community/product.
- **Fiverr** as a _secondary_ funnel (gig that delivers the template + setup) — but the product
  channel is the un-gated play.

### Pricing / tiers (per template)
| Tier | Price |
|---|---|
| Basic template | **$29–$49** |
| Template + customization guide | **$99–$149** |
| Template + implementation support | **$199–$299** |
| Bundle of related templates | **$199–$499** |

### How to get the first traffic (the hard part — be honest)
1. **Free lead-magnet template.** Give away one genuinely useful workflow → collect emails →
   upsell paid versions. The #1 tactic.
2. **YouTube walkthroughs.** Short screen-recordings demoing the workflow solving the problem;
   link the template in the description. Tutorial traffic = buyer traffic; it compounds.
3. **Build in public** on X/LinkedIn + r/n8n, r/automation, r/nocode, automation Discords.
   Answer "how do I automate X" with your template.
4. **n8n marketplace + SEO** — list where people already search; problem-focused titles.
5. **Trust docs** — step-by-step install guide + demo video per template so beginners can run it.
6. **Portfolio of 5–10 templates** → cross-sell + multiple income streams; each is a discovery surface.

### Honest reality check
Ungated by Fiverr levels ✅ and passive once built ✅ — **but you supply 100% of the
distribution**, n8n culture leans free, and it's slower to first dollar than a service gig.
It's a product + audience business. Best as a **medium-term asset**, ideally layered on top of
service income.

---

## 4. Recommendation & sequencing

These compound — don't treat them as either/or:

1. **Now (cash + credibility):** climb the **MCP** ramp. Highest ceiling, thinnest
   competition, on-lane. Land Basic gigs → reviews → climb the ladder.
2. **As you go (passive layer):** the servers/workflows you build for MCP and automation
   clients become **templates, case studies, and YouTube content** — spin them into Path B
   products for ungated, passive income.
3. **Always:** before committing to any specific gig keyword, **run the velocity +
   accessibility test** yourself.

---

## 5. Sources (live, June 2026)

- Fiverr Business Trends Index — June 2026 (official): https://www.fiverr.com/resources/guides/reports/business-trends-index-june-2026
- Fiverr High Demand 2025/2026 outlook (accio): https://www.accio.com/business/high-demand-services-on-fiverr-2025-trend
- MCP jobs board (Freelancer): https://www.freelancer.com/jobs/model-context-protocol
- Live $3,000 MCP gig (Fiverr): https://www.fiverr.com/asheshgoplan509/build-and-integrate-model-context-protocol-mcp-servers-for-you
- Complete Guide to MCP in 2026 (DEV): https://dev.to/x4nent/complete-guide-to-mcp-model-context-protocol-in-2026-architecture-implementation-and-4a11
- MCP cheat sheet 2026 (Webfuse): https://www.webfuse.com/mcp-cheat-sheet
- `@modelcontextprotocol/sdk` (npm): https://www.npmjs.com/package/@modelcontextprotocol/sdk
- n8n: 5 automations = $3,200/mo passive (Medium): https://medium.com/write-a-catalyst/i-built-5-n8n-automations-that-generate-3-200-month-passively-72e2a3050e17
- Monetize n8n — 5 strategies (Ritz7): https://ritz7.ai/blog/monetize-n8n-automation-skills
- Fastest-growing AI freelance skills 2026 (Medium/No Time): https://medium.com/no-time/the-6-fastest-growing-ai-freelance-skills-on-upwork-2026-162aeff487a2
- VRChat creator economy guide 2026: https://generalistprogrammer.com/tutorials/vrchat-creator-economy-complete-money-making-guide
