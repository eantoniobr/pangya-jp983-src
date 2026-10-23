#!/usr/bin/env python3
"""mapof.py NOME_DE_CONTROLE [cmd] — acha o(s) mapa(s) de mensagens Fresh do 983 que têm uma entrada com esse nome de
controle: anda para trás de 32 em 32 B até o começo do vetor de entradas e procura o sFRESH_MSGMAP {base, entradas} que
aponta para ele. Saída: VA do mapa, VA da 1ª entrada, nº de entradas, VA do mapa-base. Use o VA do mapa no msgmap1.py."""
import sys, os, re, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pgdis as P
def va_of(fo):
    for vs, v, rs, ro in P.secs:
        if ro <= fo < ro + max(vs, rs): return P.base + v + fo - ro
def maps(name, cmd=None):
    out = []
    for m in re.finditer(re.escape(name.encode()) + b'\0', P.d):
        if m.start() and P.d[m.start() - 1] != 0: continue
        sva = va_of(m.start())
        if sva is None: continue
        for r in re.finditer(re.escape(struct.pack('<I', sva)), P.d):
            ent = va_of(r.start() - 16)
            if ent is None: continue
            c, typ, z = struct.unpack_from('<III', P.d, r.start() + 4)
            if z or (cmd is not None and c != cmd): continue
            e = ent
            while True:   # o vetor começa onde algum mapa aponta
                k = P.d.find(struct.pack('<I', e))
                hit = None
                while k >= 0:
                    mv = va_of(k - 4)
                    if mv and 0xd00000 <= mv < 0xf80000:
                        b = struct.unpack_from('<I', P.d, k - 4)[0]
                        if b == 0 or 0xd00000 <= b < 0xf80000: hit = (mv, b); break
                    k = P.d.find(struct.pack('<I', e), k + 1)
                if hit or e < ent - 32 * 2000: break
                e -= 32
            if hit:
                n = 0
                while struct.unpack_from('<I', P.d, P.off(e) + 32 * n + 16)[0] or struct.unpack_from('<I', P.d, P.off(e) + 32 * n + 24)[0]: n += 1
                if (hit[0], e, n, hit[1]) not in out: out.append((hit[0], e, n, hit[1]))
    return out
if __name__ == '__main__':
    for mv, e, n, b in maps(sys.argv[1], int(sys.argv[2], 0) if len(sys.argv) > 2 else None):
        print('mapa %08x entradas %08x n=%d base %08x' % (mv, e, n, b))
