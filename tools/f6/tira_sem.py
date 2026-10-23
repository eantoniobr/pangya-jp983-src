# (C405) uso: tira_sem.py arq.cpp  (o exe usa /DREBANG_SEMANTIC_ONLY); confira com objeq: em ghostdocument mudou o .text
# remove ramos mortos sob /DREBANG_SEMANTIC_ONLY: #ifndef X ... [#else ...] #endif -> fica o #else; #ifdef X ... #else ... #endif -> fica o 1o
import sys,re
p=sys.argv[1]; L=open(p,encoding='latin-1').read().split('\n'); out=[]; st=[]  # st: (tipo, keep_atual) tipo: 'n','d','o'
def vivo(): return all(k for _,k in st)
for l in L:
    s=l.strip()
    if re.match(r'#\s*ifndef\s+REBANG_SEMANTIC_ONLY\b',s): st.append(('s',False)); continue
    if re.match(r'#\s*ifdef\s+REBANG_SEMANTIC_ONLY\b',s): st.append(('s',True)); continue
    if s.startswith('#if'):
        if vivo(): out.append(l)
        st.append(('o',True)); continue
    if st and st[-1][0]=='s' and s.startswith('#el'):
        assert s.startswith('#else'); st[-1]=('s',not st[-1][1]); continue
    if st and s.startswith('#endif'):
        t=st.pop()
        if t[0]=='o' and vivo(): out.append(l)
        continue
    if vivo(): out.append(l)
assert not st
open(p,'w',encoding='latin-1').write('\n'.join(out)); print(p,len(L),'->',len(out))
