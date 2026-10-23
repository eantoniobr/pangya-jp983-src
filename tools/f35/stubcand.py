#!/usr/bin/env python3
# f35/stubcand.py — para cada stub A/AB do out/F4/stubs.tsv, procura nos .obj (pg-a158 + B) um símbolo DEFINIDO com o mesmo
# método e a mesma cauda de assinatura (visão "…Ex" × classe real, ponteiro × ref, const…). Sessão 158. Uso: python3 -I stubcand.py
import subprocess,glob,re,sys,collections
stubs=[l.split('\t') for l in open('/root/jp983src/out/F4/stubs.tsv') if not l.startswith('simbolo')]
A=[s for s in stubs if s[7] in('A','AB') and s[1]=='função']
defs=collections.defaultdict(set)
for o in glob.glob('/root/jp983src/build/pg-a158/obj/src/**/*.obj',recursive=True)+glob.glob('/root/jp983src/build/B/obj/**/*.obj',recursive=True):
    out=subprocess.run(['nm','-g','--defined-only',o],capture_output=True,text=True).stdout
    for l in out.splitlines():
        p=l.split()
        if len(p)==3 and p[1] in 'TtWw' and p[2].startswith('?'): defs[p[2]].add(o.split('/obj/')[-1])
alln=set(defs)
for s in A:
    sym=s[0]
    m=re.match(r'\?(\w+)@(\w+)@@(.*)$',sym)
    if not m: print('??',sym); continue
    meth,cls,rest=m.groups()
    c=[d for d in alln if d.startswith('?'+meth+'@') and d!=sym]
    c2=[d for d in c if d.endswith('@@'+rest) or d.split('@@',1)[-1][:3]==rest[:3]]
    print(sym, '|', ' ; '.join(sorted(c2)[:3]) if c2 else ('~'+' ; '.join(sorted(c)[:2]) if c else '-'))
