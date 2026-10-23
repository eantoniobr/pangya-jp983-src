#!/usr/bin/env python3
# F3.2: classifica as unidades que não compilam (compila.tsv do pgbuild.py obj) -> nao_compilam.md.  Uso: falhas.py <dir de saída>
import re, sys, collections
out = sys.argv[1]
rows = [l.split('\t') for l in open(out + '/compila.tsv').read().split('\n')[1:] if l]
def cls(e):
    if re.search(r"'rb_|'Rb[A-Z]|rb_\w+'", e): return 'A caminho REBANG_SEMANTIC_ONLY incompleto (identificador rb_* só existe na versão naked/VC7.1)'
    if 'back_inserter' in e or '_Myptr' in e or "'second'" in e or '_Vector_const_iterator' in e: return 'B STL do VS2010 (falta <iterator>, interno _Myptr, pair, ponteiro como iterador)'
    if 'const char *' in e or 'WCHAR' in e or "'i' : undeclared" in e or '_set_security_error_handler' in e: return 'C conformidade/CRT do cl 16 (const, wchar_t nativo, escopo do for, CRT antigo)'
    if 'WMatrix::Rotate' in e or 'already has a body' in e: return 'D cabeçalho da engine no layout do 983 difere do 645 (WMatrix::Rotate, WVector2D::Normalize)'
    return 'E outro (ver o primeiro erro)'
c = collections.defaultdict(list)
for r in rows:
    if r[1] == 'nao': c[cls(r[2])].append((r[0], r[2]))
with open(out + '/nao_compilam.md', 'w') as f:
    f.write('# Unidades que não compilam com o VS2010 (F3.2) — %d de %d\n\n' % (sum(map(len, c.values())), len(rows)))
    for k in sorted(c):
        f.write('## %s — %d\n' % (k, len(c[k])))
        for u, e in c[k]: f.write('- %s — `%s`\n' % (u, re.sub(r'^.*?\) : ', '', e)[:140]))
        f.write('\n')
print('não compilam: %d de %d -> %s/nao_compilam.md' % (sum(map(len, c.values())), len(rows), out))
