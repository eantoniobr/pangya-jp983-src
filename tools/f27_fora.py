#!/usr/bin/env python3
"""f27_fora.py ordem.tsv INI FIM main|eh — complemento do f23_order.py: para cada função do shparam.obj que ficou FORA da
ordem, procura os bytes (relocações como curinga) dentro dos BURACOS da faixa; mostra quantas cabem e os trechos da
faixa que continuam sem dono. Cabe por bytes = evidência fraca para funções de 3–4 bytes (qualquer getter igual serve)."""
import sys, os, importlib.machinery, importlib.util, csv
R='/root/jp983src'
ld = importlib.machinery.SourceFileLoader('cmpfunc', R+'/tools/cmpfunc')
cf = importlib.util.module_from_spec(importlib.util.spec_from_loader('cmpfunc', ld)); ld.exec_module(cf)
ob = cf.Obj(os.environ.get('OBJ', R+'/build/obj/src/wangreal/shparam.obj')); pe = cf.PE(R+'/ref/wangreal_983.dll')  # OBJ=outro.obj para outras unidades
tsv, lo, hi, eh = sys.argv[1], int(sys.argv[2],16), int(sys.argv[3],16), sys.argv[4]=='eh'
fora={l.split('\t')[4].strip() for l in open(tsv) if '\tFORA\t' in l}
holes=[(int(l.split('\t')[0],16),int(l.split('\t')[1])) for l in open(tsv) if '\tBURACO\t' in l]
used=0; n=0; nohit=[]
cov=set()
for nm, sec, a, b, own in ob.funcs():
    if nm not in fora or nm.startswith(cf.EHFUN)!=eh: continue
    data, rel, ch = ob.secs[sec-1]
    hits, e = cf.wild(pe, data, {o: r for o, r in rel.items() if a <= o < b}, a, b)
    hh=[h for h in hits if any(x<=h<x+s for x,s in holes)]
    n+=1
    if hh:
        used+=1
        for h in hh: cov.update(range(h,h+(b-a)))
    else: nohit.append((nm[:150],b-a,len(hits)))
tot=sum(s for x,s in holes)
print('FORA',n,'com lugar em buraco',used,'| bytes de buraco cobertos',len(cov),'de',tot)
for x in nohit: print('  sem lugar em buraco:',x)
runs=[]
for x,s in holes:
    cur=None
    for v in range(x,x+s):
        if v not in cov:
            if cur and cur[0]+cur[1]==v: cur[1]+=1
            else:
                cur=[v,1]; runs.append(cur)
print('trechos sem dono:',len(runs),sum(r[1] for r in runs),'B')
for r in runs: print('  %08x %d'%(r[0],r[1]))
