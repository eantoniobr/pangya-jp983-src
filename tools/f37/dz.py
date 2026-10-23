#!/usr/bin/env python3
"""f37/dz.py VA [n_bytes|fimVA] — desmonta o exe 983 (dump) a partir de VA; nomes de map/projectg.tsv e projectg_funcs.tsv nos
alvos, texto das strings e valor de float/double apontados. `dz.py -d VA n` despeja n dwords (vtables), com o nome de cada alvo."""
import sys, os, struct, capstone
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
names = {}
for l in open(R + '/map/projectg.tsv'):
    p = l.rstrip('\n').split('\t')
    if len(p) > 1 and not l.startswith('#'): names[int(p[1], 16)] = p[0]
for l in open(R + '/map/projectg_funcs.tsv'):
    p = l.rstrip('\n').split('\t')
    if len(p) > 10 and p[0] != 'f983' and p[10]: names.setdefault(int(p[0], 16), p[10])
def rtti(vt):
    try:
        col = struct.unpack_from('<I', d, off(vt - 4))[0]; td = struct.unpack_from('<I', d, off(col + 12))[0]
        o = off(td + 8); s = d[o:d.index(b'\0', o)].decode('latin1')
        return s if s.startswith('.?A') else None
    except Exception: return None
def note(v):
    if v in names: return names[v]
    o = off(v) if base <= v < base + 0x2000000 else None
    if o is None or o + 8 > len(d): return ''
    r = rtti(v)
    if r: return 'vtable ' + r
    s = d[o:o + 60].split(b'\0')[0]
    if len(s) >= 3 and all(32 <= c < 127 for c in s): return '"%s"' % s.decode()
    f = struct.unpack_from('<f', d, o)[0]; g = struct.unpack_from('<d', d, o)[0]
    return 'f=%g d=%g dw=%08x' % (f, g, struct.unpack_from('<I', d, o)[0])
a = sys.argv[1:]
if a[0] == '-d':
    va = int(a[1], 16); n = int(a[2], 0)
    for i in range(n):
        v = struct.unpack_from('<I', d, off(va + 4 * i))[0]; print('%08x [%2d] %08x  %s' % (va + 4 * i, i, v, names.get(v, '')))
    sys.exit()
va = int(a[0], 16); n = (int(a[1], 16) - va if (len(a[1]) == 8 and not a[1].startswith('0x')) or int(a[1], 0) > va else int(a[1], 0)) if len(a) > 1 else 256
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
for i in md.disasm(d[off(va):off(va) + n], va):
    t = ''
    for w in i.op_str.replace('[', ' ').replace(']', ' ').replace(',', ' ').split():
        if w.startswith('0x') and len(w) >= 8:
            try: t = '  ; ' + note(int(w, 16))
            except ValueError: pass
    if i.mnemonic != 'int3': print('%08x  %-7s %s%s' % (i.address, i.mnemonic, i.op_str, t))
