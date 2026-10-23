#!/usr/bin/env python3
"""f37/seq.py <arquivo do dfull.sh> [base_hex tamanho_hex simbolo] — sequência de `call` (e, se der a base, dos acessos ao objeto
global [base, base+tamanho) × deslocamentos do símbolo no .obj) dos dois lados; imprime só onde as sequências diferem."""
import sys, re, difflib
f = sys.argv[1]; base = int(sys.argv[2], 16) if len(sys.argv) > 2 else None
size = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0; sym = sys.argv[4] if len(sys.argv) > 4 else None
L = []; R = []
for l in open(f):
    if l.startswith('---') or len(l) < 4: continue
    x = l[3:104].rstrip(); y = l[104:].rstrip()
    for side, t, out in (('L', x, L), ('R', y, R)):
        if not t: continue
        m = re.match(r'call\s+(.*)', t)
        if m:
            a = m.group(1)
            out.append('call ' + a[:60]); continue
        if base is None: continue
        if side == 'L':
            if '<' + sym[:6] in t:
                m = re.search(r'\[(0x[0-9a-f]+|[0-9])\]', t) or re.search(r'[ ,](0x[0-9a-f]+|[0-9])\b', t)
                out.append('+%x' % int(m.group(1), 16) if m else '+?')
        else:
            for m in re.finditer(r'0x([0-9a-f]{6,8})', t):
                v = int(m.group(1), 16)
                if base <= v < base + size: out.append('+%x' % (v - base)); break
# nomes do .obj não casam com endereços: compara calls só pela posição (rótulo genérico) e mostra os dois textos
kl = [x if x[0] == '+' else 'call' for x in L]; kr = [x if x[0] == '+' else 'call' for x in R]
sm = difflib.SequenceMatcher(None, kl, kr, autojunk=False)
print('L=%d R=%d itens' % (len(L), len(R)))
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal': continue
    print(tag, 'L[%d:%d]' % (i1, i2), ' '.join(L[i1:i2])[:300], '| R[%d:%d]' % (j1, j2), ' '.join(R[j1:j2])[:300])
if '-v' in sys.argv:
    for a, b in zip(L, R): print(a, '|', b)
