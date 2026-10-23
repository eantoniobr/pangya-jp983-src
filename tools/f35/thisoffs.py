#!/usr/bin/env python3
"""thisoffs.py [--aplica] [--ref ARQ_645] [--classe C] --t645 T[,T...] --t983 T[,T...] ARQ — troca deslocamentos crus do KR 645
relativos a `this` (GR_ULONG/GR_UCHAR/GR_FLOAT/GR_BYTE/GR_FLOAT2/GR_WND/GR_WND_SHOW/DBG_FLOAT(off) e (char*)this + off) pelo layout
do 983, só nos métodos da classe C (padrão CGolfRule) e só nas linhas iguais às do rebang (como golfdocoffs.py). Sessão 96.
Tabelas: saída do campos645.py (645) e do campos.py (983), base primeiro (ex.: ctaskmain_645.txt,cgolfrule_645.txt); a última
linha "sizeof" fecha o último campo. Regra: o deslocamento cai num campo f (maior início <= off); d = off - início.
  - f existe no 983 e tem o mesmo tamanho nos dois → início983 + d;
  - tamanho diferente → só d == 0 (início983); senão "sem" (lista para fazer à mão);
  - f não existe no 983 (saiu, ou virou static) → "sem";
  - off abaixo do 1º campo das tabelas (vptr/bases) → igual.
--valida: para cada função, desmonta o par do 983 (map/projectg_funcs.tsv, nome645 → f983) e conta se o deslocamento novo
aparece como [reg + disp] nela (e se o velho aparece) — confirmação estatística, não prova."""
import re, sys, os, collections
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
a = sys.argv[1:]
def opt(n, d=None):
    if n in a: i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return v
    return d
def flag(n):
    if n in a: a.remove(n); return True
    return False
ap = flag('--aplica'); val = flag('--valida'); cls = opt('--classe', 'CGolfRule')
EXTRA = {}
ex = opt('--extra')
if ex:  # off645 off983|sym:membro [comentário] — medido à mão no 983 (vence a regra das tabelas)
    for l in open(ex):
        p = l.split('#')[0].split()
        if len(p) >= 2: EXTRA[int(p[0], 16)] = p[1] if p[1].startswith('sym:') else int(p[1], 16)
ref = opt('--ref'); t645 = opt('--t645'); t983 = opt('--t983'); fn = a[0]
ref = ref or '/root/rebang/source/client/ProjectG/' + os.path.basename(fn)

def tabela(arqs):
    campos = {}; fim = 0
    for p in arqs.split(','):
        for l in open(p):
            o, n = l.split()[:2]; o = int(o, 16)
            if n == 'sizeof': fim = o
            else: campos[n] = o
    ordem = sorted(campos.items(), key=lambda x: x[1]); tam = {}
    for i, (n, o) in enumerate(ordem):
        tam[n] = (ordem[i + 1][1] if i + 1 < len(ordem) else fim) - o
    return campos, ordem, tam
C5, O5, T5 = tabela(t645); C9, O9, T9 = tabela(t983)
def novo(o):
    if o in EXTRA: return EXTRA[o], 'extra'
    if o < O5[0][1]: return o, None
    f = None
    for n, s in O5:
        if s <= o: f = n
        else: break
    d = o - C5[f]
    if d >= T5[f]: return None, 'fora_do_objeto'
    if f not in C9: return None, 'saiu:' + f
    if T5[f] != T9[f] and d: return None, 'tam:%s+%#x(%#x->%#x)' % (f, d, T5[f], T9[f])
    return C9[f] + d, f

NORM = lambda l: re.sub(r'M983\((0x[0-9a-f]+|\d+)\)', r'\1', l.strip())
# linhas que as s94/s95 já trocaram (CGolfDoc/CSharedDoc por membro ou por número do 983): o resto ainda é do 645
GD = re.compile(r'(?:GOLFDOC|Doc)\(\)->[\w.]+(?:\[[^\]]*\])?(?:\.[\w.]+)?|(?:GOLFDOC|SHAREDDOC)_\w+\((?:0x[0-9a-f]+|\d+)\)|'
                r'\((?:unsigned )?char ?\*\) ?(?:GOLFDOC|Doc)\(\) \+ (?:0x[0-9a-f]+|\d+)')
