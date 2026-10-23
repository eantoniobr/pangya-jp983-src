#!/usr/bin/env python3
"""dx.py VA [n] | find HEX lo hi — desmonta/procura no exe 983"""
import sys, struct, capstone
d = open('/root/jp983src/ref/ProjectG_983_dump.exe','rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
names = {}
for fn in ('projectg_seed.tsv','projectg.tsv'):
    for l in open('/root/jp983src/map/'+fn, errors='replace'):
        p = l.rstrip('\n').split('\t')
        if len(p) > 1 and not l.startswith('#'):
            try: names[int(p[1], 16)] = p[0]
            except: pass
if sys.argv[1] == 'find':
    pat = bytes.fromhex(sys.argv[2]); lo, hi = off(int(sys.argv[3],16)), off(int(sys.argv[4],16)); i = lo
    while True:
        i = d.find(pat, i, hi)
        if i < 0: break
        print('%08x' % (int(sys.argv[3],16) + i - lo)); i += 1
    sys.exit()
va = int(sys.argv[1], 16); n = int(sys.argv[2], 0) if len(sys.argv) > 2 else 256
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
for i in md.disasm(d[off(va):off(va) + n], va):
    t = ''
    for w in i.op_str.replace('[', ' ').replace(']', ' ').replace(',', ' ').split():
        if w.startswith('0x'):
            v = int(w, 16)
            if v in names: t = '  ; ' + names[v]
            elif off(v) is not None and v > base + 0x900000:
                s = d[off(v):off(v)+40].split(b'\0')[0]
                if len(s) > 3 and all(32 <= c < 127 for c in s): t = '  ; "%s"' % s.decode()
    print('%08x  %-8s %s%s' % (i.address, i.mnemonic, i.op_str, t))
