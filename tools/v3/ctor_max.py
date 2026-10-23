#!/usr/bin/env python3
"""V7: conferência independente de um sizeof tirado do `new` — maior deslocamento [this+N] que o construtor do 983 toca.

  ctor_max.py [OUT_DIR=out/V3]   -> OUT_DIR/falhas_ctor.tsv (uma linha por sizeof que FALHA no layoutcheck e tem construtor)
`alcance` = maior (deslocamento + tamanho do acesso) por registrador que guarda o this (ecx na entrada e cópias), só no
corpo do construtor (não segue chamadas: membro construído por função fica de fora, então alcance <= sizeof de verdade).
veredito: `confirma` (alcance > sizeof nosso e <= sizeof do 983), `cabe_nos_dois` (não decide), `passa_do_983` (suspeito:
o new pode ser de outra classe)."""
import sys, os, struct, csv, re
import capstone
from capstone import x86 as X
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out = sys.argv[1] if len(sys.argv) > 1 else R + '/out/V3'
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); md.detail = True
REG32 = {X.X86_REG_EAX, X.X86_REG_EBX, X.X86_REG_ECX, X.X86_REG_EDX, X.X86_REG_ESI, X.X86_REG_EDI}
def alcance(va):
    o = off(va); cur = {X.X86_REG_ECX}; mx = 0; n = 0
    for ins in md.disasm(d[o:o + 0x1000], va):
        n += 1
        if ins.id in (X.X86_INS_RET, X.X86_INS_INT3): break
        ops = ins.operands
        for op in ops:
            if op.type == X.X86_OP_MEM and op.mem.base in cur and op.mem.index == 0 and 0 <= op.mem.disp < 0x10000 and ins.id != X.X86_INS_LEA:
                mx = max(mx, op.mem.disp + op.size)
        if ins.id == X.X86_INS_CALL: cur -= {X.X86_REG_EAX, X.X86_REG_ECX, X.X86_REG_EDX}
        elif ins.id == X.X86_INS_MOV and len(ops) == 2 and ops[0].type == X.X86_OP_REG and ops[0].reg in REG32:
            if ops[1].type == X.X86_OP_REG and ops[1].reg in cur: cur.add(ops[0].reg)
            else: cur.discard(ops[0].reg)
        elif ins.id in (X.X86_INS_XOR, X.X86_INS_LEA, X.X86_INS_POP, X.X86_INS_ADD, X.X86_INS_SUB) and ops and ops[0].type == X.X86_OP_REG:
            cur.discard(ops[0].reg)
    return mx, n
rows = []
for r in csv.DictReader(open(out + '/layoutcheck.tsv'), delimiter='\t'):
    if r['tipo'] != 'SIZE' or r['resultado'] != 'FALHA': continue
    m = re.search(r'construtor ([0-9a-f]{8})', r['evidencia'])
    if not m: rows.append((r['classe'], r['valor_983'], r['valor_nosso'], '-', '-', 'sem_construtor')); continue
    mx, n = alcance(int(m.group(1), 16)); s9 = int(r['valor_983'], 16); sn = int(r['valor_nosso'], 16) if r['valor_nosso'] else 0
    v = 'passa_do_983' if mx > s9 else 'confirma' if mx > sn else 'cabe_nos_dois'
    rows.append((r['classe'], r['valor_983'], r['valor_nosso'], m.group(1), '0x%x' % mx, v))
with open(out + '/falhas_ctor.tsv', 'w') as f:
    f.write('classe\tsizeof_983\tsizeof_nosso\tconstrutor\talcance\tveredito\n')
    for r in rows: f.write('\t'.join(r) + '\n')
import collections
print('falhas de sizeof: %d; %s' % (len(rows), ', '.join('%s %d' % x for x in collections.Counter(r[5] for r in rows).most_common())))
