#!/usr/bin/env python3
"""f37/jpbuild — compila as unidades novas do JP (frente B): lista em src/projectg/jp/units.txt (um .cpp por linha,
relativo a src/projectg/jp/; `#` comenta). Mesmas flags/includes do exe (importa tools/f32/pgbuild.py), mais
/I include/jp e /I src/projectg/jp; sem pch compartilhado com a frente A (stdafx.h entra por /FI). Saída em build/B/obj;
`cmp` roda o cmpfunc de cada .obj contra o exe 983 → <out>/cmp/<unidade>/.
Uso: jpbuild.py obj|cmp [-j N] [--out DIR] [--src arquivo.cpp ...]   (--src: compila arquivos avulsos, p/ teste)"""
import os, sys, argparse, subprocess, concurrent.futures as cf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'f32'))
import pgbuild as P
ROOT = P.ROOT; B = ROOT + '/build/B'
ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('-j', type=int, default=8)
ap.add_argument('--out', default='out/F3.7/jp-base'); ap.add_argument('--src', nargs='*'); ap.add_argument('--flags')
a = ap.parse_args()
if a.src:
    us = a.src
else:
    lst = ROOT + '/src/projectg/jp/units.txt'
    us = ['src/projectg/jp/' + l.split('#')[0].strip() for l in open(lst) if l.split('#')[0].strip()] if os.path.exists(lst) else []


def obj_of(src):
    return '%s/obj/%s.obj' % (B, os.path.basename(src)[:-4])


def do_obj(src):
    obj = obj_of(src); os.makedirs(os.path.dirname(obj), exist_ok=True)
    args = (a.flags or P.OPT).split() + P.DEFS.split() + ['/I' + P.absp(i) for i in ['include/jp', 'src/projectg/jp'] + P.INC] + ['/FIstdafx.h']
    rc = P.cl(args + ['/Fo' + obj, P.absp(src)], obj[:-4] + '.log')
    return src, rc


def mapa():
    # map/projectg.tsv (frente A) + src/projectg/jp/jp.tsv (símbolos novos da frente B; vencem) -> build/B/mapa.tsv
    out = B + '/mapa.tsv'
    with open(out, 'w') as f:
        for p in (ROOT + '/map/projectg.tsv', ROOT + '/src/projectg/jp/jp.tsv'):
            if os.path.exists(p):
                f.write(open(p).read())
    # B144: vetos do cmpfunc (nome<TAB>VA, ou nome<TAB>* = sem par "por vizinho"), lidos ao lado do mapa: só os da B
    # (src/projectg/jp/jp_fora.tsv; faixas LTCG, em que a vizinhança não segue a ordem do fonte). Os da A (map/) nunca valeram aqui.
    with open(B + '/projectg_fora.tsv', 'w') as f:
        for p in (ROOT + '/src/projectg/jp/jp_fora.tsv',):
            if os.path.exists(p):
                f.write(open(p).read())
    return out


def do_cmp(src):
    obj = obj_of(src)
    if not os.path.exists(obj):
        return src, None
    od = '%s/cmp/%s' % (a.out, os.path.basename(src)[:-4])
    p = subprocess.run([ROOT + '/tools/cmpfunc', obj, '--no-build', '--ref', ROOT + '/ref/ProjectG_983_dump.exe', '--map', B + '/mapa.tsv',
                        '--funcs', ROOT + '/map/projectg_funcs.tsv', '--out', od], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=ROOT)
    return src, p.returncode


fn = {'obj': do_obj, 'cmp': do_cmp}[a.cmd]
if a.cmd == 'cmp':
    mapa()
ok = 0
with cf.ThreadPoolExecutor(a.j) as ex:
    for src, rc in ex.map(fn, us):
        ok += rc == 0
        if rc:
            print('FALHOU', src, '(log: %s)' % (obj_of(src)[:-4] + '.log'))
print('%s: %d de %d unidades ok' % (a.cmd, ok, len(us)))
sys.exit(0 if ok == len(us) else 1)
