#!/usr/bin/env python3
"""f12_refs.py OFF... — instruções da wangreal.dll 983 que usam [reg+OFF] (deslocamento de 32 bits), com a função."""
import sys, os, struct, capstone, bisect
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = open(R + '/ref/wangreal_983.dll', 'rb').read()
fs = []; nm = {}
for l in open(R + '/map/wangreal_funcs.tsv'):
    p = l.rstrip('\n').split('\t')
    if len(p) > 13 and not l.startswith(('#', 'va')): fs.append(int(p[0], 16)); nm[int(p[0], 16)] = p[13]
fs.sort()
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
lim = int(os.environ.get('N', '12'))
for a in sys.argv[1:]:
    off = int(a, 16); pat = struct.pack('<I', off); i = 0x400; n = 0; seen = set()
    while n < lim:
        i = d.find(pat, i + 1, 0x60400)
        if i < 0: break
        va = 0x10001000 + i - 0x400
        f = fs[bisect.bisect_right(fs, va) - 1]
        for back in (2, 3, 1, 4):
            ins = next(md.disasm(d[i - back:i + 12], va - back), None)
            if ins and ('0x%x' % off) in ins.op_str and '[' in ins.op_str and ins.size >= back + 4:
                key = (ins.mnemonic, ins.op_str.split('[')[0])
                if (f, key) in seen: break
                seen.add((f, key)); n += 1
                print('%05x  %08x %-28s %s %s' % (off, va - back, nm.get(f, '-')[:28] if nm.get(f, '-') != '-' else 'FUN_%08x' % f, ins.mnemonic, ins.op_str)); break
