#!/usr/bin/env python3
"""f37/unidades — F3.7.1: corta os vãos "novos" do ProjectG 983 (out/F3.3/fronteiras.tsv, classe_vao = vao_novo, antes
de 00b50000) em unidades (.cpp prováveis) e dá nome a cada uma.
Rótulo de classe de cada função, por prioridade: (1) está numa vtable RTTI (classe com menos bases entre as que a têm =
quem a define); (2) espaço de nomes do Ghidra (map/projectg_funcs.tsv, nome983); (3) escreve o endereço de uma vtable
(construtor/destrutor; a mais derivada). Só classes que o fonte do 645 (src/, include/) NÃO tem formam faixa: as do 645
aparecem nos vãos como funções em linha/overrides soltos. Faixa de classe = maior grupo de funções dela sem buraco
> --buraco bytes; faixas que se sobrepõem viram uma unidade; trecho sem classe > --solto bytes vira unidade à parte.
A biblioteca RF (00401000–0046d8d0, LTCG) é cortada pelas strings `src\\RF*.cpp` que o próprio código referencia.
Saída (em --out): unidades_novas.tsv, rf_unidades.tsv, classes_novas.tsv, resumo.txt.
Uso: tools/f37/unidades.py --out out/F3.7/s1 [--buraco 6144] [--solto 4096]"""
import os, sys, csv, re, bisect, collections, argparse
sys.path.insert(0, os.path.dirname(__file__))
from lib import ROOT, funcs
JP = '/root/jp983/out'
ap = argparse.ArgumentParser()
ap.add_argument('--out', required=True); ap.add_argument('--buraco', type=int, default=6144)
ap.add_argument('--solto', type=int, default=4096)
A = ap.parse_args()
os.makedirs(A.out, exist_ok=True)


def desm(m):
    """.?AVNome@ns@@ -> ns::Nome; modelos ficam com '<' para serem ignorados na formação de faixas"""
    s = m[4:] if m.startswith('.?A') else m
    if s.startswith('?$'):
        return s[2:].split('@')[0] + '<>'
    p = [x for x in s.split('@') if x]
    if any(x.startswith('?') for x in p):
        return '::'.join(reversed([x for x in p if not x.startswith('?')])) + '{anon}'
    return '::'.join(reversed(p))


# classes do 645 (fonte importado do rebang)
C645 = set()
rx = re.compile(r'^\s*(?:class|struct)\s+(?:\w+\s+)*?([A-Za-z_]\w*)\s*(?:[:{]|$)')
for base in ('src', 'include'):
    for dp, _, fs in os.walk(os.path.join(ROOT, base)):
        if os.path.relpath(dp, ROOT).replace(os.sep, '/').endswith(('projectg/jp', 'include/jp')):
            continue
        for f in fs:
            if f.endswith(('.h', '.cpp', '.inl', '.hpp')):
                for l in open(os.path.join(dp, f), errors='replace'):
                    m = rx.match(l)
                    if m:
                        C645.add(m.group(1))
ARQ645 = {os.path.splitext(f)[0] for dp, _, fs in os.walk(os.path.join(ROOT, 'src')) for f in fs if f.endswith('.cpp')}

nb = {}; diretas = {}
for r in csv.DictReader(open(f'{JP}/j8/r983_classes.tsv'), delimiter='\t'):
    nb[r['classe']] = int(r['n_bases']); diretas[desm(r['classe'])] = [desm(x) for x in r['diretas'].split(',') if x]
vt_cls = {}; f_vt = collections.defaultdict(set)
for r in csv.DictReader(open(f'{JP}/j8/r983_vt.tsv'), delimiter='\t'):
    vt_cls[int(r['vt'], 16)] = r['classe']; f_vt[int(r['alvo'], 16)].add(r['classe'])
f_ref = collections.defaultdict(set)
for l in open(os.path.join(ROOT, 'build', 'B', 'refs.tsv')):
    f, _, t, _ = l.split('\t'); t = int(t, 16)
    if t in vt_cls:
        f_ref[int(f, 16)].add(vt_cls[t])
j7 = {int(r['a'], 16): r['cat'] for r in csv.DictReader(open(f'{JP}/J7_exclusivas.tsv'), delimiter='\t')}
f_str = collections.defaultdict(list)
for r in csv.DictReader(open(f'{JP}/j9/s983.tsv'), delimiter='\t', quoting=csv.QUOTE_NONE):
    for f in (r['funcoes'] or '').split(','):
        if f:
            f_str[int(f, 16)].append(r['texto'])
