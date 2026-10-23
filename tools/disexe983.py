#!/usr/bin/env python3
# disexe983.py VA:len ... — desmonta o exe 983 (ref/ProjectG_983_dump.exe); rodar com python3 -I (um /tmp/dis.py velho quebra o capstone)
import sys,struct,capstone
d=open('/root/jp983src/ref/ProjectG_983_dump.exe','rb').read()
pe=struct.unpack_from('<I',d,0x3c)[0];ns=struct.unpack_from('<H',d,pe+6)[0]
oh=pe+24;base=struct.unpack_from('<I',d,oh+28)[0];st=oh+struct.unpack_from('<H',d,pe+20)[0]
secs=[struct.unpack_from('<IIII',d,st+40*i+8) for i in range(ns)]
def off(va):
    r=va-base
    for vs,v,rs,ro in secs:
        if v<=r<v+max(vs,rs): return ro+r-v
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
for a in sys.argv[1:]:
    va,n=a.split(':');va=int(va,16);n=int(n)
    print('##',hex(va))
    for i in md.disasm(d[off(va):off(va)+n],va): print(hex(i.address),i.mnemonic,i.op_str)
