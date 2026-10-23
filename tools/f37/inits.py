#!/usr/bin/env python3
"""f37/inits — inicializadores estáticos do ProjectG 983 (.text$yc, 00cc0000–00cfc000): cada um que monta um mapa de
mensagens (map/projectg_msgmaps.tsv) grava os ponteiros dos handlers como imediatos. Saída build/B/handlers.tsv:
handler, classe do mapa, inicializador, mapa. Dá classe a métodos não virtuais das janelas (que a RTTI não alcança)."""
import os, sys, csv, bisect
import capstone
from capstone import x86_const as X
sys.path.insert(0, os.path.dirname(__file__))
from lib import ROOT, funcs
d = open(os.path.join(ROOT, 'ref', 'ProjectG_983_dump.exe'), 'rb').read()
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); md.detail = True
maps = sorted((int(r['mapa'], 16), r['classes'].split(',')[0], int(r['entradas'])) for r in
              csv.DictReader(open(os.path.join(ROOT, 'map', 'projectg_msgmaps.tsv')), delimiter='\t'))
MA = [m[0] for m in maps]
F = funcs(); FA = {f['va'] for f in F}
n = ni = 0
with open(os.path.join(ROOT, 'build', 'B', 'handlers.tsv'), 'w') as o:
    for f in F:
        if not (0xcc0000 <= f['va'] < 0xcfc000):
            continue
        hs = []; ms = set()
        for ins in md.disasm(d[f['va'] - 0x400000: f['va'] - 0x400000 + f['sz']], f['va']):
            for op in ins.operands:
                v = (op.imm if op.type == X.X86_OP_IMM else op.mem.disp if op.type == X.X86_OP_MEM else 0) & 0xffffffff
                if op.type == X.X86_OP_IMM and 0x401000 <= v < 0xc3c18f and v in FA and not ins.group(X.X86_GRP_CALL) and not ins.group(X.X86_GRP_JUMP):
                    hs.append(v)
                elif 0xd80000 <= v < 0xf2b000:
                    i = bisect.bisect_right(MA, v) - 1
                    if i >= 0 and v - MA[i] <= 8 + 0x1c * (maps[i][2] + 2):
                        ms.add(i)
        if len(ms) == 1 and hs:
            ni += 1
            m = maps[ms.pop()]
            for h in hs:
                o.write('%08x\t%s\t%08x\t%08x\n' % (h, m[1], f['va'], m[0])); n += 1
print(ni, 'inicializadores com 1 mapa;', n, 'handlers')
