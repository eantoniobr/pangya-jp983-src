import struct,sys,re,subprocess
d=open('ref/ProjectG_983_dump.exe','rb').read()
pe=struct.unpack_from('<I',d,0x3c)[0]; n=struct.unpack_from('<H',d,pe+6)[0]; opt=struct.unpack_from('<H',d,pe+20)[0]; ib=struct.unpack_from('<I',d,pe+52)[0]
secs=[struct.unpack_from('<8sIIII',d,pe+24+opt+i*40) for i in range(n)]
def rd(va,k):
  for nm,vs,vaa,rs,rp in secs:
    if vaa<=va-ib<vaa+max(vs,rs): o=rp+va-ib-vaa; return d[o:o+k]
for a in sys.argv[1:]:
  va,ln=a.split(':'); va=int(va,16); ln=int(ln,16)
  open('/tmp/f.bin','wb').write(rd(va,ln))
  out=subprocess.run(['objdump','-D','-b','binary','-mi386','--adjust-vma=%#x'%va,'/tmp/f.bin'],capture_output=True,text=True).stdout
  print('==',hex(va))
  for l in out.splitlines():
    m=re.search(r'(fld[sl]|fmul[sl]|fadd[sl]|fsub[sl]|fsubr[sl]|fdiv[sl]|fdivr[sl]|fcomp?[sl])\s+0x([0-9a-f]{6,})$',l)
    if m:
      op,ad=m.group(1),int(m.group(2),16); b=rd(ad,8)
      if b is None: continue
      v=struct.unpack('<d',b)[0] if op.endswith('l') else struct.unpack('<f',b[:4])[0]
      print(l.split(':')[0].strip(), op, hex(ad), repr(v))
