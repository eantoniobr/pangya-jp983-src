# pestr.py EXE VA... — string C (cp949) num VA do exe (sem pefile) (C446)
import struct,sys
d=open(sys.argv[1],'rb').read()
pe=struct.unpack_from('<I',d,0x3c)[0]; ns=struct.unpack_from('<H',d,pe+6)[0]; oh=struct.unpack_from('<H',d,pe+20)[0]
base=struct.unpack_from('<I',d,pe+24+28)[0]; st=pe+24+oh
secs=[struct.unpack_from('<8sIIII',d,st+40*i) for i in range(ns)]
def rd(va):
    r=va-base
    for n,vs,vaa,rs,rp in secs:
        if vaa<=r<vaa+max(vs,rs): o=rp+r-vaa; return d[o:d.index(b'\0',o)]
for a in sys.argv[2:]:
    s=rd(int(a,16)); print(a,s.hex().upper(),s.decode('cp949','replace'))
