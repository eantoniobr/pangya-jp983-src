import sys,csv
def load(p):
    d={}
    for r in csv.DictReader(open(p),delimiter='\t'):
        if r['propria']=='1': d[r['funcao']]=(r['classe'],r['va983'],r['pct_instr'])
    return d
a=load(sys.argv[1]); b=load(sys.argv[2])
from collections import Counter
print('antes',Counter(v[0] for v in a.values()),'\ndepois',Counter(v[0] for v in b.values()))
for k in sorted(set(a)|set(b)):
    x=a.get(k,('-',)); y=b.get(k,('-',))
    if x[0]!=y[0] or (x!=y and len(sys.argv)>3): print(x,'->',y,k)
