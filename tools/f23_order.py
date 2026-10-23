#!/usr/bin/env python3
"""f23_order.py arquivo.obj INI-FIM [saida.tsv] [--update-map] — atribui cada função do .obj a um endereço do 983 dentro da faixa,
pela ORDEM das seções do .obj (no 983 o endereço segue a ordem das seções, F1.3). Serve para unidades cheias de
instâncias de modelo idênticas em vários lugares, que o cmpfunc deixa como "bytes*N" sem endereço.
Candidatos de cada função = lugares da faixa onde os bytes batem (relocações como curinga) + endereço do mapa;
--update-map grava os achados em map/wangreal.tsv;
escolhe a atribuição crescente, sem sobreposição, que cobre mais bytes. Depois mostra o que sobrou dos dois lados:
bytes da faixa sem dono (fora int3/enchimento) e funções do .obj sem lugar na faixa (COMDAT que o ligador tirou de
outro .obj, ou função que o 983 não tem)."""
import sys, os, importlib.machinery, importlib.util
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ld = importlib.machinery.SourceFileLoader('cmpfunc', os.path.join(R, 'tools', 'cmpfunc'))
cf = importlib.util.module_from_spec(importlib.util.spec_from_loader('cmpfunc', ld)); ld.exec_module(cf)
EH = '--eh' in sys.argv          # --eh: só os funclets de exceção (faixa na .text$x)
if EH: sys.argv.remove('--eh')
UPD = '--update-map' in sys.argv
if UPD: sys.argv.remove('--update-map')
ob = cf.Obj(sys.argv[1]); lo, hi = (int(x, 16) for x in sys.argv[2].split('-'))
pe = cf.PE(os.path.join(R, 'ref', 'wangreal_983.dll'))
mp = dict(cf.load_map(os.path.join(R, 'map', 'wangreal.tsv')))
fl = sorted((f for f in ob.funcs() if f[0].startswith(cf.EHFUN) == EH), key=lambda f: (f[1], f[2]))
info = []
for nm, sec, a, b, own in fl:
    data, rel, ch = ob.secs[sec - 1]
    hits, e = cf.wild(pe, data, {o: r for o, r in rel.items() if a <= o < b}, a, b)
    cand = sorted({h for h in hits if lo <= h < hi and (EH or h % 16 == 0)} | ({mp[nm]} if lo <= mp.get(nm, 0) < hi else set()))
    info.append([nm, e, cand, own, len(hits), set(hits)])
# melhor[i][k] = mais bytes cobertos usando as funções 0..i com a função i no candidato k
# (árvore de Fenwick de máximo sobre o endereço final das funções já postas: n·k·log n no lugar de n²·k²)
import bisect
ends = sorted({va + e for nm, e, cand, own, nh, hs in info for va in cand})
tree = [(0, None)] * (len(ends) + 1)
def tq(va):                       # melhor (bytes, (j, k)) entre as que terminam até va
    p, r = bisect.bisect_right(ends, va), (0, None)
    while p > 0:
        if tree[p][0] > r[0]: r = tree[p]
        p -= p & -p
    return r
best = []
for i, (nm, e, cand, own, nh, hs) in enumerate(info):
    row = [(tq(va)[0] + e, tq(va)[1]) for va in cand]
    for k, va in enumerate(cand):
        p = bisect.bisect_left(ends, va + e) + 1
        while p <= len(ends):
            if tree[p][0] < row[k][0]: tree[p] = (row[k][0], (i, k))
            p += p & -p
    best.append(row)
end = max(((sc, (i, k)) for i, r in enumerate(best) for k, (sc, _) in enumerate(r)), default=(0, None))[1]
place = {}
while end:
    i, k = end; place[i] = info[i][2][k]; end = best[i][k][1]
out = open(sys.argv[3], 'w') if len(sys.argv) > 3 else None
new = []
cov = bytearray(hi - lo); n_in = n_out = n_no = 0
for i, (nm, e, cand, own, nh, hs) in enumerate(info):
    va = place.get(i)
    if va is not None:
        st = 'IGUAL' if va in hs else 'MAPA'      # MAPA = endereço do mapa, bytes não idênticos (ver cmpfunc)
        cov[va - lo:va - lo + e] = b'\1' * e; n_in += 1
        if st == 'IGUAL' and nm not in mp: new.append((nm, va))
    else:
        st = 'FORA' if nh else 'SEM_BYTES'        # FORA = bate em outro lugar do 983 (COMDAT de outro .obj)
        n_out += st == 'FORA'; n_no += st != 'FORA'
    line = '%s\t%d\t%s\t%s\t%s' % ('%08x' % va if va else '-', e, st, 'propria' if own else 'inline', nm)
    if out: out.write(line + '\n')
    if st in ('SEM_BYTES', 'MAPA'): print(line[:200])
holes, p = [], 0
txt = pe.read(lo, hi - lo)
while p < hi - lo:
    if cov[p] or txt[p] == 0xcc: p += 1; continue
    q = p
    while q < hi - lo and not cov[q] and not (txt[q] == 0xcc and (q + 1 >= hi - lo or txt[q + 1] == 0xcc or (lo + q + 1) % 16 == 0)): q += 1
    holes.append((lo + p, q - p)); p = q
tot = sum(1 for p in range(hi - lo) if txt[p] != 0xcc or cov[p])
msg = '# faixa %08x-%08x: %d funções do .obj na faixa (%d bytes de %d de código = %.1f%%), %d fora, %d sem bytes; %d buracos (%d bytes)' % (
    lo, hi, n_in, sum(cov), tot, 100.0 * sum(cov) / tot, n_out, n_no, len(holes), sum(h[1] for h in holes))
print(msg)
for va, n in holes:
    line = '%08x\t%d\tBURACO\t-\t-' % (va, n); print(line)
    if out: out.write(line + '\n')
if out: out.write(msg + '\n')
if UPD and new:
    # --update-map: grava no mapa os endereços achados pela ordem (só bytes idênticos; nomes que o mapa não tinha)
    with open(os.path.join(R, 'map', 'wangreal.tsv'), 'a') as f:
        for nm, va in new: f.write('%s\t%08x\n' % (nm, va))
    print('# mapa: +%d' % len(new))
