#!/usr/bin/env python3
"""f37/fmap.py <saida do dz.py> <ini> <fim> — tabela do FunctionMapper montada num Initialize: segue mov/xor/lea de imediatos até
cada chamada de _Buynode e mostra o par {chave, id, tipo, função, ajuste} que estava na pilha (ebp-0x40…)."""
import sys, re
reg = {}; mem = {}
def val(x):
    x = x.strip()
    if x in reg: return reg[x]
    try: return int(x, 0)
    except ValueError: return None
for l in open(sys.argv[1]):
    a = l[:8]
    if not (sys.argv[2] <= a < sys.argv[3]): continue
    s = re.sub(r'\s*;.*', '', l[8:].strip()); s = s.replace('dword ptr ', '')
    m = re.match(r'(\w+)\s+(.*)', s)
    if not m: continue
    op, args = m.group(1), [x.strip() for x in m.group(2).split(',')]
    if op == 'call':
        if 'Buynode' in l or '478870' in l:
            g = lambda o: mem.get(o)
            f = lambda v: '?' if v is None else hex(v & 0xffffffff)
            print(a, 'chave', f(g(0x40)), 'id', f(g(0x38)), 'tipo', f(g(0x34)), 'func', f(g(0x30)), 'adj', f(g(0x2c)))
        for r in ('eax', 'ecx', 'edx'): reg.pop(r, None)
        continue
    if op == 'xor' and args[0] == args[1]: reg[args[0]] = 0; continue
    if op == 'mov':
        d, sr = args; v = val(sr)
        if sr.startswith('[ebp - '): v = mem.get(int(sr[7:-1], 16))
        mm = re.match(r'\[ebp - (0x[0-9a-f]+|\d+)\]', d)
        if mm: mem[int(mm.group(1), 0)] = v
        elif d in ('eax', 'ebx', 'ecx', 'edx', 'esi', 'edi'):
            if v is None: reg.pop(d, None)
            else: reg[d] = v
        continue
    if op == 'lea':
        mm = re.match(r'\[(\w+) ([+-]) (0x[0-9a-f]+|\d+)\]', args[1])
        if mm and mm.group(1) in reg:
            reg[args[0]] = reg[mm.group(1)] + (1 if mm.group(2) == '+' else -1) * int(mm.group(3), 0)
        else: reg.pop(args[0], None)
        continue
    if op in ('add', 'sub', 'inc', 'dec', 'pop', 'or', 'and') and args[0] in reg: reg.pop(args[0], None)
