#!/usr/bin/env python3
"""f37/enx.py <saida do dz.py> — a mesma listagem sem o que é molde nos pares Controller/Object (MakeInstance/Create com operator new,
registro na fábrica, destrutor com delete, registro do std::function): dessas só a 1ª linha + rótulo. Corta o comentário f=/d=/dw=."""
import sys, re
fs = []; cur = []
for l in open(sys.argv[1]):
    l = re.sub(r'  ; f=.*', '', l.rstrip('\n'))
    va = int(l[:8], 16)
    if cur and (va % 16 == 0 and re.search(r'\b(ret|jmp)\b', cur[-1]) ): fs.append(cur); cur = []
    cur.append(l)
fs.append(cur)
for f in fs:
    t = '\n'.join(f)
    k = ('new' if 'operator_new' in t and len(f) < 45 else 'fabrica' if 'AddObjectFunctor' in t else 'del' if 'operator_delete' in t and len(f) < 20
         else 'registro' if '_Impl_no_alloc1' in t else None)
    if k: print(f[0][:8], '[%s]' % k, ' '.join(re.findall(r'call    (0x[0-9a-f]+)|push    (0x[0-9a-f]{2,3})$|mov     ecx, (0x[0-9a-f]+)$', t, re.M) and [x for m in re.findall(r'call    (0x[0-9a-f]+)|push    (0x[0-9a-f]{2,3})$|mov     ecx, (0x[0-9a-f]+)$', t, re.M) for x in m if x]))
    else: print(t)
