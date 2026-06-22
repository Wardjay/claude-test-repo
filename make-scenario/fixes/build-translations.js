// build translations (skip handle clashes)
// Place this Code (ExecuteCode) module immediately BEFORE module 23 (translationsRegister).
//
// Inputs to map:
//   result      = {{6.result}}              (the AI output: handle_xx, meta_title_xx, html_body_xx, product_type)
//   digests     = {{22.result}}             (title_digest, body_html_digest, handle_digest, product_type_digest)
//   base_handle = {{6.result.handle_en}}    (the handle the product was CREATED with in module 16 = the default)
//
// Output: translationsJson  -> feed into module 23 variables.translations
//
// Why: Shopify rejects a localized handle that equals the product's default handle
// (or another locale's handle) with "<handle> is already taken as a handle for this
// resource". Snowboards make EN and DE handles identical, so DE collided. This also
// drops any entry whose digest is empty (e.g. product_type when it isn't translatable).

var r = input.result || {};
var d = input.digests || {};
var base = (input.base_handle == null ? '' : String(input.base_handle)).trim().toLowerCase();

var used = {};
if (base) used[base] = true;            // the default handle is already taken

var locales = ['en', 'fr', 'de', 'es'];
var out = [];

function add(locale, key, value, digest) {
  value = (value == null) ? '' : String(value);
  if (value.trim() === '') return;                      // skip empty value
  if (!digest || String(digest).trim() === '') return;  // skip missing digest
  out.push({ locale: locale, key: key, value: value, translatableContentDigest: digest });
}

for (var i = 0; i < locales.length; i++) {
  var loc = locales[i];

  add(loc, 'title',        r['meta_title_' + loc], d.title_digest);
  add(loc, 'body_html',    r['html_body_'  + loc], d.body_html_digest);
  add(loc, 'product_type', r.product_type,         d.product_type_digest); // skipped if no digest

  // handle: skip if empty, no digest, equals the default, or already used by another locale
  var h = r['handle_' + loc];
  h = (h == null) ? '' : String(h).trim();
  var hk = h.toLowerCase();
  if (h !== '' && d.handle_digest && !used[hk]) {
    out.push({ locale: loc, key: 'handle', value: h, translatableContentDigest: d.handle_digest });
    used[hk] = true;
  }
}

return { translationsJson: JSON.stringify(out), count: out.length };
