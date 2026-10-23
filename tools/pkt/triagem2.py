# triagem2.py: para cada caso so_983 do OnPacketCommon, desmonta o trecho do caso (dz.py) e diz quais funções chamadas
# já têm fonte (map/projectg.tsv, map/pkt_c.tsv, src/projectg/jp/jp.tsv) e quais não.
import subprocess, re, sys
R='/root/jp983src'
mapped={}
for f in ('map/projectg.tsv','map/pkt_c.tsv','src/projectg/jp/jp.tsv'):
    for l in open(f'{R}/{f}',encoding='utf-8',errors='replace'):
        c=l.rstrip('\n').split('\t')
        if len(c)>=2 and re.fullmatch(r'[0-9a-f]{8}',c[1]): mapped.setdefault(c[1],c[0])
casos=[]
for l in open(f'{R}/out/V4/pacotes_recebe_983.tsv'):
    c=l.rstrip('\n').split('\t')
    if c[0]=='009c20a0' and len(c)>=4 and c[3]: casos.append((c[2],c[3]))
vas=sorted(set(v for _,v in casos))
so=[l.split('\t')[1] for l in open(f'{R}/out/V4/rx_cmp.tsv') if l.startswith('CTask::OnPacketCommon') and '\tso_983' in l]
for i,v in casos:
    if i not in so: continue
    nx=[x for x in vas if x>v]; nx=nx[0] if nx else '%08x'%(int(v,16)+0x200)
    out=subprocess.run(['python3',f'{R}/tools/f37/dz.py',v,nx],capture_output=True,text=True).stdout
    tg=[]
    for m in re.finditer(r'call\s+0x([0-9a-f]+)(?:\s+;\s*(\S+))?',out):
        a=m.group(1).zfill(8)
        if a not in [t[0] for t in tg]: tg.append((a,m.group(2) or ''))
    falta=[f'{a}:{n}' for a,n in tg if a not in mapped and not n.startswith(('?','WReceived','WSend'))]
    tem=[mapped[a].split('@@')[0][:40] for a,n in tg if a in mapped]
    print(f'{i}\t{v}\tn={out.count(chr(10))}\tFALTA[{len(falta)}] '+' '.join(falta)+'\tTEM '+' '.join(tem))
