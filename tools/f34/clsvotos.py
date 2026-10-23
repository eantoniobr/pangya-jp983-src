#!/usr/bin/env python3
"""clsvotos.py DIR_VOTOS Classe [-v] — votos de deslocamento de uma classe (tools/f34/votes.py all): para cada off_obj, os
destinos off_983 votados (nº de funções distintas) e o delta; `*` onde o delta mais votado muda. -v mostra um exemplo."""
import sys, glob, collections
d, cls = sys.argv[1:3]; v = '-v' in sys.argv
h = collections.defaultdict(collections.Counter); ex = {}; seen = set()
for p in sorted(glob.glob(d + '/*.tsv')):
    for l in open(p):
        c = l.rstrip('\n').split('\t')
        if c[0] != cls or c[1] != 'mem': continue
        a, b = int(c[2], 16), int(c[3], 16)
        if (a, b, c[4]) in seen: continue
        seen.add((a, b, c[4])); h[a][b] += 1; ex.setdefault((a, b), c[4][:40] + ' ' + c[8])
last = None
for a in sorted(h):
    (b, n) = h[a].most_common(1)[0]
    print('0x%04x -> %-40s %s%s' % (a, ' '.join('0x%x(%+d):%d' % (q, q - a, k) for q, k in h[a].most_common(3)),
          '*' if b - a != last else '', ('   ' + ex[(a, b)]) if v else ''))
    last = b - a
