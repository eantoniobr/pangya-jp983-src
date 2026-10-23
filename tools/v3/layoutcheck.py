#!/usr/bin/env python3
"""V3: `make layoutcheck` — compila (cl /Zs, sem pch) cada unidade seguida do seu include/asserts/<unidade>.h.

  layoutcheck.py [-j N] [--out out/V3] [filtro...]
Cada cabeçalho de include/asserts diz a unidade na 2ª linha (`// unidade: src/...cpp`). O embrulho em build/C/chk inclui
a unidade inteira (com as flags/includes dela, de tools/f32/pgbuild.py; as unidades novas do JP, de tools/v3/jpunits.py) e depois os asserts; `private`/`protected` viram
`public` só nesta compilação (build/C/v3pre.h) para o sizeof/offsetof alcançar membros e classes internas.
Assert que falha: uma 2ª compilação mede o valor nosso. Saída: <out>/layoutcheck.tsv e resumo; sai com 1 se algo falha."""
import sys, os, re, glob, argparse, types, collections, concurrent.futures as cf
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, R + '/tools/f32'); import pgbuild as pb
sys.path.insert(0, R + '/tools/v3'); import jpunits
ap = argparse.ArgumentParser(); ap.add_argument('filt', nargs='*'); ap.add_argument('-j', type=int, default=8); ap.add_argument('--out', default=R + '/out/V3')
a = ap.parse_args(); B = R + '/build/C'; os.makedirs(B + '/chk', exist_ok=True)
open(B + '/v3pre.h', 'w').write('#define private public\n#define protected public\n')
US = {u[0]: u for u in pb.units() + jpunits.units()}; ns = types.SimpleNamespace(flags=None)
LN = re.compile(r'^(V3_SIZE|V3_OFF|V3_ANOT)\((.+?), (?:(\w+), )?(0x[0-9a-f]+)\)\s*//\s*(.*)$')
def run(h):
    name = os.path.basename(h)[:-2]; lines = open(h).read().split('\n'); unit = lines[1].split('unidade:')[1].strip()
    items = {i + 1: LN.match(l).groups() for i, l in enumerate(lines) if LN.match(l)}
    src, rb, pch, fi, einc = US[unit]
    # sem pch, `/FIstdafx.h` seria procurado nas pastas de inclusão e podia achar o stdafx.h de OUTRA biblioteca
    # (frlistbox.cpp pegava o do exe em vez do da Fresh): usa o cabeçalho que fica ao lado do .cpp do pch da unidade.
    if pch: fi = [('/FI' + R + '/' + os.path.dirname(pch) + '/' + f[3:]) if f.startswith('/FI') and os.path.exists(R + '/' + os.path.dirname(pch) + '/' + f[3:]) else f for f in fi]
    args = ['/Zs'] + pb.base_args(ns, einc, src) + ['/I' + R + '/include', '/FI' + B + '/v3pre.h'] + fi
    def comp(tag, extra):
        w = '%s/chk/%s%s.cpp' % (B, name, tag)
        open(w, 'w').write('#include "%s/%s"\n#include "asserts/v3.h"\n%s' % (R, unit, extra))
        pb.cl(args + [w], w[:-4] + '.log')
        return open(w[:-4] + '.log', errors='replace').read().replace('\r', '').split('\n')
    log = comp('', '#include "asserts/%s.h"\n' % name)
    res = {i: ['ok', '', ''] for i in items}; outros = []
    for l in log:
        m = re.search(r'asserts[\\/]%s\.h\((\d+)\)\s*:\s*(?:fatal )?error (C\d+): (.*)' % re.escape(name), l)
        if m and int(m.group(1)) in res:
            r = res[int(m.group(1))]
            if m.group(2) == 'C2338':
                if r[0] == 'ok': r[0] = 'FALHA'
            elif r[0] != 'erro': r[0] = 'erro'; r[2] = m.group(2) + ' ' + m.group(3)[:200]   # tipo incompleto/desconhecido: não conferido
        elif ' error ' in l: outros.append(l.strip()[:300])
    if outros:      # a unidade não compila no embrulho: nada foi conferido de verdade
        for i in res:
            if res[i][0] == 'ok': res[i] = ['nao_compila', '', outros[0]]
    bad = [i for i in res if res[i][0] == 'FALHA']
    if bad:
        pr = ''.join('char (*v3p_%d)[%s] = 1;\n' % (i, 'sizeof(%s)' % items[i][1] if items[i][0] == 'V3_SIZE' else '1 + offsetof(%s, %s)' % items[i][1:3]) for i in bad)
        for l in comp('_mede', pr):
            m = re.search(r"'char \(\*\)\[(\d+)\]'", l); k = re.search(r'_mede\.cpp\((\d+)\)', l)
            if m and k:
                i = bad[int(k.group(1)) - 3]; res[i][1] = '0x%x' % (int(m.group(1)) - (items[i][0] != 'V3_SIZE'))
    for i in bad:
        if items[i][0] == 'V3_ANOT': res[i][0] = 'anot_velha'
    return [(unit, 'include/asserts/%s.h' % name, items[i][0][3:], items[i][1], items[i][2] or '-', items[i][3]) + tuple(res[i]) + (items[i][4],) for i in sorted(items)]
hs = sorted(h for h in glob.glob(R + '/include/asserts/*.h') if os.path.basename(h) != 'v3.h' and (not a.filt or any(f in h for f in a.filt)))
rows = []
with cf.ThreadPoolExecutor(a.j) as ex:
    for r in ex.map(run, hs): rows += r
c = collections.Counter(r[6] for r in rows)
if not a.filt:
    with open(a.out + '/layoutcheck.tsv', 'w') as f:
        f.write('unidade\tcabecalho\ttipo\tclasse\tmembro\tvalor_983\tresultado\tvalor_nosso\terro\tevidencia\n')
        for r in rows: f.write('\t'.join(r) + '\n')
    open(a.out + '/layoutcheck_resumo.txt', 'w').write('layoutcheck: %d asserts em %d unidades: %s\n' % (len(rows), len(hs), ', '.join('%s %d' % x for x in c.most_common())))
print('layoutcheck: %d asserts em %d unidades: %s' % (len(rows), len(hs), ', '.join('%s %d' % x for x in c.most_common())))
for r in rows:
    if r[6] not in ('ok', 'anot_velha'): print('  %-11s %-4s %-40s 983 %-7s nosso %-7s %s %s' % (r[6], r[2], r[3] + ('::' + r[4] if r[4] != '-' else ''), r[5], r[7] or '?', r[0], r[8][:120]))
sys.exit(0 if set(c) <= {'ok', 'anot_velha'} else 1)
