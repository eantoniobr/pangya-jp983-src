#!/usr/bin/env python3
"""V3: depois de um `make layoutcheck`, tira dos asserts as anotações de cabeçalho SEM a marca 983 que não batem com o
layout atual (comentário velho, em geral deslocamento do 645 numa classe que já foi mexida para o 983). Elas vão para
tools/v3/anot_fora.tsv (classe, membro, anotado, atual, onde) e o gen.py deixa de gerá-las. As que dizem 983 ficam e falham."""
import os, csv
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); p = R + '/tools/v3/anot_fora.tsv'
old = list(csv.DictReader(open(p), delimiter='\t')) if os.path.exists(p) else []
seen = {(r['classe'], r['membro']) for r in old}; n = 0
for r in csv.DictReader(open(R + '/out/V3/layoutcheck.tsv'), delimiter='\t'):
    if r['tipo'] == 'ANOT' and r['resultado'] == 'anot_velha' and r['evidencia'].startswith('anot:') and (r['classe'], r['membro']) not in seen:
        old.append({'classe': r['classe'], 'membro': r['membro'], 'anotado': r['valor_983'], 'atual': r['valor_nosso'], 'onde': r['evidencia'].split()[-1]}); n += 1
with open(p, 'w') as f:
    f.write('classe\tmembro\tanotado\tatual\tonde\n')
    for r in sorted(old, key=lambda r: (r['classe'], int(r['atual'] or '0', 16))): f.write('\t'.join(r[k] for k in ('classe', 'membro', 'anotado', 'atual', 'onde')) + '\n')
print('anot_fora.tsv: %d anotações velhas (%d novas)' % (len(old), n))
