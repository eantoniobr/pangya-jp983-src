#!/usr/bin/env python3
"""golfdocoffs.py [--aplica] [--ref ARQ_645] ARQ — troca deslocamentos crus do KR 645 no CGolfDoc pelo layout do 983 (s94).
Só mexe nas linhas que existem iguais (sem espaços nas pontas; M983(x) lido como x) no fonte do 645 (--ref; padrão: o mesmo nome em
/root/rebang/source/client/ProjectG/): linha nova (escrita para o 983 pela A/C) fica como está e sai na lista "fora".
Formas: GOLFDOC_{FLOAT,ULONG,UCHAR,U64}(off), *(T*)((char*)GOLFDOC() + off) / ((T*)((char*)GOLFDOC() + off)) e, só o
número, qualquer (char*)/(unsigned char*)GOLFDOC() + off (memcpy, *(char**), ...). NÃO trata macros com índice de jogador
(GOLFDOC() + jogador * 0x25 + off): sShotResultMsg tem 0x26 no 983 — ver a lista "indice" na saída.
Membro com nome quando o tipo do acesso é o do membro; senão só o número. Faixas 645 → 983 medidas pelo cabeçalho
(tools/f35/campos.py CGolfDoc) e pelo histograma de deslocamentos do 983 (0x189 jogador atual ×898, 0x17c buraco ×474,
0x88 tutorial ×157, 0x11c ângulo da câmera ×43): contêineres do VS2010 (+0x10 antes de m_modelNameList), m_unknown164
virou 2 dwords (+4), m_unused196 cresceu pelo alinhamento do __int64 (+4), m_unknown440 0x2e → 0x32 (+4), sShotResultMsg
0x25 → 0x26 (faixa 0x3ac..0x43f fica de fora)."""
import re, sys, os
FAIXAS = [(0x0, 0x14, 0), (0x58, 0x164, 0x10), (0x168, 0x196, 0x14), (0x198, 0x3ac, 0x18), (0x440, 0x46e, 0x1c),
          (0x46e, 0x8c0, 0x20)]
def novo(o):
    for a, b, d in FAIXAS:
        if a <= o < b: return o + d
    return None
# (deslocamento 645, tipo do acesso) -> membro do 983 com o mesmo tipo
MEMB = {(0xc5, 'UCHAR'): 'm_playerNum', (0xcc, 'UCHAR'): 'm_unknowncc', (0x148, 'ULONG'): 'm_gameMode',
        (0x14c, 'UCHAR'): 'm_unknown14c', (0x14e, 'UCHAR'): 'm_unknown14e', (0x158, 'UCHAR'): 'm_unknown158',
        (0x15a, 'UCHAR'): 'm_unknown15a', (0x168, 'UCHAR'): 'm_currentHole', (0x16c, 'ULONG'): 'm_remainTime',
        (0x170, 'ULONG'): 'm_shotTime', (0x174, 'UCHAR'): 'm_shotPhase', (0x175, 'UCHAR'): 'm_currentPlayer',
        (0x17e, 'UCHAR'): 'm_maxGrade', (0x1a8, 'ULONG'): 'm_unknown1a8', (0x1ac, 'UCHAR'): 'm_unknown1ac',
        (0xd0, 'FLOAT'): 'm_bar.power', (0xd4, 'FLOAT'): 'm_bar.impact', (0xd8, 'FLOAT'): 'm_bar.gauge',
        (0xdc, 'FLOAT'): 'm_bar.gaugeStep', (0xec, 'FLOAT'): 'm_bar.center', (0xf0, 'FLOAT'): 'm_bar.calipers',
        (0xf4, 'FLOAT'): 'm_cameraData.distance', (0xf8, 'FLOAT'): 'm_cameraData.height',
        (0xfc, 'FLOAT'): 'm_cameraData.clearance', (0x10c, 'FLOAT'): 'm_cameraData.angle',
        (0x110, 'FLOAT'): 'm_cameraData.angleOffset', (0x10, 'CAutoTarget*'): 'm_pAutoTarget',
        (0x7c, 'std::list<unsigned long>'): 'm_list7c', (0x78, 'int'): 'm_tutorialMode',
        (0x194, 'unsigned short'): 'm_unknown194', (0x18c, 'int'): 'm_unknown18c'}
