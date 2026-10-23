#!/usr/bin/env python3
"""Quem define / cita um símbolo no conjunto do link (mesmos .obj do make v6-link).
uso: python3 tools/v6/define.py PADRAO [PADRAO...]   (PADRAO = trecho do nome decorado; ex.: GetHoleIndex@@)
saída: DEF|CITA <frente> <obj> <símbolo>"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import simbolos as S


def objs():
    for u in S.pgbuild.units():
        f = S.newest_obj(u[0])
        if f: yield f
    for l in open(S.R + '/src/projectg/jp/units.txt'):
        l = l.split('#')[0].strip()
        if not l: continue
        f = f'{S.R}/build/B/obj/{os.path.basename(l)[:-4]}.obj'
        if os.path.exists(f) and os.path.getsize(f) > 100: yield f


def main():
    pats = sys.argv[1:]
    if not pats: sys.exit(__doc__)
    for f in objs():
        r = S.coff(f)
        if not r: continue
        de, un, st, al = r
        rel = os.path.relpath(f, S.R)
        for kind, names in (('DEF', de), ('CITA', un)):
            for n in sorted(names):
                if any(p in n for p in pats): print(kind, S.front(f), rel, n, sep='\t')
        for a, b in al.items():
            if any(p in a or p in b for p in pats): print('ALT', S.front(f), rel, f'{a}={b}', sep='\t')


if __name__ == '__main__':
    main()
