#!/usr/bin/env python3
# V2: lista __asm/_emit/naked que continuam ativos com /DREBANG_SEMANTIC_ONLY.
# Avalia só as condições sobre REBANG_SEMANTIC_ONLY (definida); outras macros = ramo desconhecido (conta como ativo).
# uso: asmscan.py <saida.tsv> [raiz ...]
import sys,re,os
D='REBANG_SEMANTIC_ONLY'
def cond(expr):
    e=re.sub(r'/\*.*?\*/|//.*','',expr).strip()
    if D not in e: return None
    e2=re.sub(r'defined\s*\(\s*%s\s*\)|defined\s+%s'%(D,D),'1',e)
    # conjunção com um termo !defined(D): falso seja qual for o resto (ex.: defined(REBANG_PCH_POOL) && !defined(D))
    if '||' not in e2 and any(re.fullmatch(r'[\s(]*!\s*\(?\s*1\s*\)?[\s)]*',t) for t in e2.split('&&')): return False
    if re.fullmatch(r'[\s!()1]*',e2):
        try: return bool(eval(e2.replace('!',' not ')))
        except Exception: return None
    return None
ASM=re.compile(r'\b(__asm|_asm|_emit|__emit)\b|__declspec\s*\(\s*naked\s*\)')
FUNC=re.compile(r'^[A-Za-z_][^;{}=]*\([^;]*\)?[^;]*$')
def scan(path):
    rows=[]; st=[]  # pilha: [ativo_pai, valor(True/False/None), ja_tomado]
    act=True; fn=''; fnl=0
    try: L=open(path,encoding='latin-1').read().split('\n')
    except Exception: return rows
    cur=None
    for n,l in enumerate(L,1):
        s=l.strip()
        m=re.match(r'#\s*(ifdef|ifndef|if|elif|else|endif)\b(.*)',s)
        if m:
            k,r=m.groups()
            if k in('ifdef','ifndef','if'):
                if k=='ifdef': v=True if r.split()[:1]==[D] else None
                elif k=='ifndef': v=False if r.split()[:1]==[D] else None
                else: v=cond(r)
                st.append([act,v,v is True]); act=act and (v is not False)
            elif k=='elif' and st:
                p,v0,tk=st[-1]
                v=cond(r)
                if tk: act=False
                else:
                    if v0 is None and v is None: v=None
                    act=p and (v is not False); st[-1][2]=(v is True)
                    if v0 is None: st[-1][1]=None
            elif k=='else' and st:
                p,v0,tk=st[-1]
                act=p and (not tk) and (v0 is not True)
            elif k=='endif' and st:
                act=st.pop()[0]
            continue
        if not l[:1].isspace() and FUNC.match(l) and not s.startswith(('#','//','}','{','/*','*')) and '(' in l:
            fn=s; fnl=n
        if act and ASM.search(re.sub(r'//.*','',l)):
            if cur and cur[1]==fn and n-cur[3]<=40: cur[3]=n; cur[4]+=1
            else:
                cur=[path,fn,n,n,1,set()]; rows.append(cur)
            for k in ASM.findall(re.sub(r'//.*','',l)): cur[5].add(k or 'naked')
            if 'naked' in l: cur[5].add('naked')
    return rows
out=sys.argv[1]; roots=sys.argv[2:] or ['src','include']
R=[]
for r in roots:
    for d,_,fs in os.walk(r):
        for f in sorted(fs):
            if f.lower().endswith(('.cpp','.h','.inl','.hpp','.c','.cc')): R+=scan(os.path.join(d,f))
with open(out,'w') as o:
    o.write('arquivo\tfuncao\tlinha_ini\tlinha_fim\tlinhas_asm\ttipos\n')
    for p,fn,a,b,c,k in R: o.write('%s\t%s\t%d\t%d\t%d\t%s\n'%(p,fn[:120],a,b,c,','.join(sorted(x for x in k if x))))
files={}
for r in R: files[r[0]]=files.get(r[0],0)+r[4]
print('ocorrências (função/bloco):',len(R),'arquivos:',len(files),'linhas asm:',sum(files.values()))
for f,c in sorted(files.items(),key=lambda x:-x[1])[:60]: print('%6d %s'%(c,f))
