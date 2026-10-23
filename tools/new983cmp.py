#!/usr/bin/env python3
# new983cmp.py <983_new.tsv> <nosso_new.tsv> <nosso.map> [saida.tsv] — A262: junta as tabelas do new983.py (983 e nosso) pelo nome
# da classe do construtor (983: map/projectg.tsv; nosso: .map do link). Chave = classe COM namespace (rf::TiXmlElement != TiXmlElement).
# Imprime: classes com 2+ tamanhos no NOSSO exe (estouro de heap certo, como o FrItemAttachCardDlg do A234) e pares 983 x nosso diferentes.
# Uso: objdump -d --no-show-raw-insn X.exe > X.dis; tools/new983.py X.dis <VA do ??2@YAPAXI@Z no .map> > nosso_new.tsv
import re, sys

def cls(n):
    m = re.match(r'\?\?0(\?\$)?([^@]+)@((?:[A-Za-z_]\w*@)*)@', n or '')
    if not m:
        return None
    ns = [x for x in m.group(3).split('@') if x]
    return '::'.join(list(reversed(ns)) + [('?$' if m.group(1) else '') + m.group(2)])

def tab(fn, names):
    t = {}
    for l in open(fn):
        c, s, a = l.rstrip('\n').split('\t')
        k = cls(names.get(c)) if c != '-' else None
        if k:
            e = t.setdefault(k, [set(), c, a])
            e[0].update(s.split(','))
    return t

v983 = {}
for l in open('map/projectg.tsv', errors='replace'):
    f = l.rstrip('\n').split('\t')
    if len(f) >= 2 and not l.startswith('#'):
        v983.setdefault(f[1].lower().zfill(8), f[0])
sym = {}
for l in open(sys.argv[3], errors='replace'):
    p = l.split()
    if len(p) >= 4 and p[0].startswith('0001:') and re.fullmatch(r'[0-9a-f]{8}', p[2]):
        sym.setdefault(p[2], p[1])
A, B = tab(sys.argv[1], v983), tab(sys.argv[2], sym)
rows = ['classe\tnew983\tnew_nosso\tctor983\tctor_nosso\tsituacao']
for k in sorted(set(A) | set(B)):
    a, b = A.get(k), B.get(k)
    sa = ','.join(sorted(a[0], key=lambda x: int(x, 16))) if a else ''
    sb = ','.join(sorted(b[0], key=lambda x: int(x, 16))) if b else ''
    sit = 'DOIS_TAMANHOS' if b and len(b[0]) > 1 else ('' if not a or not b else ('IGUAL' if sa == sb else 'DIFERENTE'))
    if b and not a:
        sit = sit or 'SO_NOSSO'
    rows.append('\t'.join([k, sa, sb, a[1] if a else '', b[1] if b else '', sit or 'SO_983']))
if len(sys.argv) > 4:
    open(sys.argv[4], 'w').write('\n'.join(rows) + '\n')
par = [r for r in rows[1:] if r.split('\t')[1] and r.split('\t')[2]]
print('983 com nome %d, nosso %d, par %d, iguais %d' % (len(A), len(B), len(par), sum(r.endswith('IGUAL') for r in par)))
for r in rows[1:]:
    if r.endswith('DOIS_TAMANHOS') or r.endswith('DIFERENTE'):
        print(r)
