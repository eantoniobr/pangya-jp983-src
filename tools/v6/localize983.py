#!/usr/bin/env python3
"""localize983.py — emula o InitLocalizeSystem do 983 (00a7a9b0: cadeia s_localContentSet[a] = s_localContentSet[b] = ... ;
bitset<0xa7> em 0xf02e08, país em 0xf02e00) a partir da desmontagem e lista os conteúdos ligados, com os nomes de
src/shared/localize.h; compara com o localize_kor.h. Uso: frente C, F4 teste 3."""
import os, re, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dis = subprocess.run([sys.executable, os.path.join(R, 'tools/v6/disexe.py'), os.path.join(R, 'ref/ProjectG_983_dump.exe'),
                      '00a7a9b0', '0x1000'], capture_output=True, text=True).stdout.splitlines()
mem = {a: 0 for a in range(0xf02e08, 0xf02e20, 4)}
regs = {}; last_test = None; pushes = []; country = None; on = set(); order = []
for l in dis:
    a, mn, *rest = l.split(' ', 2); op = rest[0].split(" '")[0].strip() if rest else ''
    m = re.match(r'(e[a-d]x|esi|edi), dword ptr \[(0x[0-9a-f]+)\]$', op)
    if mn == 'mov' and m and int(m.group(2), 16) in mem: regs[m.group(1)] = mem[int(m.group(2), 16)]; continue
    m = re.match(r'dword ptr \[(0x[0-9a-f]+)\], (e[a-d]x)$', op)
    if mn == 'mov' and m and int(m.group(1), 16) in mem: mem[int(m.group(1), 16)] = regs.get(m.group(2), 0); continue
    m = re.match(r'dword ptr \[0xf02e00\], (\w+)', op)
    if mn == 'mov' and m: country = m.group(1); continue
    m = re.match(r'(e[a-d]x), (0x[0-9a-f]+|\d+)$', op)
    if mn in ('or', 'and') and m and m.group(1) in regs:
        v = int(m.group(2), 0); regs[m.group(1)] = regs[m.group(1)] | v if mn == 'or' else regs[m.group(1)] & v
        if mn == 'and': last_test = regs[m.group(1)] != 0
        continue
    if mn == 'push': pushes.append(op); continue
    if mn == 'call' and op == '0xa7a760':
        pos = int(pushes[-1], 0); val = last_test
        if pushes[-2] in ('1',): val = True
        w = 0xf02e08 + (pos >> 5) * 4
        if val: mem[w] |= 1 << (pos & 31)
        else: mem[w] &= ~(1 << (pos & 31))
        order.append((pos, val)); pushes = []; continue
    if mn == 'ret': break
# bit inicial (o "= true" do fim da cadeia): o or no 0xf02e1c antes do 1º set
names = {}
for l in open(os.path.join(R, 'src/shared/localize.h')):
    m = re.match(r'\s*(\w+)\s*=\s*(0x[0-9a-fA-F]+|\d+)', l)
    if m: names[int(m.group(2), 0)] = m.group(1)
bits = sorted(p for p in range(0xa7) if (mem[0xf02e08 + (p >> 5) * 4] >> (p & 31)) & 1)
kor = set()
txt = open(os.path.join(R, 'src/shared/localize_kor.h')).read()
inv = {v: k for k, v in names.items()}
for n in re.findall(r's_localContentSet\[(\w+)\]', txt): kor.add(inv.get(n, n))
print(f'# país (0xf02e00) = {country}; sets = {len(order)}; ligados no 983 = {len(bits)}; no localize_kor.h = {len(kor)}')
for p in bits: print(f'983\t{p:#04x}\t{names.get(p, "?")}\t{"KOR também" if p in kor else "SÓ 983"}')
for p in sorted(x for x in kor if isinstance(x, int) and x not in bits): print(f'KOR\t{p:#04x}\t{names.get(p, "?")}\tSÓ KOR (desligado no 983)')
