#!/usr/bin/env python3
"""rttiof.py VTABLE_VA… — nome RTTI da classe de cada vtable do exe 983 e os primeiros slots (uso: achar a classe de um construtor)."""
import sys, os, struct
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
    o = off(va); return struct.unpack_from('<I', d, o)[0] if o is not None and o + 4 <= len(d) else None
def name(td):
    o = off(td + 8)
    return d[o:d.index(b'\0', o)].decode('latin1') if o is not None else '?'
for a in sys.argv[1:]:
    vt = int(a, 16); col = u32(vt - 4)
    if not col or off(col) is None: print(a, 'sem RTTI'); continue
    td = u32(col + 12); chd = u32(col + 16); nb = u32(chd + 8); ba = u32(chd + 12)
    bases = [name(u32(u32(ba + 4 * i))) for i in range(min(nb or 0, 12))] if ba and off(ba) is not None else []
    lo, hi = base + secs[0][1], base + secs[0][1] + secs[0][0]; slots = []
    for i in range(64):
        s = u32(vt + 4 * i)
        if s is None or not lo <= s < hi: break
        slots.append('%08x' % s)
    print(a, name(td), 'offset', u32(col + 4), 'bases', bases, 'slots', len(slots), ' '.join(slots[:8]))
