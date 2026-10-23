#!/usr/bin/env python3
"""dv.py ARQ.diff NOME [max] — só as linhas que diferem (|, >, <) dos blocos de `cmpfunc --diff` cujo título contém NOME"""
import sys
f, nome = sys.argv[1], sys.argv[2]; mx = int(sys.argv[3]) if len(sys.argv) > 3 else 60
on = False; n = 0
for l in open(f, errors='replace'):
    if l.startswith('--- '):
        on = nome in l; n = 0
        if on: print(l.rstrip()[:150])
        continue
    if on and l[:3] in (' | ', ' > ', ' < ') :
        n += 1
        if n <= mx: print(l.rstrip()[:150])
        elif n == mx + 1: print('   …')
