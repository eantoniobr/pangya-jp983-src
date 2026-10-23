#!/usr/bin/env python3
"""layout.py UNIDADE.cpp Classe... — layout (cl /d1reportSingleClassLayout) das classes como a unidade do exe as vê
(mesmas flags/pch do tools/f32/pgbuild.py). Classe do pch: dar a fonte do pch como unidade (src/projectg/stdafx.cpp). Saída em build/f34/layout_<Classe>.txt e no terminal (resumida com -q)."""
import sys, os, re, types
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT + '/tools/f32'); import pgbuild as pb
def layout(unit, classes):
    a = types.SimpleNamespace(flags=None, B=ROOT + '/build/pg')
    os.makedirs(ROOT + '/build/f34', exist_ok=True)
    if unit in pb.pchs(pb.units()):
        # classe que vem do pch: recompila a fonte do pch (para um .pch de rascunho) com o relatório ligado
        src = unit
        args = pb.base_args(a) + ['/Yc' + os.path.basename(src)[:-4] + '.h', '/Fp' + ROOT + '/build/f34/layout.pch']
    else:
        u = [x for x in pb.units() if x[0] == unit or x[0].endswith('/' + unit)][0]
        src, rb, pch, fi, einc = u
        args = pb.base_args(a, einc) + fi
        if pch: args += ['/Yu' + os.path.basename(pch)[:-4] + '.h', '/Fp' + pb.pch_file(a, pch)]
    log = ROOT + '/build/f34/layout.log'
    pb.cl(args + ['/d1reportSingleClassLayout' + c for c in classes] + ['/Fo' + ROOT + '/build/f34/layout.obj', pb.absp(src)], log)
    txt = open(log, errors='replace').read().replace('\r', '')
    res = {}
    for m in re.finditer(r'\nclass (\S+)\s+size\((\d+)\):\n(.*?)\n(?=\n)', '\n' + txt, re.S):
        if m.group(1) in classes: res[m.group(1)] = (int(m.group(2)), m.group(0).strip('\n'))
    return res, txt
if __name__ == '__main__':
    q = '-q' in sys.argv; av = [x for x in sys.argv[1:] if x != '-q']
    res, txt = layout(av[0], av[1:])
    for c in av[1:]:
        if c not in res: print('%s: sem layout (ver build/f34/layout.log)' % c); continue
        open(ROOT + '/build/f34/layout_%s.txt' % c, 'w').write(res[c][1] + '\n')
        print('%s sizeof 0x%x' % (c, res[c][0]) if q else res[c][1])
