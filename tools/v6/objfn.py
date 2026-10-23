#!/usr/bin/env python3
# tools/v6/objfn.py A.obj B.obj — funções cujo código muda entre dois .obj (bytes + relocs por função; ignora rótulos
# $LN/$attach, hashes de namespace anônimo e números $SG). Saída: +nova -sumiu ~mudou. C216.
import sys,re,subprocess
def fns(p):
    out=subprocess.run(['objdump','-drz',p],capture_output=True,text=True).stdout
    d={};cur=None;k={}
    for l in out.splitlines():
        m=re.match(r'^[0-9a-f]+ <(.*)>:$',l)
        if m:
            s=m.group(1)
            if s.startswith('$'): continue
            s=re.sub(r'\?A0x[0-9a-f]+','?A0xH',s); k[s]=k.get(s,0)+1; cur=s+'#%d'%k[s]; d[cur]=[[],[]]; continue
        if cur is None: continue
        m=re.match(r'^\s*[0-9a-f]+:\s+((?:[0-9a-f]{2} )+)',l)
        if m: d[cur][0].append(m.group(1).replace(' ','')); continue
        m=re.match(r'^\s*([0-9a-f]+): (\w+)\s+(\S+)',l)
        if m: d[cur][1].append(m.group(1)+re.sub(r'\$SG\d+|\?A0x[0-9a-f]+|\$LN\d+','N',m.group(3)))
    return {a:''.join(b[0])+'|'+','.join(b[1]) for a,b in d.items()}
a,b=fns(sys.argv[1]),fns(sys.argv[2])
for s in sorted(set(a)|set(b)):
    if a.get(s)!=b.get(s): print(('+' if s not in a else '-' if s not in b else '~'),s[:150])
