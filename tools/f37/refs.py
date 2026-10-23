#!/usr/bin/env python3
"""f37/refs — referências código → dados do ProjectG 983 (o dump não tem .reloc: desmonta cada função do
map/projectg_funcs.tsv com o capstone e guarda imediatos/deslocamentos que caem na área de dados da imagem).
Saída: build/B/refs.tsv (func983, va_da_instrução, alvo, tipo: i=imediato d=deslocamento). ~2 min.
Uso: tools/f37/refs.py [--lo 00cfc000 --hi 00f2b000]"""
import os, sys, struct, argparse, csv
import capstone
from capstone import x86_const as X
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ap = argparse.ArgumentParser()
ap.add_argument('--lo', default='00c3d000'); ap.add_argument('--hi', default='00f2b000')
ap.add_argument('--out', default=os.path.join(ROOT, 'build', 'B', 'refs.tsv'))
a = ap.parse_args()
lo, hi = int(a.lo, 16), int(a.hi, 16)
d = open(os.path.join(ROOT, 'ref', 'ProjectG_983_dump.exe'), 'rb').read()
BASE = 0x400000  # no dump, deslocamento no arquivo = RVA
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); md.detail = True
n = 0
with open(a.out, 'w') as o:
    for r in csv.DictReader(open(os.path.join(ROOT, 'map', 'projectg_funcs.tsv')), delimiter='\t'):
        va = int(r['f983'], 16); sz = int(r['tam'])
        if va >= 0xc3d000 or sz < 5:
            continue
        code = d[va - BASE: va - BASE + sz]
        if lo.to_bytes(4, 'little')[2:3] and not any(code[i + 2] in range(lo >> 16 & 0xff, (hi >> 16 & 0xff) + 1) and code[i + 3] == 0
                                                     for i in range(len(code) - 3)):
            continue  # nenhum candidato a ponteiro: não precisa desmontar
        for ins in md.disasm(code, va):
            for op in ins.operands:
                if op.type == X.X86_OP_IMM:
                    v = op.imm & 0xffffffff; t = 'i'
                    if ins.group(X.X86_GRP_JUMP) or ins.group(X.X86_GRP_CALL):
                        continue
                elif op.type == X.X86_OP_MEM:
                    v = op.mem.disp & 0xffffffff; t = 'd'
                else:
                    continue
                if lo <= v < hi:
                    o.write('%08x\t%08x\t%08x\t%s\n' % (va, ins.address, v, t)); n += 1
print(n, 'referências em', a.out)
