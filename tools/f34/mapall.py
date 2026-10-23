#!/usr/bin/env python3
"""mapall.py [saida.tsv] — todos os mapas de mensagens Fresh do 983 com a classe dona pelo RTTI: para cada função
`mov eax, mapa; ret` (GetMessageMap) acha as vtables que a contêm e lê o nome RTTI. Saída (map/projectg_msgmaps.tsv):
mapa, GetMessageMap, classe(s), nº de entradas, mapa-base, classe-base, nomes de controle (sem repetição, até 12).
Um mapa com várias classes = classes derivadas que não redefinem o mapa (a dona é a que aparece como base de outras)."""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pgdis as P, mapof as MO
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def u32(va):
    o = P.off(va)
    return struct.unpack_from('<I', P.d, o)[0] if o is not None and o + 4 <= len(P.d) else 0
def getters():
    T0 = P.off(0x401000); T = P.d[T0:P.off(0xcfffff)]; g = {}
    for m in re.finditer(rb'\xb8(.{3}\x00)\xc3', T, re.S):
        va = struct.unpack('<I', m.group(1))[0]
        if not (0xd00000 <= va < 0xf80000) or P.off(va) is None: continue
        bas, ent = u32(va), u32(va + 4)
        if (0xd00000 <= ent < 0xf80000) and (bas == 0 or 0xd00000 <= bas < 0xf80000): g[0x401000 + m.start()] = va
    return g
def entries(mv):
    ent = u32(mv + 4); out = []
    while len(out) < 3000:
        name, cmd, typ = struct.unpack_from('<III', P.d, P.off(ent) + 16)
        if not name and not typ: break
        out.append((cmd, P.cstr(name) if name else '')); ent += 32
    return out
def classes(g):
    """{função: [nome RTTI]} — varre .rdata uma vez atrás de ponteiros para os GetMessageMap."""
    own = collections.defaultdict(list)
    for vs, v, rs, ro in P.secs:
        lo = P.base + v
        if lo + max(vs, rs) <= 0xcd0000 or lo >= 0xf80000: continue
        blob = P.d[ro:ro + max(vs, rs)]
        for k in range(0, len(blob) - 3, 4):
            f = struct.unpack_from('<I', blob, k)[0]
            if f not in g: continue
            vt = lo + k
            for _ in range(600):
                col = u32(vt - 4)
                if 0xd00000 <= col < 0x1100000 and u32(col) == 0 and u32(col + 4) < 0x1000:
                    nm = P.cstr(u32(col + 12) + 8) if P.off(u32(col + 12)) is not None else None
                    if nm and nm.startswith('.?A'):
                        nm = '::'.join(reversed(nm[4:].rstrip('@').split('@')))
                        if nm not in own[f]: own[f].append(nm)
                        break
                vt -= 4
    return own
def table():
    g = getters(); own = classes(g); bym = collections.defaultdict(list)
    for f, mv in g.items(): bym[mv].append(f)
    rows = []
    for mv, fs in sorted(bym.items()):
        cl = []
        for f in fs:
            for c in own.get(f, []):
                if c not in cl: cl.append(c)
        try: e = entries(mv)
        except Exception: continue
        rows.append((mv, fs[0], cl, e, u32(mv)))
    return rows
if __name__ == '__main__':
    rows = table(); ownm = {mv: cl for mv, f, cl, e, b in rows}
    L = ['mapa\tgetmessagemap\tclasses\tentradas\tmapa_base\tclasses_base\tcontroles']
    for mv, f, cl, e, b in rows:
        seen = []
        for c, n in e:
            if n and n not in seen: seen.append(n)
        L.append('%08x\t%08x\t%s\t%d\t%s\t%s\t%s' % (mv, f, ','.join(cl) or '-', len(e), '%08x' % b if b else '-', ','.join(ownm.get(b, [])[:3]) or '-', ' '.join(seen[:12])))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(R, 'map', 'projectg_msgmaps.tsv')
    open(out, 'w').write('\n'.join(L) + '\n')
    sys.stderr.write('%d mapas, %d com classe RTTI, %d com mais de uma classe, %d entradas\n' % (len(rows), sum(1 for r in rows if r[2]), sum(1 for r in rows if len(r[2]) > 1), sum(len(r[3]) for r in rows)))
