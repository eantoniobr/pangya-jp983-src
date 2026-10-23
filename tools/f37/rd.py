#!/usr/bin/env python3
"""f37/rd.py <f|d|u|s><VA>... — lê do dump do exe 983 um float (f), double (d), dword (u) ou texto (s) em cada VA."""
import sys, struct, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    for vs, v, rs, ro in secs:
        if v <= va - base < v + max(vs, rs): return ro + va - base - v
for a in sys.argv[1:]:
    k = a[0]; va = int(a[1:], 16); o = off(va)
    if k == 'f': v = '%.9g' % struct.unpack_from('<f', d, o)[0]
    elif k == 'd': v = '%.17g' % struct.unpack_from('<d', d, o)[0]
    elif k == 'u': v = '0x%x' % struct.unpack_from('<I', d, o)[0]
    else: v = repr(d[o:d.index(b'\0', o)].decode('cp932', 'replace'))
    print('%s %08x = %s' % (k, va, v))
