#!/usr/bin/env python3
# C295: pilha de um exception.dmp do robô -> endereços de retorno no ProjectG com símbolo do .map. Uso: tools/v6/dmpstack.py DMP MAP ESP_hex
import struct,sys,bisect,re
b=open(sys.argv[1],'rb').read()
n,rva=struct.unpack_from('<II',b,8)
mem=[]
for i in range(n):
    t,sz,r=struct.unpack_from('<III',b,rva+12*i)
    if t==5:
        cnt,=struct.unpack_from('<I',b,r)
        for j in range(cnt):
            st,ds,dr=struct.unpack_from('<QII',b,r+4+16*j); mem.append((st,ds,dr))
syms=[]
for l in open(sys.argv[2],errors='replace'):
    m=re.match(r'\s*0001:[0-9a-f]+\s+(\S+)\s+([0-9a-f]{8})\s+\S*\s*(\S*)',l)
    if m: syms.append((int(m.group(2),16),m.group(1),m.group(3)))
syms.sort(); ks=[s[0] for s in syms]
def sym(a):
    i=bisect.bisect_right(ks,a)-1
    return '%s+%x %s'%(syms[i][1][:90],a-syms[i][0],syms[i][2]) if i>=0 else '?'
esp=int(sys.argv[3],16)  # ESP do exception.log
st,ds,dr=[m for m in mem if m[0]<=esp<m[0]+m[1]][0]
for a in range(esp, min(esp+0x400, st+ds), 4):
    v,=struct.unpack_from('<I',b,dr+a-st)
    if 0x401000<=v<0xd00000: print('%08x: %08x %s'%(a,v,sym(v)))
