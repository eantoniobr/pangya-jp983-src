#!/usr/bin/env python3
"""ltcgdiff.py dll map nome va983 — lado a lado (só as linhas que diferem, com 2 de contexto) da função da dll LTCG × 983."""
import sys, re, difflib, bisect
ROOT = '/root/jp983src'
src = open(ROOT + '/tools/cmpfunc').read().split("\nif __name__ == '__main__':")[0]
G = {'__name__': 'x', '__file__': ROOT + '/tools/cmpfunc'}; exec(compile(src, 'cmpfunc', 'exec'), G)
dll, mp, nm, va = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4], 16)
dl = G['PE'](dll); ex = G['PE'](ROOT + '/ref/ProjectG_983_dump.exe')
fn = {}
for l in open(mp):
    q = l.split()
    if len(q) >= 4 and re.fullmatch(r'0001:[0-9a-f]{8}', q[0]) and q[1].startswith('?'): fn[q[1]] = int(q[2], 16)
st = sorted(set(fn.values())); x = next(v for k, v in fn.items() if nm in k)
i = bisect.bisect_right(st, x)
to = G['pe_tokens'](dl, x, st[i] if i < len(st) else x + 0x4000, set(st).__contains__)[0]
c = G['Cmp'](ex, {}, G['load_starts'](ROOT + '/map/projectg_funcs.tsv')); tr = c.ref_tokens(va)[0]
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, to.l, tr.l, autojunk=False).get_opcodes():
    if tag == 'equal':
        if i2 - i1 > 4: print('   ... %d iguais' % (i2 - i1)); continue
    for k in range(max(i2 - i1, j2 - j1)):
        a = to.txt[i1 + k] if i1 + k < i2 else ''; b = tr.txt[j1 + k] if j1 + k < j2 else ''
        print('%s %-45s | %s' % (' ' if tag == 'equal' else '*', a[:45], b[:60]))
