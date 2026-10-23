#!/usr/bin/env python3
"""f37/calibra — poder do teste da escada no exe: V nas fronteiras conhecidas (entre trechos de núcleo vizinhos de
unidades diferentes, out/F3.3/trechos_983.tsv) × V em cortes internos das mesmas unidades."""
import sys, os, csv, collections, random
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
E_ = Escada(minref(0x491ca0, 0xb50000)); F = funcs(); FA = [f['va'] for f in F]
T = [(int(r['ini983'], 16), int(r['fim983'], 16), r['unidade']) for r in csv.DictReader(open(os.path.join(ROOT, 'out/F3.3/trechos_983.tsv')), delimiter='\t')]
T.sort()
random.seed(1)
print('dados na escada (1º uso em 00491ca0–00b50000):', len(E_.D))
for W in (0x4000, 0x10000, 0x30000):
    b = []; inn = []
    for (a, bb, u), (a2, b2, u2) in zip(T, T[1:]):
        if u != u2 and 0 <= a2 - bb < 64 and 0x525cf0 <= a2 < CODE_HI:
            b.append(E_.V(a2, W)[0])
    for a, bb, u in T:
        if bb - a < 4000 or not (0x525cf0 <= a < CODE_HI):
            continue
        i0 = bisect.bisect_left(FA, a + (bb - a) // 4); i1 = bisect.bisect_left(FA, bb - (bb - a) // 4)
        for i in random.sample(range(i0, i1), min(3, max(0, i1 - i0))):
            inn.append(E_.V(FA[i], W)[0])
    q = lambda v: [sorted(v)[int(len(v) * p)] for p in (0, .1, .25, .5, .75, .9)]
    print('janela %#x: V nas %d fronteiras conhecidas (unidades coladas, região C) = %s | V em %d cortes internos, percentis 0/10/25/50/75/90 = %s'
          % (W, len(b), sorted(b), len(inn), q(inn)))
