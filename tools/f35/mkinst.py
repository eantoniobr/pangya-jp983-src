#!/usr/bin/env python3
"""mkinst.py OUT_DIR [--objs build/pg/obj] — endereço certo de cada XMakeInstance no exe 983, pela classe e não pelos bytes.

983: toda função `push N; call operator new; …; mov ecx,eax; call CTOR; …; ret` curta; a classe vem do RTTI da última
vtable que o CTOR grava em [this]. Nosso: cada `?XMakeInstance@@YIPAVIObject@@XZ` dos .obj (N e construtor pelas relocações).
Saídas: mkinst_983.tsv (va, N, ctor, classe), mkinst.tsv (nome, classe, N nosso, N 983, va certo, va no mapa, veredito),
mkinst_manual.tsv (linhas prontas para map/projectg_manual.tsv: só as de classe com 1 candidato no 983)."""
import sys, os, struct, glob, re, collections, importlib.machinery, importlib.util
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ld = importlib.machinery.SourceFileLoader('cmpfunc', R + '/tools/cmpfunc')
sp = importlib.util.spec_from_loader('cmpfunc', ld); cm = importlib.util.module_from_spec(sp); ld.exec_module(cm)
NEW = 0xc3c238
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
def u32(va):
    o = off(va)
    return struct.unpack_from('<I', d, o)[0] if o is not None and o + 4 <= len(d) else None
def rtti(vt):
    """nome da classe de uma vtable (vt[-1] -> RTTICompleteObjectLocator -> TypeDescriptor), ou None"""
    col = u32(vt - 4)
    if not col: return None
    td = u32(col + 12)
    if not td: return None
    o = off(td + 8)
    if o is None or d[o:o + 4] not in (b'.?AV', b'.?AU'): return None
    return d[o + 4:d.index(b'@@\0', o)].decode('latin1')
def ctor_class(va):
    """última vtable gravada em [reg] (C7 0x imm32) antes do 1º ret do construtor que tenha RTTI"""
    o = off(va); best = None
    if o is None: return None
    for i in range(o, min(o + 0x400, len(d) - 6)):
        if d[i] == 0xc7 and d[i + 1] in (0x00, 0x01, 0x03, 0x06, 0x07):
            n = rtti(struct.unpack_from('<I', d, i + 2)[0])
            if n: best = n
        if d[i] == 0xc3 and best and d[i + 1] in (0xcc, 0x55, 0x90): break
    return best
vs, v, rs, ro = secs[0]; lo, hi = ro, ro + max(vs, rs)
C = []   # (va função, N, ctor, classe)
i = d.find(b'\x68', lo)
while 0 <= i < hi - 16:
    if d[i + 5] == 0xe8 and base + (i - ro) + v + 10 + struct.unpack_from('<i', d, i + 6)[0] == NEW:
        n = struct.unpack_from('<I', d, i + 1)[0]; va = base + v + (i - ro)
        s = d.rfind(b'\x55\x8b\xec\x6a\xff', i - 0x30, i)
        e = min([x for x in (d.find(b'\xc3\xcc', i, i + 0x100), d.find(b'\xc3\x55\x8b\xec', i, i + 0x100)) if x > 0] or [0])
        j = min([x for x in (d.find(m, i + 10, i + 0x30) for m in (b'\x8b\xc8\xe8', b'\x8b\xce\xe8', b'\x8b\xcf\xe8', b'\x8b\xcb\xe8')) if x > 0] or [0])
        if s > 0 and e > j > 0:
            ct = base + v + (j - ro) + 7 + struct.unpack_from('<i', d, j + 3)[0]
            if off(ct) is not None and lo <= off(ct) < hi:
                cls = None; reg = {0xc8: 0x00, 0xce: 0x06, 0xcf: 0x07, 0xcb: 0x03}[d[j + 1]]
                # construtor da classe em linha no MakeInstance: a vtable é gravada aqui mesmo, depois do construtor da base
                for q in range(j + 7, e):
                    if d[q] == 0xc7 and d[q + 1] == reg and rtti(struct.unpack_from('<I', d, q + 2)[0]):
                        cls = rtti(struct.unpack_from('<I', d, q + 2)[0])
                ncall = sum(1 for q in range(s, e) if d[q] == 0xe8 and lo <= q + 5 + struct.unpack_from('<i', d, q + 1)[0] < hi)
                C.append((base + v + (s - ro), n, ct, cls or ctor_class(ct) or '?', ncall, 'linha' if cls else 'ctor'))
    i = d.find(b'\x68', i + 1)
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
with open(out + '/mkinst_983.tsv', 'w') as f:
    f.write('va983\tN\tctor983\tclasse\tchamadas\tvtable_vista_em\n')
    for a, n, c, k, nc, w in C: f.write('%08x\t0x%x\t%08x\t%s\t%d\t%s\n' % (a, n, c, k, nc, w))
