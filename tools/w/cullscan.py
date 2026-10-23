#!/usr/bin/env python3
"""cullscan.py DLL [rs] — lista os SetRenderState(rs, x) de uma dll (push rs + call [r+0xe4] em até 12 instr.; rs padrão 0x16 = CULLMODE)."""
import sys, struct, capstone
d = open(sys.argv[1], 'rb').read()
rs_id = sys.argv[2] if len(sys.argv) > 2 else '0x16'
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
for i in range(ns):
    name = d[st+40*i:st+40*i+8].rstrip(b'\0'); vs, va, rs, ro = struct.unpack_from('<IIII', d, st + 40*i + 8)
    if name != b'.text': continue
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); md.skipdata = True
    ins = list(md.disasm(d[ro:ro+rs], base+va))
    for k, x in enumerate(ins):
        if x.mnemonic == 'push' and x.op_str == rs_id:
            for j in range(k+1, min(k+12, len(ins))):
                y = ins[j]
                if y.mnemonic == 'call' and '0xe4]' in y.op_str:
                    ctx = ' ; '.join('%s %s' % (z.mnemonic, z.op_str) for z in ins[max(0, k-3):j+1])
                    print('%08x %s' % (x.address, ctx)); break
