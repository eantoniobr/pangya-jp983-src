#!/usr/bin/env python3
"""ltcgcmp.py dll map lo hi [--pares tsv] [--out tsv] — compara o código gerado com LTCG (objs /GL ligados numa dll de prova
com link /LTCG /MAP) com o 983: cada função pública do .map (só nomes com 'filtro', padrão 'rf@@') é casada com o VA do
983 dado em --pares (nome<TAB>VA) ou, sem par, com a função mais parecida em [lo,hi) ainda livre (atribuição gulosa).
Classe como no cmpfunc: IGUAL (fichas estritas iguais), QUASE (>= 90% das instruções), DIFERENTE; 'origem' = par|busca."""
import sys, re, difflib, argparse, collections
ROOT = '/root/jp983src'
src = open(ROOT + '/tools/cmpfunc').read().split("\nif __name__ == '__main__':")[0]
G = {'__name__': 'x', '__file__': ROOT + '/tools/cmpfunc'}; exec(compile(src, 'cmpfunc', 'exec'), G)
ap = argparse.ArgumentParser(); ap.add_argument('dll'); ap.add_argument('map'); ap.add_argument('lo'); ap.add_argument('hi')
ap.add_argument('--pares'); ap.add_argument('--out'); ap.add_argument('--filtro', default='rf@@'); ap.add_argument('--min', type=float, default=0.5)
a = ap.parse_args(); lo, hi = int(a.lo, 16), int(a.hi, 16)
dl = G['PE'](a.dll); ex = G['PE'](ROOT + '/ref/ProjectG_983_dump.exe')
fn = {}
for l in open(a.map):
    q = l.split()
    if len(q) >= 4 and re.fullmatch(r'0001:[0-9a-f]{8}', q[0]) and q[1].startswith('?'):
        fn[q[1]] = int(q[2], 16)
starts = sorted(set(fn.values()))
import bisect
def dtok(va):
    i = bisect.bisect_right(starts, va); lim = starts[i] if i < len(starts) else va + 0x4000
    return G['pe_tokens'](dl, va, lim, set(starts).__contains__)[0]
ec = G['Cmp'](ex, {}, G['load_starts'](ROOT + '/map/projectg_funcs.tsv'))
ref = {va: ec.ref_tokens(va)[0] for va in ec.startlist() if lo <= va < hi}
ref = {k: v for k, v in ref.items() if v is not None}
pares = {}
if a.pares:
    for l in open(a.pares):
        q = l.rstrip('\n').split('\t')
        if len(q) > 1 and q[1] not in ('-', '*'):
            try: pares[q[0]] = int(q[1], 16)
            except ValueError: pass
def cls(to, tr):
    r = G['ratio'](to.l, tr.l)
    return ('IGUAL' if to.s == tr.s else 'QUASE' if r >= 0.9 else 'DIFERENTE'), r
rows = {}; used = set()
mine = {nm: dtok(va) for nm, va in fn.items() if a.filtro in nm}
mine = {k: v for k, v in mine.items() if v is not None and len(v.m) >= 1}
for nm, to in mine.items():
    if nm in pares and pares[nm] in ref:
        c, r = cls(to, ref[pares[nm]]); rows[nm] = (pares[nm], c, r, 'par'); used.add(pares[nm])
cand = []
for nm, to in mine.items():
    if nm in rows: continue
    for va, tr in ref.items():
        if va in used or min(len(to.l), len(tr.l)) < 0.6 * max(len(to.l), len(tr.l)): continue
        sm = difflib.SequenceMatcher(None, to.l, tr.l, autojunk=False)
        if sm.real_quick_ratio() < a.min or sm.quick_ratio() < a.min: continue
        r = sm.ratio()
        if r >= a.min: cand.append((r, nm, va))
cand.sort(reverse=True)
for r, nm, va in cand:
    if nm in rows or va in used: continue
    c, r = cls(mine[nm], ref[va]); rows[nm] = (va, c, r, 'busca'); used.add(va)
out = open(a.out, 'w') if a.out else sys.stdout
out.write('funcao\tva983\tclasse\tpct\torigem\tn_ltcg\tn_983\n')
cnt = collections.Counter()
for nm in sorted(mine, key=lambda n: rows.get(n, (0,))[0]):
    to = mine[nm]
    if nm in rows:
        va, c, r, o = rows[nm]; out.write('%s\t%08x\t%s\t%.4f\t%s\t%d\t%d\n' % (nm, va, c, r, o, len(to.l), len(ref[va].l))); cnt[c] += 1
    else:
        out.write('%s\t-\tSEM_PAR\t0\t-\t%d\t0\n' % (nm, len(to.l))); cnt['SEM_PAR'] += 1
cob = sum(len(ref[v].l) for v in used)
print('ltcgcmp: %d funções da dll: %s; funções do 983 na faixa: %d, casadas %d' % (len(mine), dict(cnt), len(ref), len(used)), file=sys.stderr)
