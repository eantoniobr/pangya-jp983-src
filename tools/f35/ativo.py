# uso: ativo.py arquivo linha... -> diz se a linha compila com REBANG_SEMANTIC_ONLY definido (heurística de #if)
import sys,re
f=sys.argv[1]; want=set(int(x) for x in sys.argv[2:])
st=[]  # pilha de (ativo_do_ramo, ja_tomou, avaliavel)
def val(cond):
    c=cond.strip()
    if re.fullmatch(r'defined\s*\(?\s*REBANG_SEMANTIC_ONLY\s*\)?',c): return True
    if re.fullmatch(r'!\s*defined\s*\(?\s*REBANG_SEMANTIC_ONLY\s*\)?',c): return False
    if c=='0': return False
    if c=='1': return True
    return None
for n,l in enumerate(open(f,encoding='latin-1'),1):
    s=l.strip()
    m=re.match(r'#\s*(ifdef|ifndef|if|elif|else|endif)\b(.*)',s)
    if m:
        k,r=m.group(1),m.group(2).split('//')[0]
        if k=='ifdef': v=True if r.strip()=='REBANG_SEMANTIC_ONLY' else None; st.append([v,v is True,v is not None])
        elif k=='ifndef': v=False if r.strip()=='REBANG_SEMANTIC_ONLY' else None; st.append([v,v is True,v is not None])
        elif k=='if': v=val(r); st.append([v,v is True,v is not None])
        elif k=='elif':
            t=st[-1]; v=val(r)
            if t[1]: t[0]=False
            else: t[0]=v; t[1]= v is True
        elif k=='else':
            t=st[-1]
            if t[0] is None: pass
            else: t[0]= not t[1]
        elif k=='endif': st.pop()
    if n in want:
        act=all(x[0] is not False for x in st)
        print(n,'ATIVA' if act else 'fora', s[:100])
