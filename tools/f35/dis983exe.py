#!/usr/bin/env python3
"""dis983exe.py VA [n_bytes] — desmonta o ProjectG 983 (ref/ProjectG_983_dump.exe) a partir de VA, até o primeiro ret."""
import sys,struct,capstone
d=open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', 'ref', 'ProjectG_983_dump.exe'),'rb').read()
pe=struct.unpack_from('<I',d,0x3c)[0];ns=struct.unpack_from('<H',d,pe+6)[0];oh=pe+24;base=struct.unpack_from('<I',d,oh+28)[0];st=oh+struct.unpack_from('<H',d,pe+20)[0]
secs=[struct.unpack_from('<IIII',d,st+40*i+8) for i in range(ns)]
def off(va):
  r=va-base
  for vs,v,rs,ro in secs:
    if v<=r<v+max(vs,rs): return ro+r-v
va=int(sys.argv[1],16);n=int(sys.argv[2],0) if len(sys.argv)>2 else 256
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
for i in md.disasm(d[off(va):off(va)+n],va):
  print('%x %s %s'%(i.address,i.mnemonic,i.op_str))
  if i.mnemonic=='ret': break
