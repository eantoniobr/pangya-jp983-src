#!/usr/bin/env python3
"""vthandle.py SAIDA.tsv [--cmp DIR] — endereço no exe 983 dos HandleMsg que a comparação deixou SEM_PAR, pela vtable da classe:
RTTI (.?AV<classe>@@) → COL → vtables → TODAS as posições (candidatos). Saída: funcao, va983, classe RTTI, deslocamento do COL,
vtable, posição. Quem escolhe é o msgcasos.py --extra: fica o candidato cujo switch tem mais âncoras em comum com o nosso."""
import sys, os, re, csv, glob, struct
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
a = sys.argv[1:]; out = a[0]; cmpdir = R + '/out/F3.5/s67/depois2/cmp'
if '--cmp' in a: cmpdir = a[a.index('--cmp') + 1]
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
def va_of(o):
    for vs, v, rs, ro in secs:
        if ro <= o < ro + rs: return base + v + o - ro
def u32(va):
    o = off(va); return struct.unpack_from('<I', d, o)[0] if o is not None and o + 4 <= len(d) else None
tlo, thi = base + secs[0][1], base + secs[0][1] + secs[0][0]
def refs(v):
    """endereços onde o dword v aparece (alinhado ou não)"""
    p = struct.pack('<I', v); i = d.find(p); r = []
    while i >= 0:
        x = va_of(i)
        if x: r.append(x)
        i = d.find(p, i + 1)
    return r
quer = {}
for f in sorted(glob.glob(cmpdir + '/*/funcs.tsv')):
    for r in csv.DictReader(open(f, errors='replace'), delimiter='\t'):
        m = re.match(r'\?HandleMsg@(.+?)@@[A-Z]AEXABVMsgObject@@@Z$', r['funcao'])
        if m and r['propria'] == '1' and r['classe'] == 'SEM_PAR': quer[r['funcao']] = m.group(1)
n = 0
with open(out, 'w') as f:
    f.write('funcao\tva983\trtti\tcol_desloc\tvtable\tposicao\n')
    for fn, cl in sorted(quer.items()):
        nome = ('.?AV%s@@' % cl).encode() + b'\0'
        i = d.find(nome)
        if i < 0: print('sem RTTI:', cl); continue
        td = va_of(i) - 8
        for c in refs(td):                  # COL: signature, offset, cdOffset, pTypeDescriptor
            col = c - 12
            if u32(col) != 0: continue
            for vp in refs(col):
                vt = vp + 4
                for k in range(64):         # todas as posições: a do HandleMsg muda quando o IActor não é a 1ª base
                    h = u32(vt + 4 * k)
                    if not h or not tlo <= h < thi: break
                    o = off(h)              # ajustador de this (sub ecx,N; jmp X) -> X
                    if d[o:o + 2] == b'\x83\xe9' and d[o + 3] == 0xe9: h = (h + 8 + struct.unpack_from('<i', d, o + 4)[0]) & 0xffffffff
                    elif d[o:o + 2] == b'\x81\xe9' and d[o + 6] == 0xe9: h = (h + 11 + struct.unpack_from('<i', d, o + 7)[0]) & 0xffffffff
                    f.write('%s\t%08x\t%s\t%d\t%08x\t%x\n' % (fn, h, cl, u32(col + 4), vt, 4 * k)); n += 1
print('HandleMsg SEM_PAR: %d classes, %d candidatos em %s' % (len(quer), n, out))
