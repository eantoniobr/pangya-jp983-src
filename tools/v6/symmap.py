#!/usr/bin/env python3
"""symmap.py MAP VA... — símbolo do map do link (função mais próxima abaixo) para cada VA (pilhas do exception.log; frente C, F4)."""
import sys,re,bisect
m=[]
for l in open(sys.argv[1],errors='replace'):
    p=l.split()
    if len(p)>=4 and re.fullmatch(r'[0-9a-f]{8}',p[2]) and p[0].startswith('0001:'):
        m.append((int(p[2],16),p[1],p[-1]))
m.sort(); ks=[x[0] for x in m]
for a in sys.argv[2:]:
    v=int(a,16); i=bisect.bisect_right(ks,v)-1
    print(a, '%s+%x'%(m[i][1][:110],v-m[i][0]), m[i][2])
