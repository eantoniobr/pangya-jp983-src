#!/usr/bin/env python3
"""pkt/str.py VA... — texto (cp949) do exe 983 em VA, já como literal C com \\x (para colar no fonte) + leitura em cp949.
`str.py -b VA n` despeja n bytes em hexa (tabelas de bytes dos switch)."""
import sys, os, struct
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
a = sys.argv[1:]
if a[0] == '-b':
    o = off(int(a[1], 16)); print(' '.join('%02x' % c for c in d[o:o + int(a[2], 0)])); sys.exit()
for x in a:
    o = off(int(x, 16)); s = d[o:d.index(b'\0', o)]
    lit = ''; hexa = False
    for c in s:
        if c > 126 or c < 32:
            lit += {10: '\\n', 13: '\\r', 9: '\\t'}.get(c, '\\x%02x' % c); hexa = c > 126
        else:
            ch = chr(c)
            if ch in '"\\': ch = '\\' + ch
            # depois de \xNN um dígito hexa continuaria o escape: fecha e reabre a string
            lit += ('" "' if hexa and ch in '0123456789abcdefABCDEF' else '') + ch; hexa = False
    print('%s\t"%s"\t// %s' % (x, lit, s.decode('cp949', 'replace').replace('\n', '\\n')))
