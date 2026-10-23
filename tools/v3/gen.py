#!/usr/bin/env python3
"""V3: gera include/asserts/<unidade>.h (static_assert de sizeof/offsetof com os valores do exe 983).

  gen.py [OUT_DIR=out/V3]
Entradas: OUT_DIR/sizes_983.tsv + news_983.tsv (sizes983.py), OUT_DIR/sizes_obj.tsv (sizes_obj.py), tools/v3/manual.tsv
(asserts levantados à mão: tipo, classe, membro, valor, unidade, evidência) e tools/v3/unidade.tsv (classe -> unidade onde
ela é completa, ou `-` para não gerar; corrige a escolha automática).
Unidade de cada classe: a que define o construtor; senão a que dá `new`; senão a do cabeçalho que declara a classe.
Saída: os .h, OUT_DIR/asserts.tsv (um assert por linha) e OUT_DIR/sem_fonte.tsv (classes do 983 sem declaração no fonte)."""
import sys, os, re, csv, glob, collections
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, R + '/tools/f32'); import pgbuild as pb
sys.path.insert(0, R + '/tools/v3'); import jpunits
out = sys.argv[1] if len(sys.argv) > 1 else R + '/out/V3'
def tsv(p): return list(csv.DictReader((l for l in open(p) if not l.startswith('#')), delimiter='\t')) if os.path.exists(p) else []
s9 = tsv(out + '/sizes_983.tsv'); so = {r['classe_decorada']: r for r in tsv(out + '/sizes_obj.tsv')}
first = {}
for r in tsv(out + '/news_983.tsv'):
    for k in ('classe_em_linha', 'classe_mapa', 'classe_rtti_ctor'):
        if r[k] != '-': first.setdefault(r[k], (r['va_new'], r['ctor'])); break
ovr = {r['classe']: r['unidade'] for r in tsv(R + '/tools/v3/unidade.tsv')}
units = [u[0] for u in pb.units()] + [u[0] for u in jpunits.units()]; uset = set(units)   # V7: + unidades novas do JP
# índice das declarações: nome simples -> [arquivo]
decl = collections.defaultdict(list); inc = collections.defaultdict(list); text = {}
files = [f for pat in ('src/**/*.h', 'src/**/*.cpp', 'src/**/*.inl', 'include/**/*.h') for f in glob.glob(R + '/' + pat, recursive=True)]
for f in files:
    if '/asserts/' in f or ('/lib/' in f and '/refresh/lib/' not in f) or '/third_party/' in f: continue   # C96: a lib da RF tambem tem anotacoes (B)
    t = open(f, encoding='latin1').read(); rel = os.path.relpath(f, R); text[rel] = t
    for m in re.finditer(r'^[ \t]*(?:class|struct)\s+(?:\w+\s+)?(\w+)\s*(?:final\s*)?(?::[^;{]*)?\{', t, re.M): decl[m.group(1)].append(rel)
    if rel in uset:
        for m in re.finditer(r'#\s*include\s*["<]([^">]+)[">]', t): inc[os.path.basename(m.group(1)).lower()].append(rel)
def unit_of(dec):
    if dec in ovr and ovr[dec] != '-anot': return ovr[dec], 'unidade.tsv'
    o = so.get(dec)
    if o:
        h = [u for u in o['unidade_casa'].split(',') if u in uset]
        if len(h) == 1: return h[0], 'construtor'
        n = [u for u in o['unidades_new'].split(',') if u in uset]
        if h: return (sorted(set(h) & set(n)) or h)[0], 'construtor'
        if n: return n[0], 'new'
    for f in decl.get(dec.split('@')[0], []):
        if f in uset: return f, 'declarada na unidade'
        c = f[:-2] + '.cpp'
        for cand in (c, c.replace('include/engine/', 'src/engine/'), c.replace('src/fresh/include/', 'src/fresh/source/'),
                     c.replace('include/jp/', 'src/projectg/jp/')):
            if cand in uset: return cand, 'cabeçalho'
        us = inc.get(os.path.basename(f).lower())
        if us: return us[0], 'inclui o cabeçalho'
    return None, ''
