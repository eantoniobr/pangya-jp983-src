#!/usr/bin/env python3
# callers.py VA... — quem chama (E8/E9 rel32) ou cita (imediato de 4 bytes) cada VA no dump do 983
import sys, struct
d = open('/root/jp983src/ref/ProjectG_983_dump.exe','rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe+6)[0]
oh = pe+24; base = struct.unpack_from('<I', d, oh+28)[0]; st = oh+struct.unpack_from('<H', d, pe+20)[0]
secs = [struct.unpack_from('<IIII', d, st+40*i+8) for i in range(ns)]
vs, v, rs, ro = secs[0]
code = d[ro:ro+max(vs,rs)]; cb = base+v
for a in sys.argv[1:]:
    t = int(a,16); out=[]
    for i in range(len(code)-5):
        if code[i] in (0xe8,0xe9) and (cb+i+5+struct.unpack_from('<i',code,i+1)[0])&0xffffffff==t: out.append('%08x%s'%(cb+i,'j' if code[i]==0xe9 else ''))
    imm = struct.pack('<I',t); j=-1; cit=[]
    while True:
        j = d.find(imm, j+1)
        if j<0: break
        cit.append('@%x'%j)
    print(a, 'calls:', ' '.join(out[:30]), len(out), '| cita(off arq):', ' '.join(cit[:8]), len(cit))
