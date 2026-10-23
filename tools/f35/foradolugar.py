#!/usr/bin/env python3
"""foradolugar.py DIR_BASE SAIDA.tsv [GAP] — funções próprias (não-COMDAT) pareadas com um endereço do 983 fora do bloco da sua unidade.

As funções próprias de um .obj ficam juntas no exe (ordem de link). Para cada unidade de DIR_BASE/cmp/src_*/funcs.tsv: o bloco é o
maior grupo de endereços pareados sem salto maior que GAP (padrão 0x3000) entre vizinhos; o que cai fora dele é pareamento suspeito
(função parecida de outra classe). Unidades com menos de 8 próprias pareadas ou bloco com menos de 60% delas ficam de fora (sem bloco firme)."""
import sys, glob, os, collections
base, dst = sys.argv[1:3]; gap = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x3000
rows = []; tot = collections.Counter(); sem = 0; longe = 0; LONGE = 0x10000
for p in sorted(glob.glob(base + '/cmp/src_*/funcs.tsv')):
    u = os.path.basename(os.path.dirname(p))[4:]; h = None; F = []
    for l in open(p, errors='replace'):
        c = l.rstrip('\n').split('\t')
        if h is None: h = {k: i for i, k in enumerate(c)}; continue
        if c[h['propria']] == '1' and c[h['va983']] not in ('', '-'):
            F.append((int(c[h['va983']], 16), c[h['funcao']], c[h['classe']], c[h['origem']]))
    if len(F) < 8: sem += 1; continue
    F.sort(); g = [[F[0]]]
    for x in F[1:]:
        if x[0] - g[-1][-1][0] > gap: g.append([])
        g[-1].append(x)
    m = max(g, key=len)
    if len(m) < 0.6 * len(F): sem += 1; continue
    lo, hi = m[0][0], m[-1][0]
    for va, nm, cl, o in F:
        if not lo <= va <= hi:
            dist = lo - va if va < lo else va - hi
            rows.append((u, nm, cl, o, '%08x' % va, '%08x-%08x' % (lo, hi), '0x%x' % dist)); tot[(cl, o.split('*')[0])] += 1; longe += dist > LONGE
with open(dst, 'w') as f:
    f.write('unidade\tfuncao\tclasse\torigem\tva983\tbloco_da_unidade\tdistancia\n')
    for r in rows: f.write('\t'.join(r) + '\n')
print('%d funções fora do bloco da unidade, %d a mais de 0x%x do bloco (%d unidades sem bloco firme)' % (len(rows), longe, LONGE, sem))
for (cl, o), n in tot.most_common(): print('  %-9s %-8s %d' % (cl, o, n))
