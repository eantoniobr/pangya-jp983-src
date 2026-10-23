#!/usr/bin/env python3
"""doccriadores.py SAIDA.tsv — documentos do CContentsDoc no exe 983: cada chamada do registrador 00914760 -> criador ->
tamanho do new, tipo passado ao construtor, construtor, vtable final e nome RTTI."""
import sys, struct, capstone
d = open('/root/jp983src/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
def u32(va):
    o = off(va)
    return struct.unpack_from('<I', d, o)[0] if o is not None else None
def rtti(vt):
    try:
        col = u32(vt - 4); td = u32(col + 12); o = off(td + 8)
        s = d[o:d.index(b'\0', o)].decode('ascii', 'replace')
        return s if s.startswith('.?A') else ''
    except Exception: return ''
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
def dis(va, n):
    return list(md.disasm(d[off(va):off(va) + n], va))
REG = 0x914760; NEW = 0xc3c238
tlo, thi = 0x401000, 0xcd0000
o0 = off(tlo); o1 = off(thi - 1); out = []
i = o0
while True:
    i = d.find(b'\xe8', i, o1)
    if i < 0: break
    va = tlo + i - o0
    if (va + 5 + struct.unpack_from('<i', d, i + 1)[0]) & 0xffffffff == REG:
        # criador: último `mov ecx, imm` / `mov [eax+4], imm` antes da chamada
        cr = None
        for k in range(i - 1, i - 80, -1):
            if d[k:k + 3] == b'\xc7\x40\x04':
                cr = struct.unpack_from('<I', d, k + 3)[0]; break
        if cr is None:
            for k in range(i - 1, i - 80, -1):
                if d[k] == 0xb9: cr = struct.unpack_from('<I', d, k + 1)[0]; break
        out.append((va, cr))
    i += 1
rows = []
for va, cr in out:
    size = typ = ctor = None; vts = []
    if cr and off(cr) is not None:
        ins = dis(cr, 0x90)
        for n, x in enumerate(ins):
            if x.mnemonic == 'call' and x.op_str.startswith('0x'):
                t = int(x.op_str, 16)
                if t == NEW:
                    p = ins[n - 1]
                    if p.mnemonic == 'push': size = int(p.op_str, 0)
                elif size is not None and ctor is None:
                    ctor = t
                    for p in ins[max(0, n - 3):n]:
                        if p.mnemonic == 'push' and p.op_str.startswith('0x'): typ = int(p.op_str, 16)
            if x.mnemonic == 'ret': break
        # construtor em linha no criador: mov [reg+8], imm
        if ctor is None:
            for x in ins:
                if x.mnemonic == 'mov' and '+ 8], 0x' in x.op_str and typ is None: typ = int(x.op_str.split(',')[1], 16)
                if x.mnemonic == 'mov' and x.op_str.startswith('dword ptr [e') and '], 0x' in x.op_str and '+' not in x.op_str:
                    vts.append(int(x.op_str.split(',')[1], 16))
                if x.mnemonic == 'ret': break
        else:
            for x in dis(ctor, 0x200):
                if x.mnemonic == 'mov' and x.op_str.startswith('dword ptr [e') and '], 0x' in x.op_str and '+' not in x.op_str:
                    vts.append(int(x.op_str.split(',')[1], 16))
                if x.mnemonic == 'push' and typ is None and x.op_str.startswith('0x') and 0x80 <= int(x.op_str, 16) <= 0xff:
                    typ = int(x.op_str, 16)
                if x.mnemonic == 'ret': break
    vt = vts[-1] if vts else None
    rows.append((typ if typ is not None else -1, va, cr, size, ctor, vt, rtti(vt) if vt else ''))
rows.sort()
f = open(sys.argv[1], 'w'); f.write('tipo\tchamada\tcriador\tnew\tconstrutor\tvtable\trtti\n')
h = lambda v: '' if v is None or v == -1 else '0x%x' % v
for r in rows: f.write('\t'.join([h(r[0]), '%08x' % r[1]] + [('%08x' % v if v else '') for v in (r[2],)] + [h(r[3])] + [('%08x' % v if v else '') for v in r[4:6]] + [r[6]]) + '\n')
print(len(rows), 'registros')