mm = {}
for r in csv.DictReader(open(os.path.join(ROOT, 'map', 'projectg_msgmaps.tsv')), delimiter='\t'):
    mm[int(r['getmessagemap'], 16)] = r['classes'].split(',')[0]

hd = {}
hp = os.path.join(ROOT, 'build', 'B', 'handlers.tsv')
if os.path.exists(hp):
    for l in open(hp):
        h, c, _, _ = l.rstrip('\n').split('\t'); hd.setdefault(int(h, 16), c)
import json
calls = collections.defaultdict(set)
for l in open(f'{JP}/f983.jsonl'):
    r = json.loads(l); a = int(r['a'], 16)
    if 0x470fe0 <= a < 0xb50000:
        for c in r['c']:
            if not c.startswith('EXT'):
                try:
                    calls[a].add(int(c, 16))
                except ValueError:
                    pass
F = funcs(); FA = [f['va'] for f in F]


def rotulo(f):
    va = f['va']
    if va in f_vt:
        return desm(min(f_vt[va], key=lambda c: (nb.get(c, 99), c))), 'vt'
    if va in mm:
        return mm[va], 'msgmap'
    if va in hd:
        return hd[va], 'handler'
    n = f['nome983']
    if '::' in n:
        return n.rsplit('::', 1)[0], 'ghidra'
    if va in f_ref:
        return desm(max(f_ref[va], key=lambda c: (nb.get(c, -1), c))), 'ctor'
    return None, None


def nova(c):
    """classe própria do jogo que o 645 não tem (forma faixa)"""
    if not c or '<' in c or c.startswith(('std::', 'ATL::', 'type_info', 'boost::')):
        return False
    return c.split('::')[-1].replace('{anon}', '') not in C645


def arquivo(c):
    n = c.split('::')[-1].replace('{anon}', '')
    if n.startswith('Fr') and len(n) > 2 and n[2].isupper():
        n = n[2:]
    elif n[0] in 'CI' and len(n) > 1 and n[1].isupper():
        n = n[1:]
    return n.lower()


def limpa(s):
    return re.sub(r'[\t\r\n]', ' ', s)[:40]


vaos = [(int(r['ini983'], 16), int(r['fim983'], 16)) for r in csv.DictReader(open(os.path.join(ROOT, 'out/F3.3/fronteiras.tsv')), delimiter='\t')
        if r['classe_vao'] == 'vao_novo' and 0x470fe0 <= int(r['ini983'], 16) < 0xb50000]
