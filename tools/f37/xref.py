import struct, sys, bisect
R='/root/jp983src'
d=open(R+'/ref/ProjectG_983_dump.exe','rb').read()
pe=struct.unpack_from('<I',d,0x3c)[0]; oh=pe+24; base=struct.unpack_from('<I',d,oh+28)[0]
n=struct.unpack_from('<H',d,pe+6)[0]; st=oh+struct.unpack_from('<H',d,pe+20)[0]
secs=[]
for i in range(n):
    o=st+40*i; vs,va,rs,ro=struct.unpack_from('<IIII',d,o+8); secs.append((va,vs,rs,ro))
funcs=[]
for l in open(R+'/map/projectg_funcs.tsv'):
    p=l.rstrip('\n').split('\t')
    try: funcs.append((int(p[0],16),p[1] if len(p)>1 else ''))
    except: pass
funcs.sort(); fk=[f[0] for f in funcs]
def fn(va):
    i=bisect.bisect_right(fk,va)-1; return '%08x %s'%funcs[i] if i>=0 else '?'
for t in sys.argv[1:]:
    tgt=int(t,16)
    for va,vs,rs,ro in secs:
        blob=d[ro:ro+rs]
        for k in range(len(blob)-5):
            if blob[k]==0xe8:
                src=base+va+k
                if (src+5+struct.unpack_from('<i',blob,k+1)[0])&0xffffffff==tgt: print(t,'call de %08x em'%src, fn(src))
