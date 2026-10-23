#!/usr/bin/env python3
"""f13_objorder — ordem das seções de código de um .obj nosso × endereço da mesma função no 983.
Serve para aprender a regra de disposição do link (COMDAT × não-COMDAT, ordem dentro do .obj).
Uso: tools/f13_objorder.py arquivo.obj ... [--full]"""
import sys, os, importlib.machinery, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ld = importlib.machinery.SourceFileLoader('cmpfunc', os.path.join(ROOT, 'tools', 'cmpfunc'))
spec = importlib.util.spec_from_loader('cmpfunc', ld); cf = importlib.util.module_from_spec(spec); ld.exec_module(cf)
mp = {}
for l in open(os.path.join(ROOT, 'map', 'wangreal.tsv')):
    if l.startswith('#') or not l.strip():
        continue
    a = l.rstrip('\n').split('\t')
    mp[a[0]] = int(a[1], 16)
full = '--full' in sys.argv
for path in [a for a in sys.argv[1:] if not a.startswith('--')]:
    ob = cf.Obj(path)
    rows = []
    for nm, sec, a, b, own in ob.funcs():
        if nm.startswith(cf.EHFUN):
            continue
        rows.append((sec, a, nm, own, mp.get(nm)))
    print('== %s: %d funções, %d com endereço no 983' % (path, len(rows), sum(1 for r in rows if r[4])))
    # sequência: monotonia do endereço na ordem do .obj, separada por própria/COMDAT
    for kind in (True, False):
        seq = [r for r in rows if r[3] == kind and r[4]]
        inv = sum(1 for x, y in zip(seq, seq[1:]) if y[4] < x[4])
        if seq:
            print('  %s: n=%d  faixa 983 %x..%x  inversões=%d  seções %d..%d' % (
                'próprias' if kind else 'COMDAT  ', len(seq), min(r[4] for r in seq), max(r[4] for r in seq), inv,
                seq[0][0], seq[-1][0]))
    if full:
        for sec, a, nm, own, va in rows:
            print('  %5d %6x %s %s %s' % (sec, a, 'P' if own else 'c', '%x' % va if va else '-', nm[:90]))
