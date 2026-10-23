#!/usr/bin/env python3
"""pgdis.py VA [n_bytes] — desmonta o dump do ProjectG 983 a partir de VA (nomes de map/projectg.tsv nos alvos)."""
import sys, os, struct, capstone, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = open(os.path.join(R, 'ref', 'ProjectG_983_dump.exe'), 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
names = {}
for l in open(os.path.join(R, 'map', 'projectg.tsv')):
    p = l.rstrip('\n').split('\t')
    if len(p) > 1 and not l.startswith('#'):
        try: names.setdefault(int(p[1], 16), p[0])
        except ValueError: pass
def cstr(v):
    o = off(v)
    if o is None: return None
    s = d[o:o + 48].split(b'\0')[0]
    return s.decode('latin1') if len(s) >= 3 and all(32 <= c < 127 for c in s) else None
if __name__ == '__main__':
    va = int(sys.argv[1], 16); n = int(sys.argv[2], 0) if len(sys.argv) > 2 else 256
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    for i in md.disasm(d[off(va):off(va) + n], va):
        t = ''
        for w in re.findall(r'0x[0-9a-f]+', i.op_str):
            v = int(w, 16)
            if v in names: t = '  ; ' + names[v][:70]
            elif v > base + 0x1000:
                s = cstr(v)
                if s: t = '  ; "%s"' % s
        print('%08x  %-7s %s%s' % (i.address, i.mnemonic, i.op_str, t))
        if i.mnemonic in ('ret', 'int3') and '-r' not in sys.argv: break

def callers(target, lo=0x401000, hi=0xc3d000):
    """VAs das instruções `call target` (E8 rel32) no código."""
    code = d[off(lo):off(hi)]; out = []; i = code.find(b'\xe8')
    while i >= 0:
        if i + 5 <= len(code) and lo + i + 5 + struct.unpack_from('<i', code, i + 1)[0] == target: out.append(lo + i)
        i = code.find(b'\xe8', i + 1)
    return out

def new_sizes(ctor):
    """tamanhos dados a operator new (push imm; call 0xc3c238) logo antes de cada chamada ao construtor."""
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); res = []
    for c in callers(ctor):
        best = None
        for back in range(16, 80):
            ins = list(md.disasm(d[off(c - back):off(c) + 5], c - back))
            if not ins or ins[-1].address != c: continue
            for k in range(len(ins) - 1, 0, -1):
                if ins[k].mnemonic == 'call' and ins[k].op_str == '0xc3c238' and ins[k - 1].mnemonic == 'push' and ins[k - 1].op_str.startswith('0x'):
                    best = int(ins[k - 1].op_str, 16); break
            if best: break
        res.append((c, best))
    return res
