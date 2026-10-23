#!/usr/bin/env python3
"""dis983.py VA [n_bytes] — desmonta a wangreal.dll 983 a partir de VA (nomes de map/wangreal.tsv nos alvos)."""
import sys, os, struct, capstone
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = open(os.path.join(R, 'ref', 'wangreal_983.dll'), 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
names = {}
for fn in ('wangreal.tsv',):
    for l in open(os.path.join(R, 'map', fn)):
        p = l.rstrip('\n').split('\t')
        if len(p) > 1 and not l.startswith('#'): names[int(p[1], 16)] = p[0]
for l in open(os.path.join(R, 'map', 'wangreal_funcs.tsv')):
    p = l.rstrip('\n').split('\t')
    if len(p) > 13 and not l.startswith(('#', 'va')) and p[13] != '-': names.setdefault(int(p[0], 16), p[13])
va = int(sys.argv[1], 16); n = int(sys.argv[2], 0) if len(sys.argv) > 2 else 256
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
for i in md.disasm(d[off(va):off(va) + n], va):
    s = i.op_str; t = ''
    for w in s.replace('[', ' ').replace(']', ' ').split():
        if w.startswith('0x'):
            try:
                v = int(w, 16)
                if v in names: t = '  ; ' + names[v]
                elif base + 0x61000 < v < base + 0x90000:
                    o = off(v)
                    if o:
                        z = d[o:o + 40].split(b'\0')[0]
                        if len(z) > 3 and all(32 <= c < 127 for c in z): t = '  ; "%s"' % z.decode()
            except ValueError: pass
    print('%08x  %-7s %s%s' % (i.address, i.mnemonic, s, t))
