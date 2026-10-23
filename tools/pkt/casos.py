# casos.py id...: desmonta cada caso do OnPacketCommon do 983 (009c20a0) com os nomes do nosso mapa nas chamadas
import sys, re, subprocess
R='/root/jp983src'
n={}
for f in ('map/projectg.tsv','map/pkt_c.tsv','src/projectg/jp/jp.tsv'):
    for l in open(f'{R}/{f}',encoding='utf-8',errors='replace'):
        c=l.rstrip('\n').split('\t')
        if len(c)>=2 and re.fullmatch(r'[0-9a-f]{8}',c[1]): n.setdefault(c[1],c[0])
cs=[l.rstrip('\n').split('\t') for l in open(f'{R}/out/V4/pacotes_recebe_983.tsv')]
cs=[(c[2],c[3]) for c in cs if c[0]=='009c20a0' and len(c)>3 and c[3]]
vas=sorted(set(v for _,v in cs))
for i in sys.argv[1:]:
    v=[x for k,x in cs if k==i][0]; nx=[x for x in vas if x>v][0]
    print(f'=== {i} {v}..{nx}')
    out=subprocess.run(['python3',f'{R}/tools/f37/dz.py',v,nx],capture_output=True,text=True).stdout
    for l in out.splitlines():
        l=re.sub(r'  ; f=.*','',l)
        m=re.search(r'call\s+0x([0-9a-f]+)',l)
        if m and m.group(1).zfill(8) in n: l+='   <= '+n[m.group(1).zfill(8)]
        print(l)
