#!/usr/bin/env python3
"""mede.py unidade.cpp 'expr' ['expr'...]: valor de expressões constantes (sizeof/offsetof) medido pelo compilador com os
cabeçalhos do momento (cl /Zs da unidade inteira + sonda; mesmo esquema do tools/pkt/sz.py). Ex.:
  tools/pkt/mede.py src/projectg/taskmanager.cpp 'sizeof(sSlotInfo)' 'offsetof(sUserInfoTime, dwGuildPang)'"""
import sys, os, re, types
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, R + '/tools/f32'); import pgbuild as pb
B = R + '/build/C'; os.makedirs(B + '/sz', exist_ok=True)
open(B + '/v3pre.h', 'w').write('#define private public\n#define protected public\n')
arq, exprs = sys.argv[1], sys.argv[2:]
src, rb, pch, fi, einc = {u[0]: u for u in pb.units()}[arq]
if pch:
    fi = [('/FI' + R + '/' + os.path.dirname(pch) + '/' + f[3:]) if f.startswith('/FI') and os.path.exists(R + '/' + os.path.dirname(pch) + '/' + f[3:]) else f for f in fi]
args = ['/Zs'] + pb.base_args(types.SimpleNamespace(flags=None), einc, src) + ['/I' + R + '/include', '/FI' + B + '/v3pre.h'] + fi
w = '%s/sz/mede_%d.cpp' % (B, os.getpid())
open(w, 'w').write('#include "%s/%s"\n#include <stddef.h>\n' % (R, arq) + ''.join('char (*mp_%d)[1 + (%s)] = 1;\n' % (i, e) for i, e in enumerate(exprs)))
pb.cl(args + [w], w[:-4] + '.log')
got = {}
for l in open(w[:-4] + '.log', errors='replace'):
    m = re.search(r"'char \(\*\)\[(\d+)\]'", l); k = re.search(r'mede_\d+\.cpp\((\d+)\)', l)
    if m and k and int(k.group(1)) >= 3:
        got[int(k.group(1)) - 3] = int(m.group(1)) - 1
for i, e in enumerate(exprs):
    print('%-60s %s' % (e, '0x%x' % got[i] if i in got else '?'))
os.remove(w)
