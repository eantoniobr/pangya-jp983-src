#!/usr/bin/env python3
"""seqoffs.py 645|983 LO HI [min max] — para cada função da faixa [LO, HI) (645: /root/kr839/out/f645.jsonl + exe do PDB;
983: map/projectg_funcs.tsv + dump), em ordem de endereço, os deslocamentos N de `mov [reg+N], reg/imm` com min <= N < max
e reg != esp/ebp. Serve para alinhar, na ordem do fonte, os handlers que gravam ponteiros de controle (On*Init) no 645 e no
983: a mesma sequência de funções dá o deslocamento antigo -> novo de cada campo. Saída: va tam nome offs..."""
import sys, os, re, json, struct, capstone
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def pe_off(d):
    pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
    oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
    secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
    def off(va):
        for vs, v, rs, ro in secs:
            if v <= va - base < v + max(vs, rs): return ro + va - base - v
    return off
def funcs(which, lo, hi):
    if which == '645':
        d = open('/root/rebang/tools/original/ProjectG_ReleaseQA.exe', 'rb').read(); out = []
        for l in open('/root/kr839/out/f645.jsonl', encoding='utf-8', errors='replace'):
            j = json.loads(l); va = int(j['a'], 16)
            if lo <= va < hi: out.append((va, j.get('sz', 0), j.get('n', '')))
    else:
        d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read(); out = []
        for l in open(R + '/map/projectg_funcs.tsv'):
            c = l.rstrip('\n').split('\t')
            if c[0] == 'f983': continue
            va = int(c[0], 16)
            if lo <= va < hi: out.append((va, int(c[1]), c[6] or c[10]))
    return d, sorted(out)
def scan(which, lo, hi, mn=0x1c, mx=0x400):
    d, fs = funcs(which, lo, hi); off = pe_off(d); md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); res = []
    for va, sz, nm in fs:
        w = []
        for i in md.disasm(d[off(va):off(va) + sz], va):
            m = re.match(r'(?:dword|byte|word) ptr \[(e\w\w) \+ (0x[0-9a-f]+|\d)\], ', i.op_str)
            if i.mnemonic == 'mov' and m and m.group(1) not in ('esp', 'ebp') and mn <= int(m.group(2), 0) < mx and m.group(2) not in w: w.append(m.group(2))
        res.append((va, sz, nm, w))
    return res
if __name__ == '__main__':
    a = sys.argv[1:]; mn = int(a[3], 0) if len(a) > 3 else 0x1c; mx = int(a[4], 0) if len(a) > 4 else 0x400
    for va, sz, nm, w in scan(a[0], int(a[1], 16), int(a[2], 16), mn, mx):
        print('%08x %5d %-48s %s' % (va, sz, nm[:48], ' '.join(w)))
