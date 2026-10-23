# rbutton_map.py EXE983 — entradas sFRESH_ENTRY do 983 com cmd RBUTTONDOWN(5)/RBUTTONUP(6): slot, handler, cmd, controle (C442).
# Entrada de 32 B: pmf 16 B gravado no arranque por "mov eax,h; mov [slot],eax"; slot = nome-0x10. "?" = eax vindo de mais longe.
import struct,sys,re
d=open(sys.argv[1],'rb').read(); B=0x400000
def s(v):
    o=v-B
    if not 0<o<len(d): return None
    e=d.find(b'\0',o,o+80); t=d[o:e]
    return t.decode('latin1') if e>o and all(32<=c<127 for c in t) else None
movs={}
for m in re.finditer(rb'\xb8(.{3}\x00)\xa3(.{3}\x00)',d[0x1000:0xb2b000],re.S):
    v,a=struct.unpack('<II',m.group(1)+m.group(2)); movs.setdefault(a,v)
for p in range(0xa00000,0xf00000,4):
    nm,cmd,ft=struct.unpack_from('<III',d,p)
    if cmd in (5,6) and 1<=ft<=6 and True:
        name=s(nm)
        if not name: continue
        loc=B+p-0x10
        print('%08x\t%s\t%s\t%s'%(loc, '%08x'%movs[loc] if loc in movs else '?', 'RDOWN' if cmd==5 else 'RUP', name))
