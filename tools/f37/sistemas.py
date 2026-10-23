#!/usr/bin/env python3
"""f37/sistemas — agrupa out/F3.7/s1/unidades_novas.tsv em sistemas (tabela de padrões abaixo, 1º que casar) e confere
a ordem de link: (a) inicializadores estáticos × endereço dos handlers; (b) ordem alfabética dos nomes de arquivo.
Uso: tools/f37/sistemas.py out/F3.7/s1"""
import sys, os, csv, re, collections
D = sys.argv[1]
PAD = [
 ('controladores', r'controller|controlledobject|object\.cpp|combogauge|conditionalaux|automiracle|balldirnotify|groundinclination|losslesshit|pangya(add)?correction|windimpact|plusyard|safetyitem|powershotitem|seteffect|setability|trajectorypreview|winddirection|windvolume|clubsetexpmultiply|classicwind|mtrand'),
 ('grandprix', r'grandprix|gproom|gptype'),
 ('clubset_workshop', r'clubset|workshop(?!event)'),
 ('dados_de_jogo_GD', r'^jp/gd|gamedata|gamestringmanager|extraresource|contentsdata'),
 ('holeinone', r'holeinone'),
 ('clima', r'weather'),
 ('lobby_atores', r'lobbycaddie|lobbyitems|lobbymascot|lobbyplayer|lobbyavatar|dummyp|avatarbase|aiplayer'),
 ('salas_lobby', r'room|holeselector|singlemode|singletype|myroomwidget|lobbymain'),
 ('ui_base', r'formbase|taskform|taskwidget|uiframeset|frameset|namedpoint|namedrect|nameddim|elem\.cpp|dim\.cpp|font|tutor|icon|desc'),
 ('selfdesign', r'selfdesign|kcsplit|kcleaf|kmdata|kmcenters|kmfilter|commoditylist'),
 ('arin2014_eventos', r'arin|workshopevent|workshop2013|rf2014|specialbox'),
 ('cartas_alquimia', r'cardcompose|alchemy|mpbreak|itemcount'),
 ('quests_presenca', r'oneday|achievement|ahievement|attendance|quest'),
 ('lojas_pontos', r'pointshop|shopwi|refresh|scratch|fortune|checkout'),
 ('campeonato', r'champ|match'),
 ('guilda_social', r'guild|chat|avatarmotion|tiki|post_'),
 ('regra_subregra', r'golfrule|subgolfrule|shottrajectory|holecup|holeinfo|golfball'),
 ('fx', r'fxinterpreter|pvsfx'),
 ('rede_web', r'inet|webpage|packet'),
 ('rf_dialogos', r'^jp/rf|mastery'),
]
U = list(csv.DictReader(open(os.path.join(D, 'unidades_novas.tsv')), delimiter='\t'))
S = collections.defaultdict(lambda: [0, 0, 0, 0, []])
for u in U:
    k = next((n for n, p in PAD if re.search(p, u['arquivo'] + ' ' + u['principal'].lower())), 'outros')
    if u['confianca'] == 'sem_classe' and k == 'outros':
        k = 'sem_classe'
    u['sistema'] = k
    e = S[k]; e[0] += 1; e[1] += int(u['bytes']); e[2] += int(u['funcs']); e[3] += int(u['novas_j7']); e[4].append(u['arquivo'][3:-4])
with open(os.path.join(D, 'sistemas.tsv'), 'w') as o:
    o.write('sistema\tunidades\tbytes\tfuncs\tnovas_j7\tarquivos\n')
    for k, e in sorted(S.items(), key=lambda x: -x[1][1]):
        o.write('%s\t%d\t%d\t%d\t%d\t%s\n' % (k, e[0], e[1], e[2], e[3], ' '.join(e[4])))
        print('%-20s %3d un %8d B %5d f  j7=%d' % (k, e[0], e[1], e[2], e[3]))
cols = list(U[0].keys())
with open(os.path.join(D, 'unidades_novas.tsv'), 'w') as o:
    o.write('\t'.join(cols) + '\n')
    for u in U:
        o.write('\t'.join(u[c] for c in cols) + '\n')
# (a) inicializadores × handlers
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ini = {}
for l in open(os.path.join(R, 'build', 'B', 'handlers.tsv')):
    h, c, i, m = l.split('\t'); h = int(h, 16); i = int(i, 16)
    ini[i] = min(ini.get(i, h), h)
seq = [ini[i] for i in sorted(ini)]
asc = sum(1 for a, b in zip(seq, seq[1:]) if b > a)
# (b) ordem alfabética entre vizinhas de confiança alta, por vão
al = tot = 0
by = collections.defaultdict(list)
for u in U:
    if u['confianca'] == 'alta':
        by[u['vao']].append(u['arquivo'])
for v, l in by.items():
    for a, b in zip(l, l[1:]):
        tot += 1; al += a <= b
with open(os.path.join(D, 'ordem_de_link.txt'), 'w') as o:
    for s in ('inicializadores de mapa de mensagens em ordem de endereço: %d; pares vizinhos em que o 1º handler também sobe: %d de %d (%.0f%%)'
              % (len(seq), asc, len(seq) - 1, 100.0 * asc / (len(seq) - 1)),
              'unidades de confiança alta vizinhas no mesmo vão em ordem alfabética do nome (sem Fr/C): %d de %d (%.0f%%)' % (al, tot, 100.0 * al / tot)):
        print(s); o.write(s + '\n')
