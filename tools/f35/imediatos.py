#!/usr/bin/env python3
# F3.5 (s44): "votos de imediatos" — para cada .obj do exe, roda o cmpfunc --diff em todas as funções e conta os pares
# de instruções que só diferem num imediato (nosso -> 983). Serve para achar constantes que mudaram no 983 em bloco
# (ex.: flag de desenho 0x4000000 -> 0x8000000). Só leitura do build; saída: <out>/imediatos.tsv e imediatos_locais.tsv.
# uso: imediatos.py <out> [-j N] [filtro de caminho ...]     (objs em build/pg/obj/src/**.obj)
import sys, os, re, subprocess, collections, concurrent.futures as cf
R = '/root/jp983src'
HEXS = re.compile(r'\b0x[0-9a-f]+\b')
def um(obj):
    cmd = [R + '/tools/cmpfunc', obj, '--no-build', '--ref', R + '/ref/ProjectG_983_dump.exe', '--map', R + '/map/projectg.tsv',
           '--seed', R + '/map/projectg_seed.tsv', '--funcs', R + '/map/projectg_funcs.tsv', '--diff', '@']
    try: t = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, cwd=R).stdout
    except Exception as e: return obj, []
    res = []; fn = ''
    for l in t.splitlines():
        if l.startswith('--- '): fn = l[4:].split('  (')[0]; continue
        if not l.startswith(' | '): continue
        p = re.split(r'\s{2,}', l[3:].strip())
        if len(p) != 2: continue
        a, b = p
        ia, ib = HEXS.findall(a), HEXS.findall(b)
        if len(ia) != len(ib) or not ia: continue
        if HEXS.sub('#', a) != HEXS.sub('#', b): continue
        d = [(x, y) for x, y in zip(ia, ib) if x != y]
        if len(d) != 1: continue
        if '[' in a and re.search(r'\[[^\]]*' + re.escape(d[0][0]) + r'[^\]]*\]', a): continue   # deslocamento de campo, não imediato
        res.append((a.split()[0], d[0][0], d[0][1], fn))
    return obj, res
def main():
    a = sys.argv[1:]; out = a[0]; j = 8; filt = []
    i = 1
    while i < len(a):
        if a[i] == '-j': j = int(a[i + 1]); i += 2
        else: filt.append(a[i]); i += 1
    objs = []
    for d, _, fs in os.walk(R + '/build/pg/obj/src'):
        for f in fs:
            if f.endswith('.obj') and (not filt or any(x in d + '/' + f for x in filt)): objs.append(d + '/' + f)
    os.makedirs(out, exist_ok=True)
    cnt = collections.Counter(); un = collections.defaultdict(set); loc = []
    with cf.ThreadPoolExecutor(j) as ex:
        for obj, res in ex.map(um, sorted(objs)):
            u = os.path.relpath(obj, R + '/build/pg/obj')
            for m, x, y, fn in res:
                cnt[(x, y)] += 1; un[(x, y)].add(u); loc.append((x, y, m, u, fn))
    with open(out + '/imediatos.tsv', 'w') as f:
        f.write('nosso\t983\tvezes\tunidades\texemplos\n')
        for (x, y), n in cnt.most_common():
            f.write('%s\t%s\t%d\t%d\t%s\n' % (x, y, n, len(un[(x, y)]), ' '.join(sorted(un[(x, y)])[:4])))
    with open(out + '/imediatos_locais.tsv', 'w') as f:
        f.write('nosso\t983\tmnem\tunidade\tfuncao\n')
        for r in sorted(loc): f.write('\t'.join(r) + '\n')
    print('objs %d; pares distintos %d; ocorrências %d -> %s/imediatos.tsv' % (len(objs), len(cnt), sum(cnt.values()), out))
main()