TIPO = {'float': 'FLOAT', 'unsigned long': 'ULONG', 'unsigned char': 'UCHAR'}
a = sys.argv[1:]; ap = '--aplica' in a; a = [x for x in a if x != '--aplica']
ref = None
if '--ref' in a: i = a.index('--ref'); ref = a[i + 1]; del a[i:i + 2]
fn = a[0]; ref = ref or '/root/rebang/source/client/ProjectG/' + os.path.basename(fn)
NORM = lambda l: re.sub(r'M983\((0x[0-9a-f]+|\d+)\)', r'\1', l.strip())  # M983(id do 645) conta como a linha do 645
L645 = set(NORM(l) for l in open(ref, encoding='latin-1'))
P1 = re.compile(r'GOLFDOC_(FLOAT|ULONG|UCHAR|U64)\((0x[0-9a-f]+)\)')
P2 = re.compile(r'(\*?)\(\(?([\w:<> ]+?)\s*\*\)\(\(char\*\)GOLFDOC\(\) \+ (0x[0-9a-f]+)\)\)?')
# s95: invólucros locais com o deslocamento como argumento (fontinfo GolfInt/GolfByte/GolfDocFloat, helpmsg GOLFDOC_BYTE,
# golfplayer/tutorial GOLFDOC_FIELD(tipo, off)): só o número
P4 = re.compile(r'\b(GolfInt|GolfByte|GolfDocFloat|GOLFDOC_BYTE)\((0x[0-9a-f]+|\d+)\)')
P5 = re.compile(r'\b(GOLFDOC_FIELD\([\w:<> *]+, )(0x[0-9a-f]+|\d+)\)')
P3 = re.compile(r'(\((?:unsigned )?char\*\)GOLFDOC\(\) \+ )(0x[0-9a-f]+|\d+)\b')  # o resto: só o número
linhas = open(fn, encoding='latin-1').read().split('\n')
nt = nm = 0; fora = []; sem = []
for k, l in enumerate(linhas):
    if '#define' in l or ('GOLFDOC_' not in l and 'GOLFDOC() +' not in l and not P4.search(l)): continue
    if NORM(l) not in L645:
        if P1.search(l) or P2.search(l): fora.append((k + 1, l.strip()))
        continue
    def r1(m):
        global nt, nm
        t, o = m.group(1), int(m.group(2), 16); n = novo(o)
        if n is None: sem.append((k + 1, m.group(0))); return m.group(0)
        nt += 1
        if (o, t) in MEMB: nm += 1; return 'GOLFDOC()->' + MEMB[(o, t)]
        return 'GOLFDOC_%s(0x%x)' % (t, n)
    def r2(m):
        global nt, nm
        st, t, o = m.group(1), m.group(2).strip(), int(m.group(3), 16); n = novo(o)
        if n is None: sem.append((k + 1, m.group(0))); return m.group(0)
        nt += 1; tt = TIPO.get(t, t)
        full = m.group(0)
        if (o, tt) in MEMB and st == '*' and full.startswith('*(') :
            nm += 1; return 'GOLFDOC()->' + MEMB[(o, tt)]
        if (o, tt) in MEMB and st == '' and full.startswith('((') and full.endswith('))'):
            nm += 1; return '(&GOLFDOC()->' + MEMB[(o, tt)] + ')'
        return full.replace('+ 0x%x)' % o, '+ 0x%x)' % n).replace('GOLFDOC()', 'GOLFDOC\x01()')
    def r3(m):
        global nt
        o = int(m.group(2), 0); n = novo(o)
        if n is None: sem.append((k + 1, m.group(0))); return m.group(0)
        if n == o: return m.group(0)
        nt += 1; return m.group(1) + '0x%x' % n
    def r4(m):
        global nt
        o = int(m.group(2), 0); n = novo(o)
        if n is None: sem.append((k + 1, m.group(0))); return m.group(0)
        if n == o: return m.group(0)
        nt += 1; return '%s(0x%x)' % (m.group(1), n)
    def r5(m):
        global nt
        o = int(m.group(2), 0); n = novo(o)
        if n is None: sem.append((k + 1, m.group(0))); return m.group(0)
        if n == o: return m.group(0)
        nt += 1; return '%s0x%x)' % (m.group(1), n)
    l2 = P3.sub(r3, P2.sub(r2, P1.sub(r1, l))).replace('GOLFDOC\x01()', 'GOLFDOC()')
    l2 = P5.sub(r5, P4.sub(r4, l2))
    if l2 != l: linhas[k] = l2
for k, l in enumerate(linhas):
    if re.search(r'GOLFDOC\(\) \+ [^0-9(]', l): sem.append((k + 1, 'indice: ' + l.strip()[:140]))
print('%s: %d trocas (%d por membro); %d fora do 645 (não mexidas); %d sem faixa' % (fn, nt, nm, len(fora), len(sem)))
for k, s in fora: print('fora\t%d\t%s' % (k, s[:150]))
for k, s in sem: print('sem_faixa\t%d\t%s' % (k, s))
if ap: open(fn, 'w', encoding='latin-1', newline='').write('\n'.join(linhas))
