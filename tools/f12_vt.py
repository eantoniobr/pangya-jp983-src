#!/usr/bin/env python3
"""F1.2: vtable do 983 (build/f04/vt983w.tsv) × vtable que o fonte de src/ gera (layout do cl), slot a slot.
uso: f12_vt.py LAYOUT.txt Classe [Classe...]   -> TSV: classe slot983 va983 nome983 | slot_src metodo_src"""
import sys, os, re, difflib, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
nm = {}
for l in open(R + '/map/wangreal_funcs.tsv'):
    p = l.rstrip('\n').split('\t')
    if len(p) > 13 and not l.startswith(('#', 'va')):
        nm[int(p[0], 16)] = (p[13], p[14], p[1])
dec = collections.defaultdict(list)
for l in open(R + '/map/wangreal.tsv'):
    p = l.rstrip('\n').split('\t')
    if len(p) > 1 and not l.startswith('#'): dec[int(p[1], 16)].append(p[0])
vt = collections.defaultdict(list)
for l in open(R + '/build/f04/vt983w.tsv'):
    p = l.rstrip('\n').split('\t')
    if p[1] == 'vftable' and p[2] == '0': vt[p[0]].append((int(p[5]), int(p[6], 16), p[7]))
lay = open(sys.argv[1]).read().split('\n')
def src_vt(cls):
    out = []; on = False
    for l in lay:
        if l.startswith(cls + "::$vftable@"): on = True; continue
        if on:
            m = re.match(r'^\s*(\d+)\s*\|\s*&(\S+)', l)
            if m: out.append(m.group(2).strip())
            elif out or (l.strip() and not l.strip().startswith(('|', '+', '&'))):
                if out: break
    return out
def meth(va, raw):
    n = nm.get(va, ('-', '-', ''))[0]
    if n == '-':
        d = [x for x in dec.get(va, []) if x.startswith('?')]
        if d:
            m = re.match(r'^\?\??([^@]+)@([^@]+)@@', d[0]); n = '%s::%s' % (m.group(2), m.group(1)) if m else d[0]
    if n == '-' and 'purecall' in raw: n = '_purecall'
    return n
def short(n):
    n = n.split('(')[0]
    return n.split('::')[-1].replace('{dtor}', "`scalar_deleting_destructor'").replace('`vector_deleting_destructor\'', "`scalar_deleting_destructor'")
print('classe\tslot983\tva983\tbytes\tnome983\tslot_src\tmetodo_src\tobs')
for cls in sys.argv[2:]:
    a = sorted(vt[cls]); s = src_vt(cls)
    an = [short(meth(va, raw)) for _, va, raw in a]; sn = [short(x) for x in s]
    sm = difflib.SequenceMatcher(None, an, sn, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        n = max(i2 - i1, j2 - j1)
        for k in range(n):
            i = i1 + k if i1 + k < i2 else None; j = j1 + k if j1 + k < j2 else None
            va = a[i][1] if i is not None else 0
            print('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (cls, '' if i is None else a[i][0], '%08x' % va if va else '', nm.get(va, ('', '', ''))[2],
                  meth(va, a[i][2]) if i is not None else '', '' if j is None else j, s[j] if j is not None else '',
                  '' if tag == 'equal' else ('novo_983' if j is None else 'so_src' if i is None else 'difere')))
    print('# %s: 983 tem %d slots, fonte tem %d' % (cls, len(a), len(s)))
