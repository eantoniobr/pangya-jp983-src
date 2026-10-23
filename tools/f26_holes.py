#!/usr/bin/env python3
# holes.py order.tsv funcs.tsv — buracos da ordem que não são função já comparada (mapa) pelo cmpfunc; com quem chama
import sys,csv
known={}
for r in csv.DictReader(open(sys.argv[2]),delimiter='\t'):
    if r['va983'] not in('-',''): known[int(r['va983'],16)]=(r['classe'],r['funcao'],int(r['bytes_983'] or 0))
xr={}
for l in open('/root/jp983src/out/F2.6/xref.tsv'):
    p=l.rstrip('\n').split('\t'); xr[int(p[0],16)]=(p[2],p[3],p[4])
mapn={}
for l in open('/root/jp983src/map/wangreal_funcs.tsv'):
    p=l.rstrip('\n').split('\t')
    if p[0]!='va' and l[0]!='#': mapn[int(p[0],16)]=(p[3],p[13],p[5])
tot=0;n=0
for l in open(sys.argv[1]):
    p=l.rstrip('\n').split('\t')
    if len(p)<3 or p[2]!='BURACO': continue
    va=int(p[0],16); sz=int(p[1])
    if any(k<=va<k+max(b,1) for k,(c,f,b) in known.items()): continue
    x=xr.get(va,('','','')); m=mapn.get(va,('?','?','?'))
    tot+=sz;n+=1
    print('%08x\t%d\t%s\t%s\t%s\t%s\t%s'%(va,sz,m[0],m[2],m[1][:70],x[1][:150],x[2]))
print('# %d buracos novos, %d bytes'%(n,tot))