A = []    # (unidade, tipo, classe C++, membro, valor, evidência, nosso pelo .obj)
semf = []; semu = []
for r in s9:
    dec = r['classe_decorada']; cx = r['classe']
    if cx == '-': continue
    u, how = unit_of(dec)
    if u == '-': continue
    va, ct = first.get(dec, ('?', '-'))
    ev = '983: push %s; call operator new em %s%s (%s; %s new)' % (r['sizeof_983'], va, '' if ct == '-' else ', construtor ' + ct, r['fontes'], r['news'])
    if not u: semf.append((dec, cx, r['sizeof_983'], r['news'], r['fontes'], va, ct)); continue
    A.append((u, 'SIZE', cx, '', r['sizeof_983'], ev + '; unidade por ' + how, so.get(dec, {}).get('sizeof_nosso', '-')))
have = {(a[1], a[2], a[3]) for a in A}
cu = {a[2]: a[0] for a in A}
fora = {(r['classe'], r['membro']) for r in tsv(R + '/tools/v3/anot_fora.tsv')}
for r in tsv(R + '/tools/v3/manual.tsv') + tsv(out + '/anot.tsv'):
    k = (r['tipo'], r['classe'], r['membro'] if r['membro'] != '-' else '')
    if (r['classe'], k[2]) in fora and r['evidencia'].startswith('anot:'): continue   # comentário velho (tools/v3/anot_fora.tsv)
    if k in have: continue      # já há assert igual (o automático do `new` vale mais que a anotação)
    pp = r['classe'].split('::')
    while len(pp) > 1 and pp[0] not in decl: pp = pp[1:]     # C10: namespace na frente (IFF983::sAbility) não é a classe de fora
    u = r['unidade']; top = pp[0]
    if '-anot' in (ovr.get(r['classe']), ovr.get(top)) and r['evidencia'].startswith('anot:'): semu.append(r); continue
    if u == '-': u = ovr.get(r['classe']) or cu.get(r['classe']) or cu.get(top) or ovr.get(top) or unit_of(top)[0]
    if not u or u == '-': semu.append(r); continue
    cu.setdefault(top, u)
    A.append((u, 'ANOT' if r['evidencia'].startswith('anot:') else r['tipo'], r['classe'], k[2], r['valor'], r['evidencia'], '-')); have.add(k)
for f in glob.glob(R + '/include/asserts/*.h'):
    if os.path.basename(f) != 'v3.h': os.remove(f)
by = collections.defaultdict(list)
for a in A: by[a[0]].append(a)
def hname(u): return re.sub(r'^src_', '', u[:-4].replace('/', '_')) + '.h'
for u in sorted(by):
    with open(R + '/include/asserts/' + hname(u), 'w') as f:
        f.write('// V3: layout do 983 das classes vistas por %s (gerado por tools/v3/gen.py; não editar à mão).\n// unidade: %s\n' % (u, u))
        for _, t, c, m, v, ev, _n in sorted(by[u], key=lambda a: (a[2], a[1] != 'SIZE', int(a[4], 16))):
            f.write(('V3_SIZE(%s, %s)' % (c, v) if t == 'SIZE' else 'V3_%s(%s, %s, %s)' % (t, c, m, v)) + ' // ' + ev + '\n')
with open(out + '/asserts.tsv', 'w') as f:
    f.write('unidade\tcabecalho\ttipo\tclasse\tmembro\tvalor_983\tsizeof_nosso_obj\tevidencia\n')
    for u, t, c, m, v, ev, n in sorted(A): f.write('\t'.join((u, 'include/asserts/' + hname(u), t, c, m or '-', v, n, ev)) + '\n')
with open(out + '/sem_fonte.tsv', 'w') as f:
    f.write('classe_decorada\tclasse\tsizeof_983\tnews\tfontes\tva_new\tctor\n')
    for r in semf: f.write('\t'.join(r) + '\n')
if semu: print('sem unidade (não gerados):', sorted({r['classe'] for r in semu}))
print('asserts: %d (%d sizeof, %d offsetof do 983, %d offsetof de anotação) em %d cabeçalhos; classes do 983 sem declaração no fonte: %d' % (
    len(A), sum(1 for a in A if a[1] == 'SIZE'), sum(1 for a in A if a[1] == 'OFF'), sum(1 for a in A if a[1] == 'ANOT'), len(by), len(semf)))
