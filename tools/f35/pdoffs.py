#!/usr/bin/env python3
"""pdoffs.py [--aplica] [--ref ARQ_645] ARQ... — troca deslocamentos crus do KR 645 no sPlayerData (0xb98 no 645, 0xdb0 no 983)
pelo layout do 983 (sessão 96). Mesma regra do golfdocoffs/shareddocoffs: só linhas iguais às do fonte do 645 (M983(x) lido como x;
GOLFDOC()->m_x e Doc()->m_x já trocados pelas s94/s95 contam como iguais se o resto bate); linha nova sai em "fora".
Tabelas: tools/f35/achata.py 645|983 sPlayerData (out/F3.5/s96/tabelas/splayerdata_{645,983}.txt): folha do 645 → caminho → 983.
Formas (só o número muda; nome de membro fica para quem reescrever a função):
  CGM_CUR_ULONG/CGM_CUR_UCHAR/CURPLAYER_ULONG/CURPLAYER_UCHAR(off), GR_PD_ULONG(p, off), PlayerByte(p, off) (fontinfo)
  (char*)/(unsigned char*)PLAYER(...) + off, (char*)V + off e ((unsigned char*)V)[off] com V declarado sPlayerData* na função.
Folha com caminho diferente (array que mudou de tamanho etc.) ou fora de folha → "sem"."""
import re, sys, os, bisect
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T = ROOT + '/out/F3.5/s96/tabelas/splayerdata_%s.txt'
def load(f):
    L = []
    for l in open(f):
        p = l.split()
        if len(p) == 4 and p[0].startswith('0x'): L.append((int(p[0], 16), int(p[1]), p[2], p[3].replace('_', ' ')))
    return L
A = load(T % '645'); B = load(T % '983'); BD = {c: (o, t, ti) for o, t, c, ti in B}; AO = [f[0] for f in A]
def novo(x):
    i = bisect.bisect_right(AO, x) - 1
    while i >= 0 and not (A[i][0] <= x < A[i][0] + max(A[i][1], 1)) and A[i][0] >= x - 0x40: i -= 1
    if i < 0 or not (A[i][0] <= x < A[i][0] + max(A[i][1], 1)): return None, 'fora_de_folha'
    o, t, c, ti = A[i]
    if c not in BD: return None, 'saiu:' + c
    bo, bt, bti = BD[c]
    if x - o >= max(bt, 1): return None, 'tam:' + c
    return bo + x - o, c

a = sys.argv[1:]; ap = '--aplica' in a; a = [x for x in a if x != '--aplica']
ref = None
if '--ref' in a: i = a.index('--ref'); ref = a[i + 1]; del a[i:i + 2]
NORM = lambda l: re.sub(r'M983\((0x[0-9a-f]+|\d+)\)', r'\1', l.strip())
NUM = r'(0x[0-9a-f]+|\d+)'
# o que as s94–s96 já trocaram na linha (CGolfDoc/CSharedDoc por membro ou número do 983; this do CGolfRule pelo thisoffs.py)
GD = re.compile(r'(?:GOLFDOC|Doc)\(\)->[\w.]+(?:\[[^\]]*\])?(?:\.[\w.]+)?|(?:GOLFDOC|SHAREDDOC)_\w+\((?:0x[0-9a-f]+|\d+)\)|'
                r'\((?:unsigned )?char ?\*\) ?(?:GOLFDOC|Doc)\(\) \+ (?:0x[0-9a-f]+|\d+)|\b(?:GR|DBG)_[A-Z0-9_]+\((?:0x[0-9a-f]+|\d+)|'
                r'\((?:unsigned )?char ?\*\)this \+ (?:0x[0-9a-f]+|\d+)|GR_WND_S\(\w+')
NORM2 = lambda l: GD.sub('@', NORM(l))
P1 = re.compile(r'\b((?:CGM_CUR|CURPLAYER)_(?:ULONG|UCHAR)\()' + NUM + r'\)')
P2 = re.compile(r'\b(GR_PD_ULONG\((PLAYER\((?:[^()]|\([^()]*(?:\([^()]*\))*[^()]*\))*\)), )' + NUM + r'\)')  # s96: só com PLAYER(...) (pre0/cur são sExpected da bola)
P3 = re.compile(r'(\((?:unsigned )?char ?\*\) ?PLAYER\((?:[^()]|\([^()]*(?:\([^()]*\))*[^()]*\))*\) \+ )' + NUM + r'\b')
P4 = re.compile(r'(\bPlayerByte\(.*?, )' + NUM + r'\)')  # fontinfo: PlayerByte(player, off)
FD = re.compile(r'^[A-Za-z_][\w\s\*&:<>,]*?\b(\w+)::(~?\w+)\s*\(')
DV = re.compile(r'\bsPlayerData\s*\*\s*(?:const\s+)?(\w+)\s*[=;,)]')
TOT = {'trocas': 0}
for fn in a:
    rf = ref or '/root/rebang/source/client/ProjectG/' + os.path.basename(fn)
    L645 = set(NORM(l) for l in open(rf, encoding='latin-1')); L645b = set(NORM2(l) for l in open(rf, encoding='latin-1'))
    linhas = open(fn, encoding='latin-1').read().split('\n'); vs = set(); sem = []; fora = []; nt = 0; usos = []
    for k, l in enumerate(linhas):
        if FD.match(l) and not l.rstrip().endswith(';'): vs = set()
        vs |= set(DV.findall(l))
        pats = [P1, P2, P3, P4]
        if vs:
            alt = '|'.join(sorted(vs))
            pats += [re.compile(r'(\((?:unsigned )?char ?\*\) ?(?:%s) \+ )' % alt + NUM + r'\b'),
                     re.compile(r'(\(\((?:unsigned )?char ?\*\) ?(?:%s)\)\[)' % alt + NUM + r'\]')]
        if '#define' in l or not any(p.search(l) for p in pats): continue
        if NORM(l) not in L645 and NORM2(l) not in L645b: fora.append((k + 1, l.strip())); continue
        def rep(m):
            global nt
            if m.re is P2: return rep2(m)
            o = int(m.group(2), 0); n, c = novo(o)
            if n is None: sem.append((k + 1, m.group(0), c)); return m.group(0)
            usos.append((o, n, c))
            if n == o: return m.group(0)
            nt += 1; s = m.group(0); return m.group(1) + '0x%x' % n + s[len(m.group(1)) + len(m.group(2)):]
        def rep2(m):  # GR_PD_ULONG(PLAYER(...), off): grupos 1 (prefixo), 3 (número)
            global nt
            o = int(m.group(3), 0); n, c = novo(o)
            if n is None: sem.append((k + 1, m.group(0), c)); return m.group(0)
            usos.append((o, n, c)); nt += n != o
            return m.group(1) + '0x%x)' % n
        for p in pats: l = p.sub(rep, l)
        linhas[k] = l
    TOT['trocas'] += nt
    print('== %s: trocas %d; sem regra %d; fora %d' % (fn, nt, len(sem), len(fora)))
    for o, n, c in sorted(set(usos)): print('uso\t%#x\t%#x\t%s' % (o, n, c))
    for x in sem: print('sem\t%d\t%s\t%s' % x)
    for x in fora: print('fora\t%d\t%s' % x)
    if ap: open(fn, 'w', encoding='latin-1', newline='').write('\n'.join(linhas))
print('total trocas', TOT['trocas'])
