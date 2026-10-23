#!/usr/bin/env python3
# F3.2: semente do mapa do exe: nome decorado -> VA no 983, pelos pares 645->983 de map/projectg_funcs.tsv (fonte alta,
# media ou str) e pelos nomes decorados do .map do build do rebang (endereços do 645). É um mapa FRACO: o cmpfunc só o usa
# (--seed) quando a busca por bytes não acha lugar único e descarta o par se as instruções não parecerem (< 30%).
import re, sys, os, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MAPF = '/root/rebang/build/projectg/ProjectG_ReleaseQA.map'
by = collections.defaultdict(list)
for l in open(MAPF, errors='replace'):
    m = re.match(r'\s*[0-9a-f]{4}:[0-9a-f]{8}\s+(\S+)\s+([0-9a-f]{8}) f', l)
    if m: by[int(m.group(2), 16)].append(m.group(1))
out = {}; n = collections.Counter()
for l in open(ROOT + '/map/projectg_funcs.tsv').read().split('\n')[1:]:
    p = l.split('\t')
    if len(p) < 8 or not p[5]: continue
    if p[7] not in ('alta', 'media', 'str'): n['fonte ' + p[7]] += 1; continue
    names = by.get(int(p[5], 16))
    if not names: n['sem nome no .map'] += 1; continue
    for nm in names:
        if nm in out and out[nm] != p[0]: n['nome em 2 endereços'] += 1; out[nm] = None
        elif nm not in out: out[nm] = p[0]; n['ok'] += 1
with open(ROOT + '/map/projectg_seed.tsv', 'w') as f:
    f.write('# nome decorado (645, .map do rebang)\tVA no 983 (par da F3.1; mapa fraco, ver tools/f32/seed.py)\n')
    for k, v in sorted(out.items(), key=lambda kv: (kv[1] or '', kv[0])):
        if v: f.write('%s\t%s\n' % (k, v))
print('semente:', dict(n), '->', sum(1 for v in out.values() if v), 'nomes')