by = collections.defaultdict(list)
for a, n, c, k, nc, w in C: by[k].append((a, n, c, nc, w))
for k in by:   # vários candidatos: o MakeInstance é o que só chama operator new e o construtor
    if len(by[k]) > 1 and sum(1 for x in by[k] if x[3] == 2) == 1: by[k] = [x for x in by[k] if x[3] == 2]
objs = sys.argv[sys.argv.index('--objs') + 1] if '--objs' in sys.argv else R + '/build/pg/obj'
mp = {}
for l in open(R + '/map/projectg.tsv'):
    p = l.rstrip('\n').split('\t')
    if len(p) > 1 and not l.startswith('#'): mp[p[0]] = p[1]
rows = []; man = []
for p in sorted(glob.glob(objs + '/**/*.obj', recursive=True)):
    try: ob = cm.Obj(p)
    except SystemExit: continue
    for nm, sec, a, b, own in ob.funcs():
        if not nm.endswith('MakeInstance@@YIPAVIObject@@XZ') or not own: continue
        data, rel, ch = ob.secs[sec - 1]; n = None; ct = None
        for o, (typ, si) in sorted(rel.items()):
            if not a <= o < b: continue
            s = ob.syms[si][0]
            if s == '??2@YAPAXI@Z' and data[o - 6] == 0x68: n = struct.unpack_from('<I', data, o - 5)[0]
            elif s.startswith('??0') and n is not None and ct is None: ct = s
        if n is None or ct is None: continue
        cls = re.match(r'\?(\w+)MakeInstance@@', nm).group(1); own_ctor = ct.startswith('??0' + cls + '@')
        cand = by.get(cls, [])
        cur = mp.get(nm, '-')
        if len(cand) == 1:
            va, n9, c9, nc9, w9 = cand[0]; own_ctor = own_ctor and w9 == 'ctor'
            ver = ('ok' if '%08x' % va == cur else 'mapa_errado' if cur != '-' else 'sem_mapa') + ('' if n9 == n else ',tamanho')
            if '%08x' % va != cur:
                man.append('%s\t%08x\ts52 mkinst.py: new 0x%x + call %08x, que grava a vtable de %s (RTTI)%s' % (
                    nm, va, n9, c9, cls, '' if cur == '-' else '; o mapa tinha ' + cur))
            if own_ctor and mp.get(ct, '-') != '%08x' % c9:
                man.append('%s\t%08x\ts52 mkinst.py: construtor chamado pelo MakeInstance %08x; grava a vtable de %s (RTTI)%s' % (
                    ct, c9, va, cls, '' if ct not in mp else '; o mapa tinha ' + mp[ct]))
            rows.append((os.path.relpath(p, objs), nm, cls, n, n9, '%08x' % va, cur, ver))
        else:
            rows.append((os.path.relpath(p, objs), nm, cls, n, -1, '-', cur, 'sem_candidato' if not cand else '%d_candidatos' % len(cand)))
with open(out + '/mkinst.tsv', 'w') as f:
    f.write('obj\tfuncao\tclasse\tN_nosso\tN_983\tva_certo\tva_mapa\tveredito\n')
    for r in rows: f.write('%s\t%s\t%s\t0x%x\t%s\t%s\t%s\t%s\n' % (r[0], r[1], r[2], r[3], '0x%x' % r[4] if r[4] >= 0 else '-', r[5], r[6], r[7]))
open(out + '/mkinst_manual.tsv', 'w').write('\n'.join(sorted(set(man))) + ('\n' if man else ''))
c = collections.Counter(r[7] for r in rows)
print('983: %d funções new+ctor curtas, %d classes com RTTI; nosso: %d MakeInstance' % (len(C), len(by) - ('?' in by), len(rows)))
for k, n in c.most_common(): print('  %-22s %d' % (k, n))
print('linhas para o mapa manual: %d' % len(set(man)))
