#!/usr/bin/env python3
"""replayoffs.py [--aplica] ARQ... — troca deslocamentos crus do KR 645 do bloco de replay do CSharedDoc
(0x5b94..0x5bd4 no 645; 0x11224..0x11284 no 983) pelos membros do shareddoc.h (s88).
Sem --aplica só lista. Formas reconhecidas: SHAREDDOC_ULONG(off), SDOC(T, off), DOC_FIELD(T, off), DocInt(off),
FIELD(T, p, off), *(T*)((char*|unsigned char*)X + off), *((unsigned char*)X + off)."""
import re, sys
M = {0x5b94: 'm_replayState', 0x5b98: 'm_replayPlayType', 0x5b9c: 'm_playingMode', 0x5bc0: 'm_replayPosition',
     0x5bc4: 'm_replayDuration', 0x5bc8: 'm_replayTick', 0x5bcc: 'm_replayShotIndex', 0x5bd0: 'm_replayHoleStroke',
     0x5bd4: 'm_replayVersion'}
INTS = ('int', 'unsigned long', 'unsigned int', 'long')
def acc(doc, off, T):
    m = M[off]; e = '%s->%s' % (doc, m)
    if T in INTS or T is None or (m == 'm_replayHoleStroke' and T == 'unsigned char'): return e
    return '*(%s*)&%s' % (T, e)
OFF = r'(0x5b9[48c]|0x5bc[048c]|0x5bd[04])'
PATS = [
    (r'SHAREDDOC_ULONG\(%s\)' % OFF, lambda g: acc('Doc()', int(g[0], 16), None)),
    (r'SDOC\(([\w ]+), %s\)' % OFF, lambda g: acc('Doc()', int(g[1], 16), g[0])),
    (r'DOC_FIELD\(([\w ]+), %s\)' % OFF, lambda g: acc('Doc()', int(g[1], 16), g[0])),
    (r'DocInt\(%s\)' % OFF, lambda g: acc('Doc()', int(g[0], 16), None)),
    (r'FIELD\(([\w ]+), (CSharedDoc::Instance\(\)|Doc\(\)), %s\)' % OFF, lambda g: acc(g[1], int(g[2], 16), g[0])),
    (r'\*\(([\w ]+)\*\)\(\((?:unsigned )?char\*\)(CSharedDoc::Instance\(\)|Doc\(\)) \+ %s\)' % OFF,
     lambda g: acc(g[1], int(g[2], 16), g[0])),
    (r'\*\(\(unsigned char\*\)(CSharedDoc::Instance\(\)|Doc\(\)) \+ %s\)' % OFF,
     lambda g: acc(g[0], int(g[1], 16), 'unsigned char')),
]
ap = '--aplica' in sys.argv; tot = 0
for fn in [a for a in sys.argv[1:] if a != '--aplica']:
    s = open(fn, encoding='latin-1').read(); n0 = 0
    for p, f in PATS:
        def rep(mo):
            global tot
            r = f(mo.groups()); print('%s:%d\t%s\t->\t%s' % (fn, s.count('\n', 0, mo.start()) + 1, mo.group(0), r)); return r
        s, k = re.subn(p, rep, s); n0 += k
    tot += n0
    if ap and n0: open(fn, 'w', encoding='latin-1').write(s)
print('trocas: %d%s' % (tot, '' if ap else ' (só listado)'), file=sys.stderr)
