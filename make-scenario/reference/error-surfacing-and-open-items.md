# Hardening the production scenario — error surfacing + open items

Companion to `NEW_PRODUCTS_AUTOCREATE_ON_SHOPIFY_blueprint_FIXED.json`.
Addresses the open items from the handoff. The blueprint itself isn't in this
repo — paste it in and I'll integrate these directly.

---

## 1. Real error surfacing (the root cause)

**Problem:** Shopify GraphQL returns **HTTP 200 even when the mutation fails**.
The failure is in the `userErrors` array (business-level) or the top-level
`errors` array (transport-level: throttling, `PARSE_ERROR`, auth, cost limits).
Make's `handleErrors` only reacts to non-2xx HTTP, so the scenario shows **green
while nothing saved**.

**Fix:** drop this reusable JS guard immediately **after** each Shopify GraphQL
module. It throws on either error class, so the run actually fails loudly.

```js
// shopify-userErrors-guard  (place AFTER each Shopify GraphQL HTTP module)
// Inputs:
//   response ← parsed Shopify body, e.g. {{75.data}}
//   path     ← mutation name, e.g. "productCreate"
//   label    ← human label, e.g. "createProduct (75)"
const body = input.response || {};

// 1) Transport/GraphQL-level errors (throttling, PARSE_ERROR, auth, cost)
if (Array.isArray(body.errors) && body.errors.length) {
  const g = body.errors.map(e =>
    (e.message || 'error') +
    (e.extensions && e.extensions.code ? ` (${e.extensions.code})` : '')
  ).join(' | ');
  throw new Error(`[${input.label || 'Shopify'}] GraphQL error: ${g}`);
}

// 2) Business-level userErrors (HTTP 200, mutation silently failed)
const node = ((body.data || {})[input.path]) || {};
const errs = node.userErrors || node.mediaUserErrors || node.translationUserErrors || [];
if (Array.isArray(errs) && errs.length) {
  const u = errs.map(e => {
    const f = Array.isArray(e.field) ? e.field.join('.') : (e.field || '');
    return (f ? `${f}: ` : '') + (e.message || JSON.stringify(e));
  }).join(' | ');
  throw new Error(`[${input.label || 'Shopify'}] ${errs.length} userError(s): ${u}`);
}
return { ok: true };
```

### Where to place it

| After module | `response` | `path` | `label` |
|---|---|---|---|
| 75 createProduct | `{{75.data}}` | `productCreate` | `createProduct (75)` |
| 87 metafields | `{{87.data}}` | `productUpdate` | `metafields (87)` |
| 106 SEO | `{{106.data}}` | `productUpdate` | `SEO (106)` |
| 100 translations | `{{100.data}}` | `translationsRegister` | `translations (100)` |

> Confirm the parsed body path. The HTTP "Make a request" module
> (`http:ActionSendData`) with *Parse response = Yes* exposes the JSON body at
> `{{N.data}}`, so the GraphQL envelope is `{{N.data.data.<mutation>}}` +
> `{{N.data.errors}}`. If you used Shopify's native app module instead, adjust.

### Surface vs. resilience — pick one behaviour

- **Hard fail (default above):** guard throws → run goes **red** → Make emails
  you. Simple, but stops the current batch row.
- **Resilient (recommended for batch runs):** add an **error handler** on the
  guard → **Google Sheets ▸ Update Row** (`Status = error`,
  `Error = {{error.message}}`) with directive **Commit**. The bad row is logged
  and skipped; the rest of the batch keeps going. Pair with a Slack/email module
  in the handler if you want a ping. Either way you never get a false green.

---

## 2. `need_enrichment` Boolean metafield

**`"false"` (string) is the correct wire value** for a `boolean` metafield —
Shopify's `MetafieldInput.value` is always a String; for type `boolean` it must
be exactly `"true"` or `"false"`. So the code is right **iff the definition type
is boolean**. The skip-empty logic (107) correctly keeps it, since `"false"` is
non-empty.

Verify the definition type (run in Shopify admin ▸ GraphiQL app or your client):

```graphql
query ProductMetafieldDefs {
  metafieldDefinitions(first: 100, ownerType: PRODUCT) {
    nodes { namespace key name type { name } }
  }
}
```

Confirm `need_enrichment` → `type.name == "boolean"`. If it's anything else,
either change the definition or stop sending `"true"/"false"`.

---

## 3. Is `product_type` actually translatable?

Most likely **no**. Shopify's translatable Product keys are `title`,
`body_html`, `handle`, `meta_title`, `meta_description` (and options/values +
translation-enabled metafields). `product_type` is generally **not** in the
translatable set — so module 102 returns an empty `product_type_digest`, and
module 108 dropping it is **correct behaviour, not a bug**.

Confirm definitively for your store:

```graphql
query Translatable($id: ID!) {
  translatableResource(resourceId: $id) {
    resourceId
    translatableContent { key value digest locale }
  }
}
# variables: { "id": "gid://shopify/Product/<id>" }
```

If no `product_type` key comes back, it isn't translatable — and if you truly
need a localized type, model it as a translation-enabled **metafield** or a
**category**, not via `translationsRegister`.

---

## 4. Sheets update (94) — downstream

No Shopify validation happens here, so two things to confirm:
- It writes back the real `gid` / handle / status from module 75 (not a stale
  or empty value).
- **Failure recording:** with the guards in §1 throwing, a failed row will
  *not* reach module 94 — so the row is neither marked done nor error. Use the
  **resilient** error-handler option (§1) so failures still land in the sheet as
  `Status = error`; otherwise failed rows silently stay blank and get retried
  forever.

---

## QA checks before trusting a green run

- [ ] **Double-encoding:** open a created product's metafields in Shopify admin
      and confirm text values are **not** wrapped in literal quotes
      (`"Bamboo"` stored as `Bamboo`, not `"Bamboo"`). Literal quotes = the
      value was JSON-stringified twice in module 107 — stringify the **array
      once**, not each value and the array.
- [ ] `need_enrichment` definition is Boolean (§2).
- [ ] `translatableResource` confirms which keys are real (§3).
- [ ] Force a known failure (e.g. invalid metafield type) and confirm the run
      now goes **red / logs to the sheet** instead of green.
