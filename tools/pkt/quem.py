#!/usr/bin/env python3
"""pkt/quem.py VA... — quem referencia VA no exe 983: chamadas/saltos (E8/E9 rel32) e o VA como dword (push imm, vtable,
tabela). Para cada referência: função que a contém (map/projectg_funcs.tsv) com nome, ou, se cair numa vtable, a classe (RTTI)
e o slot. Uso típico: achar a classe de uma função nova do 983 (callback de diálogo, método virtual)."""
import sys, struct, bisect
__file__ = '/root/jp983src/tools/f37/dz.py'; exec(open(__file__).read().split('a = sys.argv[1:]')[0])
starts = sorted(int(l.split('\t')[0], 16) for l in open(R + '/map/projectg_funcs.tsv') if l[:1] in '0123456789abcdef')
def dono(va):
    i = bisect.bisect_right(starts, va) - 1
    s = starts[i] if i >= 0 else 0
    return '%08x %s' % (s, names.get(s, '?'))
def vt_de(va):
    # volta de 4 em 4 até achar um dword cujo vizinho anterior é COL válida (início da vtable)
    for k in range(0, 0x800, 4):
        r = rtti(va - k)
        if r: return '%s slot %d (vtable %08x)' % (r, k // 4, va - k)
    return None
tg = {int(t, 16): [] for t in sys.argv[1:]}
for vs, v, rs, ro in secs:
    seg = d[ro:ro + rs]
    for tgt, out in tg.items():
        pk = struct.pack('<I', tgt); i = seg.find(pk)
        while i >= 0:
            va = base + v + i
            ctx = vt_de(va) if (seg[i - 1] if i else 0) not in (0x68, 0xb8, 0xb9, 0xba, 0xbe, 0xbf, 0xc7) else None
            out.append('  dword %08x  %s' % (va, ctx or 'em ' + dono(va)))
            i = seg.find(pk, i + 1)
    for j in range(len(seg) - 5):
        if seg[j] in (0xe8, 0xe9):
            a = base + v + j + 5 + struct.unpack_from('<i', seg, j + 1)[0]
            if a in tg:
                tg[a].append('  %s  %08x  em %s' % ('call' if seg[j] == 0xe8 else 'jmp ', base + v + j, dono(base + v + j)))
for tgt, out in tg.items():
    print('== %08x %s' % (tgt, names.get(tgt, ''))); print('\n'.join(out))
