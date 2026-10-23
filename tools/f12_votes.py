#!/usr/bin/env python3
"""F1.2: votos de deslocamento de campo .obj (fonte em src/) -> 983, por classe da função.
uso: f12_votes.py SAIDA.tsv arquivo.cpp...   (usa os .obj já compilados em build/obj; mesma comparação do cmpfunc)
Para cada função com par no 983, alinha as instruções pela ficha sem imediato/deslocamento e conta, por
classe (do nome decorado), cada par (deslocamento no .obj, deslocamento no 983) de operando [reg+N] com
reg != esp/ebp, e cada par de imediato diferente (linhas 'imm')."""
import sys, os, re, collections, difflib, importlib.machinery, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ld = importlib.machinery.SourceFileLoader('cmpfunc', os.path.join(ROOT, 'tools', 'cmpfunc'))
sp = importlib.util.spec_from_loader('cmpfunc', ld); cf = importlib.util.module_from_spec(sp); ld.exec_module(cf)

MEM = re.compile(r'^(\w+:)?\[(\w*)\+(\w*)\*(\d+)\+([0-9a-f]+)\]$')

def cls_of(nm):
    m = re.match(r'^\?\??[^@]*@((?:[^@]+@)+)@', nm)
    if not m:
        return '-'
    return '::'.join(reversed(m.group(1).rstrip('@').split('@')))

def main():
    out, files = sys.argv[1], sys.argv[2:]
    pe = cf.PE(os.path.join(ROOT, 'ref', 'wangreal_983.dll'))
    c = cf.Cmp(pe, cf.load_map(os.path.join(ROOT, 'map', 'wangreal.tsv')), None)
    for r in files:
        c.run_obj(os.path.join(ROOT, 'build', 'obj', os.path.splitext(r)[0] + '.obj'), r, False)
    votes = collections.defaultdict(collections.Counter)      # (classe, tipo, off_obj) -> {off_983: n}
    ex = {}
    for x in c.rows:
        if not x['va'] or x['pct'] < 0.5:
            continue
        to, tr = c.details.get(x['nm'], (None, None))
        if not to or not tr:
            continue
        k = cls_of(x['nm'])
        sm = difflib.SequenceMatcher(None, to.r, tr.r, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != 'equal':
                continue
            for q in range(i2 - i1):
                a, b = to.s[i1 + q], tr.s[j1 + q]
                pa, pb = a.split(' ', 1), b.split(' ', 1)
                if len(pa) < 2 or len(pb) < 2:
                    continue
                oa, ob = pa[1].split(','), pb[1].split(',')
                if len(oa) != len(ob):
                    continue
                for u, v in zip(oa, ob):
                    mu, mv = MEM.match(u), MEM.match(v)
                    if mu and mv:
                        if mu.group(2) in ('esp', 'ebp', '') or mu.group(1):
                            continue
                        key = (k, 'mem', int(mu.group(5), 16))
                        votes[key][int(mv.group(5), 16)] += 1
                        ex.setdefault((key, int(mv.group(5), 16)), '%s %08x: %s' % (x['nm'][:40], x['va'], tr.txt[j1 + q]))
                    elif not mu and not mv and u != v and re.match(r'^[0-9a-f]+$', u) and re.match(r'^[0-9a-f]+$', v):
                        key = (k, 'imm', int(u, 16))
                        votes[key][int(v, 16)] += 1
                        ex.setdefault((key, int(v, 16)), '%s %08x: %s' % (x['nm'][:40], x['va'], tr.txt[j1 + q]))
    with open(out, 'w') as f:
        f.write('classe\ttipo\toff_obj\toff_983\tdelta\tvotos\toutros\texemplo\n')
        for key in sorted(votes):
            cn = votes[key]
            (v, n), rest = cn.most_common(1)[0], cn.most_common()[1:]
            f.write('%s\t%s\t0x%x\t0x%x\t%+d\t%d\t%s\t%s\n' % (key[0], key[1], key[2], v, v - key[2] if abs(v - key[2]) < 1 << 31 else 0, n,
                    ' '.join('0x%x:%d' % kv for kv in rest), ex[(key, v)]))
    print('%d chaves em %s' % (len(votes), out))

main()
