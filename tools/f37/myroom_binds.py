#!/usr/bin/env python3
"""myroom_binds.py MAP.txt INITS.txt — tabela dos handlers INIT (cmd 1) do msgmap 00e1347c (CRealMyRoomMain 983):
controle, VA, deslocamento do campo gravado (param_1+off), RTTI do tipo, 'hide' (SetVisible(0)), corpo. MAP = saida de
msgmap983.py 00e1347c; INITS = saida de dec.sh dos VAs cmd 1. (B340)"""
import re, sys
mp = {}
for l in open(sys.argv[1], encoding='latin1'):
    p = l.rstrip('\n').split('\t')
    if len(p) >= 5 and p[2] == '0x1':
        mp.setdefault(p[4], []).append(p[1])
t = open(sys.argv[2], encoding='latin1').read()
print('va\tcontroles\toff\trtti\tacao\tcorpo')
for b in re.split(r'^#### ', t, flags=re.M)[1:]:
    va = b[:8]; corpo = int(re.search(r'corpo=(\d+)', b).group(1))
    m = re.search(r'\(param_1 \+ (0x[0-9a-f]+|\d+)\) = (?:param_2|-\(uint\)\w+ & \(uint\)param_2)', b)
    off = '-'
    if m:
        off = '0x%x' % int(m.group(1), 0)
    r = re.search(r'== &?(DAT_[0-9a-f]+)', b)
    hide = '(0);' in b and '+ 0x1c))(0)' in b
    acao = 'bind' if off != '-' else ('hide' if hide else 'logica')
    if corpo > 140 and off != '-': acao = 'bind+logica'
    print('%s\t%s\t%s\t%s\t%s\t%d' % (va, ','.join(mp.get(va, [])), off, r.group(1) if r else '-', acao, corpo))
