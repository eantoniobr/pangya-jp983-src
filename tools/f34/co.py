#!/usr/bin/env python3
"""co.py Classe [lo hi] — offs.py --aberto achando o cabeçalho sozinho (src/projectg, src/fresh/include, include/engine);
mostra `desloc campo` com lo <= desloc < hi. Com -t, a linha de declaração junto."""
import sys, os, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import offs as O
R = O.ROOT
def header(cls):
    for p in sorted(glob.glob(R + '/src/projectg/*.h') + glob.glob(R + '/src/fresh/include/*.h') + glob.glob(R + '/include/engine/*.h') + glob.glob(R + '/src/shared/*.h')):
        if re.search(r'\nclass %s\b[^;{]*\{' % cls, open(p, encoding='latin-1').read()): return p
def layout(cls):
    h = header(cls); O.OPEN = True
    return h, O.measure(cls, O.fields(cls, h), (), os.path.abspath(h).replace('/', '\\\\').join(['Z:', '']))
if __name__ == '__main__':
    av = [a for a in sys.argv[1:] if a != '-t']; cls = av[0]
    lo = int(av[1], 0) if len(av) > 1 else 0; hi = int(av[2], 0) if len(av) > 2 else 1 << 30
    h, L = layout(cls); print('#', os.path.relpath(h, R)); src = open(h, encoding='latin-1').read()
    for n, v in L:
        if lo <= v < hi or n == 'sizeof':
            d = re.search(r'\n[ \t]*([^\n;]*\b%s\b[^\n;]*;)' % n, src) if '-t' in sys.argv else None
            print('0x%04x %s%s' % (v, n, '   | ' + d.group(1) if d else ''))
