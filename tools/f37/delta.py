#!/usr/bin/env python3
"""f37/delta.py <sessão anterior> <sessão nova> [unidade] — totais das funções próprias de out/F3.7/<sessão>/cmp/*/funcs.tsv, mudanças
de classe entre as duas sessões e, se der a unidade, a lista das funções novas ou não IGUAL dela (é o resumo.txt de cada sessão)."""
import glob, os, csv, collections, sys
def load(s):
    d = {}
    for f in glob.glob('out/F3.7/%s/cmp/*/funcs.tsv' % s):
        u = os.path.basename(os.path.dirname(f))
        for r in csv.DictReader(open(f), delimiter='\t'):
            if r['propria'] == '1': d[(u, r['funcao'])] = (r['classe'], r['pct_instr'], r['va983'])
    return d
sa, sb = sys.argv[1:3]; un = sys.argv[3] if len(sys.argv) > 3 else None
a = load(sa); b = load(sb)
print('total %s: %d unidades, %d proprias %s' % (sb, len(set(k[0] for k in b)), len(b), dict(collections.Counter(v[0] for v in b.values()))))
new = {k: v for k, v in b.items() if k not in a}
print('novas %d %s' % (len(new), dict(collections.Counter(v[0] for v in new.values()))))
ch = [(k, a[k], b[k]) for k in a if k in b and a[k][0] != b[k][0]]
print('mudancas de classe nas da %s: %d' % (sa, len(ch)))
for k, x, y in ch: print('  ', k[0], k[1][:70], x[0], x[1], '->', y[0], y[1])
print('sumiram:', [k for k in a if k not in b])
if un:
    h = {k: v for k, v in b.items() if k[0] == un}
    print('--- %s: %d %s; novas e nao IGUAL:' % (un, len(h), dict(collections.Counter(v[0] for v in h.values()))))
    for k, v in sorted(h.items(), key=lambda kv: kv[1][2]):
        if k in new or v[0] != 'IGUAL': print('  ', v[2], k[1][:78], v[0], v[1], '(nova)' if k in new else '')
