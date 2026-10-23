import re,sys
from collections import Counter
M={}
for l in open('/root/jp983src/src/projectg/msg983.h',encoding='latin-1'):
    m=re.match(r'#define MSG645_(0x[0-9a-f]+)\s+(0x[0-9a-fA-F]+)',l)
    if m: M[m.group(1)]=int(m.group(2),16)
s=open('/tmp/ours_onp.cpp',encoding='latin-1').read()
ours=Counter()
for m in re.finditer(r'GetActor\("(\w+)"\)\s*<<\s*MsgObject\(\s*\w+\s*,\s*([^,]+),',s):
    mid=m.group(2).strip()
    mm=re.match(r'M983\((0x[0-9a-f]+)\)',mid)
    if mm: v=M.get(mm.group(1),-1)
    else:
        try: v=int(mid,0)
        except: v=mid
    ours[(m.group(1),v)]+=1
n983=Counter()
for l in open('/tmp/m983.txt'):
    p=l.split()
    if len(p)==3 and p[2].startswith('0x'): n983[(p[1],int(p[2],16))]+=1
    elif len(p)==3: n983[(p[1],p[2])]+=1
print(sum(ours.values()),sum(n983.values()))
for k in sorted(set(ours)|set(n983),key=str):
    if ours[k]!=n983[k]: print(k,'983',n983[k],'ours',ours[k])
