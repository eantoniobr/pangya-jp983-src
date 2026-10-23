#!/usr/bin/env python3
"""pkt/pid.py — frente C, lote 12: mensagens de erro que levam o id do pacote como 1º parâmetro (M983(0x228)/M983(0x23f)/0x29d/
0x2a6/0x2ba) com um id diferente do rótulo `case` em volta (sinal de id do KR 645 que escapou da renumeração). Marca "<<";
caso PKT645_SEM_983 é cópia/rótulo morto, "None" = fora de despachante (ex.: cópia __declspec(naked)). Conferir no 983 antes de mexer
(o 0x14b do OnPacketCommon manda 0x147 de verdade)."""
import re,glob
pat=re.compile(r'(M983\(0x228\)|M983\(0x23f\)|M983\(0x210\)|0x29d|0x2a6|0x2ba)\s*,\s*(0x[0-9a-f]+)\b')
for f in sorted(glob.glob(__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))))+'/src/projectg/*.cpp')):
    s=open(f,encoding='latin-1').read()
    if not pat.search(s): continue
    case=None; lines=s.splitlines()
    for i,l in enumerate(lines):
        m=re.match(r'\s*case (0x[0-9a-f]+|PKT645_SEM_983\(0x[0-9a-f]+\))\s*:',l)
        if m and l.startswith('\tcase') : case=m.group(1)
        for m2 in pat.finditer(l):
            p=m2.group(2)
            flag='' if (case and p==case) else '<<'
            print('%s:%d\t%s\t%s %s\t%s'%(f.split('/')[-1],i+1,case,m2.group(1),p,flag))
