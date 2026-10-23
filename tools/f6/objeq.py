#!/usr/bin/env python3
"""F6: dois .obj COFF iguais fora de .debug$* (bytes das secoes, relocacoes e simbolos)? Uso: objeq.py A.obj B.obj"""
import struct, sys
def le(p):
    b = open(p, 'rb').read()
    _, ns, _, ps, nsym, oh, _ = struct.unpack_from('<HHIIIHH', b, 0)
    st = ps + nsym * 18
    def nm(raw):
        if raw[:4] == b'\0\0\0\0':
            o = struct.unpack_from('<I', raw, 4)[0]; return b[st + o:b.index(b'\0', st + o)]
        return raw.rstrip(b'\0')
    secs = []
    for k in range(ns):
        h = b[20 + oh + 40 * k:20 + oh + 40 * (k + 1)]
        n = nm(h[:8]); sz, pr, prl, _, nr, _, ch = struct.unpack_from('<IIIIHHI', h, 16)
        if n.startswith(b'.debug$'): secs.append((n, None)); continue
        secs.append((n, b[pr:pr + sz] if pr else sz, b[prl:prl + nr * 10], ch))
    syms, i = [], 0
    while i < nsym:
        r = b[ps + 18 * i:ps + 18 * (i + 1)]; na = r[17]
        syms.append((nm(r[:8]), r[8:18], b[ps + 18 * (i + 1):ps + 18 * (i + 1 + na)])); i += 1 + na
    return secs, syms
a, b = le(sys.argv[1]), le(sys.argv[2])
if a == b: print('IGUAL fora de .debug$* (%d secoes, %d simbolos)' % (len(a[0]), len(a[1]))); sys.exit(0)
print('DIFERE: secoes %s, simbolos %s' % (a[0] == b[0], a[1] == b[1])); sys.exit(1)
