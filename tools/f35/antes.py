"""Compara os funcs.tsv de uma sessão com o mais novo anterior da mesma unidade (fora da sessão)."""
import glob,os,sys,csv
ses=sys.argv[1]  # ex.: out/F3.5/s131
rank={'IGUAL':3,'QUASE':2,'DIFERENTE':1,'SEM_PAR':0}
def load(p):
    r={}
    for row in csv.DictReader(open(p),delimiter='\t'):
        if row['propria']=='1': r[row['funcao']]=(row['classe'],float(row['pct_instr']))
    return r
allf=[p for p in glob.glob('out/**/cmp/*/funcs.tsv',recursive=True) if not any(x in p for x in ('/antes/','/tmp/','/ab/'))]
for cur in sorted(glob.glob(ses+'/*/cmp/*/funcs.tsv')):
    u=cur.split('/')[-2]
    prev=[p for p in allf if p.split('/')[-2]==u and not p.startswith(ses+'/')]
    if not prev: print(u,'sem anterior'); continue
    pv=max(prev,key=os.path.getmtime); a=load(pv); b=load(cur)
    from collections import Counter
    ca=Counter(c for c,_ in a.values()); cb=Counter(c for c,_ in b.values())
    piora=[(f,a[f],b.get(f)) for f in a if f in b and (rank[b[f][0]]<rank[a[f][0]] or b[f][1]<a[f][1]-1e-4)]
    melhora=[(f,a[f],b[f]) for f in a if f in b and (rank[b[f][0]]>rank[a[f][0]] or b[f][1]>a[f][1]+1e-4)]
    print('%-40s antes %s | agora %s | pioras %d melhoras %d | só antes %d só agora %d  (%s)'%(u,dict(ca),dict(cb),len(piora),len(melhora),len(set(a)-set(b)),len(set(b)-set(a)),pv))
    for x in piora: print('   PIORA',*x)
    for x in melhora: print('   melhora',*x)
