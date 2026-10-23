#!/usr/bin/env python3
"""tabsalto.py VA_TABELA N [VA_STR...] — tabela de saltos de um switch do exe 983 (caso -> destino) e, se pedidos,
os textos C (cp949) nos VAs dados, já escapados para colar no fonte."""
import sys, os, struct
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = open(os.path.join(R, 'ref', 'ProjectG_983_dump.exe'), 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
def off(va):
    r = va - base
    for i in range(ns):
        vs, v, rs, ro = struct.unpack_from('<IIII', d, st + 40 * i + 8)
        if v <= r < v + max(vs, rs): return ro + r - v
t = int(sys.argv[1], 16); n = int(sys.argv[2], 0)
if n:
    por = {}
    for i in range(n):
        por.setdefault(struct.unpack_from('<I', d, off(t + 4 * i))[0], []).append(i)
    for a in sorted(por): print('%08x\t%s' % (a, ' '.join('0x%x' % c for c in por[a])))
for a in sys.argv[3:]:
    va = int(a, 16); o = off(va); s = d[o:d.index(b'\0', o)]
    print('%08x\t%d\t"%s"\t// %s' % (va, len(s), ''.join('\\x%02x' % c if c > 126 else chr(c) for c in s),
                                    s.decode('cp949', 'replace')))
