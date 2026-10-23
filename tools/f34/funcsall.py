#!/usr/bin/env python3
"""funcsall.py DIR_CMP SAIDA.tsv.gz — junta os funcs.tsv de cada unidade (pgbuild.py cmp --out X → X/cmp/src_*/) num
funcs_all.tsv.gz (entrada do tools/f33/mkmap.py e do tools/f31/map.py --base). A coluna `arquivo` volta a ser o .cpp."""
import sys, glob, gzip, re
d, dst = sys.argv[1:3]
n = 0
with gzip.open(dst, 'wt') as f:
    for i, p in enumerate(sorted(glob.glob(d + '/src_*/funcs.tsv'))):
        for j, l in enumerate(open(p)):
            if j == 0:
                if i == 0: f.write(l)
                continue
            c = l.split('\t', 1)
            f.write(re.sub(r'^build/pg[^/]*/obj/(.*)\.obj$', r'\1.cpp', c[0]) + '\t' + c[1]); n += 1
print('unidades:', i + 1, 'linhas:', n)
