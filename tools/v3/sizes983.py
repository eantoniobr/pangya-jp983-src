#!/usr/bin/env python3
"""V3: sizeof de cada classe no exe 983, tirado de todo `push N; call operator new` seguido do construtor.
(V7: vale também o `push` curto — `6a N`, N < 0x80 —, que a 1ª versão não lia: toda classe pequena ficava de fora.)

  sizes983.py OUT_DIR
A classe de cada `new` sai de três fontes independentes, nesta ordem de confiança:
  linha  vtable (RTTI, offset 0) gravada em [this] no próprio local do new (construtor em linha)
  mapa   o construtor chamado tem nome `??0Classe@…` em map/projectg*.tsv
  rtti   última vtable com RTTI (offset 0) que o construtor chamado grava em [this]
Saída: OUT_DIR/news_983.tsv (um new por linha) e OUT_DIR/sizes_983.tsv (classe, sizeof, nº de news, fontes, conflito)."""
import sys, os, struct, collections
import capstone
from capstone import x86 as X
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
def cxx(dec):
    """'sToolTipData@FrWnd' -> 'FrWnd::sToolTipData'; None se for template ou nome estranho"""
    if not dec or '?' in dec or '<' in dec: return None
    return '::'.join(reversed(dec.split('@')))
_rt = {}
def rtti(vt):
    """(classe, offset da vtable no objeto) pelo RTTICompleteObjectLocator em vt[-1], ou None"""
    if vt in _rt: return _rt[vt]
    r = None; col = u32(vt - 4) if vt and off(vt) is not None and off(vt) >= 4 else None
    if col and off(col) is not None and u32(col) == 0:
        td = u32(col + 12); o = off(td + 8) if td else None
        if o is not None and d[o:o + 4] in (b'.?AV', b'.?AU'):
            e = d.find(b'@@\0', o, o + 300)
            if e > 0: r = (d[o + 4:e].decode('latin1'), u32(col + 4))
    _rt[vt] = r; return r
vs, v, rs, ro = secs[0]; lo, hi = ro, ro + max(vs, rs); tlo, thi = base + v, base + v + max(vs, rs)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); md.detail = True
def ctor_class(va):
    """última vtable (offset 0) que o construtor grava em [this] — só por registrador que guarda o this (ecx na entrada e
    cópias dele); vtable de membro construído em linha (outro registrador, vindo de lea) não conta"""
    best = None; o = off(va); cur = {X.X86_REG_ECX}
    if o is None: return None
    for ins in md.disasm(d[o:o + 0x800], va):
        if ins.id == X.X86_INS_RET or ins.id == X.X86_INS_INT3: break
        ops = ins.operands
        if ins.id == X.X86_INS_CALL: cur -= {X.X86_REG_EAX, X.X86_REG_ECX, X.X86_REG_EDX}
        elif ins.id == X.X86_INS_MOV and len(ops) == 2:
            a, b = ops
            if a.type == X.X86_OP_REG and a.reg in REG32:
                if b.type == X.X86_OP_REG and b.reg in cur: cur.add(a.reg)
                else: cur.discard(a.reg)
            elif a.type == X.X86_OP_MEM and b.type == X.X86_OP_IMM and a.mem.base in cur and a.mem.disp == 0 and a.mem.index == 0 and a.size == 4:
                r = rtti(b.imm & 0xffffffff)
                if r and r[1] == 0: best = r[0]
        elif ins.id in (X.X86_INS_XOR, X.X86_INS_LEA, X.X86_INS_POP, X.X86_INS_ADD, X.X86_INS_SUB) and ops and ops[0].type == X.X86_OP_REG:
            cur.discard(ops[0].reg)
    return best
REG32 = {X.X86_REG_EAX, X.X86_REG_EBX, X.X86_REG_ECX, X.X86_REG_EDX, X.X86_REG_ESI, X.X86_REG_EDI}
names = collections.defaultdict(list)
for fn in ('projectg.tsv', 'projectg_manual.tsv'):
    for l in open(R + '/map/' + fn):
        p = l.rstrip('\n').split('\t')
        if len(p) > 1 and not l.startswith('#') and p[0].startswith('??0'):
            try: names[int(p[1], 16)].append(p[0])
            except ValueError: pass
def map_class(va):
    c = {n[3:n.index('@@')] for n in names.get(va, []) if '@@' in n}
    return c.pop() if len(c) == 1 else None
