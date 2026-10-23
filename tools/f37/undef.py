# undef.py <obj> [hdr...] — externos não definidos do .obj que faltam no build/B/mapa.tsv; com cabeçalhos, propõe VA pelo "// VA"
import struct,sys,re
d=open(sys.argv[1],'rb').read()
nsec=struct.unpack_from('<H',d,2)[0]; symp,nsym=struct.unpack_from('<II',d,8)
strt=symp+nsym*18
und=set(); i=0
while i<nsym:
    o=symp+i*18; nm=d[o:o+8]
    if nm[:4]==b'\0\0\0\0':
        so=struct.unpack_from('<I',nm,4)[0]; name=d[strt+so:d.index(b'\0',strt+so)].decode('latin1')
    else: name=nm.rstrip(b'\0').decode('latin1')
    val,sec,typ,cls,aux=struct.unpack_from('<IhHBB',d,o+8)
    if sec==0 and cls==2: und.add(name)
    i+=1+aux
have=set(l.split('\t')[0] for l in open('/root/jp983src/build/B/mapa.tsv'))
miss=sorted(n for n in und if n not in have)
H={}
cls=None
for h in sys.argv[2:]:
    for l in open(h,encoding='utf-8',errors='replace'):
        m=re.match(r'\s*(?:class|struct)\s+(\w+)',l)
        if m and not l.rstrip().endswith(';'): cls=m.group(1)
        m=re.search(r'[\s*&~](~?\w+)\s*\([^;]*\)[^;]*;\s*//\s*([0-9a-f]{8})',l)
        if m and cls: H[(cls,m.group(1))]=m.group(2)
        m=re.match(r'\s*(?:const )?\w[\w\s\*]*?__fastcall\s+(\w+)\s*\(.*;\s*//\s*([0-9a-f]{8})',l)
        if m: H[('',m.group(1))]=m.group(2)
for n in miss:
    m=re.match(r'\?(\w+)@(\w+)@@',n); va=''
    if m: va=H.get((m.group(2),m.group(1)),'')
    m2=re.match(r'\?(\w+)@@Y',n)
    if m2: va=H.get(('',m2.group(1)),'')
    print(n+'\t'+va)
