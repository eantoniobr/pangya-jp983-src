#!/usr/bin/env python3
"""V3: out/V3/falhas.tsv — os static_assert que falham, com a confiança da identificação da classe no 983.
confiança: alta = vtable RTTI gravada no local do new, ou mapa e RTTI do construtor concordam; media = só RTTI do
construtor (this seguido por registrador); mapa = só o nome do construtor em map/projectg.tsv (classe sem vtable/RTTI)."""
import os, csv, collections
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); O = R + '/out/V3'
def cx(d): return '::'.join(reversed(d.split('@')))
ev = collections.defaultdict(set)
for r in csv.DictReader(open(O + '/news_983.tsv'), delimiter='\t'):
    c = r['classe_em_linha'] if r['classe_em_linha'] != '-' else r['classe_mapa'] if r['classe_mapa'] != '-' else r['classe_rtti_ctor']
    if c == '-': continue
    ev[cx(c)].add('alta' if r['classe_em_linha'] != '-' or (r['classe_mapa'] != '-' and r['classe_rtti_ctor'] in (r['classe_mapa'], 'CPost_ReceiveDlg'))
                  else 'media' if r['classe_mapa'] == '-' else 'mapa')
hand = open(R + '/HANDOFF.md', encoding='utf8', errors='replace').read(); n = collections.Counter(); rows = []
for r in csv.DictReader(open(O + '/layoutcheck.tsv'), delimiter='\t'):
    if r['resultado'] != 'FALHA': continue
    cf = 'alta' if 'alta' in ev[r['classe']] else 'media' if 'media' in ev[r['classe']] else 'mapa' if ev[r['classe']] else 'manual'
    d = int(r['valor_983'], 16) - int(r['valor_nosso'], 16) if r['valor_nosso'] else 0
    rows.append((r['classe'], r['tipo'], r['membro'], r['valor_983'], r['valor_nosso'], '%+d' % d, cf, 'sim' if r['classe'] + ' 0x' in hand else 'nao', r['unidade'], r['evidencia'])); n[cf] += 1
with open(O + '/falhas.tsv', 'w') as f:
    f.write('classe\ttipo\tmembro\tvalor_983\tvalor_nosso\tdiferenca\tconfianca\tcitada_no_HANDOFF\tunidade\tevidencia\n')
    for r in sorted(rows, key=lambda r: (r[8], r[0])): f.write('\t'.join(r) + '\n')
print('falhas: %d (%s)' % (len(rows), ', '.join('%s %d' % x for x in n.most_common())))
for r in sorted(rows, key=lambda r: (r[8], r[0])): print('| %s | %s | %s | %s | %s | %s |' % (r[0], r[3], r[4], r[5], r[6], r[8].replace('src/', '')))
