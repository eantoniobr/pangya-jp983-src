#!/usr/bin/env python3
"""lcuse.py OBJDIR [--tsv SAIDA] — confere as constantes de IsLocalContent/IsLocalCountry de cada função do nosso fonte com as
da MESMA função no 983 (par pelo map/projectg.tsv). Sessão 155 (pedido C84.2): o localize.h do 983 renumerou os conteúdos
(+1 de 0x22 a 0x69, -1/-3 depois de 0x70), e trechos que ficaram do 645 podem perguntar o número velho.
Constante = último `mov ecx, imm` (fastcall) antes da chamada; IsLocalCountry (__int64 na pilha) = os dois push antes.
Saída: arquivo, função, va983, 'IGUAL'/'DIFERE'/'SEM_PAR', constantes do .obj, constantes do 983."""
import sys, os, re, struct, bisect, collections, importlib.machinery, importlib.util
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ld = importlib.machinery.SourceFileLoader('cmpfunc', R + '/tools/cmpfunc')
cf = importlib.util.module_from_spec(importlib.util.spec_from_loader('cmpfunc', ld)); ld.exec_module(cf)
TGT = {'?IsLocalContent@@YI_NW4localContentType_t@@@Z': ('C', 0x00a7a8d0), '?IsLocalCountry@@YI_N_J@Z': ('P', 0x00a7a6c0)}
BYVA = {v: k for k, v in TGT.values()}
a = [x for x in sys.argv[1:]]
out = a[a.index('--tsv') + 1] if '--tsv' in a else None
objdir = a[0]
mp = {}
for l in open(R + '/map/projectg.tsv'):
    if l.startswith('#'): continue
    p = l.rstrip('\n').split('\t')
    if len(p) >= 2 and re.fullmatch(r'[0-9a-fA-F]{8}', p[1]): mp[p[0]] = int(p[1], 16)
# pares do comparador (funcs.tsv mais novo de cada unidade, como o painel; fora /antes/ /tmp/ /ab/)
import glob
best = {}
for fp in glob.glob(R + '/out/**/cmp/src_*/funcs.tsv', recursive=True):
    if any(x in fp for x in ('/antes/', '/tmp/', '/ab/')): continue
    u = os.path.basename(os.path.dirname(fp)); t = os.path.getmtime(fp)
    if u not in best or t > best[u][0]: best[u] = (t, fp)
for t, fp in best.values():
    for l in open(fp):
        p = l.rstrip('\n').split('\t')
        if len(p) > 5 and re.fullmatch(r'[0-9a-f]{8}', p[5]) and p[1] not in mp: mp[p[1]] = int(p[5], 16)
starts = sorted(set(mp.values()) | set(int(l.split('\t')[0], 16) for l in open(R + '/map/projectg_funcs.tsv')
                                       if re.match(r'[0-9a-f]{8}\t', l)))
pe = cf.PE(R + '/ref/ProjectG_983_dump.exe')

def consts(insns, iscall):
    """para cada chamada (iscall(i) -> 'C'/'P'/None), na ordem do código: constante de ecx (com `mov reg, imm` / `push imm; pop`
    rastreados em linha reta) ou dos 2 push anteriores (IsLocalCountry)"""
    res = []; reg = {}; last_push = None
    for k, it in enumerate(insns):
        kind = iscall(it)
        if kind:
            v = '?'
            if kind == 'C':
                v = hex(reg['ecx']) if 'ecx' in reg else '?'
            else:
                ps = [p for p in insns[max(k - 8, 0):k] if p.mnemonic == 'push']
                if len(ps) >= 2:
                    try: v = hex(int(ps[-1].op_str, 0) | (int(ps[-2].op_str, 0) << 32))
                    except ValueError: v = '?'
            res.append(kind + ':' + v)
        mn, op = it.mnemonic, it.op_str
        m = re.fullmatch(r'(e[a-d]x|e[sd]i|ebp), (0x[0-9a-f]+|\d+)', op)
        if mn == 'mov' and m: reg[m.group(1)] = int(m.group(2), 0)
        elif mn == 'mov' and re.fullmatch(r'(e[a-d]x|e[sd]i), (e[a-d]x|e[sd]i)', op):
            d_, s_ = op.split(', ')
            if s_ in reg: reg[d_] = reg[s_]
            else: reg.pop(d_, None)
        elif mn == 'push' and re.fullmatch(r'0x[0-9a-f]+|\d+', op): last_push = int(op, 0); continue
        elif mn == 'pop' and last_push is not None and re.fullmatch(r'e[a-d]x|e[sd]i', op): reg[op] = last_push
        elif mn == 'call': [reg.pop(r_, None) for r_ in ('eax', 'ecx', 'edx')]
        elif mn.startswith('j') or mn in ('ret',): pass
        else:
            dst = op.split(',')[0].strip()
            for r_ in list(reg):
                if dst == r_ or (len(dst) == 2 and r_[1:] .startswith(dst[0])) : reg.pop(r_, None)
        last_push = None
    return res

rows = []
for dp, dn, fn in os.walk(objdir):
    for f in sorted(fn):
        if not f.endswith('.obj'): continue
        path = os.path.join(dp, f)
        try: ob = cf.Obj(path)
        except SystemExit: continue
        tsi = {i: TGT[s[0]][0] for i, s in ob.syms.items() if s[0] in TGT}
        if not tsi: continue
        for nm, sec, s, e, own in ob.funcs():
            data, rel, ch = ob.secs[sec - 1]
            hits = {o - s: tsi[si] for o, (typ, si) in rel.items() if s <= o < e and si in tsi and typ == 0x14}
            if not hits: continue
            ins = list(cf.md.disasm(data[s:e], 0))
            co = consts(ins, lambda it: hits.get(it.address + 1) if it.mnemonic == 'call' else None)
            va = mp.get(nm)
            if va is None:
                rows.append((os.path.relpath(path, objdir), nm, '-', 'SEM_PAR', ' '.join(co), '')); continue
            nxt = starts[bisect.bisect_right(starts, va)] if bisect.bisect_right(starts, va) < len(starts) else va + 0x4000
            _, size = cf.pe_tokens(pe, va, nxt)
            ins9 = list(cf.md.disasm(pe.read(va, size or (nxt - va)), va))
            def is9(it):
                if it.mnemonic != 'call': return None
                try: return BYVA.get(int(it.op_str, 16))
                except ValueError: return None
            c9 = consts(ins9, is9)
            rows.append((os.path.relpath(path, objdir), nm, '%08x' % va, 'IGUAL' if sorted(co) == sorted(c9) else 'DIFERE', ' '.join(co), ' '.join(c9)))
cnt = collections.Counter(r[3] for r in rows)
txt = ['arquivo\tfuncao\tva983\testado\tobj\t983'] + ['\t'.join(r) for r in rows]
if out: open(out, 'w').write('\n'.join(txt) + '\n')
for r in rows:
    if r[3] != 'IGUAL': print('\t'.join(r))
print('# funções: %d; %s' % (len(rows), dict(cnt)))
