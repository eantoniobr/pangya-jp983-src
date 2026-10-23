#!/usr/bin/env python3
# f37/dprova.py DIFF_ALL.txt NOME... — por funcao DIFERENTE: calls/constantes so de um lado (prova de mesma logica)
import re,sys,collections
SYM={}
for ln in open('out/F3.7/s286/c_scoreboard/simbolos.tsv',encoding='utf-8',errors='replace').read().split('\n')[1:]:
    f=ln.split('\t')
    if len(f)>=2 and f[1]: SYM[f[0]]=f[1]
def norm(t):
    t=t.replace('call <','').replace('call ','').strip('<> ')
    if re.fullmatch(r'[0-9a-f]{8}',t): return t
    if t in SYM: return SYM[t]
    c=[v for k,v in SYM.items() if k.startswith(t)]
    return c[0] if c else t
txt=open(sys.argv[1],encoding='utf-8',errors='replace').read().split('\n--- ')
want=sys.argv[2:]
def toks(s):
    calls=re.findall(r'call [^\n]*?<([^>]+)>',s)
    c=re.findall(r'call (?:0x[0-9a-f]+|\S+)',s)
    imm=re.findall(r'(?<![\w.])(0x[0-9a-f]+|\d+)(?![\w])',s)
    return [norm(x) for x in (calls or c)], [i for i in imm if not (i.startswith('0x') and int(i,16)>=0x400000)]
for blk in txt[1:]:
    head=blk.split('\n',1)[0]
    name=head.split('(')[0].strip()
    if want and not any(w in name for w in want): continue
    L=[];R=[]
    for ln in blk.split('\n')[1:]:
        if len(ln)<4 or ln[1]!=' ' and ln[:2] not in (' |',' <',' >',' ~'): continue
        if ln[:3] not in (' | ',' < ',' > ',' ~ '): continue
        parts=re.split(r'\s{3,}',ln[3:].strip(' '),maxsplit=1)
        if ln[1] in '|~': 
            l,r=(parts+[''])[:2]
        elif ln[1]=='<': l,r=ln[3:].strip(),''
        else: l,r='',ln[3:].strip()
        L.append(l);R.append(r)
    cl,il=toks('\n'.join(L)); cr,ir=toks('\n'.join(R))
    a=collections.Counter(cl)-collections.Counter(cr); b=collections.Counter(cr)-collections.Counter(cl)
    ia=collections.Counter(il)-collections.Counter(ir); ib=collections.Counter(ir)-collections.Counter(il)
    print(f"{name}\n   calls so-nosso={dict(a)} so-983={dict(b)}\n   imm so-nosso={dict(ia)} so-983={dict(ib)}")
