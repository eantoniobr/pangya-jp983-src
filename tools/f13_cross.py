#!/usr/bin/env python3
"""f13_cross — para cada vão entre funções (corte c), quantas chamadas diretas atravessam c com as duas pontas dentro
de [lo, hi). Dentro de um .obj as funções e os COMDAT se entrelaçam (muitas travessias); numa fronteira de .obj só
atravessam as chamadas a símbolos externos. Uso: tools/f13_cross.py LO HI [--max N] [--win BYTES]"""
import sys, pickle, os, argparse
sys.path.insert(0, os.path.dirname(__file__))
from f13_lib import *
ap = argparse.ArgumentParser(); ap.add_argument('lo'); ap.add_argument('hi')
ap.add_argument('--max', type=int, default=0); ap.add_argument('--win', type=lambda x: int(x, 0), default=0)
a = ap.parse_args()
lo, hi = int(a.lo, 16), int(a.hi, 16)
calls = pickle.load(open(os.path.join(ROOT, 'build', 'f13', 'calls.pkl'), 'rb'))
edges = [(min(c, t), max(c, t)) for t, cs in calls.items() for c in cs if lo <= t < hi and lo <= c < hi]
prev = None
for r in FUNCS:
    c = r['va']
    if lo < c < hi:
        w = a.win or (hi - lo)
        n = sum(1 for x, y in edges if x < c <= y and y - x <= 2 * w and c - x <= w and y - c <= w) if a.win else \
            sum(1 for x, y in edges if x < c <= y)
        if n <= a.max:
            print('%x  travessias=%d  (%s %s | %s %s)' % (c, n, prev['obj'], prev['nome'][:30], r['obj'], r['nome'][:30]))
    prev = r
