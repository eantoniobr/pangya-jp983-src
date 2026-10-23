#!/usr/bin/env python3
"""f37/gemeo2.py <RefStem> <ini ref> <fim ref> <NewStem> <ini novo> <fim novo> <habilidade ref hex> <habilidade nova hex>
Gera um par controlador/objeto gêmeo de um par já escrito (qualquer um, não só o PangyaCorrection do gemeo.py): copia
include/jp/<ref>{controller,object}.h e src/projectg/jp/<ref>{controller,object}.cpp trocando o nome (C<Stem>…, <stem>… em minúsculas),
os endereços (pela ordem dos inícios de função das duas faixas, que têm de ter a mesma contagem) e a habilidade; acrescenta as
linhas em jp.tsv e units.txt. Conferir ANTES por diff do desmonte normalizado (norm.py) que só mudam vtable, nome e habilidade.
O cabeçalho de comentário dos .cpp vira uma linha só; o enum eSpecialAbility_<NewStem> tem de ser posto à mão em controlledobject.h."""
import sys, os, re, subprocess
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rs, ri, rf, ns, ni, nf, ra, na = sys.argv[1:]
def starts(a, b, tag):
    o = subprocess.run([sys.executable, R + '/tools/f37/dz.py', a, '0x' + b], stdout=subprocess.PIPE, text=True).stdout
    t = '/tmp/gemeo2_%s.txt' % tag; open(t, 'w').write(o)
    return subprocess.run([sys.executable, R + '/tools/f37/ini.py', t], stdout=subprocess.PIPE, text=True).stdout.split()[2:]
ref = starts(ri, rf, 'r'); new = starts(ni, nf, 'n')
assert len(ref) == len(new), (len(ref), len(new))
amap = dict(zip(ref, new))
ra, na = int(ra, 16), int(na, 16)
def tr(s):
    s = s.replace(rs, ns).replace(rs.lower(), ns.lower())
    s = re.sub(r'\b00[0-9a-f]{6}\b', lambda m: amap.get(m.group(0), m.group(0)), s)
    return s.replace('habilidade 0x%02x' % ra, 'habilidade 0x%02x' % na).replace('{ 0x%02x,' % ra, '{ 0x%02x,' % na)
for d, e in (('include/jp', '.h'), ('src/projectg/jp', '.cpp')):
    for k in ('controller', 'object'):
        s = tr(open('%s/%s/%s%s%s' % (R, d, rs.lower(), k, e)).read())
        if e == '.cpp':
            s = re.sub(r'\A(//.*\n)+', '// JP 983: unidade do C%s%s (faixa %s–%s com o par; gêmea do C%s%s, gerada por tools/f37/gemeo2.py e conferida no 983).\n'
                       % (ns, k.capitalize(), ni, nf, rs, k.capitalize()), s)
        open('%s/%s/%s%s%s' % (R, d, ns.lower(), k, e), 'w').write(s)
t = R + '/src/projectg/jp/jp.tsv'; L = open(t).read().splitlines(); have = set(l.split('\t')[0] for l in L)
for l in list(L):
    p = l.split('\t')
    if len(p) > 1 and p[1] in amap and rs in p[0]:
        n = p[0].replace(rs, ns)
        if n not in have: L.append(n + '\t' + amap[p[1]])
open(t, 'w').write('\n'.join(L) + '\n')
u = R + '/src/projectg/jp/units.txt'; s = open(u).read()
for k in ('controller', 'object'):
    f = ns.lower() + k + '.cpp\n'
    if f not in s: s += f
open(u, 'w').write(s)
print(ns, len(new), 'funções', ni, nf)
