#!/usr/bin/env python3
"""dispgrep.py DISP [DISP...] — todas as instruções do exe 983 com [reg + DISP] (ou lea) para os deslocamentos dados, com a função
do mapa (map/projectg_funcs.tsv) em que caem. Desmontagem linear das faixas de função do mapa (sem dessincronia entre funções).
Sessão 99: conferir m_tradeMode/m_rmrMode do CSharedDoc (+0x11214/+0x11215) no 983 inteiro."""
import sys, os, struct, bisect, capstone
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
want = set(int(a, 16) for a in sys.argv[1:])
funcs = []
for l in open(R + '/map/projectg_funcs.tsv'):
    p = l.rstrip('\n').split('\t')
    if p[0] == 'f983' or len(p) < 3: continue
    try: a = int(p[0], 16); n = int(p[1], 16) if p[1].startswith('0x') else int(p[1])
    except ValueError: continue
    funcs.append((a, n, p[10] if len(p) > 10 and p[10] else (p[6] if len(p) > 6 else '')))
funcs.sort()
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); md.detail = True
for a, n, nome in funcs:
    o = off(a)
    if o is None or n <= 0 or n > 0x40000: continue
    for ins in md.disasm(d[o:o + n], a):
        for op in ins.operands:
            if op.type == capstone.x86.X86_OP_MEM and op.mem.base != 0 and (op.mem.disp & 0xffffffff) in want:
                print('%08x\t%08x\t%s\t%s %s' % (a, ins.address, nome, ins.mnemonic, ins.op_str)); break
