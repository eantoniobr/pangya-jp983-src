#!/usr/bin/env python3
"""ab.py DIR_ANTES DIR_DEPOIS [titulo] — A/B de duas linhas de base do exe (pastas com cmp/src_*/funcs.tsv, funções próprias):
totais por estado, transições e as unidades que mais ganharam IGUAL; lista as funções que saíram de IGUAL."""
import sys, glob, os, collections
def load(d):
    r = {}
    for p in glob.glob(d + '/cmp/src_*/funcs.tsv'):
        u = os.path.basename(os.path.dirname(p)); h = None
        for l in open(p, errors='replace'):
            c = l.rstrip('\n').split('\t')
            if h is None: h = {k: i for i, k in enumerate(c)}; continue
            if c[h['propria']] != '1': continue
            r[(u, c[h['funcao']])] = c[h['classe']]
    return r
a, b = load(sys.argv[1]), load(sys.argv[2])
print(sys.argv[3] if len(sys.argv) > 3 else 'A/B %s -> %s' % tuple(sys.argv[1:3]))
ca, cb = collections.Counter(a.values()), collections.Counter(b.values())
for k in ('IGUAL', 'QUASE', 'DIFERENTE', 'SEM_PAR'): print('  %-9s %d -> %d' % (k, ca[k], cb[k]))
tr = collections.Counter((a[k], b[k]) for k in a if k in b and a[k] != b[k])
for (x, y), n in tr.most_common(): print('  %-9s -> %-9s %d' % (x, y, n))
print('  só antes: %d, só depois: %d' % (len(set(a) - set(b)), len(set(b) - set(a))))
g = collections.Counter(k[0] for k in b if b[k] == 'IGUAL' and a.get(k) != 'IGUAL')
print('viraram IGUAL por unidade: ' + ', '.join('%s +%d' % (u[4:], n) for u, n in g.most_common(25)))
print('saíram de IGUAL:')
for k in sorted(a):
    if a[k] == 'IGUAL' and b.get(k, 'IGUAL') != 'IGUAL': print('  %s %s -> %s' % (k[0][4:], k[1][:70], b[k]))
