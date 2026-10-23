#!/usr/bin/env python3
"""vtcmp.py VA983 VA_NOSSO N — compara slot a slot uma vtable da wangreal 983 com a da nossa dll.
Cada slot: função do 983 × função nossa; 'ok' se o par (out/F2.11/image/funcoes.tsv ou map) bate."""
import sys, struct, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def load(p):
    d = open(p, 'rb').read()
    pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
    oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
    secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
    def rd(va):
        rva = va - base
        for vs, v, rs, ro in secs:
            if v <= rva < v + max(vs, rs): return struct.unpack_from('<I', d, ro + rva - v)[0]
    return rd
ref = load(os.path.join(R, 'ref/wangreal_983.dll'))
our = load(sys.argv[4] if len(sys.argv) > 4 else os.path.join(R, 'build/wangreal-full/wangreal.dll'))
n983 = {}; pair = {}
for l in open(os.path.join(R, 'map/wangreal.tsv')):
    p = l.rstrip('\n').split('\t')
    if len(p) > 1 and not l.startswith('#'):
        try: n983.setdefault(int(p[1], 16), p[0])
        except ValueError: pass
nn = {}
mp = os.path.join(R, 'build/wangreal-full/wangreal.map')
for l in open(mp):
    p = l.split()
    if len(p) >= 3 and p[0].startswith('000') and ':' in p[0]:
        try: nn.setdefault(int(p[2], 16), p[1])
        except ValueError: pass
for l in open(os.path.join(R, 'out/F2.11/image/funcoes.tsv')):
    p = l.rstrip('\n').split('\t')
    if p[0] == 'classe' or p[4] in ('', '-'): continue
    try: pair[int(p[4], 16)] = (int(p[2], 16), p[0])
    except ValueError: pass
a, b, n = int(sys.argv[1], 16), int(sys.argv[2], 16), int(sys.argv[3])
bad = 0
for i in range(n):
    f983, fn = ref(a + 4 * i), our(b + 4 * i)
    pr = pair.get(fn)
    ok = 'ok' if pr and pr[0] == f983 else ('NOME' if n983.get(f983) == nn.get(fn) and nn.get(fn) else 'DIF')
    if ok == 'DIF': bad += 1
    print('%3d %08x %08x %-4s %-6s %s | %s' % (i, f983, fn, ok, pr[1] if pr else '-', n983.get(f983, '?')[:70], nn.get(fn, '?')[:70]))
print('# slots diferentes:', bad)
