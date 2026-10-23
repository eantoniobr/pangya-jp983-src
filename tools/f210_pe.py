#!/usr/bin/env python3
# F2.10: compara cabeçalho PE, seções, exports e imports de duas dlls (nossa × 983).
# uso: f210_pe.py nossa.dll ref.dll
import struct,sys
class PE:
    def __init__(s,p):
        s.d=d=open(p,'rb').read(); pe=struct.unpack_from('<I',d,0x3c)[0]; s.pe=pe
        s.nsec,=struct.unpack_from('<H',d,pe+6); s.chars,=struct.unpack_from('<H',d,pe+22)
        opt=pe+24; s.opt=opt; osz,=struct.unpack_from('<H',d,pe+20)
        s.linker=d[opt+2],d[opt+3]; s.entry,=struct.unpack_from('<I',d,opt+16); s.base,=struct.unpack_from('<I',d,opt+28)
        s.secalign,s.filealign=struct.unpack_from('<II',d,opt+32)
        s.osver=struct.unpack_from('<HH',d,opt+40); s.subver=struct.unpack_from('<HH',d,opt+48)
        s.subsys,s.dllchars=struct.unpack_from('<HH',d,opt+68)
        s.stack=struct.unpack_from('<II',d,opt+72); s.heap=struct.unpack_from('<II',d,opt+80)
        s.dirs=[struct.unpack_from('<II',d,opt+96+8*i) for i in range(16)]
        s.secs=[]
        for i in range(s.nsec):
            o=opt+osz+40*i; n=d[o:o+8].rstrip(b'\0').decode()
            vs,va,rs,ro=struct.unpack_from('<IIII',d,o+8); ch,=struct.unpack_from('<I',d,o+36)
            s.secs.append((n,va,vs,ro,rs,ch))
    def off(s,rva):
        for n,va,vs,ro,rs,ch in s.secs:
            if va<=rva<va+max(vs,rs): return ro+rva-va
    def cstr(s,rva):
        o=s.off(rva); return s.d[o:s.d.index(b'\0',o)].decode('latin1')
    def imports(s):
        r={}; rva=s.dirs[1][0]; o=s.off(rva)
        while True:
            ilt,_,_,name,iat=struct.unpack_from('<IIIII',s.d,o)
            if not name: break
            L=[]; t=s.off(ilt or iat)
            while True:
                v,=struct.unpack_from('<I',s.d,t)
                if not v: break
                L.append('#%d'%(v&0xffff) if v>>31 else s.cstr(v+2)); t+=4
            r[s.cstr(name).lower()]=L; o+=20
        return r
    def exports(s):
        rva=s.dirs[0][0]
        if not rva: return []
        o=s.off(rva); base,nf,nn,af,an,ao=struct.unpack_from('<IIIIII',s.d,o+16)
        return [(struct.unpack_from('<H',s.d,s.off(ao)+2*i)[0]+base, s.cstr(struct.unpack_from('<I',s.d,s.off(an)+4*i)[0])) for i in range(nn)]
if __name__=='__main__':
    a,b=PE(sys.argv[1]),PE(sys.argv[2])
    for k in ('linker','chars','entry','base','secalign','filealign','osver','subver','subsys','dllchars','stack','heap'):
        x,y=getattr(a,k),getattr(b,k); f=lambda v: hex(v) if isinstance(v,int) else str(tuple(hex(i) if i>99 else i for i in v))
        print('%-10s nosso %-22s 983 %-22s %s'%(k,f(x),f(y),'=' if x==y else 'DIFERE'))
    print('exports nosso:',a.exports()); print('exports 983  :',b.exports())
    print('seções nosso:',[(n,'%X'%vs) for n,va,vs,ro,rs,ch in a.secs]); print('seções 983  :',[(n,'%X'%vs) for n,va,vs,ro,rs,ch in b.secs])
    ia,ib=a.imports(),b.imports(); ta=tb=0; dif=0
    print('ordem das dlls nosso:',list(ia)); print('ordem das dlls 983  :',list(ib))
    for dll in sorted(set(ia)|set(ib)):
        x,y=set(ia.get(dll,[])),set(ib.get(dll,[])); ta+=len(x); tb+=len(y); dif+=len(x^y)
        print('%-13s nosso %3d  983 %3d  comuns %3d  só nosso: %s | só 983: %s'%(dll,len(x),len(y),len(x&y),sorted(x-y),sorted(y-x)))
    print('total imports nosso %d, 983 %d, diferenças %d'%(ta,tb,dif))
