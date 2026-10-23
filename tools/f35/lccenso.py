#!/usr/bin/env python3
"""lccenso.py — censo das constantes de IsLocalContent no exe 983 inteiro (faixas de map/projectg_funcs.tsv; constante pelo mesmo
rastreio do lcuse.py). Saída: constante, nº de chamadas, funções (va). Sessão 155."""
import os, sys, re, collections, importlib.machinery, importlib.util
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.argv = [sys.argv[0], '/nonexistent']
ld = importlib.machinery.SourceFileLoader('lcuse', R + '/tools/f35/lcuse.py')
src = open(R + '/tools/f35/lcuse.py').read().split('rows = []')[0]
g = {'__file__': R + '/tools/f35/lcuse.py', '__name__': 'x'}; exec(src, g)
cf, pe, consts = g['cf'], g['pe'], g['consts']
fs = []
for l in open(R + '/map/projectg_funcs.tsv'):
    p = l.split('\t')
    if re.fullmatch(r'[0-9a-f]{8}', p[0]): fs.append((int(p[0], 16), int(p[1]), p[3] if len(p) > 3 else ''))
by = collections.defaultdict(list)
for va, size, unit in fs:
    code = pe.read(va, size)
    if b'\xe8' not in code: continue
    ins = list(cf.md.disasm(code, va))
    def isc(it):
        if it.mnemonic != 'call': return None
        try: return 'C' if int(it.op_str, 16) == 0x00a7a8d0 else None
        except ValueError: return None
    for c in consts(ins, isc): by[c[2:]].append('%08x:%s' % (va, unit.split('/')[-1]))
for k in sorted(by, key=lambda x: int(x, 16) if x != '?' else 999):
    print('%s\t%d\t%s' % (k, len(by[k]), ' '.join(sorted(set(by[k])))))
