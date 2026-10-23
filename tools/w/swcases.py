#!/usr/bin/env python3
"""swcases.py VA983 VA_NOSSO N983 N_NOSSO [dll_nossa] — função com switch por tabela de salto: separa cada caso (do
alvo da tabela até o primeiro jmp/ret) nas duas dlls e mostra o diff caso a caso, com a tradução de endereços do
vadiff.py. Serve quando o cl reordena os blocos dos casos e o diff linear do vadiff vira ruído."""
import sys, os, re, struct, difflib, importlib.util
spec = importlib.util.spec_from_file_location('vadiff', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vadiff.py'))
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
a, b, na, nb = int(sys.argv[1], 16), int(sys.argv[2], 16), int(sys.argv[3]), int(sys.argv[4])
def cases(blob, va, n, names):
    ad = []; L = V.dis(blob, va, n, names, ad)
    tbl = None
    for i, s in enumerate(L):
        m = re.match(r'jmp dword ptr \[(\w+)\*4 \+ (\S+)\]', s)
        if m: tbl = (i, m.group(2))
    raw = [x for x in V.capstone.Cs(V.capstone.CS_ARCH_X86, V.capstone.CS_MODE_32).disasm(blob(va, n), va)]
    tva = None
    for x in raw:
        m = re.match(r'jmp dword ptr \[\w+\*4 \+ (0x[0-9a-f]+)\]', x.op_str and ('jmp ' + x.op_str) or '')
        if x.mnemonic == 'jmp' and '*4 +' in x.op_str: tva = int(x.op_str.split('+')[1].strip(' ]'), 16)
    out = {}
    if tva is None: return out, L
    k = 0
    while True:
        t = struct.unpack('<I', blob(tva + 4 * k, 4))[0]
        if not (va <= t < va + n): break
        j = ad.index(t) if t in ad else None
        blk = []
        while j is not None and j < len(L):
            blk.append(L[j])
            if L[j].startswith('jmp') or L[j].startswith('ret'): break
            j += 1
        out[k] = blk; k += 1
    return out, L
CA, LA = cases(V.ref, a, na, V.n983); CB, LB = cases(V.ours, b, nb, V.nn)
print('casos: 983 %d, nossa %d' % (len(CA), len(CB)))
for k in sorted(set(CA) | set(CB)):
    A, B = CA.get(k, []), CB.get(k, [])
    # rótulos internos (Lxxx) mudam de valor entre as dlls: comparar sem eles
    na_ = [re.sub(r'L[0-9a-f]+', 'L', x) for x in A]; nb_ = [re.sub(r'L[0-9a-f]+', 'L', x) for x in B]
    if na_ == nb_: print('caso %d: IGUAL (%d instr)' % (k, len(A))); continue
    print('caso %d: DIFERE' % k)
    for l in difflib.unified_diff(na_, nb_, '983', 'nossa', n=1, lineterm=''): print('   ', l)
