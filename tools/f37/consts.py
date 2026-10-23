#!/usr/bin/env python3
"""f37/consts.py <arquivo do dfull.sh> — sequência das constantes de ponto flutuante dos dois lados (.obj: nome `__real@…`;
983: valor lido no endereço) e dos imediatos ≥ 0x10 de cmp/mov/push/and/test/add/sub; imprime onde diferem."""
import sys, re, struct, os, difflib
R_ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = open(R_ + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    for vs, v, rs, ro in secs:
        if v <= va - base < v + max(vs, rs): return ro + va - base - v
L = []; R = []; LI = []; RI = []
for l in open(sys.argv[1]):
    if l.startswith('---'): continue
    x = l[3:104].strip(); y = l[104:].strip()
    m = re.search(r'__real@([0-9a-f]+)', x)
    if m:
        h = m.group(1); v = struct.unpack('>f' if len(h) == 8 else '>d', bytes.fromhex(h))[0]; L.append('%.6g' % v)
    m = re.match(r'f\w+ (dword|qword) ptr \[0x([0-9a-f]{6,8})\]', y)
    if m and 0xcf0000 <= int(m.group(2), 16) < 0xe40000:
        o = off(int(m.group(2), 16)); v = struct.unpack_from('<f' if m.group(1) == 'dword' else '<d', d, o)[0]; R.append('%.6g' % v)
    for t, out in ((x, LI), (y, RI)):
        if '<' in t: continue
        m = re.match(r'(cmp|mov|push|and|test|add|sub|or|imul) .*?[, ](0x[0-9a-f]+|\d+)$', t)
        if m and 'esp' not in t:
            v = int(m.group(2), 0)
            if v >= 0x10: out.append('%s %x' % (m.group(1), v))
for nm, a, b in (('float', L, R), ('imediato', LI, RI)):
    print(nm, 'L=%d R=%d' % (len(a), len(b)), 'conjuntos iguais' if sorted(a) == sorted(b) else 'CONJUNTOS DIFEREM: só L %s | só R %s' % (
        sorted(set(a) - set(b)), sorted(set(b) - set(a))))
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag != 'equal': print('  ', tag, a[i1:i2], '|', b[j1:j2])
