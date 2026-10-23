import re,struct
from collections import Counter
d=open('/root/jp983src/ref/ProjectG_983_dump.exe','rb').read()
pe=struct.unpack_from('<I',d,0x3c)[0];ns=struct.unpack_from('<H',d,pe+6)[0];oh=pe+24;base=struct.unpack_from('<I',d,oh+28)[0];st=oh+struct.unpack_from('<H',d,pe+20)[0]
secs=[struct.unpack_from('<IIII',d,st+40*i+8) for i in range(ns)]
def off(va):
    r=va-base
    for vs,v,rs,ro in secs:
        if v<=r<v+max(vs,rs): return ro+r-v
def cstr(a):
    o=off(a)
    return d[o:o+30].split(b'\0')[0].decode('latin-1') if o else '?'
L=[l.split(None,1) for l in open('/tmp/full983.txt',errors='replace').read().split('\n') if l.strip()]
ins=[(a,t) for a,t in (x for x in L if len(x)==2)]
res=[]
for i,(a,t) in enumerate(ins):
    if re.match(r'call\s+0x9bac50$',t):
        name=None;stores=[];
        for j in range(i-1,max(0,i-22),-1):
            tj=ins[j][1]
            m=re.match(r'push\s+(0x[0-9a-f]+)$',tj)
            if m and name is None and int(m.group(1),16)>0xc00000: name=cstr(int(m.group(1),16))
            m=re.match(r'mov\s+dword ptr \[ebp - (0x[0-9a-f]+)\], (\w+)$',tj)
            if m: stores.append((int(m.group(1),16),m.group(2),j))
        # sender = highest ebp offset magnitude among stores; id = offset-4
        mid=None
        if stores:
            top=max(s[0] for s in stores)
            for o,v,j in stores:
                if o==top-4:
                    mid=v
                    if not v.startswith('0x') and not v.isdigit():
                        for k in range(j,max(0,j-400),-1):
                            m=re.match(r'mov\s+%s, (0x[0-9a-f]+|\d+)$'%v,ins[k][1])
                            if m: mid=m.group(1);break
        if mid is None or not (mid.startswith('0x') or mid.isdigit()):
            for j in range(i-1,max(0,i-40),-1):
                if re.match(r'call\s+0x46e780$',ins[j][1]):
                    ps=[]
                    for k in range(j-1,max(0,j-30),-1):
                        tk=ins[k][1]
                        if tk.startswith('push'): ps.append(tk.split(None,1)[1])
                        elif re.match(r'(lea|mov|movzx|xor|sub|add)\b',tk): continue
                        else: break
                        if len(ps)>=2: break
                    if len(ps)>=2 and re.match(r'(0x[0-9a-f]+|\d+)$',ps[1]): mid=ps[1]
                    break
        res.append((ins[i][0],name,mid))
import sys
for r in res: print(*r)
