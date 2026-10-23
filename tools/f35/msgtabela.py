#!/usr/bin/env python3
"""msgtabela.py SAIDA [DIR_msgvotos2 [casos_votos.tsv [msg_pares.tsv anterior]]] — tabela 645 → 983 dos números de mensagem entre atores, a partir dos votos:
  E = envios em funções com par (msgvotos2.py: env_votos.tsv), D = despachante comum (s66/msg_votos.tsv),
  R = testes do switch nos HandleMsg com par (rec_votos.tsv; só números > 0x10, peso menor).
Modelo: a enumeração do 983 é a do 645 com inserções e remoções, logo o par (645, 983) é estritamente crescente nos dois lados.
1) escolhe o maior subconjunto crescente dos pares votados (peso = votos); o resto sai como `rejeitado`;
2) usa o modelo para alinhar as funções em que os dois lados têm quantidades diferentes de envio (LCS só com pares que cabem no
   intervalo do modelo) e repete o passo 1 com os pares novos (fonte A);
3) classifica cada número do 645: `voto` (âncora), `interpolado` (as âncoras dos dois lados têm o mesmo deslocamento) ou
   `intervalo` (deslocamento muda entre as âncoras vizinhas: fica aberto).
Números >= 0x2710 (Gateway) ficam iguais (votos confirmam 0x2712–0x271b).
Saída: msg_pares.tsv (todos os pares e a decisão), msg_tabela.tsv (um número do 645 por linha), msg_uso.tsv (números usados no
fonte, quantos locais, estado)."""
import sys, os, re, csv, glob, collections, bisect
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out = sys.argv[1]; d2 = sys.argv[2] if len(sys.argv) > 2 else out
GW = 0x2710
P = collections.defaultdict(lambda: collections.Counter())      # (x, y) -> {fonte: peso}
def add(x, y, src, w):
    if 0 < x < GW and 0 < y < GW: P[(x, y)][src] += w
for r in csv.DictReader(open(d2 + '/env_votos.tsv'), delimiter='\t'):
    add(int(r['msg_645'], 16), int(r['msg_983'], 16), 'E', int(r['votos']))
for r in csv.DictReader(open(R + '/out/F3.5/s66/msg_votos.tsv'), delimiter='\t'):
    add(int(r['msg_645'], 16), int(r['msg_983'], 16), 'D', int(r['votos']))
for r in csv.DictReader(open(d2 + '/rec_votos.tsv'), delimiter='\t'):
    x, y = int(r['imediato_nosso'], 16), int(r['imediato_983'], 16)
    if x > 0x10 and y > 0x10: add(x, y, 'R', 0.5 * int(r['funcoes']))
# K = `case` dos HandleMsg pareados pelo switch (msgcasos.py, s68): exato = 2, corpo parecido (>= 0,8) = 1, (>= 0,5) = 0,5
if len(sys.argv) > 3:
    for r in csv.DictReader(open(sys.argv[3]), delimiter='\t'):
        if r['msg_983'] == '-': continue
        w = 2 if r['modo'] == 'exato' else 1 if float(r['sim']) >= 0.8 else 0.5 if float(r['sim']) >= 0.5 else 0
        if w: add(int(r['msg_645'], 16), int(r['msg_983'], 16), 'K', w)
def lis(pairs):
    """maior subconjunto com x e y estritamente crescentes, por peso"""
    it = sorted(pairs, key=lambda p: (p[0], p[1]))
    best = [0.0] * len(it); prev = [-1] * len(it)
    for i, (x, y, w) in enumerate(it):
        best[i] = w
        for k in range(i):
            if it[k][0] < x and it[k][1] < y and best[k] + w > best[i]: best[i] = best[k] + w; prev[i] = k
    i = max(range(len(it)), key=lambda k: best[k]); sel = []
    while i >= 0: sel.append(it[i][:2]); i = prev[i]
    return sorted(sel)
