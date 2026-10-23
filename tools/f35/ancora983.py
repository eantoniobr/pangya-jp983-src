#!/usr/bin/env python3
"""ancora983.py [saida.tsv] — funções do exe 983 que posicionam pela tela REAL: leem [g_view(00f02458)]+0x19c/+0x1a0
(largura/altura em float). Por função: VA, nome do mapa, unidade, nº de leituras, se chama FrWnd::SetRect/MoveWindow,
e se o nome existe no nosso fonte (map/projectg.tsv). Base do item 0(a) da out/F4/PRIORIDADE.md (A169)."""
import sys, struct, bisect
sys.path.insert(0, '/root/jp983src/tools/f35')
from pe983 import d, secs, ib
R = '/root/jp983src/'
F = []
for l in open(R + 'map/projectg_funcs.tsv').read().split('\n')[1:]:
    p = l.split('\t')
    if len(p) > 10: F.append((int(p[0], 16), p[10], p[3].replace('source/client/ProjectG/', '')))
F.sort(); ks = [f[0] for f in F]
N = {}
for l in open(R + 'map/projectg.tsv'):
    p = l.rstrip('\n').split('\t')
    if len(p) > 1 and not l.startswith('#'): N.setdefault(int(p[1], 16), p[0])
va0, vs0, ro0, rs0 = secs[0]
code = d[ro0:ro0 + rs0]; base = ib + va0
def fun(va):
    i = bisect.bisect_right(ks, va) - 1
    return F[i] if i >= 0 else (0, '?', '?')
G = struct.pack('<I', 0x00f02458)
hits = {}
for disp in (0x19c, 0x1a0):
    pat = struct.pack('<I', disp); i = code.find(pat)
    while i >= 0:
        op, modrm = code[i - 2], code[i - 1]
        if op in (0xd9, 0x8b, 0xd8, 0xdc) and (modrm >> 6) == 2 and (modrm & 7) != 4:
            f = fun(base + i - 2)
            h = hits.setdefault(f[0], [f, 0, 0]); h[1 if disp == 0x19c else 2] += 1
        i = code.find(pat, i + 1)
SR = {0x00be87c0}  # FrWnd::SetRect(const WRect&)
for v, n in N.items():
    if '?SetRect@FrWnd' in n or '?MoveWindow@Fr' in n: SR.add(v)
out = []
for fva, (f, nw, nh) in sorted(hits.items()):
    nxt = ks[bisect.bisect_right(ks, fva)] if bisect.bisect_right(ks, fva) < len(ks) else fva + 0x1000
    body = code[fva - base:nxt - base]
    if G not in body: continue
    calls = set()
    for j in range(len(body) - 5):
        if body[j] == 0xe8: calls.add((fva + j + 5 + struct.unpack_from('<i', body, j + 1)[0]) & 0xffffffff)
    nome = N.get(fva, f[1])
    out.append('%08x\t%s\t%s\t%d\t%d\t%s\t%s' % (fva, nome, f[2] or '-', nw, nh, 'sim' if calls & SR else 'nao',
                                                 'sim' if fva in N else 'nao'))
hdr = 'va983\tnome\tunidade\tleituras_w\tleituras_h\tSetRect_ou_Move\tno_mapa'
txt = hdr + '\n' + '\n'.join(out) + '\n'
(open(sys.argv[1], 'w').write(txt) if len(sys.argv) > 1 else sys.stdout.write(txt))
print('%d funções' % len(out), file=sys.stderr)
