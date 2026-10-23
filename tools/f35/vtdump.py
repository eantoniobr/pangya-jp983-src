#!/usr/bin/env python3
"""vtdump.py PREFIXO [n] — tabelas virtuais do exe 983 cujas classes RTTI começam por PREFIXO: n posições por tabela, com o
nome do mapa e a marca '=' quando a posição é a mesma função da 1ª tabela listada da classe-base (saída TSV)."""
import sys, os, struct, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
def u32(va):
    o = off(va)
    return struct.unpack_from('<I', d, o)[0] if o is not None and o + 4 <= len(d) else None
names = {}
for fn in ('projectg_seed.tsv', 'projectg.tsv'):
    for l in open(R + '/map/' + fn, errors='replace'):
        p = l.rstrip('\n').split('\t')
        if len(p) > 1 and not l.startswith('#'):
            try: names[int(p[1], 16)] = p[0]
            except ValueError: pass
pref = sys.argv[1].encode(); n = int(sys.argv[2]) if len(sys.argv) > 2 else 17
tds = {}
for m in re.finditer(rb'\.\?AV' + re.escape(pref) + rb'[A-Za-z0-9_]*@@\0', d):
    tds[m.start() - 8] = m.group()[4:-3].decode()
# deslocamento de arquivo -> VA
def va_of(o):
    for vs, v, rs, ro in secs:
        if ro <= o < ro + rs: return base + v + o - ro
tdva = {va_of(o): nm for o, nm in tds.items()}
out = []
text_lo, text_hi = base + 0x1000, base + 0x8f0000  # o despejo tem uma seção só: código antes de 00cf0000
for vs, v, rs, ro in secs[:1]:
    for o in range(ro, ro + rs - 4, 4):
        col = struct.unpack_from('<I', d, o)[0]
        co = off(col) if base < col < base + 0x2000000 else None
        if co is None or co + 20 > len(d): continue
        sig, offs, cd, td, ch = struct.unpack_from('<5I', d, co)
        if sig != 0 or td not in tdva: continue
        f0 = struct.unpack_from('<I', d, o + 4)[0]
        if not (text_lo <= f0 < text_hi): continue
        vt = va_of(o + 4)
        out.append((vt, tdva[td], offs, [u32(vt + 4 * i) for i in range(n)]))
out.sort()
ref = next((s for vt, nm, offs, s in out if nm == sys.argv[1]), None)
print('vtable\tclasse\tpos\tfuncao\tigual_base\tnome')
for vt, nm, offs, sl in out:
    for i, f in enumerate(sl):
        if f is None or not (text_lo <= f < text_hi): break
        print('%08x\t%s\t%d\t%08x\t%s\t%s' % (vt, nm, i, f, '=' if ref and ref[i] == f else '', names.get(f, '')))