REG32 = {X.X86_REG_EAX, X.X86_REG_EBX, X.X86_REG_ECX, X.X86_REG_EDX, X.X86_REG_ESI, X.X86_REG_EDI}
def site(i, k=10):
    """a partir do fim do `call new` (k = tamanho de push + call: 10, ou 7 com o push curto): (ctor va|None, classe em linha|None)"""
    va = base + v + (i - ro) + k; cur = {X.X86_REG_EAX}; ct = None; inl = None; n = 0
    for ins in md.disasm(d[i + k:i + k + 0x100], va):
        n += 1
        if n > 48 or ins.id in (X.X86_INS_RET, X.X86_INS_JMP, X.X86_INS_INT3): break
        ops = ins.operands
        if ins.id == X.X86_INS_CALL:
            if ct is not None: break
            if ops[0].type == X.X86_OP_IMM and tlo <= ops[0].imm < thi and X.X86_REG_ECX in cur and ops[0].imm != NEW:
                ct = ops[0].imm; cur = {r for r in cur if r in (X.X86_REG_EBX, X.X86_REG_ESI, X.X86_REG_EDI)} | {X.X86_REG_EAX}
                continue
            break
        if ins.id == X.X86_INS_MOV and len(ops) == 2:
            a, b = ops
            if a.type == X.X86_OP_REG and a.reg in REG32:
                if b.type == X.X86_OP_REG and b.reg in cur: cur.add(a.reg)
                else: cur.discard(a.reg)
            elif a.type == X.X86_OP_MEM and b.type == X.X86_OP_IMM and a.mem.base in cur and a.mem.disp == 0 and a.mem.index == 0:
                r = rtti(b.imm & 0xffffffff)
                if r and r[1] == 0: inl = r[0]
        elif ins.id in (X.X86_INS_XOR, X.X86_INS_LEA, X.X86_INS_POP) and ops and ops[0].type == X.X86_OP_REG:
            cur.discard(ops[0].reg)
    return ct, inl
rows = []
for op, k in ((b'\x68', 10), (b'\x6a', 7)):      # push imm32 (5 bytes) | push imm8 (2 bytes), depois call rel32
    i = d.find(op, lo)
    while 0 <= i < hi - 16:
        if d[i + k - 5] == 0xe8 and base + (i - ro) + v + k + struct.unpack_from('<i', d, i + k - 4)[0] == NEW:
            n = struct.unpack_from('<I', d, i + 1)[0] if k == 10 else d[i + 1]; va = base + v + (i - ro)
            if k == 10 or n < 0x80:
                ct, inl = site(i, k)
                mc = map_class(ct) if ct else None; rc = ctor_class(ct) if ct else None
                rows.append((va, n, ct, inl, mc, rc))
        i = d.find(op, i + 1)
rows.sort()
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
with open(out + '/news_983.tsv', 'w') as f:
    f.write('va_new\tN\tctor\tclasse_em_linha\tclasse_mapa\tclasse_rtti_ctor\n')
    for va, n, ct, inl, mc, rc in rows:
        f.write('%08x\t0x%x\t%s\t%s\t%s\t%s\n' % (va, n, '%08x' % ct if ct else '-', inl or '-', mc or '-', rc or '-'))
# por classe: votos (N -> nº de news) por fonte
by = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
for va, n, ct, inl, mc, rc in rows:
    if inl: by[inl]['linha'][n] += 1
    elif mc: by[mc]['mapa'][n] += 1
    elif rc: by[rc]['rtti'][n] += 1
    if not inl and mc and rc and mc != rc: by[rc]['rtti_x_mapa'][n] += 1   # o mapa diz outra classe: só informativo
res = []
for k in sorted(by):
    allv = collections.Counter()
    for s in ('linha', 'mapa', 'rtti'): allv.update(by[k][s])
    if not allv: continue
    (n, c), tot = allv.most_common(1)[0], sum(allv.values())
    src = ','.join('%s=%d' % (s, sum(by[k][s].values())) for s in ('linha', 'mapa', 'rtti') if by[k][s])
    conf = '' if len(allv) == 1 else ' '.join('0x%x×%d' % x for x in allv.most_common())
    res.append((k, cxx(k) or '-', n, tot, src, conf))
with open(out + '/sizes_983.tsv', 'w') as f:
    f.write('classe_decorada\tclasse\tsizeof_983\tnews\tfontes\tconflito\n')
    for r in res: f.write('%s\t%s\t0x%x\t%d\t%s\t%s\n' % r)
print('983: %d `new` com tamanho imediato; %d com construtor chamado; %d com classe; %d classes (%d com conflito de tamanho)' % (
    len(rows), sum(1 for r in rows if r[2]), sum(1 for r in rows if r[3] or r[4] or r[5]), len(res), sum(1 for r in res if r[5])))
