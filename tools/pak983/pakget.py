import sys,struct,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from paklist import lst
SEC=[0xff21,0x834f,0x675f,0x34,0xf237,0x815f,0x4765,0x233]
def lz(src,n,v2):
    out=bytearray();i=0
    while len(out)<n and i<len(src):
        raw=src[i];i+=1;d1=raw^0xc8 if v2 else raw
        for _ in range(8):
            if len(out)>=n: break
            if d1&1:
                d2=struct.unpack_from('<H',src,i)[0];i+=2
                if v2:d2^=SEC[(raw>>3)&7]
                l=(d2>>12)+2;p=len(out)-(d2&0xfff)
                for k in range(l): out.append(out[p+k])
            else:
                out.append(src[i]);i+=1
            d1>>=1
    return bytes(out[:n])
def get(pak,name):
    d=None
    for fn,t,off,ps,sz in lst(pak):
        if fn.lower()==name.lower():
            d=open(pak,'rb').read()[off:off+ps]
            return {0:lambda:d,1:lambda:lz(d,sz,0),3:lambda:lz(d,sz,1)}[t&0xf]()
if __name__=='__main__':
    sys.stdout.buffer.write(get(sys.argv[1],sys.argv[2]))
