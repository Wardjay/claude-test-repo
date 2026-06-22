# Fix: "handle is already taken" on translationsRegister (module 23)

## The error
```
[200] Error(s):
translations.9.value - bataleon-stereo-team-snowboard is already taken
as a handle for this resource
Code: RuntimeError   Origin: Shopify
```

## Root cause (exact)
Module 23 (`translationsRegister`) sends a **hard-coded** array of 15 translations.
`translations.9` (0-based) is the **German `handle`** = `{{6.result.handle_de}}`.

Module 16 created the product with `handle = {{6.result.handle_en}}` — that's the
product's **default** handle. Shopify won't let a *localized* handle equal the
default handle (or another locale's handle); it errors with "already taken."

For snowboards the AI returns the **same** slug for EN and DE
(`bataleon-stereo-team-snowboard` — "snowboard" is identical in both languages),
so the DE handle collides. FR passed because it differs
(`...-planche-snowboard`); Shopify just reports the first clash it hits.

This is bug #3 from the handoff — it is **not** fixed in this blueprint version
(there's no "build translations" code module; module 23 is still hard-coded).

## The fix
Stop hard-coding. Build the translations array in code and **skip any handle that
equals the default or another locale's handle**, plus skip empty values/digests
(which also makes the `product_type` non-translatable issue disappear quietly).

### Step 1 — add a Code module before module 23
Insert a **Tools → Code (Execute Code, JavaScript)** module between module 22
(digests) and module 23 (translationsRegister). Paste the code from
[`build-translations.js`](./build-translations.js).

Map its 3 inputs:

| Input name | Value |
|---|---|
| `result` | `{{6.result}}` |
| `digests` | `{{22.result}}` |
| `base_handle` | `{{6.result.handle_en}}` |

> Tip: you can paste `translations-codemodule.clipboard.json` straight onto the
> canvas (Ctrl/Cmd-V) — it arrives with these 3 inputs **pre-filled**. Then just
> drag it so it sits between module 22 and module 23. Note the module number Make
> assigns it (it won't necessarily be "25").

### Step 2 — point module 23 at the new module
Open module 23 (translationsRegister). Keep the `query` and
`Variables input format = object`. Replace the **Variables** field with:

```json
{
  "resourceId": "{{16.id}}",
  "translations": {{NN.result.translationsJson}}
}
```

Replace **`NN`** with the new code module's number (or, cleaner: delete the old
`translations: [...]` block and re-map it by picking
`translationsJson` from the new module in Make's field picker — that inserts the
correct id automatically). This mirrors exactly how module 19 consumes
`{{18.result.metafieldsJson}}` for metafields, so it's a proven pattern in your
own scenario.

That's the whole fix — one new module + one field edited. No re-import, so you
**don't** have to reconnect Google / Shopify / OpenAI / SerpApi / Cloudinary.

## Why not just delete the handle lines?
You'd lose localized URLs (bad for FR/ES SEO, which *do* differ). The code keeps
every valid, unique localized handle and only drops the ones that would collide —
best of both.

## After applying — quick check
- Re-run the same Bataleon row: module 23 should now succeed (DE handle dropped,
  FR/ES kept if unique).
- Open the product → Translations: FR/ES have localized URLs; DE falls back to the
  default (expected).
- The run goes green and module 24 (Sheets update) records the row.

## Related (from the handoff, still worth doing)
- **`need_enrichment`**: code sends `"false"` — correct **only if** the metafield
  definition type is `boolean`. Verify in Settings → Custom data → Products.
- **`product_type` translations**: almost certainly not translatable → its digest
  is empty → the new code now **skips** those entries automatically (no more dead
  weight in the array).
