#!/usr/bin/env python3
"""f37/vtfind — acha vtables sem símbolo: procura o endereço de um método como dword na imagem do exe 983 e imprime os
dwords em volta (2 antes, 10 depois). Uso: python3 tools/f37/vtfind.py <VA do método> [...]"""
import struct, sys
R = '/root/jp983src'
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]
ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = struct.unpack_from('<H', d, pe + 20)[0]
base = struct.unpack_from('<I', d, pe + 52)[0]
secs = []
for i in range(ns):
    o = pe + 24 + oh + 40 * i
    vs, va, rs, ro = struct.unpack_from('<IIII', d, o + 8)
    secs.append((base + va, max(vs, rs), ro))

def va_of(off):
    for a, s, o in secs:
        if o <= off < o + s:
            return a + off - o

for arg in sys.argv[1:]:
    t = int(arg, 16)
    j = d.find(struct.pack('<I', t))
    while j >= 0:
        v = va_of(j)
        if v:
            print('%08x em %08x:' % (t, v), ' '.join('%08x' % x for x in struct.unpack_from('<12I', d, j - 8)))
        j = d.find(struct.pack('<I', t), j + 4)
