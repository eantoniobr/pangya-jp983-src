#!/usr/bin/env python3
"""f37/sum.py <dz.txt> — resumo por função de uma saída do dz.py: início, nº de linhas, chamadas (nome ou endereço), strings e
vtables citadas. Ler isto ANTES de abrir qualquer corpo."""
import sys, re
fs = []; cur = []
for l in open(sys.argv[1]):
    l = l.rstrip('\n')
    if not l[:8].strip(): continue
    va = int(l[:8], 16)
    if cur and va % 16 == 0 and re.search(r'\b(ret|jmp|int3)\b', cur[-1]): fs.append(cur); cur = []
    cur.append(l)
fs.append(cur)
for f in fs:
    t = []
    for l in f:
        m = re.search(r'(call|jmp) +(dword ptr \[)?0x([0-9a-f]+)\]?(?:  ; (.*))?', l)
        if m and m.group(1) == 'call': t.append((m.group(4) or m.group(3))[:48] if not (m.group(4) or '').startswith('f=') else m.group(3))
        elif '; "' in l or '; vtable' in l: t.append(l.split('; ', 1)[1][:48])
        elif re.search(r'call +dword ptr \[e.. \+ (0x[0-9a-f]+)\]', l): t.append('v' + re.search(r'\+ (0x[0-9a-f]+)\]', l).group(1))
    print(f[0][:8], '%3d' % len(f), ' | '.join(t)[:330])
