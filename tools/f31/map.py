#!/usr/bin/env python3
# F3.1 — mapa unidade do 645 (módulo do PDB / build-projectg.json do rebang) -> faixa e funções do ProjectG 983.
#
# Método:
#   1. âncoras função 983 -> função 645 -> módulo: (a) ponte 645->839 (kr839 match2) x 839->983 (jp983 J3 + J7);
#      (b) direto por string única dos dois lados; (c) direto por classe RTTI do 983 cuja classe, no 645, tem os
#      métodos num módulo só (âncora de unidade, não de função).
#   2. segmentação da .text do 983 na ordem dos endereços (Viterbi: custo de âncora discordante x custo de trocar de
#      unidade) -> trechos contíguos por unidade.
#   3. cada função do 983 dentro de um trecho = "nucleo"; entre dois trechos = "fronteira" (unidade incerta).
#   4. validação por retirada (5 partes): refaz a segmentação sem 20% das âncoras e mede em qual trecho caem.
#
# uso: python3 tools/f31/map.py [--out out/F3.1] [--map map]
import argparse, bisect, collections, csv, os, random, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import *  # noqa

LAMBDA = 2.0      # custo de trocar de unidade
LAMBDA0 = 0.75    # custo de entrar/sair da região misturada
E0 = 0.5          # custo de uma âncora na região misturada (x peso)
SALTO = 0x8000    # salto máximo entre âncoras do mesmo trecho
PESO = {'alta': 1.0, 'media': 0.8, 'baixa': 0.5, 'str': 1.0, 'cls': 0.6, 'obj': 1.0, 'obj_viz': 0.8, 'inl': 0.5}
MIN_OBJ = 16      # âncora 'obj': tamanho mínimo da função (menores dobram por ICF com as de outras unidades)


def classe_de(nome):
    """'A::B<x::y>::metodo' -> 'A::B<x::y>'"""
    prof = 0
    corte = -1
    for i, ch in enumerate(nome):
        if ch == '<':
            prof += 1
        elif ch == '>':
            prof -= 1
        elif ch == ':' and prof == 0 and nome[i:i + 2] == '::':
            corte = i
    return nome[:corte] if corte > 0 else ''


def ancoras(mods, f645, f983, sem_classe=False):
    by645 = {f['a']: f for f in f645}
    p1, p2 = pairs_645_839(), pairs_983_839()
    anc = {}  # 983 -> (645 ou '', módulo, fonte)
    for a, (b, how, conf) in p1.items():
        f = by645.get(a)
        if f is None or f['m'] is None:
            continue
        for x in p2.get(b, ()):
            if x[1] != 'gemea':
                anc[x[0]] = (a, f['m'], conf)

    def uniq(fs):
        c = collections.defaultdict(list)
        for f in fs:
            for s in set(f.get('s', [])):
                if len(s) >= 6:
                    c[s].append(f['a'])
        return {s: v[0] for s, v in c.items() if len(v) == 1}
    u6, u9 = uniq(f645), uniq(f983)
    votos = collections.defaultdict(collections.Counter)
    for s in set(u6) & set(u9):
        votos[u6[s]][u9[s]] += 1
    nstr = 0
    for a, v in votos.items():
        t = v.most_common(1)[0][0]
        if t not in anc and by645[a]['m'] is not None:
            anc[t] = (a, by645[a]['m'], 'str')
            nstr += 1
    ncls = 0
    if not sem_classe:
        cm = collections.defaultdict(collections.Counter)
        for f in f645:
            c = classe_de(f['n'])
            if c and f['m'] is not None and not c.startswith(('std::', 'ATL::', 'WTL::')):
                cm[c][f['m']] += 1
        dono = {}
        for c, v in cm.items():
            m, n = v.most_common(1)[0]
            tot = sum(v.values())
            if tot >= 3 and n / tot >= 0.8:
                dono[c] = m
        for a, c in classes983().items():
            if a not in anc and c in dono:
                anc[a] = ('', dono[c], 'cls')
                ncls += 1
    return anc, nstr, ncls


