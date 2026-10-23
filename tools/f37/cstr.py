import struct,sys
d=open('/root/jp983src/ref/ProjectG_983_dump.exe','rb').read()
pe=struct.unpack_from('<I',d,0x3c)[0];ns=struct.unpack_from('<H',d,pe+6)[0];oh=pe+24;base=struct.unpack_from('<I',d,oh+28)[0];st=oh+struct.unpack_from('<H',d,pe+20)[0]
secs=[struct.unpack_from('<IIII',d,st+40*i+8) for i in range(ns)]
def off(va):
  r=va-base
  for vs,v,rs,ro in secs:
    if v<=r<v+max(vs,rs): return ro+r-v
for a in sys.argv[1:]:
  o=off(int(a,16)); s=d[o:o+2000].split(b'\0')[0]
  print(a, '"'+''.join(chr(c) if 32<=c<127 and c not in (92,34) else '\\%03o'%c for c in s)+'"')
