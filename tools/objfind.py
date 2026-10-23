#!/usr/bin/env python3
# objfind.py <arquivo.obj> <pe de referência> : prova rápida de build (F0.2), não é o comparador da F0.3.
# Para cada função do .obj (símbolos de função nas seções de código do COFF), procura os bytes na seção .text
# do PE de referência, com os campos de relocação (4 bytes) como curinga. Saída: nome, tamanho, VA(s) achados.
import sys, struct, re

def coff_funcs(path):
    d = open(path, 'rb').read()
    mach, nsec, _, symoff, nsym, opt, _ = struct.unpack_from('<HHIIIHH', d, 0)
    assert mach == 0x14c, 'esperado COFF i386'
    stroff = symoff + nsym * 18
    def name(raw):
        if raw[:4] == b'\0\0\0\0':
            o = struct.unpack_from('<I', raw, 4)[0]
            return d[stroff + o:d.index(b'\0', stroff + o)].decode('latin1')
        return raw.rstrip(b'\0').decode('latin1')
    secs = []
    for i in range(nsec):
        o = 20 + opt + i * 40
        _, _, _, size, raw, relp, _, nrel, _, ch = struct.unpack_from('<8sIIIIIIHHI', d, o)
        rel = set()
        for r in range(nrel):
            va, _, typ = struct.unpack_from('<IIH', d, relp + r * 10)
            rel.update(range(va, va + 4))
        secs.append((d[raw:raw + size] if raw else b'', rel, ch))
    syms = {}
    i = 0
    while i < nsym:
        raw, val, sec, typ, cls, naux = struct.unpack_from('<8sIhHBB', d, symoff + i * 18)
        if sec > 0 and cls in (2, 3) and typ == 0x20 and secs[sec - 1][2] & 0x20:
            syms.setdefault(sec, []).append((val, name(raw)))
        i += 1 + naux
    for sec, lst in syms.items():
        data, rel, _ = secs[sec - 1]
        lst.sort()
        for k, (val, nm) in enumerate(lst):
            end = lst[k + 1][0] if k + 1 < len(lst) else len(data)
            while end > val and data[end - 1] in (0xcc, 0x90) and (end - 1) not in rel: end -= 1
            yield nm, data[val:end], [o - val for o in rel if val <= o < end]

def pe_text(path):
    d = open(path, 'rb').read()
    pe = struct.unpack_from('<I', d, 0x3c)[0]
    nsec, opt = struct.unpack_from('<H', d, pe + 6)[0], struct.unpack_from('<H', d, pe + 20)[0]
    base = struct.unpack_from('<I', d, pe + 24 + 28)[0]
    for i in range(nsec):
        o = pe + 24 + opt + i * 40
        nm, vs, va, rs, rp = struct.unpack_from('<8sIIII', d, o)
        if nm.rstrip(b'\0') == b'.text': return d[rp:rp + min(vs, rs)], base + va
    raise SystemExit('sem .text')

text, va = pe_text(sys.argv[2])
tot = ok = tb = okb = 0
for nm, code, rel in sorted(coff_funcs(sys.argv[1]), key=lambda x: x[0]):
    if not code: continue
    rel = set(rel)
    pat = b''.join(b'.' if i in rel else re.escape(code[i:i + 1]) for i in range(len(code)))
    hits = [m.start() for m in re.finditer(b'(?=' + pat + b')', text, re.S)]
    tot += 1; tb += len(code)
    if hits: ok += 1; okb += len(code)
    print('%-9s %5d  %-22s %s' % ('ACHADA' if hits else 'nao', len(code),
          ','.join('%08x' % (va + h) for h in hits[:3]) + ('+%d' % (len(hits) - 3) if len(hits) > 3 else ''), nm))
print('TOTAL: %d/%d funcoes achadas (%d/%d bytes) em %s' % (ok, tot, okb, tb, sys.argv[2]))
