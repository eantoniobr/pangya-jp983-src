#!/usr/bin/env python3
# f37/imp.py <VA>... — nome da importação (dll + função) de cada endereço da IAT do exe 983 (lê o diretório de importação do dump)
import struct, sys
d = open('/root/jp983src/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]
nsec = struct.unpack_from('<H', d, pe + 6)[0]; opt = pe + 24
base = struct.unpack_from('<I', d, opt + 28)[0]
imp_rva = struct.unpack_from('<I', d, opt + 104)[0]
so = opt + struct.unpack_from('<H', d, pe + 20)[0]; secs = []
for i in range(nsec):
    vs, va, rs, ro = struct.unpack_from('<IIII', d, so + 8); secs.append((va, max(vs, rs), ro)); so += 40
def off(rva):
    for va, vs, ro in secs:
        if va <= rva < va + vs: return rva - va + ro
def cstr(o): return d[o:d.index(b'\0', o)].decode('latin1')
want = set(int(a, 16) for a in sys.argv[1:])
o = off(imp_rva)
while True:
    oft, _, _, name, ft = struct.unpack_from('<IIIII', d, o)
    if not name: break
    dll = cstr(off(name)); t = off(oft or ft); i = 0
    while True:
        v = struct.unpack_from('<I', d, t + 4 * i)[0]
        if not v: break
        a = base + ft + 4 * i
        if not want or a in want:
            print('%08x\t%s\t%s' % (a, dll, ('ord %d' % (v & 0xffff)) if v >> 31 else cstr(off(v) + 2)))
        i += 1
    o += 20
