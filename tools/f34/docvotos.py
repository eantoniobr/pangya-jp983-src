#!/usr/bin/env python3
"""docvotos.py DIR_VOTOS LAYOUT.txt [lo hi] — cruza os votos de deslocamento (todas as classes) com o layout de uma classe
grande acessada por ponteiro (CSharedDoc via Doc()): para cada campo de 1º nível, os pares (off_obj -> off_983) votados
dentro dele, com o delta. LAYOUT.txt = saída do tools/f34/layout.py. Votos de outras classes grandes contaminam: por
isso mostra os 2 destinos mais votados e o nº de funções."""
import sys, glob, re, collections, bisect
d, lay = sys.argv[1:3]
mem = []
for l in open(lay, errors='replace'):
    m = re.match(r'^\s*(\d+)\s*\|\s([^ |].*)$', l)
    if m: mem.append((int(m.group(1)), m.group(2).split()[-1]))
mem.sort(); offs = [o for o, _ in mem]
lo = int(sys.argv[3], 0) if len(sys.argv) > 3 else offs[0]; hi = int(sys.argv[4], 0) if len(sys.argv) > 4 else 1 << 30
big = collections.defaultdict(collections.Counter); ex = {}; seen = set()
for p in sorted(glob.glob(d + '/*.tsv')):
    for l in open(p):
        c = l.rstrip('\n').split('\t')
        if c[1] != 'mem': continue
        a, b = int(c[2], 16), int(c[3], 16)
        if not (lo <= a < hi) or (a, b, c[4]) in seen: continue
        seen.add((a, b, c[4])); big[a][b] += 1; ex.setdefault((a, b), c[4][:50])
last = None
for a in sorted(big):
    i = bisect.bisect_right(offs, a) - 1
    if i < 0: continue
    top = big[a].most_common(2)
    if top[0][1] < 2: continue
    o, nm = mem[i]
    if nm != last: print('%s @0x%x (%d)' % (nm, o, o)); last = nm
    print('   +0x%-5x 0x%05x -> %s   %s' % (a - o, a, '  '.join('0x%05x(%+d)x%d' % (b, b - a, n) for b, n in top), ex[(a, top[0][0])]))
