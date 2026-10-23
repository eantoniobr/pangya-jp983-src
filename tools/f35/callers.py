# callers.py VA...  — conta chamadores (call rel32) de cada VA no exe 983 e lista as funções
import struct,sys,bisect,collections
d=open('/root/jp983src/ref/ProjectG_983_dump.exe','rb').read()
pe=struct.unpack_from('<I',d,0x3c)[0]; ns=struct.unpack_from('<H',d,pe+6)[0]; oh=pe+24
base=struct.unpack_from('<I',d,oh+28)[0]; st=oh+struct.unpack_from('<H',d,pe+20)[0]
secs=[struct.unpack_from('<IIII',d,st+40*i+8) for i in range(ns)]
vs,v,rs,ro=secs[0]
F=[]
for l in open('/root/jp983src/map/projectg_funcs.tsv').read().split('\n')[1:]:
    p=l.split('\t')
    if len(p)>10: F.append((int(p[0],16),p[10],p[3].replace('source/client/ProjectG/','')))
F.sort(); ks=[f[0] for f in F]
T={int(a,16) for a in sys.argv[1:]}
res=collections.defaultdict(list)
i=ro; end=ro+rs
while True:
    i=d.find(b'\xe8',i,end)
    if i<0: break
    va=base+v+i-ro; t=(va+5+struct.unpack_from('<i',d,i+1)[0])&0xffffffff
    if t in T: res[t].append(va)
    i+=1
for t in T:
    c=collections.Counter()
    for va in res[t]: c[F[bisect.bisect_right(ks,va)-1]]+=1
    print('%08x: %d chamadas em %d funções'%(t,len(res[t]),len(c)))
    u=collections.Counter()
    for f,n in c.items(): u[f[2]]+=n
    print('  por unidade:',', '.join('%s %d'%(k or '?',n) for k,n in u.most_common(40)))
