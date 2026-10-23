#!/usr/bin/env python3
"""swtab.py BYTES_VA ALVOS_VA BASE N — switch de duas tabelas do 983 (movzx byte [eax+BYTES]; jmp [eax*4+ALVOS]): alvo -> ids (sessão 130)."""
import sys, struct
d=open('/root/jp983src/ref/ProjectG_983_dump.exe','rb').read()
pe=struct.unpack_from('<I',d,0x3c)[0];ns=struct.unpack_from('<H',d,pe+6)[0];oh=pe+24;base=struct.unpack_from('<I',d,oh+28)[0];st=oh+struct.unpack_from('<H',d,pe+20)[0]
def off(va):
    r=va-base
    for i in range(ns):
        vs,v,rs,ro=struct.unpack_from('<IIII',d,st+40*i+8)
        if v<=r<v+max(vs,rs): return ro+r-v
bt,jt,sub,n=[int(x,0) for x in sys.argv[1:5]]
from collections import defaultdict
m=defaultdict(list)
for i in range(n):
    b=d[off(bt)+i]; tgt=struct.unpack_from('<I',d,off(jt)+4*b)[0]; m[tgt].append(hex(i+sub))
for t in sorted(m): print(hex(t), ' '.join(m[t]) if len(m[t])<10 else '(default %d)'%len(m[t]))
