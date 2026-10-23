#!/usr/bin/env python3
# new983.py <983.dis> — tabela "push N; call operator new(0xc3c238)" -> construtor chamado com ecx=eax (983)
import re, sys, collections
NEW = sys.argv[2] if len(sys.argv) > 2 else '0xc3c238'
ins = []
rx = re.compile(r'^\s*([0-9a-f]+):\s+(.*)$')
for l in open(sys.argv[1], errors='replace'):
    m = rx.match(l)
    if m: ins.append((m.group(1), m.group(2).strip()))
out = collections.defaultdict(list)
for i, (a, t) in enumerate(ins):
    if not t.startswith('call') or not t.endswith(NEW): continue
    p = ins[i-1][1]
    m = re.match(r'push\s+\$0x([0-9a-f]+)$', p)
    if not m: continue
    size = int(m.group(1), 16)
    ctor = None; ecx = False
    for b, u in ins[i+1:i+14]:
        if re.match(r'mov\s+%eax,%ecx', u) or re.match(r'mov\s+%e[a-z]x,%ecx', u): ecx = True
        mm = re.match(r'call\s+0x([0-9a-f]+)$', u)
        if mm:
            if ecx: ctor = mm.group(1).zfill(8)
            break
    out[ctor].append((size, ins[i-1][0].zfill(8)))
for ctor, l in sorted(out.items(), key=lambda x: x[0] or ''):
    sizes = sorted(set(s for s, _ in l))
    print('%s\t%s\t%s' % (ctor or '-', ','.join(hex(s) for s in sizes), ','.join(a for _, a in l[:4])))
