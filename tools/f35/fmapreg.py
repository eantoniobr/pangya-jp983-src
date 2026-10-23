#!/usr/bin/env python3
"""fmapreg.py VA N_BYTES [SAIDA.tsv] — registros de um FunctionMapper no exe 983: o `Initialize` de um manipulador do Gateway
traz os `AddFunctionType` em linha (monta o par na pilha e chama _Buynode 00478870 + _Linsert). Emula só constantes
(mov/xor/lea entre registradores e [ebp-x]) e, a cada chamada de 00478870, mostra o par: chave (-0x40), os campos do
sFunctionHandler (-0x38: sub-código, -0x34: tipo, -0x30: função, -0x2c/-0x28/-0x24: resto do ponteiro de membro)."""
import sys, struct, capstone
from capstone import x86 as X
d = open('/root/jp983src/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
va, n = int(sys.argv[1], 16), int(sys.argv[2], 0)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); md.detail = True
reg = {}; mem = {}; rows = []
M = 0xffffffff
def val(op):
    if op.type == X.X86_OP_IMM: return op.imm & M
    if op.type == X.X86_OP_REG: return reg.get(op.reg)
    if op.type == X.X86_OP_MEM and op.mem.base == X.X86_REG_EBP and op.mem.index == 0: return mem.get(op.mem.disp)
    return None
for i in md.disasm(d[off(va):off(va) + n], va):
    ops = i.operands
    if i.mnemonic == 'call':
        if ops[0].type == X.X86_OP_IMM and ops[0].imm == 0x478870:
            rows.append((i.address, [mem.get(k) for k in (-0x40, -0x38, -0x34, -0x30, -0x2c, -0x28, -0x24)]))
        for r in (X.X86_REG_EAX, X.X86_REG_ECX, X.X86_REG_EDX): reg.pop(r, None)
    elif i.mnemonic == 'mov' and len(ops) == 2:
        v = val(ops[1])
        if ops[0].type == X.X86_OP_REG: reg[ops[0].reg] = v
        elif ops[0].type == X.X86_OP_MEM and ops[0].mem.base == X.X86_REG_EBP and ops[0].mem.index == 0: mem[ops[0].mem.disp] = v
    elif i.mnemonic == 'xor' and ops[0].type == X.X86_OP_REG and ops[1].type == X.X86_OP_REG and ops[0].reg == ops[1].reg:
        reg[ops[0].reg] = 0
    elif i.mnemonic == 'lea' and ops[0].type == X.X86_OP_REG:
        m = ops[1].mem
        if m.base != X.X86_REG_EBP and m.index == 0 and reg.get(m.base) is not None: reg[ops[0].reg] = (reg[m.base] + m.disp) & M
        else: reg[ops[0].reg] = None
    elif ops and ops[0].type == X.X86_OP_REG and i.mnemonic not in ('push', 'cmp', 'test'):
        reg[ops[0].reg] = None
h = lambda v: '?' if v is None else '0x%x' % v
out = ['va\tchave\tsub\ttipo\tfuncao\tm2c\tm28\tm24'] + ['%08x\t%s' % (a, '\t'.join(h(v) for v in r)) for a, r in rows]
print('\n'.join(out))
if len(sys.argv) > 3: open(sys.argv[3], 'w').write('\n'.join(out) + '\n')
