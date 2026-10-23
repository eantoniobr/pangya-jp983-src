#!/usr/bin/env python3
"""fxicalls.py LO HI — chamadas de [LO,HI) do exe 983 para a unidade do FxInterpreter (0087f2d0..0088e8b0), com as 6 instruções anteriores
(uso: ver por qual membro o dono chega ao seu FxInterpreter e com que argumentos)."""
import sys, os, struct, capstone
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; oh = pe + 24
base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
vs, v, rs, ro = struct.unpack_from('<IIII', d, st + 8)
lo, hi = int(sys.argv[1], 16), int(sys.argv[2], 16)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
for va in range(lo, hi):
    o = ro + va - base - v
    if d[o] != 0xe8: continue
    t = va + 5 + struct.unpack_from('<i', d, o + 1)[0]
    if not 0x87f2d0 <= t < 0x88e8b0: continue
    best = None
    for back in range(40, 8, -1):   # acha um começo de decodificação que termina exatamente no call
        ins = list(md.disasm(d[o - back:o], va - back))
        if ins and ins[-1].address + ins[-1].size == va and len(ins) >= 6: best = ins; break
    print('== %08x call %08x' % (va, t))
    for i in (best or [])[-6:]: print('   %08x  %s %s' % (i.address, i.mnemonic, i.op_str))
