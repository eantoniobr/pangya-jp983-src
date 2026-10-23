# C115: % por sistema (telas iguais/total de out/F5/TELAS.tsv) na coluna "telas" de out/F5/SISTEMAS.tsv.
# Uso: flock out/F5/SISTEMAS.lock python3 tools/v6/sistemas_pct.py
import csv, collections
D = 'out/F5/'
cnt = collections.defaultdict(lambda: [0, 0])
for r in csv.DictReader(open(D + 'TELAS.tsv', encoding='utf-8'), delimiter='\t'):
    c = cnt[r['sistema']]
    c[0] += r['estado'].lower().startswith('igual')
    c[1] += 1
rows = [l.split('\t') for l in open(D + 'SISTEMAS.tsv', encoding='utf-8').read().rstrip('\n').split('\n')]
if 'telas' not in rows[0]:
    rows[0].insert(3, 'telas')
for r in rows[1:]:
    if len(r) < len(rows[0]):  # linha gravada por outra frente sem a coluna
        r.insert(3, '')
    i, t = cnt.get(r[0], (0, 0))
    r[3] = '%d/%d %d%%' % (i, t, 100 * i // t) if t else '0/0 (a medir)'
open(D + 'SISTEMAS.tsv', 'w', encoding='utf-8').write(''.join('\t'.join(r) + '\n' for r in rows))
for r in rows[1:]:
    print(r[1], r[3], r[0], sep='\t')
