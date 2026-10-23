#!/usr/bin/env python3
"""Frente C, C-PKT lote 9 — sizeof dos blocos lidos pelos despachantes, medido pelo COMPILADOR.

  sz.py   -> out/V4/sizeof_fonte.tsv (arquivo, expressão de tipo, sizeof) — lido pelo tools/v4/rx.py
Para cada despachante de tools/v4/rx.py junta as expressões `sizeof(...)` dos `DecodeBuffer` (variável local -> tipo da
declaração no caso), monta uma sonda `char (*p)[sizeof(T)] = 1;` depois da unidade inteira e compila com `cl /Zs`
(mesmo esquema do tools/v3/layoutcheck.py; ~10–40 s por unidade). O erro C2440 de cada linha traz o tamanho.
Rodar de novo quando a frente A mudar layout (os valores são do cabeçalho do momento)."""
import sys, os, re, types
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, R + '/tools/v4'); import rx
sys.path.insert(0, R + '/tools/f32'); import pgbuild as pb
B = R + '/build/C'
os.makedirs(B + '/sz', exist_ok=True)
open(B + '/v3pre.h', 'w').write('#define private public\n#define protected public\n')
US = {u[0]: u for u in pb.units()}
ns = types.SimpleNamespace(flags=None)
tz = rx.tamanhos()
rows = []
for va, arq, func, *_ in rx.DISP:
    if not arq or arq not in US:
        continue
    fonte = rx.casos_fonte(arq, func)
    pede = []
    for idn, txt in (fonte or {}).items():
        rx.leituras_fonte(txt, tz, arq, None, pede)
    exprs = sorted(set(pede))
    if not exprs:
        continue
    src, rb, pch, fi, einc = US[arq]
    if pch:
        fi = [('/FI' + R + '/' + os.path.dirname(pch) + '/' + f[3:]) if f.startswith('/FI') and os.path.exists(R + '/' + os.path.dirname(pch) + '/' + f[3:]) else f for f in fi]
    args = ['/Zs'] + pb.base_args(ns, einc, src) + ['/I' + R + '/include', '/FI' + B + '/v3pre.h'] + fi
    w = '%s/sz/%s.cpp' % (B, os.path.basename(arq)[:-4])
    open(w, 'w').write('#include "%s/%s"\n' % (R, arq) + ''.join('char (*szp_%d)[sizeof(%s)] = 1;\n' % (i, e) for i, e in enumerate(exprs)))
    pb.cl(args + [w], w[:-4] + '.log')
    got = {}
    for l in open(w[:-4] + '.log', errors='replace'):
        m = re.search(r"'char \(\*\)\[(\d+)\]'", l)
        k = re.search(r'[\\/]sz[\\/][^\\/(]+\.cpp\((\d+)\)', l)
        if m and k and int(k.group(1)) >= 2:
            got[int(k.group(1)) - 2] = int(m.group(1))
    for i, e in enumerate(exprs):
        rows.append((arq, e, '0x%x' % got[i] if i in got else '?'))
    print('%-36s %3d expressões, %3d medidas' % (arq, len(exprs), len(got)))
with open(rx.SZF, 'w') as f:
    for r in rows:
        f.write('\t'.join(r) + '\n')
print('->', os.path.relpath(rx.SZF, R), len(rows), 'linhas;', sum(r[2] == '?' for r in rows), 'sem medida')
