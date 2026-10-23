#!/usr/bin/env python3
"""f13_stairs — "escada" dados × código do 983. Como o link põe as contribuições de cada .obj em ordem (e cada COMDAT
fica no primeiro .obj que o define), um dado em D só pode ser usado primeiro (menor endereço de código) por uma função
do mesmo .obj; então minref(D) sobe em degraus conforme D avança. Imprime, em ordem de endereço do dado, o menor
endereço de função que o referencia, em corridas por rótulo de .obj; e os pontos de corte possíveis
(máximo do prefixo <= mínimo do sufixo).
Uso: tools/f13_stairs.py [--lo VA --hi VA] [--raw] [--cuts]"""
import sys, collections, argparse
sys.path.insert(0, __import__('os').path.dirname(__file__))
from f13_lib import *
ap = argparse.ArgumentParser()
ap.add_argument('--lo', default='10062000'); ap.add_argument('--hi', default='1006f000')
ap.add_argument('--raw', action='store_true'); ap.add_argument('--cuts', action='store_true')
ap.add_argument('--code-hi', default='1005bf60', help='só funções abaixo disto contam (fora CRT e .text$x)')
a = ap.parse_args()
lo, hi, chi = int(a.lo, 16), int(a.hi, 16), int(a.code_hi, 16)
mn = {}
for f, t in refs():
    if secof(f) != '.text' or not (lo <= t < hi) or f >= chi:
        continue
    fn = func_at(f)
    if fn is None:
        continue
    if t not in mn or fn['va'] < mn[t]['va']:
        mn[t] = fn
ts = sorted(mn)
if a.raw:
    for t in ts:
        print('%x\t%x\t%s\t%s' % (t, mn[t]['va'], mn[t]['obj'], mn[t]['nome'][:60]))
    sys.exit()
if a.cuts:
    pm = []; m = 0
    for t in ts:
        m = max(m, mn[t]['va']); pm.append(m)
    sm = [0] * len(ts); m = 1 << 32
    for i in range(len(ts) - 1, -1, -1):
        m = min(m, mn[ts[i]]['va']); sm[i] = m
    for i in range(len(ts) - 1):
        if pm[i] < sm[i + 1]:
            print('corte: dado %x|%x  código %x|%x  (%s | %s)' % (ts[i], ts[i + 1], pm[i], sm[i + 1],
                  func_at(pm[i])['obj'], func_at(sm[i + 1])['obj']))
    sys.exit()
run = None
for t in ts + [None]:
    o = mn[t]['obj'] if t else None
    if run and run[0] == o:
        run[2] = t; run[3] += 1; run[4] = min(run[4], mn[t]['va']); run[5] = max(run[5], mn[t]['va'])
    else:
        if run:
            print('%x..%x  n=%-4d %-22s código %x..%x' % (run[1], run[2], run[3], run[0], run[4], run[5]))
        if t:
            run = [o, t, t, 1, mn[t]['va'], mn[t]['va']]
