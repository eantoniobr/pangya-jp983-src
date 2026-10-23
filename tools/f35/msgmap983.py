#!/usr/bin/env python3
"""msgmap983.py MAPA_VA — entradas de um sFRESH_MSGMAP do exe 983 com o manipulador de cada uma.
No 983 a entrada tem 32 bytes {pfn (ponteiro de membro, 16 B), nome, cmd, tipo, x}; o pfn está ZERADO no arquivo e é gravado
por um inicializador dinâmico (`mov eax, pfn; mov [entrada], eax`). O script acha o inicializador pelas referências a
[entrada+0], emula esses `mov` e mostra: índice, controle, cmd, tipo, VA do manipulador e o nome do map/projectg.tsv.
MAPA_VA = 1ª coluna de map/projectg_msgmaps.tsv (ex.: 00e390d8 = FrLoginDlg)."""
import sys, struct, capstone
from capstone import x86 as X
R = '/root/jp983src/'
d = open(R + 'ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
def o2va(o):
    for vs, v, rs, ro in secs:
        if ro <= o < ro + rs: return base + v + o - ro
def cs(va):
    o = off(va); return d[o:d.index(b'\0', o)].decode('cp949', 'replace')
m = int(sys.argv[1], 16); ent = struct.unpack_from('<I', d, off(m) + 4)[0]
n = 0
while struct.unpack_from('<I', d, off(ent) + 32 * n + 16)[0]: n += 1
i = d.find(struct.pack('<I', ent)); ini = None
while i >= 0:
    if d[i - 1] == 0xa3 or d[i - 2:i] == b'\x89\x05':
        o = i - 1
        while not (d[o - 1] in (0xcc, 0xc3) and o2va(o) % 16 == 0): o -= 1   # começo da função (depois do preenchimento)
        ini = o2va(o); break
    i = d.find(struct.pack('<I', ent), i + 1)
pfn = {}
if ini:
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); md.detail = True; regs = {}
    for ins in md.disasm(d[off(ini):off(ini) + 0x2000], ini):
        if ins.mnemonic == 'ret': break
        if ins.mnemonic == 'xor' and ins.operands[0].type == X.X86_OP_REG: regs[ins.operands[0].reg] = 0
        if ins.mnemonic != 'mov' or len(ins.operands) != 2: continue
        a, b = ins.operands
        v = b.imm if b.type == X.X86_OP_IMM else regs.get(b.reg) if b.type == X.X86_OP_REG else None
        if a.type == X.X86_OP_REG: regs[a.reg] = v
        elif a.type == X.X86_OP_MEM and a.mem.base == 0 and ent <= a.mem.disp < ent + 32 * n and (a.mem.disp - ent) % 32 == 0:
            pfn[(a.mem.disp - ent) // 32] = v
nomes = {}
for l in open(R + 'map/projectg.tsv', encoding='latin-1'):
    p = l.rstrip('\n').split('\t')
    if len(p) > 1: nomes.setdefault(p[1], p[0])
print('# entradas %08x, %d entradas, inicializador ~%s' % (ent, n, '%08x' % ini if ini else '?'))
for k in range(n):
    e = off(ent + 32 * k); nm, cmd, tp = struct.unpack_from('<III', d, e + 16)
    v = pfn.get(k)
    print('%d\t%s\t0x%x\t%d\t%s\t%s' % (k, cs(nm), cmd, tp, '%08x' % v if v else '-', nomes.get('%08x' % v, '') if v else ''))
