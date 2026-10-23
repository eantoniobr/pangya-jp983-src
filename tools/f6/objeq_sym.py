#!/usr/bin/env python3
"""(C405) objeq por símbolo: compara cada seção pelo nome do 1o símbolo externo/estático que a define (bytes + relocações
com o nome do símbolo alvo), ignorando a ORDEM das seções/símbolos. Uso: objeq_sym.py A.obj B.obj"""
import struct, sys
def le(p):
    b = open(p, 'rb').read()
    _, ns, _, ps, nsym, oh, _ = struct.unpack_from('<HHIIIHH', b, 0); st = ps + nsym * 18
    def nm(raw):
        if raw[:4] == b'\0\0\0\0':
            o = struct.unpack_from('<I', raw, 4)[0]; return b[st + o:b.index(b'\0', st + o)]
        return raw.rstrip(b'\0')
    syms = {}; i = 0; names = {}
    while i < nsym:
        r = b[ps + 18 * i:ps + 18 * (i + 1)]; v, sec, ty, cl, na = struct.unpack_from('<IhHBB', r, 8)
        names[i] = nm(r[:8])
        if sec > 0 and cl in (2, 3) and not names[i].startswith(b'.') and v == 0: syms.setdefault(sec, names[i])
        i += 1 + na
    out = {}
    for k in range(ns):
        h = b[20 + oh + 40 * k:20 + oh + 40 * (k + 1)]; n = nm(h[:8])
        if n.startswith(b'.debug$'): continue
        sz, pr, prl, _, nr, _, ch = struct.unpack_from('<IIIIHHI', h, 16)
        rel = tuple((struct.unpack_from('<I', b, prl + 10 * j)[0], names.get(struct.unpack_from('<I', b, prl + 10 * j + 4)[0]),
                     struct.unpack_from('<H', b, prl + 10 * j + 8)[0]) for j in range(nr))
        key = (n, syms.get(k + 1, b'?%d' % k if not syms.get(k + 1) else b''))
        out.setdefault(key, []).append((b[pr:pr + sz] if pr else sz, rel, ch))
    return out
a, b = le(sys.argv[1]), le(sys.argv[2])
dif = [k for k in set(a) | set(b) if sorted(map(repr, a.get(k, []))) != sorted(map(repr, b.get(k, [])))]
anon = [k for k in dif if k[1].startswith(b'?')]
print(('IGUAL por simbolo (%d chaves)' % len(a)) if not dif else 'DIFERE em %d chaves (%d sem nome): %s' % (len(dif), len(anon), [k for k in dif][:6]))
