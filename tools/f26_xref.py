#!/usr/bin/env python3
# xref.py — para cada função SEM_COBERTURA da faixa wd3d8: quem chama (call/jmp/push imm/vtable) -> build/f26/xref.tsv
import sys,struct,bisect,capstone
d=open('/root/jp983src/ref/wangreal_983.dll','rb').read()
pe=struct.unpack_from('<I',d,0x3c)[0]; ns=struct.unpack_from('<H',d,pe+6)[0]
oh=pe+24; base=struct.unpack_from('<I',d,oh+28)[0]; st=oh+struct.unpack_from('<H',d,pe+20)[0]
secs=[(d[st+40*i:st+40*i+8].rstrip(b'\0').decode(),)+struct.unpack_from('<IIII',d,st+40*i+8) for i in range(ns)]
img=bytearray(max(v+max(vs,rs) for n,vs,v,rs,ro in secs))
for n,vs,v,rs,ro in secs: img[v:v+rs]=d[ro:ro+rs]
img=bytes(img)
funcs=[]
for l in open('/root/jp983src/map/wangreal_funcs.tsv'):
    p=l.rstrip('\n').split('\t')
    if p[0]=='va' or l[0]=='#': continue
    funcs.append((int(p[0],16),int(p[1]),p[13],p[10]))
funcs.sort(); starts=[f[0] for f in funcs]
def owner(va):
    i=bisect.bisect_right(starts,va)-1
    return funcs[i] if i>=0 and va<funcs[i][0]+max(funcs[i][1],1) else None
cov={}
for l in open('/root/jp983src/out/F2.6/cobertura_antes.tsv'):
    p=l.rstrip('\n').split('\t')
    if l[0]=='#' or p[2]!='F': continue
    cov[int(p[0],16)]=(p[3],p[4])
callers={}
tv=[(v,max(vs,rs)) for n,vs,v,rs,ro in secs if n=='.text'][0]
for o in range(tv[0],tv[0]+tv[1]-5):
    if img[o] in (0xe8,0xe9):
        t=base+o+5+struct.unpack_from('<i',img,o+1)[0]
        if t in cov:
            f=owner(base+o); src=f[0] if f else base+o
            if src!=t: callers.setdefault(t,set()).add(src)
# ponteiros em .rdata/.data (vtables, tabelas)
dref={}
for n,vs,v,rs,ro in secs:
    if n in('.rdata','.data'):
        d=img[v:v+rs]; b0=base+v
        for o in range(0,len(d)-3,4):
            t=struct.unpack_from('<I',d,o)[0]
            if t in cov: dref.setdefault(t,[]).append(b0+o)
def nm(va):
    c=cov.get(va); 
    if c: return '%08x:%s:%s'%(va,c[0][:5],c[1][:50])
    f=owner(va); return '%08x:?:%s'%(va,f[2][:50] if f else '')
for va in sorted(cov):
    c=cov[va]
    if c[0]!='SEM_COBERTURA': continue
    f=owner(va)
    print('%08x\t%d\t%s\t%s\t%s'%(va,f[1],c[1][:90],' | '.join(nm(x) for x in sorted(callers.get(va,[]))[:6]),' '.join('%08x'%x for x in dref.get(va,[])[:3])))
