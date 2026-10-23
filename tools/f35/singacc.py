#!/usr/bin/env python3
"""singacc.py GLOBAL [N] — acessos [reg + disp] logo depois de cada "mov reg, [GLOBAL]" no exe 983 (até N=8 instruções, para no
call/jmp/ret ou quando reg é reescrito). Serve para medir o layout de um singleton pelo uso de fora da classe (s97: CCameraWork em
00e74d30). Saída: endereço do mov, endereço do acesso, instrução."""
import struct, capstone, sys, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]; oh = pe + 24
base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def va(o):
    for vs, v, rs, ro in secs:
        if ro <= o < ro + rs: return base + v + o - ro
g = int(sys.argv[1], 16); N = int(sys.argv[2]) if len(sys.argv) > 2 else 8
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
pat = struct.pack('<I', g); i = 0
while True:
    i = d.find(pat, i + 1)
    if i < 0: break
    for k in (1, 2):
        a = va(i - k)
        if a is None: continue
        ins = list(md.disasm(d[i - k:i - k + 80], a))
        if not ins or ins[0].mnemonic != 'mov' or hex(g) not in ins[0].op_str or ins[0].op_str.startswith('dword ptr'): continue
        reg = ins[0].op_str.split(',')[0]
        for x in ins[1:N + 1]:
            if '[%s + 0x' % reg in x.op_str: print('%08x %08x %s %s' % (a, x.address, x.mnemonic, x.op_str))
            if x.op_str.startswith(reg + ',') and x.mnemonic in ('mov', 'lea', 'xor', 'pop'): break
            if x.mnemonic in ('call', 'ret', 'jmp'): break
        break
