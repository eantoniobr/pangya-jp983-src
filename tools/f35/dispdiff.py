#!/usr/bin/env python3
"""dispdiff.py OBJ FUNCS.tsv [MIN] [--so NOME] — por função pareada (funcs.tsv do cmpfunc), os deslocamentos [reg + disp]
(reg != esp/ebp, disp >= MIN, padrão 0x20) que só o .obj usa e os que só o 983 usa, com contagem. Função cujo layout já está
no do 983 e ainda tem disp só de um lado = campo errado no fonte (s98: o C do #else do camerawork lia m_f18c onde o asm do
645 e o 983 leem +0x190/+0x1c0) ou campo novo do 983. Saída: nome, va, 'obj:' disp×n …, '983:' disp×n …"""
import sys, os, collections, importlib.machinery, importlib.util
from capstone import x86 as X
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ld = importlib.machinery.SourceFileLoader('cmpfunc', R + '/tools/cmpfunc')
cf = importlib.util.module_from_spec(importlib.util.spec_from_loader('cmpfunc', ld)); ld.exec_module(cf)
a = [x for x in sys.argv[1:] if not x.startswith('--')]
so = sys.argv[sys.argv.index('--so') + 1] if '--so' in sys.argv else None
if so: a.remove(so)
objp, fp = a[:2]; MIN = int(a[2], 16) if len(a) > 2 else 0x20
ob = cf.Obj(objp); pe = cf.PE(R + '/ref/ProjectG_983_dump.exe')
fun = {n: (sec, s, e) for (n, sec, s, e, own) in ob.funcs()}
rows = [l.rstrip('\n').split('\t') for l in open(fp)][1:]
vas = sorted(int(r[5], 16) for r in rows if r[5] not in ('-', ''))
pat = __import__('re').compile(r'\[(e[a-ds][xip]|e[sd]i)\s*\+\s*(0x[0-9a-f]+)\]')
def disps(code, base):
    c = collections.Counter()
    for it in cf.md.disasm(code, base):
        for m in pat.finditer(it.op_str):
            if m.group(1) in ('esp', 'ebp'): continue
            v = int(m.group(2), 16)
            if v >= MIN and v < 0x10000: c[v] += 1
    return c
for r in rows:
    if r[2] != '1' or r[5] in ('-', '') or r[1] not in fun: continue
    if so and so not in r[1]: continue
    sec, s, e = fun[r[1]]
    co = disps(ob.secs[sec - 1][0][s:e], 0)
    va = int(r[5], 16); nxt = min([v for v in vas if v > va] or [va + 0x2000])
    _, size = cf.pe_tokens(pe, va, nxt)
    cp = disps(pe.read(va, size), va) if size else collections.Counter()
    so_o = co - cp; so_p = cp - co
    if so_o or so_p:
        f = lambda c: ' '.join('%x×%d' % (k, v) for k, v in sorted(c.items()))
        print('%s\t%s\t%s\tobj: %s\t983: %s' % (r[1][:70], r[5], r[3], f(so_o), f(so_p)))
