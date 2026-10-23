#!/usr/bin/env python3
"""initsweep.py [-o saida.tsv] [filtro_de_classe] — varredura de layout pelas telas Fresh: para cada BEGIN_FRESH_MSGMAP do
fonte (src/projectg, src/fresh) acha o mapa de mensagens do 983 pela sequência de nomes de controle (sem depender de nome
de função no mapa), e para cada entrada compara os deslocamentos que o handler grava em `this` no nosso .obj
(build/pg/obj) com os do handler do 983 da mesma entrada. Saída por classe: entradas pareadas, iguais, deltas mais comuns;
com -v, uma linha por entrada. Só olha handlers que gravam alguma coisa (Init e afins)."""
import sys, os, re, struct, glob, collections, difflib, importlib.machinery, importlib.util
import capstone
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pgdis as P, msgmap1 as M1
ld = importlib.machinery.SourceFileLoader('cmpfunc', os.path.join(R, 'tools', 'cmpfunc'))
sp = importlib.util.spec_from_loader('cmpfunc', ld); cf = importlib.util.module_from_spec(sp); ld.exec_module(cf)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
def stores(code, va=0, lo=0x1c, hi=0x8000):
    """deslocamentos gravados em `this` (ecx ou o registrador que o recebeu), na ordem."""
    w = []; th = {'ecx'}
    for i in md.disasm(code, va):
        m = re.match(r'(?:dword|byte|word) ptr \[(e\w\w) \+ (0x[0-9a-f]+)\], ', i.op_str)
        if i.mnemonic == 'mov' and m and m.group(1) in th and lo <= int(m.group(2), 16) < hi and int(m.group(2), 16) not in w: w.append(int(m.group(2), 16))
        m = re.match(r'(e\w\w), (e\w\w)$', i.op_str)
        if i.mnemonic == 'mov' and m:
            if m.group(2) == 'ecx' and 'ecx' in th: th.add(m.group(1))
            else: th.discard(m.group(1))
        elif i.mnemonic in ('mov', 'lea', 'pop', 'xor', 'movzx') and i.op_str.split(',')[0] in th: th.discard(i.op_str.split(',')[0])
        if i.mnemonic == 'call': th -= {'ecx', 'eax', 'edx'}
        if i.mnemonic in ('ret', 'int3'): break
    return w
def tables983():
    """todos os mapas do 983: {va_do_mapa: [(handler, cmd, nome)]} a partir das funções `mov eax, mapa; ret`."""
    T = P.d[P.off(0x401000):P.off(0xcfffff)]; out = {}
    for m in re.finditer(rb'\xb8(.{3}\x00)\xc3', T, re.S):
        va = struct.unpack('<I', m.group(1))[0]
        if va in out or not (0xd00000 <= va < 0xf80000) or P.off(va) is None: continue
        bas, ent = struct.unpack_from('<II', P.d, P.off(va))
        if not (0xd00000 <= ent < 0xf80000) or not (bas == 0 or 0xd00000 <= bas < 0xf80000) or P.off(ent) is None: continue
        try: t = M1.table('%x' % va)
        except Exception: continue
        if t and len(t) < 600: out[va] = [(h, c, n) for h, c, n, e in t]
    return out
CMD = None
def cmdval(sym):
    global CMD
    if CMD is None:
        t = open(R + '/src/fresh/include/frcmdtarget.h', encoding='latin-1').read()
        CMD = {n: i for i, n in enumerate(re.findall(r'FRCMD_\w+', t[t.index('enum eFrCmd'):t.index('};')]))}
    if re.fullmatch(r'0x[0-9a-fA-F]+|\d+', sym): return int(sym, 0)
    return CMD.get(sym, -1)
def sources():
    """[(classe, cpp, [(nome, cmd_txt, handler)])]"""
    out = []
    for p in sorted(glob.glob(R + '/src/projectg/*.cpp') + glob.glob(R + '/src/fresh/*.cpp')):
        s = open(p, encoding='latin-1').read()
        for m in re.finditer(r'BEGIN_FRESH_MSGMAP\(\s*(\w+)\s*,\s*\w+\s*\)(.*?)END_FRESH_MSGMAP', s, re.S):
            e = re.findall(r'ON_FRESH_\w+\(\s*"([^"]*)"\s*,\s*(\w+)\s*,\s*(?:\(\w+\)\s*)?&?\s*\w+::(\w+)\s*\)', re.sub(r'//[^\n]*', '', m.group(2)))
            if e: out.append((m.group(1), p, e))
    return out
def objfuncs(cpp):
    o = os.path.join(R, 'build/pg/obj', os.path.relpath(cpp, R)[:-4] + '.obj')
    if not os.path.exists(o): return None
    ob = cf.Obj(o); r = {}
    for nm, sec, a, b, own in ob.funcs(): r[nm] = ob.secs[sec - 1][0][a:b]
    return r
def short(n): return (n or '').split('.')[-1]
BYCLS = {}; RTTI = False; OWN = {}; SHORTC = {}; SRC = set()
def load_rtti():
    global RTTI
    p = os.path.join(R, 'map', 'projectg_msgmaps.tsv')
    if not os.path.exists(p): return
    RTTI = True
    for l in open(p).read().split('\n')[1:]:
        f = l.split('\t')
        if len(f) > 3:
            OWN[int(f[0], 16)] = f[2]
            for c in f[2].split(','):
                BYCLS.setdefault(c, int(f[0], 16))
                if '::' in c: SHORTC.setdefault(c.split('::')[-1], []).append(int(f[0], 16))
    for c, v in SHORTC.items():   # classe que no 983 está dentro de namespace (_gateway::FrSpecialBoxDlg)
        if len(set(v)) == 1: BYCLS.setdefault(c, v[0])
