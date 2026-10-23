#!/usr/bin/env python3
"""abdirs.py NOVO ANTIGO1 [ANTIGO2...] — A/B das funções próprias: para cada unidade de NOVO/cmp, compara a classe de cada
função com a da mesma unidade no primeiro ANTIGO*/cmp que a tiver. Imprime os totais, as transições e as que saíram de IGUAL."""
import sys, os, csv, collections
def load(d, u):
    p = os.path.join(d, 'cmp', u, 'funcs.tsv')
    if not os.path.exists(p): return None
    r = {}
    for x in csv.DictReader(open(p, errors='replace'), delimiter='\t'):
        if x['propria'] == '1': r[x['funcao']] = x['classe']
    return r
new = sys.argv[1]; olds = sys.argv[2:]
ta = collections.Counter(); tb = collections.Counter(); tr = collections.Counter(); saiu = []; entrou = []; n = 0; sem = []
for u in sorted(os.listdir(os.path.join(new, 'cmp'))):
    b = load(new, u); a = None
    for o in olds:
        a = load(o, u)
        if a is not None: break
    if a is None: sem.append(u); continue
    n += 1
    for f in set(a) | set(b):
        x = a.get(f, '(nova)'); y = b.get(f, '(saiu)')
        if f in a: ta[x] += 1
        if f in b: tb[y] += 1
        if x != y:
            tr[(x, y)] += 1
            if x == 'IGUAL': saiu.append((u, f, y))
            if y == 'IGUAL': entrou.append((u, f, x))
print('%d unidades (sem linha de base: %d)' % (n, len(sem)))
print('antes ', dict(ta)); print('depois', dict(tb))
for (x, y), c in tr.most_common(): print('%4d %s -> %s' % (c, x, y))
print('--- entraram em IGUAL'); [print('  ', *e) for e in entrou]
print('--- saíram de IGUAL'); [print('  ', *e) for e in saiu]
