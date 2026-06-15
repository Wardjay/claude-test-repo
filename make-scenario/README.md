# Auto-create Shopify products from Google Sheets (Make.com)

A rebuilt, **break-resistant** Make.com scenario that turns a single product
idea in a Google Sheet into a fully-built Shopify product:

1. Read new rows from Google Sheets (just a product name/idea per row).
2. **OpenAI** generates everything else — title, description, type, vendor,
   tags, price, SEO, and an image search query — as **guaranteed-valid JSON**.
3. **SERP** finds a real product image from the web using that query.
4. **Shopify GraphQL** creates the product **+ variant + image + ALL
   metafields in a single API call** (`productSet`).
5. Write the result (product ID, handle, status) back to the sheet so the row
   is never processed twice.

> TL;DR of why your old one broke and this one won't: fewer API calls
> (1 GraphQL call instead of 5+ REST calls), **structured JSON output** from
> OpenAI (no more parse failures), per-module **error handlers** that log to the
> sheet instead of killing the run, **idempotent** row selection (status
> column), and **batching** so rate limits never cascade. See
> [Why the old build breaks](#why-the-old-build-keeps-breaking).

---

## Contents

| File | What it is |
|------|------------|
| `blueprint.json` | Importable Make scenario scaffold. Import, then attach your connections. |
| `google-sheet-template.csv` | The exact column layout for your sheet. |
| `reference/openai-system-prompt.md` | The system prompt for product generation. |
| `reference/openai-request.json` | The full OpenAI HTTP request body, incl. the strict JSON schema. |
| `reference/shopify-productSet.graphql` | The one-call create mutation. |
| `reference/shopify-body.example.json` | The full Shopify HTTP body with Make field mappings. |
| `reference/serp-request.md` | SERP image-search config (SerpApi + cheaper Serper.dev alt). |

---

## Architecture (the flow)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Google Sheets ▸ Search Rows   (scheduled, e.g. every 15 min, limit 10)    │
│  filter: Status is EMPTY        ── idempotent: only unprocessed rows        │
└───────────────┬──────────────────────────────────────────────────────────┘
                │  (one bundle per row)
        ┌───────▼────────┐
        │ Filter         │  Product Name is not empty  (data validation)
        └───────┬────────┘
        ┌───────▼────────────────────┐
        │ HTTP ▸ OpenAI Chat Compl.  │  Structured Outputs (json_schema, strict)
        │   → guaranteed valid JSON  │  ⮕ error handler → mark row "error"
        └───────┬────────────────────┘
        ┌───────▼────────┐
        │ JSON ▸ Parse   │  parse choices[0].message.content → fields
        └───────┬────────┘
        ┌───────▼────────────────────┐
        │ HTTP ▸ SERP image search   │  q = image_search_query
        │                            │  ⮕ error handler → Resume (no image)
        └───────┬────────────────────┘
        ┌───────▼────────────────────┐
        │ JSON ▸ Create JSON         │  safely build productSet variables
        │   (arrays, metafields)     │  ← plug your metafields in HERE
        └───────┬────────────────────┘
        ┌───────▼────────────────────┐
        │ HTTP ▸ Shopify GraphQL     │  productSet: product+variant+image+
        │   productSet (1 call)      │  metafields. ⮕ Break+retry on 429/5xx
        └───────┬────────────────────┘
        ┌───────▼────────┐
        │ Router         │  userErrors empty?  ── no → mark row "error"
        └───────┬────────┘
        ┌───────▼────────────────────┐
        │ Google Sheets ▸ Update Row │  Status=done, Product ID, Handle, time
        └────────────────────────────┘
```

Every external call (OpenAI, SERP, Shopify) has an **error handler** that writes
the failure back to the sheet (`Status = error`, `Error` column) and moves on, so
**one bad row never stops the scenario**.

---

## Prerequisites (one-time)

1. **Shopify custom app + Admin API token**
   - Shopify admin ▸ Settings ▸ Apps and sales channels ▸ Develop apps ▸ Create
     an app.
   - Admin API access scopes: **`write_products`**, **`read_products`**
     (these also cover product **metafields**).
   - Install the app, copy the **Admin API access token** (`shpat_…`).
   - Note your store domain: `your-store.myshopify.com`.
2. **OpenAI API key** (`sk-…`) with access to a model that supports
   **Structured Outputs** (e.g. `gpt-4.1`, `gpt-4o`, or your latest).
3. **SERP provider key** — [SerpApi](https://serpapi.com) (`google_images`) or the
   cheaper [Serper.dev](https://serper.dev) `/images`. See `reference/serp-request.md`.
4. **Google account** connected to Make for Sheets.
5. A Google Sheet built from `google-sheet-template.csv`.

---

## The Google Sheet

Use `google-sheet-template.csv` as your header row (first sheet/tab). Columns:

| Col | Header | You fill? | Purpose |
|-----|--------|-----------|---------|
| A | `Product Name` | ✅ yes | Your input — e.g. "Bamboo cutting board" |
| B | `Status` | leave empty | Trigger: empty = process. Becomes `done` / `error`. |
| C | `Shopify Product ID` | auto | `gid://shopify/Product/…` written back |
| D | `Handle` | auto | Shopify product handle |
| E | `Admin URL` | auto | Direct link to edit the product |
| F | `Error` | auto | Failure reason (only on errors) |
| G | `Processed At` | auto | Timestamp |

> To process a row, just type a product name and leave `Status` blank. To
> re-run a failed row, clear its `Status` cell.

---

## Build it step by step

You can **import `blueprint.json`** (Make ▸ Create a new scenario ▸ ⋯ ▸ Import
Blueprint) and then attach connections + paste keys — or build the 9 modules
manually with the configs below. The manual route takes ~15 min and is the
source of truth if the import complains about a module version.

> **After importing**, you must: (1) re-attach the **Google connection** on the
> two Sheets modules, (2) set your **Spreadsheet ID** + sheet name, and
> (3) paste your **API keys** into the header values
> (`YOUR_OPENAI_KEY`, `YOUR_SERPAPI_KEY`, `YOUR_ADMIN_TOKEN`,
> `YOUR-STORE`). The blueprint ships the **happy path** — add the
> **error handlers** (step 3/5/7) in the UI, since those are easiest to wire
> visually. The `{{2.…}}`, `{{3.…}}` field references below are illustrative;
> when you pick a field from Make's visual mapper it inserts the correct
> module number for your build automatically.

### 1. Google Sheets ▸ Search Rows  *(trigger, scheduled)*
- Connection: your Google account. Spreadsheet + sheet: your products sheet.
- Filter: **`Status`** `Is empty`.
- Sort: by row number ascending. **Maximum number of returned rows: `10`**
  (this is your batch size — keep it small so rate limits never cascade).
- Scheduling (bottom-left clock): **Every 15 minutes** (tune to taste).

> Why Search Rows and not Watch Rows? Watch Rows tracks a moving cursor and can
> skip or re-process rows when runs fail mid-way. Search-by-`Status` is
> **idempotent**: a row is only picked up while `Status` is blank, and we set it
> to `done`/`error` at the end — so nothing is ever created twice.

### 2. Filter  *(after module 1)*
- Condition: `Product Name` **Exists** / text is not empty. Label it
  "Has product name". Stops blank rows.

### 3. HTTP ▸ Make a request — OpenAI
- URL: `https://api.openai.com/v1/chat/completions`  ·  Method: `POST`
- Headers:
  - `Authorization: Bearer YOUR_OPENAI_KEY`
  - `Content-Type: application/json`
- Body type: **Raw** ·  Content type: **JSON (application/json)**
- Body: paste `reference/openai-request.json` and map the product name into the
  user message (`{{1.`Product Name`}}`).
- **Parse response: Yes.**
- ⚙️ **Error handler** (right-click module ▸ Add error handler):
  attach a **Google Sheets ▸ Update Row** that sets `Status = error`,
  `Error = {{error.message}}`. Directive: **Commit** (log and stop this row).

### 4. JSON ▸ Parse JSON
- JSON string: `{{3.data.choices[1].message.content}}` (the model's reply is a
  JSON string — this turns it into mapped fields: `title`, `description_html`,
  `price`, `tags[]`, `image_search_query`, …).

### 5. HTTP ▸ Make a request — SERP image search
- See `reference/serp-request.md`. Map `q` = `{{4.image_search_query}}`.
- Parse response: Yes.
- ⚙️ **Error handler: Resume** with a bundle of `{ image_url: "" }` — so a SERP
  miss still lets the product be created **without** an image instead of failing.

### 6. JSON ▸ Create JSON — build the Shopify variables
- Pick/define a data structure matching `ProductSetInput` (see
  `reference/shopify-body.example.json`). Map the parsed OpenAI fields + the SERP
  image URL into it.
- **This is where your metafields go** — see
  [Plug in your metafields](#plug-in-your-metafields).
- Using Create JSON (instead of hand-typing arrays into the HTTP body) is what
  makes arrays like `tags` and the metafields list serialize correctly. This
  single detail kills a whole class of "invalid JSON" breakages.

### 7. HTTP ▸ Make a request — Shopify GraphQL `productSet`
- URL: `https://YOUR-STORE.myshopify.com/admin/api/2025-01/graphql.json`
- Method: `POST` · Headers:
  - `X-Shopify-Access-Token: YOUR_ADMIN_TOKEN`
  - `Content-Type: application/json`
- Body type: **Raw / JSON**. Body:
  `{"query": "<mutation from shopify-productSet.graphql>", "variables": {"input": <output of module 6>}}`
- Parse response: Yes.
- ⚙️ **Error handler: Break** — retries: `3`, interval: `15` minutes. Break
  auto-retries transient `429`/`5xx` errors later without losing the row.

### 8. Router — check Shopify userErrors
- Route A (filter: `{{7.data.data.productSet.userErrors}}` **is empty**) → success.
- Route B (fallback) → **Update Row**: `Status = error`,
  `Error = {{7.data.data.productSet.userErrors[].message}}`.

### 9. Google Sheets ▸ Update Row  *(success route)*
- Row number: `{{1.__ROW_NUMBER__}}` (`__IMTINDEX__` / Row number from module 1).
- `Status = done`
- `Shopify Product ID = {{7.data.data.productSet.product.id}}`
- `Handle = {{7.data.data.productSet.product.handle}}`
- `Admin URL = https://YOUR-STORE.myshopify.com/admin/products/` + numeric id
- `Processed At = {{now}}`

---

## Plug in your metafields

You said you'll send your exact list — here's exactly where it goes. In the
**Create JSON** module (step 6), the `metafields` array takes one object per
metafield:

```json
{ "namespace": "custom", "key": "material", "type": "single_line_text_field", "value": "Bamboo" }
```

Rules that prevent metafield breakage:
- **`type` must match the metafield definition** already in Shopify
  (Settings ▸ Custom data ▸ Products). Mismatched types are the #1 metafield
  error. Pre-create your definitions there first.
- Common `type` values: `single_line_text_field`, `multi_line_text_field`,
  `number_decimal`, `number_integer`, `boolean`, `url`, `json`,
  `list.single_line_text_field`.
- **List** types: `value` must be a **JSON-encoded string**, e.g.
  `"[\"Cotton\",\"Linen\"]"` for `list.single_line_text_field`.
- Want OpenAI to fill some metafields? Add those keys to the JSON schema in
  `reference/openai-request.json` and map them in step 6.

Send me your list (namespace · key · type · where the value comes from) and I'll
finalize the Create JSON structure + extend the OpenAI schema for any
AI-generated ones.

---

## Why the old build keeps breaking

| Common cause | This build's fix |
|---|---|
| OpenAI returns prose / malformed JSON → parse fails | **Structured Outputs** (`json_schema`, `strict:true`) — output is *always* schema-valid |
| 5+ chained REST calls (product, variant, image, each metafield) — any one fails | **One** `productSet` GraphQL call does it all |
| One bad row aborts the whole run | **Per-module error handlers** log to the sheet and continue |
| Rate limits (429) cascade across many rows | **Batch of 10/run** + **Break with retry** on 429/5xx |
| Rows processed twice / skipped | **Idempotent** `Status`-based selection + write-back |
| Broken/unreachable image URL kills product | Image handler **Resumes**; product still created without image |
| Metafield type mismatch | Types pinned to definitions; documented list/JSON encoding |
| Arrays (tags/metafields) corrupt the JSON body | Built via **Create JSON** module, not hand-typed |

---

## Go-live checklist

- [ ] Products created as **`DRAFT`** first (default in this build) — review a few,
      then switch `status` to `ACTIVE` in step 6 when you trust the output.
- [ ] Verify your metafield **definitions** exist in Shopify and types match.
- [ ] Run with **2–3 test rows** before turning on the schedule.
- [ ] Confirm error rows get `Status = error` + a readable `Error` message.
- [ ] Set the schedule + batch size to respect your OpenAI/SERP/Shopify limits.
- [ ] ⚠️ **Images from SERP** are pulled from the open web — verify you have the
      right to use them commercially. Prefer your own/licensed images, or use
      SERP only as a placeholder for draft products you finalize by hand.

---

## Tuning notes

- **Cost/quality:** `gpt-4o-mini` / `gpt-4.1-mini` are cheap and fine for most
  catalogs; step up to `gpt-4.1`/`gpt-4o` for richer copy.
- **Throughput:** raise the schedule frequency and/or batch size once you've
  confirmed you're under your rate limits. Add a **Sleep** module before Shopify
  if you ever see sustained 429s.
- **Duplicates guard (optional):** before `productSet`, add a Shopify
  `productByHandle` query and skip if it already exists — useful if multiple
  people edit the sheet.