def ancoras_obj(mods, base, imp):
    """F3.3: âncoras do mesmo compilador. Função própria de uma unidade nossa (src/..., vinda do rebang) que o
    cmpfunc achou IGUAL/QUASE no 983 (out/F3.2/funcs_all.tsv.gz) -> (va983, módulo do 645 dessa unidade).
    Ficam de fora: lugar ambíguo ('bytes*N'), origem 'semente' (vem do próprio mapa da F3.1: seria circular),
    funções menores que MIN_OBJ e endereços reclamados por mais de uma unidade (ICF)."""
    import gzip
    reb = {}
    for r in csv.DictReader(open(imp), delimiter='\t'):
        reb[r['aqui']] = os.path.splitext(r['rebang'])[0].lower()
    pm = {os.path.splitext(md['path'])[0].lower(): m for m, md in mods.items() if md['path']}
    dono = collections.defaultdict(set)
    linhas = {}
    fora = collections.Counter()
    for r in csv.DictReader(gzip.open(base, 'rt'), delimiter='\t'):
        if r['propria'] != '1' or r['classe'] not in ('IGUAL', 'QUASE'):
            continue
        m = pm.get(reb.get(r['arquivo'], ''))
        if m is None:
            fora['unidade sem modulo no 645'] += 1
            continue
        dono[r['va983']].add(m)
        if '*' in r['origem']:
            fora['lugar ambiguo'] += 1
        elif r['origem'] == 'semente':
            fora['semente'] += 1
        elif int(r['bytes_983'] or 0) < MIN_OBJ:
            fora['pequena'] += 1
        else:
            linhas[r['va983']] = (r['funcao'], m, 'obj' if r['origem'] in ('bytes', 'alvo') else 'obj_viz')
    out = {}
    for va, x in linhas.items():
        if len(dono[va]) > 1:
            fora['mais de uma unidade (ICF)'] += 1
        else:
            out[va] = x
    # funções em linha/modelos (COMDAT) que só uma unidade nossa instancia e que têm lugar único por bytes:
    # ficam dentro da faixa da unidade (medido: 741 dentro x 92 fora, com as âncoras próprias). Peso baixo.
    inl = collections.defaultdict(set)
    nm = {}
    for r in csv.DictReader(gzip.open(base, 'rt'), delimiter='\t'):
        if r['propria'] == '0' and r['classe'] == 'IGUAL' and r['origem'] == 'bytes' \
                and int(r['bytes_983'] or 0) >= MIN_OBJ:
            inl[r['va983']].add(pm.get(reb.get(r['arquivo'], '')))
            nm[r['va983']] = r['funcao']
    for va, ms in inl.items():
        m = next(iter(ms))
        if len(ms) == 1 and m is not None and va not in dono:
            out[va] = (nm[va], m, 'inl')
    return out, fora


def segmenta(seq, lam=LAMBDA, lam0=LAMBDA0, e0=E0):
    """seq: lista ordenada (va, módulo, peso). Devolve o estado de cada âncora: um módulo ou None.
    None = região misturada (sem unidade dominante): cada âncora ali custa e0*peso; entrar/sair custa lam0."""
    estados = sorted({m for _, m, _ in seq})
    idx = {m: i for i, m in enumerate(estados)}
    n, k = len(seq), len(estados)
    custo = [lam0] * k + [0.0]          # começa na região misturada
    volta = []
    for va, m, w in seq:
        mi = idx[m]
        cmin = min(custo[:k])
        amin = custo.index(cmin)
        c0 = custo[k]
        novo = [0.0] * (k + 1)
        bp = [0] * (k + 1)
        for s in range(k):
            best, de = custo[s], s
            if c0 + lam0 < best:
                best, de = c0 + lam0, k
            if cmin + lam < best:
                best, de = cmin + lam, amin
            novo[s] = best + (0.0 if s == mi else w)
            bp[s] = de
        if cmin + lam0 < c0:
            novo[k], bp[k] = cmin + lam0 + e0 * w, amin
        else:
            novo[k], bp[k] = c0 + e0 * w, k
        custo = novo
        volta.append(bp)
    s = custo.index(min(custo))
    out = [None] * n
    for i in range(n - 1, -1, -1):
        out[i] = estados[s] if s < k else None
        s = volta[i][s]
    return out