def main():
    load_rtti()
    av = sys.argv[1:]; v = '-v' in av
    if v: av.remove('-v')
    outp = None
    if '-o' in av: k = av.index('-o'); outp = av[k + 1]; del av[k:k + 2]
    filt = av[0] if av else ''
    tabs = tables983(); keys = {va: [n for h, c, n in t] for va, t in tabs.items()}
    rows = []
    allsrc = sources(); SRC.update(c for c, p, e in allsrc)
    for cls, cpp, ents in allsrc:
        if filt and not re.search(filt, cls): continue
        mine = [n for n, c, h in ents]
        best = sorted(((difflib.SequenceMatcher(None, mine, k, autojunk=False).ratio(), va) for va, k in keys.items() if set(k) & set(mine)), reverse=True)[:2]
        if cls in BYCLS:   # a classe dona pelo RTTI (map/projectg_msgmaps.tsv, tools/f34/mapall.py) decide antes da semelhança de nomes
            va = BYCLS[cls]
            if va not in tabs: tabs[va] = [(h, c, n) for h, c, n, e in M1.table('%x' % va)]; keys[va] = [n for h, c, n in tabs[va]]
            best = [(difflib.SequenceMatcher(None, mine, keys[va], autojunk=False).ratio(), va)]
            if not (set(short(n) for n in keys[va]) & set(short(n) for n in mine)):
                rows.append((cls, cpp, None, 0, 0, 0, 'mapa do 983 (%08x, %d entradas) sem nenhum nome de controle em comum: tela refeita' % (va, len(keys[va])), [])); continue
        if cls in BYCLS: pass
        elif RTTI and best and OWN.get(best[0][1], '-').split('::')[-1] in SRC:   # o mapa mais parecido é de outra classe do nosso fonte
            rows.append((cls, cpp, None, 0, 0, 0, 'classe sem mapa no 983 (RTTI); o mais parecido é o de %s' % OWN[best[0][1]], [])); continue
        elif not best or best[0][0] < 0.5 or (len(best) > 1 and best[1][0] == best[0][0] and tabs[best[0][1]] != tabs[best[1][1]]):
            rows.append((cls, cpp, None, 0, 0, 0, 'sem mapa único no 983 (%s)' % (best and '%.2f' % best[0][0]), [])); continue
        va = best[0][1]; t = tabs[va]; fn = objfuncs(cpp)
        if fn is None: rows.append((cls, cpp, va, 0, 0, 0, 'unidade não compila', [])); continue
        byk = collections.defaultdict(list)
        for h, c, n in t: byk[(n, c)].append(h)
        det = []; dl = collections.Counter(); seenk = collections.Counter()
        for n, c, hn in ents:
            k = (n, cmdval(c)); i = seenk[k]; seenk[k] += 1
            code = next((b for nm, b in fn.items() if nm.startswith('?%s@%s@@' % (hn, cls))), None)
            h9 = byk[k][i] if i < len(byk[k]) else 0
            if code is None or not h9: continue
            a = stores(code); b = stores(P.d[P.off(h9):P.off(h9) + 600], h9)
            if not a and not b: continue
            d = (b[0] - a[0]) if a and b and len(a) == len(b) else None
            dl['?' if d is None else '%+d' % d] += 1
            det.append((n, c, hn, h9, a, b, d))
        only9 = [(n, c, h) for h, c, n in t if (n, c) not in {(n2, cmdval(c2)) for n2, c2, h2 in ents}]
        onlyme = [(n, c, h) for n, c, h in ents if (n, cmdval(c)) not in byk]
        rows.append((cls, cpp, va, len(det), dl.get('+0', 0), best[0][0], ' '.join('%s:%d' % kv for kv in dl.most_common(6)), det, only9, onlyme))
    rows.sort(key=lambda r: -(r[3] - r[4]))
    L = ['classe\tunidade\tmapa_983\tpareadas\tiguais\tsemelhanca\tdeltas\tso_983\tso_nosso\tclasse_983']
    for r in rows:
        L.append('%s\t%s\t%s\t%d\t%d\t%.2f\t%s\t%d\t%d\t%s' % (r[0], os.path.basename(r[1]), '%08x' % r[2] if r[2] else '-', r[3], r[4], r[5], r[6], len(r[8]) if len(r) > 8 else 0, len(r[9]) if len(r) > 9 else 0, OWN.get(r[2], '-') if r[2] else '-'))
        if v and len(r) > 8:
            for n, c, hn, h9, a, b, d in r[7]:
                L.append('    %-34s %-18s %-30s %08x nosso %-14s 983 %-14s %s' % (n, c, hn, h9, ','.join('%x' % x for x in a), ','.join('%x' % x for x in b), '=' if d == 0 else ('?' if d is None else '%+d' % d)))
            for n, c, h in r[8]: L.append('    %-34s cmd=%-14x só no 983: handler %08x grava %s' % (n, c, h, ','.join('%x' % x for x in stores(P.d[P.off(h):P.off(h) + 600], h)) if h else '?'))
            for n, c, h in r[9]: L.append('    %-34s %-18s %-30s só no nosso fonte' % (n, c, h))
    txt = '\n'.join(L) + '\n'
    if outp: open(outp, 'w').write(txt)
    else: sys.stdout.write(txt)
    done = [r for r in rows if r[3]]
    sys.stderr.write('%d classes com mapa no fonte, %d pareadas com gravações; %d com tudo igual, %d com diferença; entradas %d, iguais %d\n' % (
        len(rows), len(done), sum(1 for r in done if r[3] == r[4]), sum(1 for r in done if r[3] != r[4]), sum(r[3] for r in rows), sum(r[4] for r in rows)))
main()
