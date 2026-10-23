#!/usr/bin/env python3
# (A488) uso: cmp983.py OUT_DO_PGBUILD_CMP [saida.tsv]  -> out/F6/CMP_983.tsv
# Uma linha por função própria de src/projectg: classe do cmpfunc (IGUAL/QUASE/DIFERENTE/SEM_PAR) e origem:
# 645 = "Classe::Func" (ou "Func(" livre) aparece no .cpp de mesmo nome do rebang (/root/rebang/source/client/ProjectG); senão 983.
import sys, glob, os, re, collections
base = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else 'out/F6/CMP_983.tsv'
RB = '/root/rebang/source/client/ProjectG'
rbsrc = {}
def rb(unit):
    if unit not in rbsrc:
        p = os.path.join(RB, unit + '.cpp')
        rbsrc[unit] = open(p, encoding='latin-1').read() if os.path.exists(p) else ''
    return rbsrc[unit]
def short(m):  # ?Func@Class@ns@@... -> (Class, Func); operadores/ctor ficam pelo nome cru
    m2 = re.match(r'\?([A-Za-z_]\w*)@((?:[A-Za-z_]\w*@)*)@', m)
    if not m2: return None, m.lstrip('_?')
    cls = m2.group(2).split('@')[0] if m2.group(2) else None
    return cls, m2.group(1)
rows = []; tot = collections.Counter()
for f in sorted(glob.glob(os.path.join(base, 'cmp', 'src_projectg_*', 'funcs.tsv'))):
    unit = os.path.basename(os.path.dirname(f))[len('src_projectg_'):]
    for l in open(f, encoding='latin-1').read().split('\n')[1:]:
        c = l.split('\t')
        if len(c) < 7 or c[2] != '1': continue
        cls, fn = short(c[1]); s = rb(unit)
        hit = s and ((cls and (cls + '::' + fn) in s) or (not cls and re.search(r'\b' + re.escape(fn) + r'\s*\(', s)))
        org = '645' if hit else '983'
        rows.append((unit, c[1], c[5], c[3], c[4], org)); tot[(c[3], org)] += 1
with open(out, 'w') as o:
    o.write('unidade\tfuncao\tva983\tclasse\tpct_instr\torigem\n')
    for r in rows: o.write('\t'.join(r) + '\n')
print(len(rows), 'funções ->', out)
for k, v in sorted(tot.items()): print('%-10s %s %6d' % (k[0], k[1], v))
