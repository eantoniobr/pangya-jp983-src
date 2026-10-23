import sys,re,bisect
m=sys.argv[1]; addrs=[int(a,16) for a in sys.argv[2:]]
syms=[]
for l in open(m,errors='ignore'):
    p=l.split()
    if len(p)>=4 and re.fullmatch(r'[0-9a-f]{4}:[0-9a-f]{8}',p[0]) and re.fullmatch(r'[0-9a-f]{8}',p[2]):
        syms.append((int(p[2],16),p[1],p[-1]))
syms.sort(); ks=[s[0] for s in syms]
for a in addrs:
    i=bisect.bisect_right(ks,a)-1; s=syms[i]
    print('%08x %s+0x%x %s'%(a,s[1],a-s[0],s[2]))
