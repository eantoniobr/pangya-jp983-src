#!/usr/bin/env python3
"""quem.py VA... — lista cada `call rel32` do exe 983 para os VAs dados: va_da_chamada  função_que_contém (nome do mapa)  unidade."""
import struct,sys,bisect
sys.path.insert(0,'/root/jp983src/tools/f34'); import pgdis as P
d=P.d; vs,v,rs,ro=P.secs[0]
F=[]
for l in open('/root/jp983src/map/projectg_funcs.tsv').read().split('\n')[1:]:
    p=l.split('\t')
    if len(p)>10: F.append((int(p[0],16),p[10],p[3].replace('source/client/ProjectG/','')))
F.sort(); ks=[f[0] for f in F]
N={}
for l in open('/root/jp983src/map/projectg.tsv'):
    p=l.rstrip('\n').split('\t')
    if len(p)>1 and not l.startswith('#'):
        try: N.setdefault(int(p[1],16),p[0])
        except ValueError: pass
T={int(a,16) for a in sys.argv[1:]}
i=ro; end=ro+rs
while True:
    i=d.find(b'\xe8',i,end)
    if i<0: break
    va=P.base+v+i-ro; t=(va+5+struct.unpack_from('<i',d,i+1)[0])&0xffffffff
    if t in T:
        f=F[bisect.bisect_right(ks,va)-1]
        print('%08x <- %08x  em %08x %s  [%s]'%(t,va,f[0],N.get(f[0],f[1]),f[2]))
    i+=1
