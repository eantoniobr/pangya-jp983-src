# Uso: python3 -I tools/c571/k2l_xref.py src/projectg/X.cpp ... -> literal coreano cru no nosso cujo texto o 983 passa a K2L (00b4ec60); "K" = xref seguida de call K2L. Falso positivo: fragmento de concatenacao / K2L na linha anterior.
import re,sys,struct
d=open('ref/ProjectG_983_dump.exe','rb').read()
B=0x400000; K=0x00b4ec60
pat=re.compile(rb'"((?:[^"\\\n]|\\.)*)"')
def unesc(t): return re.sub(rb'\\x([0-9a-fA-F]{2})',lambda x:bytes([int(x.group(1),16)]),t).replace(b"\\\\",b"\\").replace(b"\\n",b"\n")
def k2l_after(va):
    r=[];key=struct.pack('<I',va);i=d.find(key)
    while i>=0:
        w=d[i+4:i+24]; hit=False
        for j in range(len(w)-4):
            if w[j]==0xe8:
                tgt=B+i+4+j+5+struct.unpack('<i',w[j+1:j+5])[0]
                if tgt==K: hit=True
                break
        r.append((B+i-1,hit)); i=d.find(key,i+1)
    return r
for f in sys.argv[1:]:
    for n,l in enumerate(open(f,'rb').read().split(b'\n'),1):
        if l.lstrip().startswith(b'//') or b'K2L_' in l or b'Translate983' in l: continue
        for m in pat.finditer(l):
            raw=unesc(m.group(1))
            if not re.search(rb'[\xb0-\xc8][\xa1-\xfe]',raw): continue
            # find full string (nul-terminated, starting at aligned pos) containing raw
            i=d.find(raw)
            if i<0: continue
            s=i
            while s>0 and d[s-1]!=0: s-=1
            xs=k2l_after(B+s)
            if any(h for _,h in xs): print(f.split('/')[-1],n,hex(B+s),['%x%s'%(a,'K' if h else '') for a,h in xs][:4],raw[:40].decode('cp949','replace'))
