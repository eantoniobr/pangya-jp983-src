"""F6 (C399): como objeq.py, mas ignora a ORDEM das secoes COMDAT: compara, por simbolo externo, bytes + relocacoes (por nome)."""
import sys,struct
def le(p):
    b=open(p,'rb').read(); _,ns,_,ps,nsym,oh,_=struct.unpack_from('<HHIIIHH',b,0); st=ps+nsym*18
    def nm(raw):
        if raw[:4]==b'\0\0\0\0':
            o=struct.unpack_from('<I',raw,4)[0]; return b[st+o:b.index(b'\0',st+o)]
        return raw.rstrip(b'\0')
    idx={}; syms=[]; i=0
    while i<nsym:
        r=b[ps+18*i:ps+18*(i+1)]; n=nm(r[:8]); v,sec,t,cl,na=struct.unpack_from('<IhHBB',r,8)
        idx[i]=(n,sec); syms.append((n,v,sec,cl)); i+=1+na
    secs=[]
    for k in range(ns):
        h=b[20+oh+40*k:20+oh+40*(k+1)]; n=nm(h[:8]); sz,pr,prl,_,nr,_,ch=struct.unpack_from('<IIIIHHI',h,16)
        if n.startswith(b'.debug$'): secs.append(None); continue
        rel=[]
        for j in range(nr):
            va,si,ty=struct.unpack_from('<IIH',b,prl+10*j); s=idx[si]; rel.append((va,s[0],ty))
        secs.append((n,b[pr:pr+sz] if pr else sz,tuple(rel),ch))
    out={}
    for n,v,sec,cl in syms:
        if sec>0 and cl==2 and secs[sec-1] is not None: out[n]=(v,secs[sec-1])
    return out
A,B=le(sys.argv[1]),le(sys.argv[2])
d=[k for k in set(A)|set(B) if A.get(k)!=B.get(k)]
print('IGUAL por simbolo (%d)'%len(A) if not d else 'DIFERE em %d: %r'%(len(d),d[:5]))
