#!/usr/bin/env python3
"""disexe.py EXE VA N — desmonta N bytes a partir de VA (qualquer PE; dump do 983 ou exe nosso); strings cp949 ao lado dos imm32."""
import sys, struct, capstone
d = open(sys.argv[1], 'rb').read(); va0 = int(sys.argv[2], 16); n = int(sys.argv[3], 0)
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
def s(va):
    o = off(va)
    if o is None or o >= len(d): return ''
    e = d.find(b'\0', o, o + 200)
    t = d[o:e] if e > o else b''
    if len(t) >= 2 and all(c >= 0x20 or c in (9, 10, 13) for c in t): return repr(t.decode('cp949', 'replace'))
    return ''
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
o = off(va0)
for i in md.disasm(d[o:o + n], va0):
    x = ''
    for tok in i.op_str.replace('[', ' ').replace(']', ' ').replace(',', ' ').split():
        if tok.startswith('0x') and len(tok) > 6: x += ' ' + s(int(tok, 16))
    print(f'{i.address:08x} {i.mnemonic} {i.op_str}{x}')
