#!/usr/bin/env python3
"""Regenerate reference/rest-endpoints.md from drillr's public OpenAPI contract.

    python3 scripts/gen-reference.py                     # fetches https://gateway.drillr.ai/api/v2/openapi.json
    python3 scripts/gen-reference.py path/to/openapi.json

The contract is the source of truth for paths, parameters, credits and refresh
cadence; this file only lays it out for an agent to skim.
"""
import json, sys, urllib.request, re

SRC = sys.argv[1] if len(sys.argv) > 1 else 'https://gateway.drillr.ai/api/v2/openapi.json'
raw = open(SRC).read() if not SRC.startswith('http') else urllib.request.urlopen(SRC, timeout=30).read().decode()
d = json.loads(raw)
DOCS = 'https://drillr.ai/docs/api'

def schema_str(s):
    if not s: return ''
    if 'anyOf' in s:
        return ' | '.join(schema_str(x) for x in s['anyOf'])
    t = s.get('type'); t = '|'.join(t) if isinstance(t, list) else (t or '')
    if t == 'array':
        inner = s.get('items', {}); e = inner.get('enum')
        return 'csv of ' + (', '.join(f'`{v}`' for v in e) if e else schema_str(inner)) + (f' (max {s["maxItems"]})' if s.get('maxItems') else '')
    if s.get('enum'): return ', '.join(f'`{v}`' for v in s['enum'])
    out = t
    if s.get('format'): out += f' ({s["format"]})'
    if s.get('pattern'): out += f' `{s["pattern"]}`'
    if s.get('default') not in (None, ''): out += f', default `{s["default"]}`'
    if s.get('maximum') is not None: out += f', max {s["maximum"]}'
    return out

groups = {}
for path, ops in d['paths'].items():
    for method, op in ops.items():
        if path.endswith('/openapi.json'): continue
        tag = (op.get('tags') or ['Other'])[0]
        groups.setdefault(tag, []).append((method.upper(), path, op))

lines = [f"# drillr Public Data API v2 — endpoint reference",
         "",
         "Generated from https://gateway.drillr.ai/api/v2/openapi.json (`" + d['info']['version'] + "`) by `scripts/gen-reference.py`. Do not edit by hand.",
         "",
         f"Base URL `{d['servers'][0]['url']}` — every path below is absolute under it. Auth header `X-API-KEY: drl_…` (create at https://drillr.ai/account/api-keys). Rate limit 100 requests/min per key. Responses are `{{\"data\": [rows]}}`; every row derived from a disclosure links to the source filing. Full pages with response fields and worked examples: {DOCS}/<endpoint>.",
         ""]
for tag, items in groups.items():
    desc = next((t.get('description', '') for t in d.get('tags', []) if t['name'] == tag), '')
    lines += [f"## {tag}", "", desc, ""] if desc else [f"## {tag}", ""]
    for method, path, op in items:
        slug = path.rsplit('/', 1)[-1]
        lines += [f"### `{method} {path}` — {op.get('summary','')}", "",
                  f"{op.get('description','').split(chr(10))[0]}", "",
                  f"Cost **{op.get('x-credits','?')}** · refresh: {op.get('x-refresh','?')} · docs: {DOCS}/{slug}", ""]
        params = op.get('parameters') or []
        if params:
            lines += ["| param | required | type / values |", "|---|---|---|"]
            for p in params:
                lines.append(f"| `{p['name']}` | {'yes' if p.get('required') else ''} | {schema_str(p.get('schema'))}{(' — ' + p['description']) if p.get('description') else ''} |")
            lines.append("")
        rb = op.get('requestBody')
        if rb:
            sch = rb['content']['application/json']['schema']; req = set(sch.get('required', []))
            lines += ["JSON body:", "", "| field | required | type / values |", "|---|---|---|"]
            for name, s in sch['properties'].items():
                lines.append(f"| `{name}` | {'yes' if name in req else ''} | {schema_str(s)} |")
            if sch.get('anyOf'): lines.append(f"\nAt least one of: {', '.join('`'+a['required'][0]+'`' for a in sch['anyOf'])}.")
            ex = rb['content']['application/json'].get('example')
            if ex: lines += ["", "Example body:", "", "```json", json.dumps(ex, indent=2), "```"]
            lines.append("")
        m = re.search(r'Example request: `(GET [^`]+)`', op.get('description', ''))
        if m: lines += [f"Example: `{m.group(1)}`", ""]
open('reference/rest-endpoints.md', 'w').write('\n'.join(lines) + '\n')
print(f"wrote reference/rest-endpoints.md: {sum(len(v) for v in groups.values())} endpoints in {len(groups)} groups")
