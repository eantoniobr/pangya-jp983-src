#!/usr/bin/env python3
"""vt.py VA_VTABLE... — classe (RTTI do MSVC), deslocamento do subobjeto, bases e slots de uma vtable do ProjectG 983."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pgdis as P
def u32(va):
    o = P.off(va); return struct.unpack_from('<I', P.d, o)[0] if o is not None else 0
def name(td):
    o = P.off(td + 8); return P.d[o:o + 120].split(b'\0')[0].decode('latin1')
def info(vt):
    col = u32(vt - 4); offs, td, chd = u32(col + 4), u32(col + 12), u32(col + 16)
    n, arr = u32(chd + 8), u32(chd + 12)
    bases = []
    for i in range(min(n, 40)):
        b = u32(arr + 4 * i); bases.append('%s@%x' % (name(u32(b)), u32(b + 8)))
    slots = []
    v = vt
    while True:
        f = u32(v)
        if not (0x401000 <= f < 0xd00000) or (v != vt and v in P.names): break
        slots.append(f); v += 4
        if u32(v - 4 + 4) and P.off(u32(v)) is None: break
        if len(slots) > 400: break
    return name(td), offs, bases, slots
if __name__ == '__main__':
    for a in sys.argv[1:]:
        if a.startswith('-'): continue
        nm, offs, bases, slots = info(int(a, 16))
        print('%s  vtable %s  subobjeto +0x%x  slots~%d' % (nm, a, offs, len(slots)))
        print('  bases:', ' '.join(bases))
        if '-s' in sys.argv:
            for i, f in enumerate(slots): print('  [%2d] %08x %s' % (i, f, P.names.get(f, '')))
