"""pe983.py — modulo: d (bytes do dump 983), secs, ib, o2va(off), findall(bytes) -> VAs, xref(va) -> VAs que citam va como dword."""
import struct,sys
d=open('/root/jp983src/ref/ProjectG_983_dump.exe','rb').read()
pe=struct.unpack_from('<I',d,0x3c)[0]
nsec=struct.unpack_from('<H',d,pe+6)[0]; opt=struct.unpack_from('<H',d,pe+20)[0]
ib=struct.unpack_from('<I',d,pe+52)[0]
secs=[]
for i in range(nsec):
    o=pe+24+opt+40*i
    vs,va,rs,ro=struct.unpack_from('<IIII',d,o+8);secs.append((va,vs,ro,rs))
def o2va(off):
    for va,vs,ro,rs in secs:
        if ro<=off<ro+rs: return ib+va+off-ro
def findall(b):
    r=[];i=d.find(b)
    while i>=0: r.append(o2va(i)); i=d.find(b,i+1)
    return r
def xref(va): return findall(struct.pack('<I',va))
