#!/usr/bin/env python3
# C184: endereço da exceção de um exception.dmp do robô (stream 6 do minidump). Uso: tools/v6/dmpaddr.py out/F4/resultados/ID/exception.dmp ...
import struct,sys
for p in sys.argv[1:]:
    b=open(p,'rb').read()
    n,rva=struct.unpack_from('<II',b,8)
    for i in range(n):
        t,sz,r=struct.unpack_from('<III',b,rva+12*i)
        if t==6:
            code,fl,rec,addr=struct.unpack_from('<IIQQ',b,r+8)
            print(p,hex(code),hex(addr))
