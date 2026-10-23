#!/usr/bin/env python3
"""f12_annot.py LAYOUT.txt Classe VOTOS.tsv [classe_dos_votos] — junta votos de deslocamento com o campo do layout do fonte."""
import sys, re
lay, cls, vot = sys.argv[1:4]; vcls = sys.argv[4] if len(sys.argv) > 4 else cls
mem = []; on = False
for l in open(lay):
    if re.match(r'^class %s\tsize' % re.escape(cls), l): on = True; continue
    if on:
        if '$vftable@' in l or '$vbtable@' in l or l.startswith('class ') or 'vfptr}' in l and mem and 0: break
        m = re.match(r'^\s*(\d+)\s*((?:\| )+)(\S.*)$', l)
        if m and not m.group(3).startswith(('+', '&')):
            mem.append((int(m.group(1)), len(m.group(2)) // 2, m.group(3).split()[-1]))
        if re.match(r'^\s*\+---\s*$', l) and mem and len(mem) > 3 and l.startswith('\t+---'): break
top = sorted((o, n) for o, d, n in mem if d == min(dd for _, dd, _ in mem) or True)
def field(o):
    best = None
    for off, n in top:
        if off <= o: best = (off, n)
    return '%s+0x%x' % (best[1], o - best[0]) if best and o != best[0] else (best[1] if best else '?')
last = None
for l in open(vot):
    p = l.rstrip('\n').split('\t')
    if p[0] != vcls or p[1] != 'mem': continue
    o, r, n = int(p[2], 16), int(p[3], 16), int(p[5])
    if o >= 0x80000000: continue
    d = r - o
    print('%s0x%05x -> 0x%05x  %+6d (%+#x) v=%-3d %-34s %s' % ('*' if d != last else ' ', o, r, d, d, n, field(o)[:34], p[6][:40]))
    last = d
