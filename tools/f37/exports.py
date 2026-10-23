# exports.py exe — tabela de exportação do exe (VA <TAB> nome decorado), ordenada por VA. O 983 exporta as classes da RF (dllexport).
import struct, sys
d = open(sys.argv[1] if len(sys.argv) > 1 else '/root/jp983src/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]
ns = struct.unpack_from('<H', d, pe + 6)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(rva):
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
erva = struct.unpack_from('<I', d, oh + 96)[0]; o = off(erva)
nf, nn, af, an, ao = struct.unpack_from('<IIIII', d, o + 20)
funcs = [struct.unpack_from('<I', d, off(af) + 4 * i)[0] for i in range(nf)]
out = []
for i in range(nn):
    s = off(struct.unpack_from('<I', d, off(an) + 4 * i)[0]); nm = d[s:s + 512].split(b'\0')[0].decode()
    out.append((funcs[struct.unpack_from('<H', d, off(ao) + 2 * i)[0]] + base, nm))
for va, nm in sorted(out): print('%08x\t%s' % (va, nm))
