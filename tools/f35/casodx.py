#!/usr/bin/env python3
"""casodx.py DESP_VA ID... — resumo do desmonte de cada caso do despachante do exe 983 (out/V4/pacotes_recebe_983.tsv):
do VA do caso até o próximo caso do mesmo despachante (teto 0x300 bytes): chamadas (nome do mapa), push de imediato,
cmp com imediato, cadeias. Serve para casar um `case` do fonte (ids do 645) com o caso do 983."""
import sys, struct, csv, capstone, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
names = {}
for fn in ('projectg_seed.tsv', 'projectg.tsv'):
    for l in open(R + '/map/' + fn, errors='replace'):
        p = l.rstrip('\n').split('\t')
        if len(p) > 1 and not l.startswith('#'):
            try: names[int(p[1], 16)] = p[0]
            except: pass
for l in open(R + '/map/projectg_funcs.tsv', errors='replace').read().split('\n')[1:]:
    p = l.split('\t')
    if len(p) > 10 and p[6]: names.setdefault(int(p[0], 16), p[6])
desp = sys.argv[1].lower().replace('0x', '').zfill(8)
rows = [r for r in csv.DictReader(open(R + '/out/V4/pacotes_recebe_983.tsv'), delimiter='\t') if r['despachante983'] == desp]
vas = sorted(set(int(r['va_caso'], 16) for r in rows))
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
for a in sys.argv[2:]:
    i0 = int(a, 16); r = [x for x in rows if int(x['id'], 16) == i0]
    if not r: print('%s: nao e caso' % a); continue
    va = int(r[0]['va_caso'], 16); nx = [v for v in vas if v > va]; end = min(nx[0] if nx else va + 0x300, va + 0x300)
    out = []
    for i in md.disasm(d[off(va):off(end)], va):
        o = i.op_str
        if i.mnemonic == 'call':
            try: t = int(o, 16); out.append('call ' + names.get(t, '%08x' % t).split('@@')[0][:48])
            except ValueError: out.append('call ' + o.replace('dword ptr ', ''))
        elif i.mnemonic == 'push' and o.startswith('0x'):
            v = int(o, 16); s = None
            if off(v) is not None and v > base + 0x800000:
                s = d[off(v):off(v) + 40].split(b'\0')[0]
                s = '"%s"' % s.decode('cp932', 'replace') if len(s) > 2 else None
            out.append('push ' + (s or o))
        elif i.mnemonic == 'push' and o.isdigit(): out.append('push ' + o)
        elif i.mnemonic in ('cmp', 'sub', 'add') and ', 0x' in o and 'esp' not in o: out.append(i.mnemonic + ' ' + o.replace('dword ptr ', ''))
        elif i.mnemonic == 'mov' and '[0x' in o and o.startswith('e'): out.append('mov ' + o.replace('dword ptr ', ''))
        elif i.mnemonic == 'jmp' and o.startswith('0x') and not (va <= int(o, 16) < end): out.append('jmp-fora'); 
    print('== %s  %08x..%08x (%d B)  %s' % (a, va, end, end - va, r[0]['leituras_no_trecho']))
    print('   ' + '; '.join(out))
