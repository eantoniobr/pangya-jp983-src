#!/usr/bin/env python3
"""casa.py lo hi obj... — casa as funções próprias dos .obj com as funções do 983 em [lo,hi) por semelhança de
mnemônicos (difflib sobre as fichas 'hm' do cmpfunc), para faixas LTCG em que a busca por bytes não acha nada.
Saída: nome<TAB>VA<TAB>razão<TAB>n.obj<TAB>n.983<TAB>2º melhor (atribuição gulosa 1:1 pela razão, ≥ --min).
Opções: --min 0.6 (corte); --skip arquivo.tsv (nomes já com VA: não reatribui nem gasta o VA)."""
import sys, os, difflib, bisect, argparse
ROOT = '/root/jp983src'
src = open(ROOT + '/tools/cmpfunc').read().split("\nif __name__ == '__main__':")[0]
G = {'__name__': 'cmpfunc_lib', '__file__': ROOT + '/tools/cmpfunc'}; exec(compile(src, 'cmpfunc', 'exec'), G)
ap = argparse.ArgumentParser(); ap.add_argument('lo'); ap.add_argument('hi'); ap.add_argument('objs', nargs='+')
ap.add_argument('--min', type=float, default=0.6); ap.add_argument('--skip')
a = ap.parse_args(); lo, hi = int(a.lo, 16), int(a.hi, 16)
pe = G['PE'](ROOT + '/ref/ProjectG_983_dump.exe')
starts = G['load_starts'](ROOT + '/map/projectg_funcs.tsv')
c = G['Cmp'](pe, {}, starts)
sl = c.startlist()
ref = {}
for va in sl:
    if lo <= va < hi:
        tr, sz = c.ref_tokens(va)
        if tr is not None and len(tr.m) >= 3: ref[va] = tr.m
skip = {}
if a.skip:
    for l in open(a.skip):
        q = l.rstrip('\n').split('\t')
        if len(q) > 1 and not l.startswith('#'):
            try: skip[q[0]] = int(q[1], 16)
            except ValueError: pass
used = set(skip.values())
mine = []
for o in a.objs:
    ob = G['Obj'](o)
    for nm, sec, s, e, own in ob.funcs():
        if own and nm not in skip:
            to = G['obj_tokens'](ob, sec, s, e)
            if len(to.m) >= 3: mine.append((nm, to.m))
cand = []
for nm, m in mine:
    sc = []
    for va, r in ref.items():
        if va in used or min(len(m), len(r)) < 0.5 * max(len(m), len(r)): continue
        sm = difflib.SequenceMatcher(None, m, r, autojunk=False)
        if sm.real_quick_ratio() < a.min or sm.quick_ratio() < a.min: continue
        sc.append((sm.ratio(), va, len(r)))
    sc.sort(reverse=True)
    for k, x in enumerate(sc[:4]): cand.append((x[0], nm, x[1], len(m), x[2], sc[1][0] if len(sc) > 1 else 0))
cand.sort(reverse=True)
done = set()
for r, nm, va, n1, n2, r2 in cand:
    if r < a.min or nm in done or va in used: continue
    done.add(nm); used.add(va)
    print('%s\t%08x\t%.3f\t%d\t%d\t%.3f' % (nm, va, r, n1, n2, r2))
for nm, m in mine:
    if nm not in done: print('%s\t-\t0\t%d\t0\t0' % (nm, len(m)))