def modelo(anc):
    xs = [a[0] for a in anc]
    def faixa(x):
        """(lo, hi) do número do 983 para o x do 645"""
        i = bisect.bisect_left(xs, x)
        if i < len(xs) and xs[i] == x: return anc[i][1], anc[i][1]
        lo = anc[i - 1][1] + (x - anc[i - 1][0]) if i > 0 else x
        hi = anc[i][1] - (anc[i][0] - x) if i < len(xs) else None
        return lo, hi
    return faixa
def peso(c): return sum(c.values())
anc = lis([(x, y, peso(c)) for (x, y), c in P.items()])
# 2) alinhamento das funções de tamanhos diferentes
def lcs(s, q, ok):
    n, m = len(s), len(q); T = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for k in range(m - 1, -1, -1):
            T[i][k] = T[i + 1][k + 1] + 1 if ok(s[i], q[k]) else max(T[i + 1][k], T[i][k + 1])
    i = k = 0; res = []
    while i < n and k < m:
        if ok(s[i], q[k]): res.append((s[i], q[k])); i += 1; k += 1
        elif T[i + 1][k] >= T[i][k + 1]: i += 1
        else: k += 1
    return res
faixa = modelo(anc); novos = 0; ANC = anc; XS = [a[0] for a in anc]
def cabe(a, b):
    if a[0] != b[0] or a[1] is None or b[1] is None: return False
    if a[1] >= GW or b[1] >= GW or a[1] == 0: return a[1] == b[1]
    # folgado: entre as âncoras vizinhas (o 983 também removeu números; ex.: +1 em 0x2a–0x2f e +0 de novo em 0x3b)
    i = bisect.bisect_left(XS, a[1])
    if i < len(XS) and XS[i] == a[1]: return ANC[i][1] == b[1]
    return (i == 0 or ANC[i - 1][1] < b[1]) and (i == len(XS) or b[1] < ANC[i][1])
def seqs(txt): return [(t[0], int(t[1:], 16) if t[1:] != '?' else None) for t in txt.split()]
f_env = d2 + '/env_funcs.tsv'
if os.path.exists(f_env):
    for r in csv.DictReader(open(f_env), delimiter='\t'):
        if r['estado'] != 'tamanho' or not r['msgs_983']: continue
        for a, b in lcs(seqs(r['msgs_nosso']), seqs(r['msgs_983']), cabe):
            if 0 < a[1] < GW: add(a[1], b[1], 'A', 1); novos += 1
for r in csv.DictReader(open(R + '/out/F3.5/s66/msg_casos.tsv'), delimiter='\t'):
    if r['estado'] != 'tamanho' or not r['msgs_983'] or not r['msgs_fonte_645']: continue
    s = [('C', int(t, 16) if t != '?' else None) for t in r['msgs_fonte_645'].split()]
    q = [('C', int(t, 16) if t != '?' else None) for t in r['msgs_983'].split()]
    for a, b in lcs(s, q, cabe):
        if 0 < a[1] < GW: add(a[1], b[1], 'A', 1); novos += 1
# P = âncoras da rodada anterior que esta rodada não refez (o alinhamento A depende do modelo e muda quando entram âncoras novas):
# voltam com o peso que tinham, para que um voto fraco novo não tome o lugar delas
if len(sys.argv) > 4:
    for r in csv.DictReader(open(sys.argv[4]), delimiter='\t'):
        k = (int(r['msg_645'], 16), int(r['msg_983'], 16))
        if r['decisao'] == 'ancora' and k not in P: add(k[0], k[1], 'P', float(r['peso']))
anc = lis([(x, y, peso(c)) for (x, y), c in P.items()]); faixa = modelo(anc); A = dict(anc)
os.makedirs(out, exist_ok=True)
with open(out + '/msg_pares.tsv', 'w') as f:
    f.write('msg_645\tmsg_983\tdesloc\tpeso\tfontes\tdecisao\n')
    for (x, y), c in sorted(P.items()):
        f.write('0x%x\t0x%x\t%+d\t%g\t%s\t%s\n' % (x, y, y - x, peso(c), ' '.join('%s%g' % kv for kv in sorted(c.items())),
                                                 'ancora' if A.get(x) == y else 'rejeitado'))
