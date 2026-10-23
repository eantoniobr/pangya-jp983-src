#!/usr/bin/env python3
"""campos983.py OBJ FUNCS.tsv CAMPOS.txt Classe — mapa de layout de uma classe pelo uso: para cada campo (saída do campos.py:
`off nome`, sizeof no fim) conta, nas funções pareadas da própria Classe (nome decorado com @Classe@@), os acessos [reg+disp]
dentro do campo que aparecem nos DOIS lados (confere), só no 983 e só no nosso .obj. Campo com `só983`/`sóobj` e sem `ambos`
= deslocamento suspeito. Sessão A193 (docs/LAYOUTS.md). Saída TSV: off tamanho nome ambos só983 sóobj funções_exemplo."""
import sys, os, re, collections, importlib.machinery, importlib.util
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ld = importlib.machinery.SourceFileLoader('cmpfunc', R + '/tools/cmpfunc')
cf = importlib.util.module_from_spec(importlib.util.spec_from_loader('cmpfunc', ld)); ld.exec_module(cf)
objp, fp, cp, cls = sys.argv[1:5]
ob = cf.Obj(objp); pe = cf.PE(R + '/ref/ProjectG_983_dump.exe')
fun = {n: (sec, s, e) for (n, sec, s, e, own) in ob.funcs()}
rows = [l.rstrip('\n').split('\t') for l in open(fp)][1:]
vas = sorted(int(r[5], 16) for r in rows if r[5] not in ('-', ''))
pat = re.compile(r'\[(e[a-ds][xip]|e[sd]i)\s*\+\s*(0x[0-9a-f]+)\]')
def disps(code, base):
    return {int(m.group(2), 16) for it in cf.md.disasm(code, base) for m in pat.finditer(it.op_str)}
fields = []
for l in open(cp):
    a = l.split()
    if len(a) >= 2 and a[0].startswith('0x'): fields.append((int(a[0], 16), a[1]))
fields.sort(); size = dict((n, o) for o, n in fields).get('sizeof', fields[-1][0] + 4)
fields = [f for f in fields if f[1] != 'sizeof']
ends = [f[0] for f in fields[1:]] + [size]
def field(d):
    for (o, n), e in zip(fields, ends):
        if o <= d < e: return n
cnt = collections.defaultdict(collections.Counter); ex = collections.defaultdict(set)
for r in rows:
    if r[2] != '1' or r[5] in ('-', '') or r[1] not in fun or '@%s@@' % cls not in r[1]: continue
    sec, s, e = fun[r[1]]
    do = {d for d in disps(ob.secs[sec - 1][0][s:e], 0) if d < size}
    va = int(r[5], 16); nxt = min([v for v in vas if v > va] or [va + 0x2000])
    _, sz = cf.pe_tokens(pe, va, nxt)
    dp = {d for d in disps(pe.read(va, sz), va) if d < size} if sz else set()
    for d, k in [(d, 'ambos') for d in do & dp] + [(d, 'só983') for d in dp - do] + [(d, 'sóobj') for d in do - dp]:
        n = field(d)
        if n: cnt[n][k] += 1; ex[n].add(r[1].split('@')[0].lstrip('?'))
print('off\ttamanho\tcampo\tambos\tsó983\tsóobj\tfunções')
for (o, n), e in zip(fields, ends):
    c = cnt[n]
    print('0x%x\t0x%x\t%s\t%d\t%d\t%d\t%s' % (o, e - o, n, c['ambos'], c['só983'], c['sóobj'], ','.join(sorted(ex[n])[:3])))
