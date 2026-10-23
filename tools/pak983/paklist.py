import struct,sys,os
K=(0x020a5fd4,0x01eebdff,0x02b3c6a0,0x04f6a3e1);D=0x9e3779b9;M=0xffffffff
def dec(a,b):
    s=(D*16)&M
    for _ in range(16):
        b=(b-((((a<<4)^(a>>5))+a)^(s+K[(s>>11)&3])))&M; s=(s-D)&M
        a=(a-((((b<<4)^(b>>5))+b)^(s+K[s&3])))&M
    return a,b
def lst(p):
    d=open(p,'rb').read()
    names,num=struct.unpack_from('<ii',d,len(d)-9)
    o=names;r=[]
    for i in range(num):
        nl=d[o];t=d[o+1];o+=2
        if t&0xf0==0:t|=0x10
        off,ps,sz=struct.unpack_from('<iii',d,o);o+=12
        if t&0xf0==0x20:
            fn=bytearray(d[o:o+nl]);o+=nl
            off,sz=dec(off&M,sz&M)
            for b in range(0,nl,8):
                x,y=struct.unpack_from('<II',fn,b);fn[b:b+8]=struct.pack('<II',*dec(x,y))
            fn=bytes(fn).split(b'\0')[0]
        elif t&0xf0==0x10:
            fn=bytes(c^0x71 for c in d[o:o+nl]);o+=nl+1;sz^=0x71
        else:
            fn=d[o:o+nl];o+=nl+1
        r.append((fn.decode('cp949','replace'),t,off,ps,sz))
    return r
if __name__=='__main__':
    for p in sys.argv[1:]:
        for fn,t,off,ps,sz in lst(p): print('%s\t%s\t%02x\t%d\t%d\t%d'%(os.path.basename(p),fn,t,off,ps,sz))
