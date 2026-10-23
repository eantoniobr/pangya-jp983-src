#!/usr/bin/env python3
"""Frente C, C-PKT lote 56 — sub-despachantes do 983: funções que leem o tipo (Decode2) e o comparam com um id fixo
(`cmp ax,imm`, `mov ecx,imm; cmp ax,cx`, `sub eax,imm`), fora dos despachantes do tools/v4/rx.py (DISP).
São os "ProcessPacket"-like que relêem o pacote depois de `Reset` (CItemBuff::ProcessPacket 0x181 foi o 1º achado, C62).

  subdisp.py [saída.tsv]  -> va, nome no mapa, fonte (map/projectg.tsv|pkt_c.tsv|jp.tsv), Reset?, ids comparados, nº Decode*
Só leitura."""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'v4'))
from lib import R, PE, Funcs, cs
import pk, rx
from capstone import x86 as X

RESET = (0xa4df70, 0x5ab1f0)
D2 = {a for a, op in pk.API983.items() if op == 'D2'}
DEC = {a for a, op in pk.API983.items() if op.startswith('D')}
fonte = {}
for f in ('map/projectg.tsv', 'map/pkt_c.tsv', 'src/projectg/jp/jp.tsv'):
    for l in open(os.path.join(R, f), encoding='utf-8', errors='replace'):
        c = l.rstrip('\n').split('\t')
        if len(c) >= 2 and re.fullmatch(r'[0-9a-f]{8}', c[1]):
            fonte.setdefault(int(c[1], 16), (f.split('/')[-1], c[0]))
pe = PE()
F = Funcs()
md = cs(True)
disp = {d[0] for d in rx.DISP}
txt = pe.secs[0]      # código (o dump não tem nome de seção)
rows = []
for va, tam, uni, n645, n983 in F.l:
    if not (txt[1] <= va < txt[1] + txt[2]) or tam <= 0 or tam > 0x20000 or va in disp:
        continue
    code = pe.bytes(va, tam)
    ins = list(md.disasm(code, va))
    calls = [(k, i.operands[0].imm) for k, i in enumerate(ins)
             if i.mnemonic == 'call' and i.operands and i.operands[0].type == X.X86_OP_IMM]
    if not any(t in D2 for _, t in calls):
        continue
    ids = []
    for k, t in calls:
        if t not in D2:
            continue
        const = {}
        for i in ins[k + 1:k + 6]:
            ops = i.operands
            if i.mnemonic == 'mov' and len(ops) == 2 and ops[0].type == X.X86_OP_REG and ops[1].type == X.X86_OP_IMM:
                const[ops[0].reg] = ops[1].imm
                continue
            if i.mnemonic in ('cmp', 'sub') and len(ops) == 2 and ops[0].type == X.X86_OP_REG \
                    and ops[0].reg in (X.X86_REG_AX, X.X86_REG_EAX):
                v = ops[1].imm if ops[1].type == X.X86_OP_IMM else const.get(ops[1].reg)
                if v is not None and v >= 0x10:
                    ids.append(v)
                break
            if i.mnemonic == 'call':
                break
    if not ids:
        continue
    reset = any(t in RESET for _, t in calls)
    ndec = sum(t in DEC for _, t in calls)
    fn = fonte.get(va)
    rows.append(('%08x' % va, F.nome(va), fn[0] if fn else '-', fn[1][:70] if fn else '-', 'Reset' if reset else '',
                 ' '.join('0x%x' % v for v in sorted(set(ids))), str(ndec)))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(R, 'out', 'V4', 'subdisp_983.tsv')
with open(out, 'w') as f:
    f.write('va983\tnome_mapa\tmapa\tsimbolo_fonte\treset\tids\tn_decode\n')
    for r in rows:
        f.write('\t'.join(r) + '\n')
print(len(rows), 'funções ->', os.path.relpath(out, R))