U = []; CL = collections.defaultdict(lambda: [0, 0, None, None, ''])
for lo, hi in vaos:
    fs = F[bisect.bisect_left(FA, lo):bisect.bisect_left(FA, hi)]
    if not fs:
        continue
    lab = [(f, *rotulo(f)) for f in fs]
    pos = collections.defaultdict(list)
    for f, c, via in lab:
        if nova(c):
            pos[c].append(f['va'])
    spans = []
    for c, ps in pos.items():
        grupos = [[ps[0]]]
        for p in ps[1:]:
            (grupos[-1].append(p) if p - grupos[-1][-1] <= A.buraco else grupos.append([p]))
        grupos.sort(key=len, reverse=True)
        for i, g in enumerate(grupos):
            if i == 0 or len(g) >= 3:
                spans.append([g[0], g[-1], {c}])
    spans.sort(key=lambda s: s[0])
    cl = []
    for s in spans:
        if cl and s[0] <= cl[-1][1]:
            cl[-1][1] = max(cl[-1][1], s[1]); cl[-1][2] |= s[2]
        else:
            cl.append(s)
    # limites: cada unidade vai do 1º rótulo dela até o 1º rótulo da seguinte; trecho sem classe grande vira unidade
    segs = []
    cur = lo
    for i, (a, b, cs) in enumerate(cl):
        if a - cur > A.solto and (i > 0 or True):
            if i == 0:
                segs.append([cur, a, None])
            else:
                fim_ant = fs[bisect.bisect_right([f['va'] for f in fs], cl[i - 1][1]) - 1]
                corte = fim_ant['va'] + fim_ant['sz']
                if a - corte > A.solto:
                    segs[-1][1] = corte; segs.append([corte, a, None])
                else:
                    segs[-1][1] = a
        elif segs:
            segs[-1][1] = a
        else:
            a = lo
        segs.append([a, hi, cs])
        cur = b
    if not segs:
        segs = [[lo, hi, None]]
    else:
        ult = fs[bisect.bisect_right([f['va'] for f in fs], cl[-1][1]) - 1]
        corte = ult['va'] + ult['sz']
        if hi - corte > A.solto:
            segs[-1][1] = corte; segs.append([corte, hi, None])
    # --- trechos sem classe: juntar ao vizinho quando há indício (regra anotada na coluna `juntou`)
    fva = [f['va'] for f in fs]

    def dentro(s):
        return fs[bisect.bisect_left(fva, s[0]):bisect.bisect_left(fva, s[1])]

    def arestas(s, t):
        n = 0
        for x, y in ((s, t), (t, s)):
            for f in dentro(x):
                n += sum(1 for c in calls.get(f['va'], ()) if y[0] <= c < y[1])
        return n

    for s_ in segs:
        s_.append('')
    mudou = True
    while mudou:
        mudou = False
        for i, sg in enumerate(segs):
            pv = segs[i - 1] if i > 0 else None; nx = segs[i + 1] if i + 1 < len(segs) else None
            if sg[2] is not None:
                if nx and nx[2] is not None and sg[2] & nx[2]:
                    sg[1] = nx[1]; sg[2] |= nx[2]; sg[3] += nx[3] + 'mesma_classe '; del segs[i + 1]; mudou = True; break
                continue
            lc = {c for f in dentro(sg) for c in [rotulo(f)[0]] if nova(c)}
            alvo = None
            if pv and nx and pv[2] and nx[2] and pv[2] & nx[2]:
                pv[1] = nx[1]; pv[2] |= nx[2]; pv[3] += nx[3] + 'entre_partes '; del segs[i:i + 2]; mudou = True; break
            if lc and nx and nx[2] and lc & nx[2] and not (pv and pv[2] and lc & pv[2]):
                alvo = 'nx'; regra = 'classe_dentro '
            elif lc and pv and pv[2] and lc & pv[2] and not (nx and nx[2] and lc & nx[2]):
                alvo = 'pv'; regra = 'classe_dentro '
            else:
                ep = arestas(sg, pv) if pv and pv[2] else 0; en = arestas(sg, nx) if nx and nx[2] else 0
                if max(ep, en) >= 3 and max(ep, en) >= 2 * min(ep, en) + 1:
                    alvo = 'pv' if ep > en else 'nx'; regra = 'chamadas(%d×%d) ' % (ep, en)
            if alvo == 'nx':
                nx[0] = sg[0]; nx[3] += regra; del segs[i]; mudou = True; break
            if alvo == 'pv':
                pv[1] = sg[1]; pv[3] += regra; del segs[i]; mudou = True; break
    for a, b, cs, juntou in segs:
        sub = [x for x in lab if a <= x[0]['va'] < b]
        if not sub:
            continue
        by = sum(x[0]['sz'] for x in sub)
        cc = collections.Counter(); cb = collections.Counter()
        for f, c, via in sub:
            if c and '<' not in c and not c.startswith('std::'):
                cc[c] += 1; cb[c] += f['sz']
        novas = [c for c in cb if nova(c)]
        nj7 = sum(1 for f, _, _ in sub if j7.get(f['va']) == 'NOVA')
        st = []
        for f, _, _ in sub:
            for s in f_str.get(f['va'], []):
                if s not in st and len(s) >= 4 and re.match(r'^[\x20-\x7e]+$', s):
                    st.append(s)
        rot = sum(1 for _, c, _ in sub if nova(c))
        if cs:
            princ = max(novas, key=lambda c: cb[c]) if novas else sorted(cs)[0]
            nome = arquivo(princ)
            conf = 'alta' if rot >= 5 else ('media' if rot >= 3 else 'baixa')
        else:
            princ = ''
            ex = [c for c, _ in cc.most_common(1)]
            nome = 'semclasse_%08x' % a; conf = 'sem_classe'
        for c in novas:
            e = CL[c]; e[0] += cc[c]; e[1] += cb[c]; e[4] = nome
        U.append(dict(ini='%08x' % a, fim='%08x' % b, bytes=by, funcs=len(sub), rotuladas=rot, novas_j7=nj7,
                      arquivo=('jp/' + nome + '.cpp'), ja_no_645=('sim' if nome in ARQ645 else ''), confianca=conf, principal=princ,
                      classes=', '.join('%s%s(%d)' % ('*' if nova(c) else '', c, n) for c, n in cc.most_common(10)),
                      strings=' | '.join(limpa(s) for s in st[:8]), juntou=juntou.strip(), vao='%08x-%08x' % (lo, hi)))
