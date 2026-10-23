#!/usr/bin/env python3
# f37/dprova2.py DIFF_ALL.txt [filtro] — por funcao: calls e imediatos (fora de operandos de pilha) so de um lado, parse de 2 colunas
import re,sys,collections
SYM={}
for ln in open('out/F3.7/s286/c_scoreboard/simbolos.tsv',encoding='utf-8',errors='replace').read().split('\n')[1:]:
    f=ln.split('\t')
    if len(f)>=2 and f[1]: SYM[f[0]]=f[1]
txt=open(sys.argv[1],encoding='utf-8',errors='replace').read().split('\n--- ')[1:]
want=sys.argv[2:]
STK=re.compile(r'\[(?:ebp|esp)\s*[-+]\s*0x[0-9a-f]+\]|\[(?:ebp|esp)\]')
def parse(ins):
    ins=ins.strip()
    if not ins: return None
    m=re.match(r'call (.*)',ins)
    if m:
        t=m.group(1); mm=re.search(r'<([^>]+)>',t); t=mm.group(1) if mm else t
        t=t.strip(); t=SYM.get(t) or next((v for k,v in SYM.items() if k.startswith(t)),t) if not re.fullmatch(r'[0-9a-f]{8}',t) else t
        return ('c',t)
    s=STK.sub('[S]',ins)
    s=re.sub(r'<[^>]*>','',s)
    s=re.sub(r'\[0\]','[G]',s)
    imm=[x for x in re.findall(r'(?<![\w.])(0x[0-9a-f]+|\d+)(?![\w])',s) if not (x.startswith('0x') and int(x,16)>=0x400000)]
    return ('i',imm,ins.split()[0])
out=[]
for blk in txt:
    head=blk.split('\n',1)[0]; name=head.split('  (')[0].strip()
    if want and not any(w in name for w in want): continue
    L=[];R=[]
    for ln in blk.split('\n')[1:]:
        if len(ln)<4 or ln[:3] not in ('   ',' | ',' < ',' > ',' ~ '): continue
        body=ln[3:]
        if ln[1]=='<': l,r=body.strip(),''
        elif ln[1]=='>': l,r='',body.strip()
        else:
            p=re.split(r'\s{3,}',body.strip(),maxsplit=1); l,r=(p+[''])[:2]
        L.append(l);R.append(r)
    def sig(X):
        c=collections.Counter();i=collections.Counter()
        for x in X:
            p=parse(x)
            if not p: continue
            if p[0]=='c': c[p[1][:40]]+=1
            else:
                for v in p[1]: i[v]+=1
        return c,i
    cl,il=sig(L);cr,ir=sig(R)
    dc=(cl-cr, cr-cl); di=(il-ir, ir-il)
    nc=sum(dc[0].values())+sum(dc[1].values()); ni=sum(di[0].values())+sum(di[1].values())
    print(f"{name}\tcalls_dif={nc}\timm_dif={ni}\tN={dict(di[0])}\tR={dict(di[1])}\tcN={dict(dc[0])}\tcR={dict(dc[1])}")
