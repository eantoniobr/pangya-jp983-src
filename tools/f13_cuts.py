#!/usr/bin/env python3
"""f13_cuts — para cada vão entre funções do 983 (corte de código c), o nº mínimo de violações V(c) da escada
dados × código: V(c) = min_s [ #{dado < s com minref > c} + #{dado >= s com minref < c} ].
V = 0: corte limpo (pode ser fronteira de .obj); V alto: c está dentro de um .obj (dados de antes e depois do corte
se entrelaçam). Um COMDAT emitido e não usado pelo próprio .obj (constante real morta) ou um extern definido noutro
.obj dá V = 1 numa fronteira verdadeira, por isso o limiar é parâmetro.
Uso: tools/f13_cuts.py [--max V] [--lo VA --hi VA]  (faixa de código)"""
import sys, bisect, argparse
sys.path.insert(0, __import__('os').path.dirname(__file__))
from f13_lib import *
ap = argparse.ArgumentParser()
ap.add_argument('--max', type=int, default=0)
ap.add_argument('--lo', default='10001000'); ap.add_argument('--hi', default='1005bf50')
ap.add_argument('--tsv')
a = ap.parse_args()
clo, chi = int(a.lo, 16), int(a.hi, 16)
AREAS = [('rdata', 0x10062398, 0x100663a0, (0x10063900, 0x10065f10)), ('data', 0x1006c000, 0x1006d600, None), ('bss', 0x1006d600, 0x1006f000, None)]
R = [(f, t) for f, t in refs() if secof(f) == '.text' and f < 0x1005bf50]  # sem o wmath: ele usa constantes reais que os .obj do início emitiram sem usar


def minref(lo, hi, skip=None):
    mn = {}
    for f, t in R:
        if lo <= t < hi and not (skip and skip[0] <= t < skip[1]):
            v = func_at(f)['va']
            if t not in mn or v < mn[t]:
                mn[t] = v
    return [mn[t] for t in sorted(mn)], sorted(mn)


def viol(seq, c):
    """c = endereço da 1ª função depois do corte; itens com minref < c são 'antes'"""
    b = [1 if v < c else 0 for v in seq]       # 1 = antes
    tot_b = sum(b)
    best = None; after_before = tot_b; before_after = 0
    # s = 0: tudo depois -> violações = nº de 'antes'
    best = (after_before, 0)
    for i, x in enumerate(b):
        if x:
            after_before -= 1
        else:
            before_after += 1
        if after_before + before_after < best[0]:
            best = (after_before + before_after, i + 1)
    return best


areas = [(nm,) + minref(lo, hi, sk) for nm, lo, hi, sk in AREAS]
out = []
for i, r in enumerate(FUNCS):
    c = r['va']
    if not (clo < c <= chi) or i == 0:
        continue
    vs = []
    for nm, seq, ts in areas:
        v, s = viol(seq, c)
        vs.append((v, ts[s] if s < len(ts) else 0, ts[s - 1] if s else 0))
    out.append((c, FUNCS[i - 1], r, vs))
if a.tsv:
    with open(a.tsv, 'w') as fo:
        fo.write('corte_va\tV_rdata\tV_data\tV_bss\tdado_rdata\tobj_antes\tobj_depois\n')
        for c, p, r, vs in out:
            fo.write('%x\t%d\t%d\t%d\t%x\t%s\t%s\n' % (c, vs[0][0], vs[1][0], vs[2][0], vs[0][1], p['obj'], r['obj']))
for c, p, r, vs in out:
    if vs[0][0] <= a.max:
        print('%x  V rdata=%d data=%d bss=%d  rdata %x|%x  %s | %s' % (c, vs[0][0], vs[1][0], vs[2][0], vs[0][2], vs[0][1],
              p['obj'], r['obj']))