# nomes repetidos (mesma classe principal em dois vãos): sufixo
cnt = collections.Counter(u['arquivo'] for u in U); k = collections.Counter()
for u in U:
    if cnt[u['arquivo']] > 1:
        k[u['arquivo']] += 1
        if k[u['arquivo']] > 1:
            u['arquivo'] = u['arquivo'][:-4] + '_p%d.cpp' % k[u['arquivo']]
cols = ['ini', 'fim', 'bytes', 'funcs', 'rotuladas', 'novas_j7', 'arquivo', 'ja_no_645', 'confianca', 'principal', 'classes', 'strings', 'juntou', 'vao']
with open(os.path.join(A.out, 'unidades_novas.tsv'), 'w') as o:
    o.write('\t'.join(cols) + '\n')
    for u in U:
        o.write('\t'.join(str(u[c]) for c in cols) + '\n')
with open(os.path.join(A.out, 'classes_novas.tsv'), 'w') as o:
    o.write('classe\tfuncs\tbytes\tunidade\tbases_diretas\n')
    for c, e in sorted(CL.items(), key=lambda x: -x[1][1]):
        o.write('%s\t%d\t%d\tjp/%s.cpp\t%s\n' % (c, e[0], e[1], e[4], ','.join(diretas.get(c, []))))

# ---- biblioteca RF: strings de nome de arquivo usadas pelo código (asserts)
RF_LO, RF_HI = 0x401000, 0x46d8d0
anc = []
for r in csv.DictReader(open(f'{JP}/j9/s983.tsv'), delimiter='\t', quoting=csv.QUOTE_NONE):
    t = r['texto'].replace('\\\\', '\\')
    if re.search(r'\.(cpp|c|h|inl)$', t, re.I) and r['funcoes']:
        for f in r['funcoes'].split(','):
            v = int(f, 16)
            if RF_LO <= v < RF_HI:
                anc.append((v, t))
anc.sort()
rf = []
for v, t in anc:
    if rf and rf[-1][2] == t:
        rf[-1][1] = v; rf[-1][3] += 1
    else:
        rf.append([v, v, t, 1])
with open(os.path.join(A.out, 'rf_unidades.tsv'), 'w') as o:
    o.write('1a_func_com_a_string\tultima\tn_funcs\tarquivo_na_string\tfuncs_ate_a_proxima\tbytes_ate_a_proxima\tclasses_no_trecho\n')
    for i, (a, b, t, n) in enumerate(rf):
        prox = rf[i + 1][0] if i + 1 < len(rf) else RF_HI
        sub = F[bisect.bisect_left(FA, a):bisect.bisect_left(FA, prox)]
        cc = collections.Counter(c for c in (rotulo(f)[0] for f in sub) if c and '<' not in c and not c.startswith('std::'))
        o.write('%08x\t%08x\t%d\t%s\t%d\t%d\t%s\n' % (a, b, n, t, len(sub), sum(f['sz'] for f in sub),
                                                      ', '.join('%s(%d)' % x for x in cc.most_common(6))))
tot = sum(u['bytes'] for u in U)
with open(os.path.join(A.out, 'resumo.txt'), 'w') as o:
    def p(*a):
        s = ' '.join(str(x) for x in a); print(s); o.write(s + '\n')
    p('vãos novos tratados (00470fe0–00b50000):', len(vaos), '| funções:', sum(u['funcs'] for u in U), '| bytes de função:', tot)
    p('unidades propostas:', len(U))
    for k_ in ('alta', 'media', 'baixa', 'sem_classe'):
        s = [u for u in U if u['confianca'] == k_]
        p('  %-10s %4d unidades %8d B (%.1f%%)' % (k_, len(s), sum(u['bytes'] for u in s), 100.0 * sum(u['bytes'] for u in s) / tot))
    p('classes do 645 reconhecidas no fonte:', len(C645))
    p('nome igual ao de arquivo que o 645 já tem:', sum(1 for u in U if u['ja_no_645']))
    p('classes novas com faixa:', len(CL), '| funções rotuladas com classe nova:', sum(u['rotuladas'] for u in U))
    p('RF: %d âncoras de nome de arquivo, %d trechos, %d arquivos distintos' % (len(anc), len(rf), len({r[2] for r in rf})))
