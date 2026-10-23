#!/usr/bin/env python3
"""f37/norm.py <saida do dz.py> — desmonte normalizado para diff entre unidades gêmeas: sem a coluna de endereço, endereços de dentro
da unidade viram F<n> (início de função, pela ordem) ou L, sem comentário de float; uma linha `== F<n> <va>` abre cada função."""
import sys, re
L = [re.sub(r'  ; f=.*', '', l.rstrip('\n')) for l in open(sys.argv[1])]
vas = [int(l[:8], 16) for l in L]; lo, hi = vas[0], vas[-1]
st = [vas[0]] + [vas[i] for i in range(1, len(L)) if vas[i] % 16 == 0 and re.search(r'\b(ret|jmp)\b', L[i - 1])]
ix = {v: i for i, v in enumerate(st)}
def sub(m):
    v = int(m.group(0), 16)
    return ('F%d' % ix[v]) if v in ix else ('L' if lo <= v <= hi else m.group(0))
for l, v in zip(L, vas):
    if v in ix: print('== F%d %08x' % (ix[v], v))
    print(re.sub(r'0x[0-9a-f]{6}\b', sub, re.sub(r'  ; (FUN_|vtable|").*', '', l[10:])))