def trechos(seq, est, fim983, tam645):
    """junta âncoras consecutivas do mesmo estado: [módulo, ini, fim, n_concorda, n_discorda].
    Corta o trecho num salto entre âncoras maior que max(SALTO, 1,5 x .text da unidade no 645) e descarta
    pedaços com menos de 3 âncoras concordes (viram fronteira)."""
    t = []
    ult = None
    for (va, m, w), s in zip(seq, est):
        if s is None:
            ult = None
            continue
        if t and ult == s and va - t[-1][5] <= max(SALTO, 1.5 * tam645.get(s, 0)):
            if m == s:
                t[-1][2] = fim983(va)
                t[-1][5] = va
        else:
            t.append([s, va, fim983(va), 0, 0, va])
        t[-1][3 if m == s else 4] += 1
        ult = s
    out = []
    for x in t:
        if x[3] >= 3:
            out.append(x[:5])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='out/F3.1')
    ap.add_argument('--map', default='map')
    ap.add_argument('--base', help='F3.3: funcs_all.tsv.gz da linha de base (âncoras do mesmo compilador)')
    ap.add_argument('--imp', default='out/F3.2/importados.tsv')
    ap.add_argument('--base-tsv', default='out/F3.2/base.tsv', help='base.tsv (ondas reais por % IGUAL)')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    mods = modules645()
    C = contribs645()
    mo = ModOf(C)
    f645, f983 = funcs645(), funcs983()
    for f in f645:
        f['m'] = mo(int(f['a'], 16))
    f983.sort(key=lambda f: int(f['a'], 16))
    k983 = [int(f['a'], 16) for f in f983]
    sz983 = {int(f['a'], 16): f.get('sz', 0) for f in f983}

    def fim983(va):
        return va + max(sz983.get(va, 1), 1)

    # tamanho e nº de funções de cada módulo na .text do 645
    txt645 = collections.Counter()
    ini645 = {}
    for va, fim, m in C:
        txt645[m] += fim - va
        ini645.setdefault(m, va)
    nf645 = collections.Counter(f['m'] for f in f645)

    anc, nstr, ncls = ancoras(mods, f645, f983)
    nome_obj = {}
    cruz = collections.Counter()
    discordes_obj = []
    if a.base:
        ao, fora_obj = ancoras_obj(mods, a.base, a.imp)
        for va, (nm, m, src) in ao.items():
            if va in anc:
                v = anc[va]
                k = ('ponte ' if v[2] != 'cls' else 'classe ') + ('concorda' if v[1] == m else 'discorda')
                cruz[k] += 1
                if v[1] != m:
                    discordes_obj.append((va, nm, m, v[1], v[2]))
            anc[va] = (anc[va][0] if va in anc and anc[va][1] == m else '', m, src)
            nome_obj[va] = nm
    seq = sorted((int(k, 16), v[1], PESO[v[2]]) for k, v in anc.items())
    est = segmenta(seq)
    T = trechos(seq, est, fim983, txt645)

    # ---- validação por retirada (só âncoras de função)
    rnd = random.Random(983)
    chaves = sorted(k for k, v in anc.items() if v[2] not in ('cls', 'inl'))
    rnd.shuffle(chaves)
    val = collections.Counter()
    for parte in range(5):
        fora = set(chaves[parte::5])
        s2 = sorted((int(k, 16), v[1], PESO[v[2]]) for k, v in anc.items() if k not in fora)
        t2 = trechos(s2, segmenta(s2), fim983, txt645)
        ini = [t[1] for t in t2]
        for k in fora:
            va = int(k, 16)
            i = bisect.bisect_right(ini, va) - 1
            if i >= 0 and va < t2[i][2]:
                val['nucleo_certo' if t2[i][0] == anc[k][1] else 'nucleo_errado'] += 1
            else:
                viz = {t2[j][0] for j in (i, i + 1) if 0 <= j < len(t2)}
                val['fronteira_vizinho' if anc[k][1] in viz else 'fronteira_outro'] += 1

    # ---- funções do 983 -> unidade
    tini = [t[1] for t in T]
    exc = {}
    for r in csv.DictReader(open(f'{JP}/J7_exclusivas.tsv'), delimiter='\t'):
        exc[r['a']] = r['cat']
    par839 = {}
    for l in open(f'{JP}/j3/pairs.tsv'):
        c = l.rstrip('\n').split('\t')
        par839[c[0]] = (c[1], c[4] if len(c) > 4 else '')
    cls983 = classes983()
    porT = [dict(nf=0, by=0, nova=0, alt=0, dif=0, idem=0) for _ in T]
    fr = collections.defaultdict(lambda: dict(nf=0, by=0, nova=0, alt=0, cls=collections.Counter()))
    linhas = []
    for f in f983:
        va = int(f['a'], 16)
        i = bisect.bisect_right(tini, va) - 1
        cat = exc.get(f['a'], '')
        p = par839.get(f['a'])
        corpo = p[1] if p else ''
        a645 = anc.get(f['a'], ('', None, ''))
        if i >= 0 and va < T[i][2]:
            d = porT[i]
            un, onde = T[i][0], 'nucleo'
        else:
            d = fr[i]
            un, onde = None, 'fronteira'
            if f['a'] in cls983:
                d['cls'][cls983[f['a']]] += 1
        d['nf'] += 1
        d['by'] += f.get('sz', 0)
        if cat == 'NOVA':
            d['nova'] += 1
        elif cat == 'ALTERADA' or corpo == 'dif':
            d['alt'] += 1
        if onde == 'nucleo':
            if corpo == 'hx':
                d['idem'] += 1
        linhas.append((f['a'], f.get('sz', 0), onde, un, i, a645[0], a645[2], a645[1], cat or corpo, f['n']))

    def nome(m):
        if m is None:
            return ''
        return mods[m]['path'] or mods[m]['obj']

    porU = collections.defaultdict(list)
    for i, t in enumerate(T):
        porU[t[0]].append(i)

    # ---- fronteiras (vãos entre trechos): âncoras soltas, candidatas pela ordem de link do 645, classes do 983
    cls645 = {classe_de(f['n']) for f in f645}
    forte = set(porU)
    soltas = collections.defaultdict(collections.Counter)
    for k, v in anc.items():
        va = int(k, 16)
        i = bisect.bisect_right(tini, va) - 1
        if not (i >= 0 and va < T[i][2]) and v[1] not in forte:
            soltas[i][v[1]] += 1
    jogo = [m for m in sorted(ini645, key=ini645.get) if mods[m]['grupo'] != 'lib' and txt645[m] >= 64]
    lugar = {}   # módulo sem trecho -> (classe do mapa, índice da fronteira)
    cand = {}
    for i in sorted(fr):
        c = []
        if 0 <= i and i + 1 < len(T):
            x, y = ini645.get(T[i][0], 0), ini645.get(T[i + 1][0], 0)
            if x < y:
                c = [m for m in jogo if x < ini645[m] < y and m not in forte]
                if any(m in forte for m in jogo if x < ini645[m] < y):
                    c = []        # há unidade forte entre as duas no 645: a ordem mudou aqui, não dá para inferir
        if c and fr[i]['by'] < 0.3 * sum(txt645[m] for m in c):
            c = []            # o vão é pequeno demais para as candidatas: não estão aqui (ou saíram do 983)
        cand[i] = c
        for m in c:
            lugar[m] = ('ordem', i)
    for i, cnt in soltas.items():
        for m, n in cnt.items():
            tot = sum(c2[m] for c2 in soltas.values())
            if n * 2 > tot and (m not in lugar or lugar[m][1] == i):
                lugar[m] = ('fraco+ordem' if m in lugar else 'fraco', i)

    # ---- F3.3: classe de cada vão (o que há entre dois trechos)
    #   vao_unidade  há unidade(s) do 645 sem trecho que cabem aqui (âncoras soltas e/ou ordem de link), ou o vão
    #                separa dois trechos da mesma unidade
    #   vao_novo     código que o 645 não tem: maioria das classes RTTI do vão não existe no PDB do 645, ou
    #                >= 30% das funções são NOVA na J7 (JP x KR839)
    #   vao_borda    as duas vizinhas são consecutivas na ordem de link do 645: é cauda de uma ou cabeça da outra
    #   fronteira    nada disso (ordem mudou, sem indício)
    pos = {m: j for j, m in enumerate(jogo)}
    gcl = {}
    for i in sorted(fr):
        d = fr[i]
        ant = T[i][0] if i >= 0 else None
        dep = T[i + 1][0] if i + 1 < len(T) else None
        us = [m for m, (c, j) in lugar.items() if j == i]
        ncl = sum(d['cls'].values())
        nnovo = sum(n for c, n in d['cls'].items() if c not in cls645)
        if ant is not None and ant == dep:
            gcl[i] = ('vao_unidade', nome(ant))
        elif (ncl >= 3 and nnovo * 2 > ncl) or d['nova'] >= 0.3 * max(d['nf'], 1):
            gcl[i] = ('vao_novo', ' | '.join(nome(m) for m in us))
        elif us:
            gcl[i] = ('vao_unidade', ' | '.join(nome(m) for m in sorted(us, key=lambda m: ini645.get(m, 0))))
        elif ant in pos and dep in pos and pos[dep] == pos[ant] + 1:
            gcl[i] = ('vao_borda', nome(ant) + ' | ' + nome(dep))
        else:
            gcl[i] = ('fronteira', '')

    # ---- map/projectg_funcs.tsv
    by645 = {f['a']: f for f in f645}
    with open(f'{a.map}/projectg_funcs.tsv', 'w') as o:
        o.write('f983\ttam\tonde\tunidade\ttrecho\tpar645\tnome645\tfonte\tunidade_da_ancora\tj3j7\tnome983\n')
        for f9, sz, onde, un, i, a6, src, am, cat, n9 in linhas:
            if onde == 'fronteira':
                onde, un_txt = gcl[i]
            else:
                un_txt = nome(un)
            o.write('\t'.join([f9, str(sz), onde, un_txt, str(i), a6,
                               by645[a6]['n'] if a6 else nome_obj.get(f9, ''), src,
                               nome(am) if am is not None and am != un else '', cat, n9]) + '\n')

    def faixa_fr(i):
        ini = T[i][2] if i >= 0 else k983[0]
        fim = T[i + 1][1] if i + 1 < len(T) else fim983(k983[-1])
        return ini, fim
    with open(f'{a.out}/fronteiras.tsv', 'w') as o:
        o.write('ini983\tfim983\tbytes_funcs\tfuncs\tnovas_j7\talteradas\tantes\tdepois\tancoras_soltas\t'
                'candidatas_pela_ordem(bytes645)\tclasses_983 (*=classe que o 645 não tem)\tclasse_vao\n')
        for i in sorted(fr):
            d = fr[i]
            ini, fim = faixa_fr(i)
            o.write('\t'.join([f'{ini:08x}', f'{fim:08x}', str(d['by']), str(d['nf']), str(d['nova']), str(d['alt']),
                               nome(T[i][0]) if i >= 0 else '', nome(T[i + 1][0]) if i + 1 < len(T) else '',
                               ', '.join(f'{os.path.basename(nome(m))}({n})' for m, n in soltas[i].most_common(8)),
                               ', '.join(f'{os.path.basename(nome(m))}({txt645[m]})' for m in cand[i][:12]) +
                               (f' +{len(cand[i]) - 12}' if len(cand[i]) > 12 else ''),
                               ', '.join(('' if c in cls645 else '*') + f'{c}({n})'
                                         for c, n in d['cls'].most_common(8)), gcl[i][0]]) + '\n')

    # ---- por unidade
    base = {}
    if a.base and os.path.exists(a.base_tsv):
        reb = {os.path.splitext(r['rebang'])[0].lower(): r['aqui']
               for r in csv.DictReader(open(a.imp), delimiter='\t') if r['aqui'].endswith(('.cpp', '.c'))}
        bt = {r['unidade']: r for r in csv.DictReader(open(a.base_tsv), delimiter='\t')}
        for m, md in mods.items():
            r = bt.get(reb.get(os.path.splitext(md['path'])[0].lower(), ''))
            if r:
                base[m] = r
    mapa = {}
    ondas = collections.Counter()
    ondab = collections.Counter()
    nanc = collections.Counter(v[1] for v in anc.values())
    ordem983 = []
    with open(f'{a.map}/projectg_units.tsv', 'w') as o:
        o.write('unidade\tgrupo\testado_rebang\tmodulo645\tobj645\tini645\tbytes645\tfuncs645\tancoras\tclasse_mapa\t'
                'ini983\tfim983\tbytes983\tfuncs983\tconcorda\tdiscorda\tnovas_j7\talteradas\tidenticas_839\t'
                'outros_trechos\tonda\tproprias_obj\tbytes_obj\tpct_bytes_igual_quase\tpct_bytes_sem_par\n')
        for m in sorted(mods, key=lambda m: (ini645.get(m, 1 << 32), m)):
            md = mods[m]
            if md['lib'] not in ('projectg.exe', 'fresh.lib', 'lua51.lib', 'freetype.lib') and m not in porU:
                continue
            ts = sorted(porU.get(m, []), key=lambda i: -(T[i][3]))
            if ts:
                i = ts[0]
                t, d = T[i], porT[i]
                forte = t[3] >= 3
                cm = 'forte' if forte else 'fraco'
                if forte:
                    ordem983.append((t[1], ini645.get(m, 0), m))
                cols = [f'{t[1]:08x}', f'{t[2]:08x}', str(d['by']), str(d['nf']), str(t[3]), str(t[4]),
                        str(d['nova']), str(d['alt']), str(d['idem']),
                        ' '.join(f'{T[j][1]:08x}-{T[j][2]:08x}({T[j][3]})' for j in ts[1:])]
            else:
                cm = 'sem_ancora' if not nanc[m] else 'so_ancoras_soltas'
                cols = [''] * 10
                if m in lugar:
                    cm, i = lugar[m]
                    x, y = faixa_fr(i)
                    cols = [f'{x:08x}', f'{y:08x}', str(fr[i]['by']), str(fr[i]['nf'])] + [''] * 6
            mapa[m] = cm
            # onda da F3.4 (indicador indireto: tamanho 983/645 e novas+alteradas JP x KR839 dentro da faixa)
            if md['grupo'] == 'lib':
                onda = '- biblioteca externa'
            elif md['estado'] != 'cpp':
                onda = '4 sem fonte no rebang'
            elif cm != 'forte':
                onda = '2 cpp, faixa incerta'
            else:
                rz = d['by'] / max(txt645[m], 1)
                mud = (d['nova'] + d['alt']) / max(d['nf'], 1)
                onda = '1 cpp, mudou pouco' if 0.7 <= rz <= 1.3 and mud <= 0.05 else '2 cpp, alterada'
            bcols = [''] * 4
            if a.base and md['grupo'] != 'lib' and md['estado'] == 'cpp':
                r = base.get(m)
                if r is None:
                    onda = '2 cpp, fora da linha de base'
                elif r['estado'] != 'ok':
                    onda = '2 cpp, nao compila'
                else:
                    bb = [int(r[k] or 0) for k in ('B_IGUAL', 'B_QUASE', 'B_DIFERENTE', 'B_SEM_PAR')]
                    tb = sum(bb)
                    pq = 100.0 * (bb[0] + bb[1]) / tb if tb else 0.0
                    bcols = [r['proprias'], str(tb), f'{pq:.1f}', f"{100.0 * bb[3] / tb if tb else 0.0:.1f}"]
                    onda = ('- cpp sem funcao propria' if not tb else '1 cpp, mudou pouco' if pq >= 50 else
                            '2 cpp, alterada')
            ondas[onda] += 1
            ondab[onda] += txt645[m]
            cols.append(onda)
            cols += bcols
            o.write('\t'.join([nome(m), md['grupo'], md['estado'], str(m), md['obj'],
                               f'{ini645[m]:08x}' if m in ini645 else '', str(txt645[m]), str(nf645[m]),
                               str(nanc[m]), cm] + cols) + '\n')

    # ---- trechos na ordem do 983
    with open(f'{a.out}/trechos_983.tsv', 'w') as o:
        o.write('ini983\tfim983\tunidade\tgrupo\testado\tconcorda\tdiscorda\tfuncs\tbytes\tnovas_j7\talteradas\n')
        for t, d in zip(T, porT):
            md = mods[t[0]]
            o.write('\t'.join([f'{t[1]:08x}', f'{t[2]:08x}', nome(t[0]), md['grupo'], md['estado'], str(t[3]),
                               str(t[4]), str(d['nf']), str(d['by']), str(d['nova']), str(d['alt'])]) + '\n')

    # ---- ordem de link: maior subsequência crescente das unidades fortes (ordem 983 x ordem 645)
    ordem983.sort()
    v = [x[1] for x in ordem983]
    tails = []
    for x in v:
        j = bisect.bisect_left(tails, x)
        if j == len(tails):
            tails.append(x)
        else:
            tails[j] = x
    lis = len(tails)

    # ---- resumo
    tot_f = len(f983)
    tot_b = sum(sz983.values())
    nuc_f = sum(d['nf'] for d in porT)
    nuc_b = sum(d['by'] for d in porT)
    R = []
    R.append(f'funcoes 645: {len(f645)}; modulos do PDB: {len(mods)}; funcoes 983 (export J6): {tot_f}, {tot_b} B')
    src = collections.Counter(v[2] for v in anc.values())
    R.append(f'ancoras: {len(anc)}  ' + ' '.join(f'{k}={v}' for k, v in sorted(src.items())))
    if a.base:
        R.append('ancoras obj x ancoras da F3.1 no mesmo endereco: ' +
                 ', '.join(f'{k}={v}' for k, v in sorted(cruz.items())) +
                 '; fora das ancoras obj: ' + ', '.join(f'{k}={v}' for k, v in sorted(fora_obj.items())))
        with open(f'{a.out}/ancoras_discordes.tsv', 'w') as o:
            o.write('va983\tfuncao_nossa\tunidade_pelo_obj\tunidade_pela_F3.1\tfonte_F3.1\n')
            for va, nm, m, m0, src0 in sorted(discordes_obj):
                o.write('\t'.join([va, nm, nome(m), nome(m0), src0]) + '\n')
    R.append(f'trechos: {len(T)}; unidades com trecho: {len(porU)}; com trecho forte (>=3 ancoras concordes): '
             f'{len(ordem983)}')
    R.append(f'ancoras concordes com o trecho: {sum(t[3] for t in T)}; discordes: {sum(t[4] for t in T)}')
    R.append(f'funcoes 983 em nucleo: {nuc_f} ({100 * nuc_f / tot_f:.1f}%), {nuc_b} B ({100 * nuc_b / tot_b:.1f}%); '
             f'em fronteira: {tot_f - nuc_f}, {tot_b - nuc_b} B')
    R.append(f'ordem de link: {lis} de {len(ordem983)} unidades fortes na mesma ordem relativa do 645')
    tv = sum(val.values())
    R.append('validacao por retirada (5 partes, %d ancoras de funcao): ' % tv +
             ', '.join(f'{k}={v} ({100 * v / tv:.1f}%)' for k, v in sorted(val.items())))
    est = collections.Counter()
    estb = collections.Counter()
    for m, md in mods.items():
        if md['grupo'] == 'lib' or m not in mapa:
            continue
        est[(md['grupo'], md['estado'], mapa[m])] += 1
        estb[(md['grupo'], md['estado'], mapa[m])] += txt645[m]
    R.append('unidades do rebang por grupo / estado no rebang / classe do mapa: quantas, bytes de .text no 645')
    for k, v in sorted(est.items()):
        R.append(f'  {k[0]:9s} {k[1]:4s} {k[2]:18s} {v:4d} {estb[k]:9d}')
    regs = [(0x401000, 'A RF (UI nova, sem par no 645)'), (0x491ca0, 'B mistura'), (0x525cf0, 'C unidades do jogo'),
            (0xb50000, 'D bibliotecas (Wangreal, png, Fresh, lua)'), (0xc3d000, 'E GameGuard, CRT, blocos de excecao')]
    rg = collections.defaultdict(collections.Counter)
    for f9, sz, onde, un, i, a6, src, am, cat, n9 in linhas:
        va = int(f9, 16)
        g = [r for r in regs if r[0] <= va][-1]
        rg[g]['f'] += 1
        rg[g]['b'] += sz
        rg[g]['nb'] += sz if onde == 'nucleo' else 0
        if onde != 'nucleo':
            rg[g][gcl[i][0]] += sz
        rg[g]['a'] += 1 if src else 0
    R.append('ondas (unidades do rebang; com --base = % dos bytes proprios IGUAL+QUASE na linha de base): quantas, bytes de .text no 645')
    for k in sorted(ondas):
        R.append(f'  {k:24s} {ondas[k]:4d} {ondab[k]:9d}')
    R.append('regioes do 983 (inicio, funcoes, bytes, ancoras; % dos bytes: nucleo, vao_unidade, vao_novo, '
             'vao_borda, fronteira):')
    for g in regs:
        c = rg[g]
        R.append(f"  {g[0]:08x} {g[1]:42s} {c['f']:6d} {c['b']:8d} {c['a']:5d}  " + ' '.join(
            f"{100 * c[k] / max(c['b'], 1):5.1f}%" for k in ('nb', 'vao_unidade', 'vao_novo', 'vao_borda', 'fronteira')))
    open(f'{a.out}/resumo.txt', 'w').write('\n'.join(R) + '\n')
    print('\n'.join(R))


if __name__ == '__main__':
    main()
