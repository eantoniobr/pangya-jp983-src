#!/usr/bin/env python3
"""C99 (C-F4.21): compara dois uitrace.txt do robô (original × nosso): arquivos abertos (FILE) que só um dos dois abriu,
na ordem do original, e contagem de SPR/TXT. Uso: uicmp.py RES_ORIG RES_NOSSO [max]  (pastas out/F4/resultados/<id> ou .txt)"""
import os, sys


def le(p):
    if os.path.isdir(p): p = os.path.join(p, 'uitrace.txt')
    fs, n = [], {'SPR': 0, 'TXT': 0, 'FILE': 0, 'FALHOU': 0}
    for l in open(p, errors='replace'):
        k = l.split(' ', 1)[0]
        if k in n: n[k] += 1
        if l.startswith('HOOK') and 'FALHOU' in l: n['FALHOU'] += 1
        if k == 'FILE':
            p2 = l.split(None, 2)
            if len(p2) == 3: fs.append(p2[2].strip().lower())
    return fs, n


def main():
    a, b = le(sys.argv[1]), le(sys.argv[2])
    mx = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    print('orig %s\nnosso %s' % (a[1], b[1]))
    if b[1]['FALHOU']: print('AVISO: ganchos falharam no nosso (C99.1, uitrace_end.txt)')
    sb, sa = set(b[0]), set(a[0])
    so_a = [f for f in dict.fromkeys(a[0]) if f not in sb]
    so_b = [f for f in dict.fromkeys(b[0]) if f not in sa]
    print('só no original: %d' % len(so_a)); [print('  ' + f) for f in so_a[:mx]]
    print('só no nosso: %d' % len(so_b)); [print('  ' + f) for f in so_b[:mx]]


main()
