#!/usr/bin/env python3
"""mapcls.py VA_DO_MAPA... — de quem é um mapa de mensagens Fresh do 983: acha o GetMessageMap (`mov eax, mapa; ret`), a
vtable que o contém e o nome RTTI dela (e o sizeof, se o construtor for chamado logo depois de um operator new)."""
import sys, os, re, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pgdis as P, mapof as MO
def u32(va): return struct.unpack_from('<I', P.d, P.off(va))[0]
def owner(mv):
    out = []
    for m in re.finditer(re.escape(b'\xb8' + struct.pack('<I', mv) + b'\xc3'), P.d):
        f = MO.va_of(m.start())
        if f is None: continue
        for r in re.finditer(re.escape(struct.pack('<I', f)), P.d):
            s = MO.va_of(r.start())
            if s is None or not (0xd00000 <= s < 0xf80000): continue
            vt = s
            for k in range(400):   # sobe até o ponteiro do RTTI Complete Object Locator (antes da vtable)
                col = u32(vt - 4)
                if 0xd00000 <= col < 0x1100000 and P.off(col) is not None and u32(col) == 0 and P.off(u32(col + 12)) is not None:
                    td = u32(col + 12); nm = P.cstr(td + 8)
                    if nm and nm.startswith('.?A'): out.append((f, vt, u32(col + 4), nm)); break
                vt -= 4
    return out
if __name__ == '__main__':
    for a in sys.argv[1:]:
        for f, vt, sub, nm in owner(int(a, 16)): print('mapa %s GetMessageMap %08x vtable %08x (+0x%x) %s' % (a, f, vt, sub, nm))
