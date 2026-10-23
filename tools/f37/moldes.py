#!/usr/bin/env python3
"""f37/moldes.py <obj> <ini> <fim> [funcs.tsv do cmp] — cobertura da faixa [ini, fim) do 983 pelo .obj: cada início de função
do 983 (map/projectg_funcs.tsv) na faixa sai como PROPRIA (VA no funcs.tsv do cmp), MOLDE (os bytes de alguma função do .obj,
COMDAT ou não, aparecem ali com as relocações como curinga: wild() do tools/cmpfunc) ou FALTA. Resumo no fim (contagem e bytes)."""
import sys, os, importlib.machinery, importlib.util
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ld = importlib.machinery.SourceFileLoader('cmpfunc', R + '/tools/cmpfunc')
sp = importlib.util.spec_from_loader('cmpfunc', ld); cf = importlib.util.module_from_spec(sp); ld.exec_module(cf)
obj, lo, hi = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
own = {}
if len(sys.argv) > 4:
    for l in open(sys.argv[4]):
        q = l.rstrip('\n').split('\t')
        if len(q) > 5 and q[5] not in ('', '-', 'va983'):
            own[int(q[5], 16)] = q[1]
starts = []
for l in open(R + '/map/projectg_funcs.tsv'):
    q = l.split('\t')
    try:
        va = int(q[0], 16)
    except ValueError:
        continue
    if lo <= va < hi:
        starts.append((va, int(q[1])))
pe = cf.PE(R + '/ref/ProjectG_983_dump.exe')
ob = cf.Obj(obj)
hit = {}
for nm, sec, a, b, o in ob.funcs():
    data, rel, ch = ob.secs[sec - 1]
    hs, e = cf.wild(pe, data, {x: r for x, r in rel.items() if a <= x < b}, a, b)
    for h in hs:
        if lo <= h < hi:
            hit.setdefault(h, nm)
tot = {'PROPRIA': [0, 0], 'MOLDE': [0, 0], 'FALTA': [0, 0]}
for va, sz in starts:
    k = 'PROPRIA' if va in own else 'MOLDE' if va in hit else 'FALTA'
    tot[k][0] += 1; tot[k][1] += sz
    print('%08x\t%d\t%s\t%s' % (va, sz, k, own.get(va) or hit.get(va) or ''))
print('# ' + ', '.join('%s %d (%d B)' % (k, n, b) for k, (n, b) in tot.items()), file=sys.stderr)
