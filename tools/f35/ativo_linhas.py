#!/usr/bin/env python3
"""ativo_linhas.py ARQ LINHA... — diz se cada linha compila com /DREBANG_SEMANTIC_ONLY (fora dos ramos #ifndef REBANG_SEMANTIC_ONLY
e dos #else de #ifdef REBANG_SEMANTIC_ONLY) e em que função está (última linha 'Tipo X::Y(' antes dela)."""
import sys, re
src = open(sys.argv[1], encoding='latin-1').read().split('\n')
want = set(int(x) for x in sys.argv[2:])
st = []; fn = '?'
for i, l in enumerate(src, 1):
    s = l.strip()
    if s.startswith('#if'):
        st.append(False if re.match(r'#ifndef\s+REBANG_SEMANTIC_ONLY', s) else True if re.match(r'#ifdef\s+REBANG_SEMANTIC_ONLY', s) else None)
    elif s.startswith('#else') and st:
        st[-1] = (not st[-1]) if st[-1] is not None else None
    elif s.startswith('#endif') and st: st.pop()
    m = re.match(r'^[A-Za-z_][\w\s\*&<>,:~]*?(\w+::~?\w+)\s*\(', l)
    if m and not l.rstrip().endswith(';'): fn = m.group(1)
    if i in want: print('%s:%d\t%s\t%s' % (sys.argv[1], i, 'ATIVA' if all(x is not False for x in st) else 'inativa', fn))
