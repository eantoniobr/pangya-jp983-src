#!/usr/bin/env python3
"""fieldref.py OFF [OFF...] — lista as instruções que citam [reg + OFF] na wangreal 983 e na nossa dll, por função
(nomes: map/wangreal.tsv e build/wangreal-full/wangreal.map), e marca as funções com contagem diferente."""
import sys, os, struct, re, bisect, capstone, collections
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def text(p):
    d = open(p, 'rb').read()
    pe = struct.unpack_from('<I', d, 0x3c)[0]; oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]
    st = oh + struct.unpack_from('<H', d, pe + 20)[0]
    vs, va, rs, ro = struct.unpack_from('<IIII', d, st + 8)
    return d[ro:ro + vs], base + va
def names(kind):
    n = {}
    if kind == 'ref':
        for l in open(os.path.join(R, 'map/wangreal.tsv')):
            p = l.rstrip('\n').split('\t')
            if len(p) > 1 and not l.startswith('#'):
                try: n.setdefault(int(p[1], 16), p[0])
                except ValueError: pass
    else:
        for l in open(os.path.join(R, 'build/wangreal-full/wangreal.map')):
            p = l.split()
            if len(p) >= 3 and ':' in p[0] and p[0].startswith('0001'):
                try: n.setdefault(int(p[2], 16), p[1])
                except ValueError: pass
    return n
offs = [int(x, 16) for x in sys.argv[1:]]
pat = re.compile(r'\[e[a-z]{2} \+ (0x[0-9a-f]+)\]')
res = {}
for kind, path in (('ref', 'ref/wangreal_983.dll'), ('our', 'build/wangreal-full/wangreal.dll')):
    code, va = text(os.path.join(R, path)); nm = names(kind); ks = sorted(nm)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); md.skipdata = True
    cnt = collections.Counter(); lines = collections.defaultdict(list)
    for x in md.disasm(code, va):
        for m in pat.finditer(x.op_str):
            if int(m.group(1), 16) in offs:
                i = bisect.bisect_right(ks, x.address) - 1
                f = nm[ks[i]] if i >= 0 else '?'
                cnt[f] += 1; lines[f].append('%08x %s %s' % (x.address, x.mnemonic, x.op_str))
    res[kind] = (cnt, lines)
allf = sorted(set(res['ref'][0]) | set(res['our'][0]))
for f in allf:
    a, b = res['ref'][0][f], res['our'][0][f]
    print('%s %3d %3d %s' % ('  ' if a == b else '!!', a, b, f[:110]))
    if a != b:
        for k in ('ref', 'our'):
            for l in res[k][1][f]: print('      %s %s' % (k, l))
