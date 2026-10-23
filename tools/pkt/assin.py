#!/usr/bin/env python3
"""Frente C, C-PKT lote 22 — candidatos a par pela ASSINATURA de pacote (P(id) E4 ... >destino).
Junta as funções nossas `sem_par` de out/V4/pk_cmp.tsv com as do 983 sem fonte (out/V4/pk_983_sem_fonte.tsv) cuja
assinatura é idêntica. Só candidato: conferir no desmonte (tools/f37/dz.py VA; tools/pkt/quem.py VA) antes de pôr no
map/pkt_c.tsv. Rodar depois de `make v4`."""
import csv, collections, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ours = collections.defaultdict(list)
for r in csv.reader(open(R + '/out/V4/pk_cmp.tsv'), delimiter='\t'):
    if r and r[0] == 'sem_par':
        ours[r[-1].strip()].append((r[1], r[2]))
th = collections.defaultdict(list)
for r in list(csv.reader(open(R + '/out/V4/pk_983_sem_fonte.tsv'), delimiter='\t'))[1:]:
    th[r[4].strip()].append((r[0], r[1], r[2][:60]))
n = 0
for s in sorted(ours):
    if s in th:
        n += 1
        tag = 'UNICO' if len(ours[s]) == 1 and len(th[s]) == 1 else 'AMBIGUO'
        print(f'{tag}\t{s}')
        for u, nm in ours[s]: print(f'\tnosso\t{u}\t{nm}')
        for va, nm, un in th[s]: print(f'\t983\t{va}\t{nm}\t{un}')
print(f'# {n} assinaturas em comum')
