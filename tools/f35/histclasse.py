#!/usr/bin/env python3
"""histclasse.py Classe [faixa_lo faixa_hi] — histograma dos deslocamentos [reg + disp] (e lea) nos métodos do 983 cujo nome983
(map/projectg_funcs.tsv) ou o nome645 de par "nucleo" começa com "Classe::"; com faixa, lista cada uso (função, endereço, instrução). Sessão 96: validar o
layout do CGolfRule do 983 (a região de m_wind/som em 0x3dc, quadros do PVS 0x5b0..). Não prova que o registro é `this`."""
import sys, os, re, struct, collections, capstone
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
cls = sys.argv[1]; lo = int(sys.argv[2], 16) if len(sys.argv) > 2 else None; hi = int(sys.argv[3], 16) if len(sys.argv) > 3 else lo
fs = []
for l in open(R + '/map/projectg_funcs.tsv'):
    p = l.rstrip('\n').split('\t')
    if len(p) > 10 and (p[10].startswith(cls + '::') or (p[2] == 'nucleo' and p[6].startswith(cls + '::'))): fs.append((int(p[0], 16), int(p[1]), p[10] or p[6]))
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); h = collections.Counter()
for va, n, nome in fs:
    for i in md.disasm(d[off(va):off(va) + n], va):
        for m in re.finditer(r'\[e(?:ax|bx|cx|dx|si|di) \+ (0x[0-9a-f]+)\]', i.op_str):
            o = int(m.group(1), 16); h[o] += 1
            if lo is not None and lo <= o <= hi: print('%s\t%08x\t%s %s' % (nome, i.address, i.mnemonic, i.op_str))
if lo is None:
    print('# %d funções' % len(fs))
    for o in sorted(h): print('%#x\t%d' % (o, h[o]))
