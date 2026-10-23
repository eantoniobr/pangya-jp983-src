# (C405) uso: tira_if0.py arq.cpp LINHA_DO_#if0  -> tira o ramo #if 0 (fica o #else); confira com objeq
import sys
p,ln=sys.argv[1],int(sys.argv[2]); L=open(p,encoding='latin-1').read().split('\n')
i=ln-1; assert L[i].startswith('#if 0'),L[i]
d=0; els=None
for j in range(i,len(L)):
    s=L[j].strip()
    if s.startswith('#if'): d+=1
    elif s.startswith('#endif'):
        d-=1
        if d==0: end=j; break
    elif d==1 and (s.startswith('#else') or s.startswith('#elif')): 
        assert s.startswith('#else'); els=j
drop=set(range(i,(els if els is not None else end)+1))|{end}
print(p,ln,'else',els and els+1,'end',end+1,'-',len(drop))
open(p,'w',encoding='latin-1').write('\n'.join(l for k,l in enumerate(L) if k not in drop))
