#!/usr/bin/env python3
"""dispg.py VA [n_bytes] — desmonta o ProjectG 983 (ref/ProjectG_983_dump.exe) com nomes do map/projectg.tsv nos alvos."""
import sys, struct, capstone
R = '/root/jp983src'
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
names = {}
for l in open(R + '/map/projectg.tsv', errors='replace'):
    p = l.rstrip('\n').split('\t')
    if len(p) > 1 and not l.startswith('#'):
        try: names[int(p[1], 16)] = p[0]
        except ValueError: pass
va = int(sys.argv[1], 16); n = int(sys.argv[2], 0) if len(sys.argv) > 2 else 256
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
for i in md.disasm(d[off(va):off(va) + n], va):
    s = '%08x  %-7s %s' % (i.address, i.mnemonic, i.op_str)
    for t in i.op_str.replace('[', ' ').replace(']', ' ').split():
        try: v = int(t, 16)
        except ValueError: continue
        if v in names: s += '   ; ' + names[v][:90]
        elif 0xd00000 <= v < 0xf00000 and off(v):
            b = d[off(v):off(v) + 40].split(b'\0')[0]
            if len(b) > 3 and all(32 <= c < 127 for c in b): s += '   ; "%s"' % b.decode()
    print(s)
