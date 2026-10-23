#!/usr/bin/env python3
"""initoffs.py Classe [lo hi] — para cada função mapeada da classe (map/projectg.tsv) com nome On*Init/On*, mostra os
deslocamentos [reg+N] gravados (mov [reg+N], reg/imm) no 983, N em [lo, hi). Serve para tirar do binário o lugar de cada
ponteiro de controle (OnXxxInit grava m_pXxx)."""
import sys, os, re, capstone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pgdis as P
cls = sys.argv[1]; lo = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x100; hi = int(sys.argv[3], 0) if len(sys.argv) > 3 else 1 << 20
pat = sys.argv[4] if len(sys.argv) > 4 else r'Init@'
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
for va, n in sorted(P.names.items()):
    if '@%s@@' % cls not in n or not re.search(pat, n): continue
    w = []
    for i in md.disasm(P.d[P.off(va):P.off(va) + 400], va):
        m = re.match(r'(?:dword|byte|word) ptr \[e\w\w \+ (0x[0-9a-f]+)\], ', i.op_str)
        if i.mnemonic == 'mov' and m and lo <= int(m.group(1), 16) < hi: w.append(m.group(1))
        if i.mnemonic in ('ret', 'int3'): break
    print('%08x %-34s %s' % (va, n.split('@')[0].lstrip('?'), ' '.join(w)))
