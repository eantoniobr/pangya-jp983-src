#!/usr/bin/env python3
# V2 (prova pelo compilador): pré-processa cada unidade do exe com as flags do build (cl /E, sem pch) e lista onde
# sobram __asm/_emit/naked depois do pré-processador. uso: prepro.py <saida.tsv> [-j N] [filtro ...]
import sys,os,re,subprocess,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))+'/../f32')
import pgbuild as P
class A: flags=None
ASM=re.compile(rb'\b(__asm|_asm|_emit|__emit)\b|__declspec\s*\(\s*naked\s*\)')
LN=re.compile(rb'#line (\d+) "([^"]+)"')
def run(u):
    src,rb,pch,fi,einc=u
    args=P.base_args(A,einc,src)+fi+['/E',P.absp(src)]
    p=subprocess.run([P.ROOT+'/tools/vs.sh','cl','/nologo']+args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=P.ROOT,env=dict(os.environ,VS=P.VS))
    hits={}; f=b'?'; n=0; nl=0
    for l in p.stdout.split(b'\n'):
        nl+=1
        m=LN.match(l)
        if m: n=int(m.group(1))-1; f=m.group(2); continue
        n+=1
        if ASM.search(l):
            k=f.decode('latin-1').replace('\\\\','/').replace('\\','/')
            hits.setdefault(k,[]).append(n)
    return src,p.returncode,nl,hits
a=sys.argv[1:]; out=a.pop(0); j=8
if '-j' in a: i=a.index('-j'); j=int(a[i+1]); del a[i:i+2]
us=P.units()
ps=[(s,s,None,[],[]) for s in P.pchs(us)]
us=us+ps
if a: us=[u for u in us if any(f in u[0] for f in a)]
agg={}; bad=[]; n=0
with cf.ThreadPoolExecutor(j) as ex:
    for src,rc,nl,hits in ex.map(run,us):
        n+=1
        if rc or nl<50: bad.append((src,rc,nl))
        for f,ls in hits.items():
            d=agg.setdefault(f,{'units':set(),'lines':set()}); d['units'].add(src); d['lines'].update(ls)
with open(out,'w') as o:
    o.write('arquivo\tlinhas_asm\tprimeira\tultima\tunidades\texemplo\n')
    for f,d in sorted(agg.items()):
        o.write('%s\t%d\t%d\t%d\t%d\t%s\n'%(f,len(d['lines']),min(d['lines']),max(d['lines']),len(d['units']),sorted(d['units'])[0]))
print('unidades pré-processadas:',n,'falhas:',len(bad),bad[:5]); print('arquivos com asm ativo:',len(agg))
for f,d in sorted(agg.items()): print('%5d linhas  %4d unidades  %s'%(len(d['lines']),len(d['units']),f))
