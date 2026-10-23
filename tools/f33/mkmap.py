#!/usr/bin/env python3
# F3.3 — mapa forte do exe: nome decorado -> VA no 983, a partir da linha de base (out/F3.2/funcs_all.tsv.gz).
# Entra: função IGUAL ou QUASE com lugar sem ambiguidade (origem bytes, alvo ou vizinho; 'bytes*N' fica de fora) e,
# vinda da semente (par de outra versão), só se IGUAL. Um nome com dois endereços (estática de mesmo nome em duas
# unidades, COMDAT divergente) fica de fora. O cmpfunc trata o mapa como verdade: na dúvida, não entra.
# uso: mkmap.py funcs_all.tsv.gz map/projectg.tsv
import collections, csv, gzip, sys

src, dst = sys.argv[1:3]
va = collections.defaultdict(set)
como = {}
fora = collections.Counter()
import os
# s52: pares vetados (map/projectg_fora.tsv: nome, VA) — função própria pareada longe do bloco da sua unidade
# (tools/f35/foradolugar.py); sem isto o par errado volta ao mapa a cada rodada e arrasta os vizinhos
veto = set()
pf = os.path.join(os.path.dirname(dst), 'projectg_fora.tsv')
if os.path.exists(pf):
    for l in open(pf):
        c = l.rstrip('\n').split('\t')
        if len(c) > 1 and not l.startswith('#'):
            veto.add((c[0], c[1]))
for r in csv.DictReader(gzip.open(src, 'rt'), delimiter='\t'):
    if r['classe'] not in ('IGUAL', 'QUASE'):
        continue
    if (r['funcao'], r['va983']) in veto or (r['funcao'], '*') in veto:  # s109: '*' = nenhum endereço
        fora['vetado (fora do bloco da unidade)'] += 1
        continue
    o = r['origem']
    if '*' in o or r['va983'] in ('', '-'):
        fora['lugar ambiguo'] += 1
        continue
    if o == 'semente' and r['classe'] != 'IGUAL':
        fora['semente QUASE'] += 1
        continue
    va[r['funcao']].add(r['va983'])
    como.setdefault(r['funcao'], (r['classe'], o, r['propria']))
import os
man = os.path.join(os.path.dirname(dst), 'projectg_manual.tsv')   # entradas à mão (com evidência na 3ª coluna): vencem
if os.path.exists(man):
    for l in open(man):
        c = l.rstrip('\n').split('\t')
        if len(c) > 1 and not l.startswith('#'):
            va[c[0]] = {c[1]}; como[c[0]] = ('MANUAL', 'manual', '1')
n = collections.Counter()
with open(dst, 'w') as f:
    f.write('# nome decorado\tVA no 983 (gerado por tools/f33/mkmap.py da linha de base; tools/cmpfunc --update-map '
            'acrescenta; editar à mão é permitido)\n')
    for nome in sorted(va, key=lambda k: (min(va[k]), k)):
        if len(va[nome]) > 1:
            fora['nome com 2+ enderecos'] += 1
            continue
        f.write(f'{nome}\t{min(va[nome])}\n')
        c = como[nome]
        n['propria' if c[2] == '1' else 'em linha', c[0], c[1]] += 1
print('nomes no mapa:', sum(n.values()))
for k in sorted(n):
    print('  ', *k, n[k])
print('fora:', dict(fora))
