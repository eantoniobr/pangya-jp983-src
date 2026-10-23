#!/usr/bin/env python3
"""histfaixa.py LO HI [MIN MAX] — histograma dos deslocamentos [e?? + disp] numa faixa de endereços do exe 983 (sem depender do
mapa de funções, ao contrário do histclasse.py). s97: comparar o uso de campos de uma unidade inteira (camerawork 006cde30..006dcae1)
com o asm do 645 e achar onde entraram campos novos. Saída: disp_hex contagem (só MIN <= disp < MAX; padrão 0x80..0x400)."""
import struct, capstone, collections, sys, re, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]; oh = pe + 24
base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(a):
    for vs, v, rs, ro in secs:
        if v <= a - base < v + max(vs, rs): return ro + a - base - v
lo, hi = int(sys.argv[1], 16), int(sys.argv[2], 16)
mn, mx = (int(sys.argv[3], 16), int(sys.argv[4], 16)) if len(sys.argv) > 4 else (0x80, 0x400)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); md.skipdata = True
h = collections.Counter()
for x in md.disasm(d[off(lo):off(hi)], lo):
    for m in re.findall(r'\[e(?:si|di|cx|bx|ax|dx|bp) \+ (0x[0-9a-f]+)\]', x.op_str): h[int(m, 16)] += 1
for k in sorted(h):
    if mn <= k < mx: print(hex(k), h[k])
