#!/usr/bin/env python3
"""vtpar.py obj... — pares nome decorado -> VA no 983 pelas vtables: cada ??_7Classe@...@6B@ do .obj (relocações = funções
das posições) é casada com a vtable do 983 achada pela RTTI (.?AVClasse@ns@@). Só classes de herança simples (1 vtable).
Saída: nome<TAB>VA<TAB>classe+posição (só funções definidas no .obj; puras/importadas puladas)."""
import struct, sys, re
ROOT = '/root/jp983src'
d = open(ROOT + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def va_of(o):
    for vs, v, rs, ro in secs:
        if ro <= o < ro + rs: return base + v + o - ro
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
def vtables(rtti):
    i = d.find(rtti.encode() + b'\0')
    if i < 0: return []
    td = va_of(i - 8); out = []
    for j in range(0, len(d) - 20, 4):
        if struct.unpack_from('<III', d, j + 4)[2] == td and struct.unpack_from('<II', d, j) == (0, 0):
            col = va_of(j); k = d.find(struct.pack('<I', col))
            while k >= 0:
                out.append(va_of(k) + 4); k = d.find(struct.pack('<I', col), k + 1)
    return out
src = open(ROOT + '/tools/cmpfunc').read().split("\nif __name__ == '__main__':")[0]
G = {'__name__': 'x', '__file__': ROOT + '/tools/cmpfunc'}; exec(compile(src, 'cmpfunc', 'exec'), G)
for o in sys.argv[1:]:
    ob = G['Obj'](o)
    defined = {nm for i, (nm, val, sec, cls, typ) in ob.syms.items() if sec > 0 and typ == 0x20}
    for i, (nm, val, sec, cls, typ) in ob.syms.items():
        m = re.match(r'\?\?_7(\w+)@(.*?)@6B@$', nm)
        if not m or sec <= 0: continue
        cl = m.group(1); ns = m.group(2)
        vts = vtables('.?AV%s@%s@' % (cl, ns) if ns else '.?AV%s@' % cl)
        if len(vts) != 1:
            print('#', cl, 'vtables no 983:', [hex(v) for v in vts], file=sys.stderr); continue
        data, rel, ch = ob.secs[sec - 1]
        for off_, (t, si) in sorted(rel.items()):
            if off_ < val or t != 6: continue
            slot = (off_ - val) // 4
            fn = ob.syms[si][0]
            vaf = struct.unpack_from('<I', d, off(vts[0] + 4 * slot))[0]
            if fn in defined and not fn.startswith('__'):
                print('%s\t%08x\t%s+%x' % (fn, vaf, cl, slot * 4))