NORM2 = lambda l: GD.sub('@', NORM(l))
L645 = set(NORM(l) for l in open(ref, encoding='latin-1')); L645b = set(NORM2(l) for l in open(ref, encoding='latin-1'))
igual645 = lambda l: NORM(l) in L645 or NORM2(l) in L645b
P1 = re.compile(r'\b(GR_ULONG|GR_UCHAR|GR_FLOAT|GR_BYTE|GR_FLOAT2|GR_WND_SHOW|GR_WND|DBG_FLOAT)\((0x[0-9a-f]+|\d+)\b')
P2 = re.compile(r'(\((?:unsigned )?char ?\*\)this \+ )(0x[0-9a-f]+|\d+)\b')
FD = re.compile(r'^[A-Za-z_][\w\s\*&:<>,]*?\b(\w+)::(~?\w+)\s*\(')
linhas = open(fn, encoding='latin-1').read().split('\n')
cur = fun = None; nt = 0; sem = []; fora = []; usos = collections.defaultdict(list)  # fun -> [(velho, novo)]
for k, l in enumerate(linhas):
    m = FD.match(l)
    if m and not l.rstrip().endswith(';'): cur, fun = m.group(1), m.group(1) + '::' + m.group(2)
    if '#define' in l or cur != cls or not (P1.search(l) or P2.search(l)): continue
    if not igual645(l): fora.append((k + 1, l.strip())); continue
    def rep(m, pre):
        global nt
        o = int(m.group(2), 0); n, f = novo(o)
        if n is None: sem.append((k + 1, fun, m.group(0), f)); return m.group(0)
        if isinstance(n, str):  # membro que saiu do objeto no 983 (estático provisório): pelo endereço dele
            if m.group(1) == 'GR_WND': nt += 1; return 'GR_WND_S(' + n[4:]
            if not pre: nt += 1; return '(char*)&' + n[4:]
            sem.append((k + 1, fun, m.group(0), 'sym')); return m.group(0)
        usos[fun].append((o, n))
        if n == o: return m.group(0)
        nt += 1; return (m.group(1) + '(' if pre else m.group(1)) + '0x%x' % n
    l2 = P1.sub(lambda m: rep(m, True), l)
    l2 = P2.sub(lambda m: rep(m, False), l2)
    linhas[k] = l2
print('trocas: %d; sem regra: %d; linhas novas (fora do 645, não tocadas): %d' % (nt, len(sem), len(fora)))
for x in sem: print('sem\t%d\t%s\t%s\t%s' % x)
for x in fora: print('fora\t%d\t%s' % x)
if val:
    sys.path.insert(0, R + '/tools/f37'); import subprocess
    par = {}
    for l in open(R + '/map/projectg_funcs.tsv'):
        c = l.rstrip('\n').split('\t')
        if len(c) > 6 and c[6] and c[2] == 'nucleo': par.setdefault(c[6], (int(c[0], 16), int(c[1])))
    ok = so_velho = nada = semf = 0; rel = []
    for f, us in sorted(usos.items()):
        if f not in par: semf += len(us); continue
        va, n = par[f]
        t = subprocess.run([sys.executable, R + '/tools/f37/dz.py', hex(va), str(n)], capture_output=True, text=True).stdout
        disp = set(int(x, 16) for x in re.findall(r'\[e\w\w \+ (0x[0-9a-f]+)\]', t))
        for o, nn in us:
            if o == nn: continue
            if nn in disp: ok += 1
            elif o in disp: so_velho += 1; rel.append('so_velho\t%s\t%#x->%#x' % (f, o, nn))
            else: nada += 1; rel.append('nenhum\t%s\t%#x->%#x' % (f, o, nn))
    print('valida: novo presente %d; só o velho %d; nenhum %d; função sem par %d' % (ok, so_velho, nada, semf))
    for x in rel: print(x)
if ap: open(fn, 'w', encoding='latin-1', newline='').write('\n'.join(linhas))
