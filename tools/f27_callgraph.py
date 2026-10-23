#!/usr/bin/env python3
# cg.py LO HI — grafo de chamadas da faixa: por função, quem chama e quem ela chama (call/jmp rel32 + push/mov imm de endereço)
import sys,struct,bisect,capstone,re
d=open('/root/jp983src/ref/wangreal_983.dll','rb').read()
pe=struct.unpack_from('<I',d,0x3c)[0]; ns=struct.unpack_from('<H',d,pe+6)[0]
oh=pe+24; base=struct.unpack_from('<I',d,oh+28)[0]; st=oh+struct.unpack_from('<H',d,pe+20)[0]
secs=[(d[st+40*i:st+40*i+8].rstrip(b'\0').decode(),)+struct.unpack_from('<IIII',d,st+40*i+8) for i in range(ns)]
img=bytearray(max(v+max(vs,rs) for n,vs,v,rs,ro in secs))
for n,vs,v,rs,ro in secs: img[v:v+rs]=d[ro:ro+rs]
img=bytes(img)
funcs=[]
for fn,ci in(('map/wangreal_funcs.tsv',13),('map/wangreal_gaps.tsv',-1)):
    for l in open('/root/jp983src/'+fn):
        p=l.rstrip('\n').split('\t')
        if p[0]=='va' or l[0]=='#': continue
        funcs.append((int(p[0],16),int(p[1]),p[ci] if ci>0 else 'gap'))
funcs.sort(); starts=[f[0] for f in funcs]
def owner(va):
    i=bisect.bisect_right(starts,va)-1
    return funcs[i][0] if i>=0 and va<funcs[i][0]+max(funcs[i][1],1) else None
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
tlo,thi=0x10001000,0x10062000
callers={};callees={}
for va,sz,nm in funcs:
    if not(tlo<=va<thi): continue
    for ins in md.disasm(img[va-base:va-base+sz],va):
        m=re.search(r'0x(100[0-6][0-9a-f]{4})',ins.op_str)
        if not m: continue
        t=int(m.group(1),16)
        if t in starts and t!=va and (ins.mnemonic in('call','jmp','push','mov','lea')):
            callers.setdefault(t,set()).add(va); callees.setdefault(va,[]).append(t)
# vtables/dados
for n,vs,v,rs,ro in secs:
    if n in('.rdata','.data'):
        for o in range(0,rs-3,4):
            t=struct.unpack_from('<I',img,v+o)[0]
            if tlo<=t<thi and t in callers.keys()|set(starts) and bisect.bisect_left(starts,t)<len(starts) and starts[bisect.bisect_left(starts,t)]==t:
                callers.setdefault(t,set()).add(base+v+o)
lo,hi=int(sys.argv[1],16),int(sys.argv[2],16)
for va,sz,nm in funcs:
    if lo<=va<hi:
        print('%08x\t%d\t%s\t<-%s\t->%s'%(va,sz,nm[:50],','.join('%x'%c for c in sorted(callers.get(va,[]))),','.join('%x'%c for c in dict.fromkeys(callees.get(va,[])))))
