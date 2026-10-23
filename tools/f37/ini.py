#!/usr/bin/env python3
"""f37/ini.py <dz.txt>... — inícios de função de uma saída do dz.py (endereço múltiplo de 16 logo após ret/jmp ou vão de int3) e tamanho."""
import sys
for f in sys.argv[1:]:
    L = [l.split(None, 2) for l in open(f) if l[:8].strip()]
    st = []; prev = None; pa = None
    for p in L:
        a = int(p[0], 16)
        if prev is None or (a % 16 == 0 and (prev in ('ret', 'jmp') or a - pa > 15)): st.append(a)
        prev = p[1]; pa = a
    print(f, len(st), ' '.join('%08x' % a for a in st))
