#!/usr/bin/env python3
"""
apply-translations-fix.py
=========================
Fixes the `translationsRegister` handle-collision in the "NEW PRODUCTS AUTOCREATE
ON SHOPIFY" Make scenario and writes a fully importable blueprint.

It operates on YOUR exact exported file, so your large tuned OpenAI prompt and all
module settings stay byte-for-byte intact.

USAGE
-----
1. In Make: open the scenario -> bottom toolbar (...) -> "Export Blueprint".
   Save it, e.g. as  scenario.json
2. Run:
       python3 apply-translations-fix.py scenario.json scenario-fixed.json
   (Python 3.7+, no dependencies. Also accepts the copied-modules / clipboard
    {"subflows":[...]} format.)
3. In Make: Create a new scenario -> (...) -> "Import Blueprint" -> scenario-fixed.json
   Re-link connections if prompted (importing into the same org usually keeps them).

WHAT IT CHANGES
---------------
- Inserts a Code module ("build translations (skip handle clashes)") immediately
  before the translationsRegister module. It builds the translations array and
  drops any handle equal to the product's default handle or another locale's
  handle, plus any empty value/digest (so non-translatable product_type is skipped).
- Repoints the translationsRegister module's variables.translations at that module.
- Leaves everything else untouched.
"""
import json
import sys

BUILD_JS = r'''// build translations (skip handle clashes)
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

  // handle: skip if empty, no digest, equals the default, or already used
  var h = r['handle_' + loc];
  h = (h == null) ? '' : String(h).trim();
  var hk = h.toLowerCase();
  if (h !== '' && d.handle_digest && !used[hk]) {
    out.push({ locale: loc, key: 'handle', value: h, translatableContentDigest: d.handle_digest });
    used[hk] = true;
  }
}

return { translationsJson: JSON.stringify(out), count: out.length };
'''


def find_flow_and_index(flow, predicate):
    """Recursively search a flow (and nested routes / onerror) for a module
    matching `predicate`. Returns (containing_list, index) or None."""
    for i, mod in enumerate(flow):
        if predicate(mod):
            return flow, i
    for mod in flow:
        for route in (mod.get('routes') or []):
            sub = route.get('flow')
            if sub:
                hit = find_flow_and_index(sub, predicate)
                if hit:
                    return hit
        oe = mod.get('onerror')
        if oe:
            hit = find_flow_and_index(oe, predicate)
            if hit:
                return hit
    return None


def find_module(flow, predicate):
    hit = find_flow_and_index(flow, predicate)
    return hit[0][hit[1]] if hit else None


def collect_ids(obj, acc):
    if isinstance(obj, dict):
        if isinstance(obj.get('id'), int) and 'module' in obj:
            acc.add(obj['id'])
        for v in obj.values():
            collect_ids(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            collect_ids(v, acc)


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python3 apply-translations-fix.py INPUT.json OUTPUT.json")
    inp, outp = sys.argv[1], sys.argv[2]

    with open(inp, encoding='utf-8') as f:
        bp = json.load(f)

    # ---- normalise to a single main flow -------------------------------------
    if isinstance(bp, dict) and 'flow' in bp:
        main_flow = bp['flow']
        original = bp
        from_clipboard = False
    elif isinstance(bp, dict) and 'subflows' in bp:
        main_flow = bp['subflows'][0]['flow']
        original = None
        from_clipboard = True
    else:
        sys.exit("Unrecognised format: expected a Make blueprint or clipboard export.")

    # ---- locate the modules we depend on -------------------------------------
    def is_translations(m):
        if m.get('module') != 'shopify:makeAnApiCall':
            return False
        return 'translationsRegister' in ((m.get('mapper') or {}).get('query') or '')

    hit = find_flow_and_index(main_flow, is_translations)
    if not hit:
        sys.exit("Could not find the translationsRegister module - nothing to fix.")
    flow, idx = hit
    tr_module = flow[idx]

    ai = find_module(main_flow, lambda m: m.get('module') == 'openai-gpt-3:CreateCompletion')
    digest = find_module(main_flow, lambda m: m.get('module') == 'code:ExecuteCode'
                         and 'title_digest' in ((m.get('mapper') or {}).get('codeEditorJavascript') or ''))
    create = find_module(main_flow, lambda m: m.get('module') == 'shopify:createProduct')

    ai_id = ai['id'] if ai else 6
    digest_id = digest['id'] if digest else 22
    create_id = create['id'] if create else 16

    # ---- build + insert the new Code module ----------------------------------
    ids = set()
    collect_ids(bp, ids)
    new_id = (max(ids) + 1) if ids else 100

    base_xy = (tr_module.get('metadata') or {}).get('designer') or {}
    code_module = {
        "id": new_id,
        "module": "code:ExecuteCode",
        "version": 1,
        "parameters": {},
        "mapper": {
            "input": [
                {"name": "result", "value": "{{%d.result}}" % ai_id},
                {"name": "digests", "value": "{{%d.result}}" % digest_id},
                {"name": "base_handle", "value": "{{%d.result.handle_en}}" % ai_id},
            ],
            "language": "javascript",
            "inputFormat": "editor",
            "dependencies": [],
            "codeEditorJavascript": BUILD_JS,
        },
        "metadata": {
            "designer": {
                "x": base_xy.get("x", 5400),
                "y": base_xy.get("y", 300) + 150,
                "name": "build translations (skip handle clashes)",
            }
        },
    }
    flow.insert(idx, code_module)

    # ---- repoint translationsRegister variables ------------------------------
    tr_module.setdefault('mapper', {})
    tr_module['mapper']['variables'] = (
        '{\n  "resourceId": "{{%d.id}}",\n  "translations": {{%d.result.translationsJson}}\n}'
        % (create_id, new_id)
    )
    tr_module['mapper']['variablesDataSource'] = 'object'

    # ---- emit an importable blueprint ----------------------------------------
    if not from_clipboard:
        original.setdefault('metadata', {}).setdefault('version', 1)
        if original.get('name'):
            original['name'] = original['name'] + " (fixed)"
        blueprint = original
    else:
        blueprint = {
            "name": "NEW PRODUCTS AUTOCREATE ON SHOPIFY (fixed)",
            "flow": main_flow,
            "metadata": {
                "instant": False,
                "version": 1,
                "scenario": {"roundtrips": 1, "maxErrors": 3, "autoCommit": True,
                             "autoCommitTriggerLast": True, "sequential": False, "slots": None,
                             "confidential": False, "dataloss": False, "dlq": False,
                             "freshVariables": False},
                "designer": {"orphans": []},
                "zone": "eu2.make.com",
            },
        }

    with open(outp, 'w', encoding='utf-8') as f:
        json.dump(blueprint, f, ensure_ascii=False, indent=2)

    print("OK")
    print("  inserted Code module id %d ('build translations (skip handle clashes)')" % new_id)
    print("  reads result from {{%d.result}}, digests from {{%d.result}}" % (ai_id, digest_id))
    print("  repointed translationsRegister -> {{%d.result.translationsJson}} (resourceId {{%d.id}})"
          % (new_id, create_id))
    print("  wrote", outp)


if __name__ == '__main__':
    main()
