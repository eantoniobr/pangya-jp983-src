#!/usr/bin/env python3
"""f21_cover.py funcs.tsv INI-FIM [INI-FIM ...] — cobertura de uma faixa do 983 pelas funções do cmpfunc (--inline --all).
Para cada função de map/wangreal_funcs.tsv e cada vão de map/wangreal_gaps.tsv na faixa: qual símbolo do .obj a cobre
(mesmo endereço, ou dentro do intervalo va983..va983+bytes_983 de uma função comparada) e com que classe."""
import sys, os, csv
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = [r for r in csv.DictReader(open(sys.argv[1]), delimiter='\t') if r['va983'] not in ('-', '')]
rng = [tuple(int(x, 16) for x in a.split('-')) for a in sys.argv[2:]]
items = []
for fn, k, col in (('wangreal_funcs.tsv', 'F', 13), ('wangreal_gaps.tsv', 'V', 3)):
    for l in open(os.path.join(R, 'map', fn)):
        p = l.rstrip('\n').split('\t')
        if l[0] in '#v': continue
        va = int(p[0], 16)
        if any(a <= va < b for a, b in rng): items.append((va, int(p[1]), k, p[col]))
tot = {}
for va, sz, k, nm in sorted(items):
    hit = [r for r in rows if int(r['va983'], 16) <= va and va + sz <= int(r['va983'], 16) + int(r['bytes_983'])]
    hit.sort(key=lambda r: int(r['va983'], 16) != va)
    c = hit[0]['classe'] if hit else 'SEM_COBERTURA'
    how = '' if not hit else ('' if int(hit[0]['va983'], 16) == va else ' (dentro de %s)' % hit[0]['va983'])
    tot[(k, c)] = tot.get((k, c), 0) + 1
    print('%08x\t%d\t%s\t%s\t%s%s' % (va, sz, k, c, hit[0]['funcao'] if hit else nm, how))
print('# ' + '; '.join('%s %s=%d' % (k, c, n) for (k, c), n in sorted(tot.items())))
