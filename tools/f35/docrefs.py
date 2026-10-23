#!/usr/bin/env python3
"""docrefs.py BASE_HEX TAMANHO_HEX — lista, no exe 983, as instruções cujo deslocamento de 32 bits cai em [BASE, BASE+TAMANHO)
(ex.: uma estrutura embutida no CSharedDoc: docrefs.py 1095f 4c). Saída: +desl, VA, função, unidade, instrução.
Coincidências numéricas aparecem (olhar a instrução); serve para medir o layout de uma estrutura em minutos."""
import struct, sys, bisect, capstone
R = '/root/jp983src/'
d = open(R + 'ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]; oh = pe + 24
base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
F = []
for l in open(R + 'map/projectg_funcs.tsv').read().split('\n')[1:]:
    p = l.split('\t')
    if len(p) > 10: F.append((int(p[0], 16), p[10], p[3].split('/')[-1]))
F.sort(); ks = [f[0] for f in F]
vs, v, rs, ro = secs[0]
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
b0 = int(sys.argv[1], 16); n = int(sys.argv[2], 16)
for off in range(n):
    pat = struct.pack('<I', b0 + off); i = ro
    while True:
        i = d.find(pat, i, ro + rs)
        if i < 0: break
        a = base + v + i - ro; txt = '?'
        for back in range(1, 5):
            ins = list(md.disasm(d[i - back:i + 12], a - back, 1))
            if ins and ins[0].size >= back + 4 and '0x%x' % (b0 + off) in ins[0].op_str: txt = ins[0].mnemonic + ' ' + ins[0].op_str; break
        f = F[bisect.bisect_right(ks, a) - 1]
        print('+%#x\t%08x\t%08x\t%s\t%s\t%s' % (off, a, f[0], f[2], f[1][:40], txt))
        i += 1