# números usados no fonte (fora de src/projectg/jp, que já nasce com os números do 983)
PAT = [('envio', re.compile(r'\bMsgObject\(\s*[^,()]+,\s*(0x[0-9a-fA-F]+|\d+)\s*,')),
       ('envio', re.compile(r'\b(?:Afx)?(?:Send|Post)Msg\(\s*[^,()]+,\s*[^,]+,\s*(0x[0-9a-fA-F]+|\d+)\s*,'))]
CASE = re.compile(r'^\s*case\s+(0x[0-9a-fA-F]+|\d+)\s*:')
uso = collections.defaultdict(collections.Counter); arqs = collections.defaultdict(set)
for fn in sorted(glob.glob(R + '/src/projectg/**/*.cpp', recursive=True) + glob.glob(R + '/src/projectg/**/*.h', recursive=True)):
    if '/jp/' in fn: continue
    txt = open(fn, encoding='latin1').read()
    for k, p in PAT:
        for m in p.finditer(txt):
            uso[int(m.group(1), 0)][k] += 1; arqs[int(m.group(1), 0)].add(os.path.basename(fn))
    em = False; prof = 0
    for l in txt.split('\n'):
        if re.search(r'switch\s*\(\s*(msg\.message|message|msg\.m_message)\s*\)', l): em = True; prof = 0; continue
        if em:
            m = CASE.match(l)
            if m and prof <= 1: uso[int(m.group(1), 0)]['case'] += 1; arqs[int(m.group(1), 0)].add(os.path.basename(fn))
            prof += l.count('{') - l.count('}')
            if prof <= 0 and '}' in l: em = False
def estado(x):
    if x >= GW or x == 0: return 'igual', x, x
    lo, hi = faixa(x)
    if x in A: return 'voto', lo, hi
    if hi is not None and lo == hi: return 'interpolado', lo, hi
    if hi is not None and lo > hi: lo, hi = hi, lo
    return 'intervalo', lo, hi
mx = max(max(A), max((x for x in uso if x < GW), default=0))
cnt = collections.Counter()
with open(out + '/msg_tabela.tsv', 'w') as f:
    f.write('msg_645\testado\tmsg_983\tmsg_983_max\tdesloc\tusado_no_fonte\n')
    for x in range(1, mx + 1):
        e, lo, hi = estado(x)
        f.write('0x%x\t%s\t0x%x\t%s\t%+d\t%d\n' % (x, e, lo, '0x%x' % hi if hi is not None else '?', lo - x, sum(uso[x].values()) if x in uso else 0))
cu = collections.Counter(); cl = collections.Counter()
with open(out + '/msg_uso.tsv', 'w') as f:
    f.write('msg_645\testado\tmsg_983\tmsg_983_max\tenvios\tcases\tarquivos\n')
    for x in sorted(uso):
        e, lo, hi = estado(x); n = sum(uso[x].values())
        if e != 'igual' and lo == x and hi == x: e += '_igual'
        cu[e] += 1; cl[e] += n
        f.write('0x%x\t%s\t0x%x\t%s\t%d\t%d\t%s\n' % (x, e, lo, '0x%x' % hi if hi is not None else '?', uso[x]['envio'], uso[x]['case'],
                                                    ' '.join(sorted(arqs[x])[:8])))
rej = sum(1 for (x, y) in P if A.get(x) != y)
print('pares votados %d (do alinhamento %d votos) | âncoras %d | rejeitados %d' % (len(P), novos, len(anc), rej))
print('números usados no fonte %d: %s' % (len(uso), dict(cu)))
print('locais no fonte %d: %s' % (sum(cl.values()), dict(cl)))
