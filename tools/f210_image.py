#!/usr/bin/env python3
"""f210_image.py nossa.dll nossa.map ref983.dll --out DIR
F2.10: compara a dll ligada inteira com a do 983, sem depender de nomes.
 1. Código: corta a .text das duas em funções (nossa: símbolos do .map; 983: map/wangreal_funcs.tsv + wangreal_gaps.tsv;
    .text$x: um trecho por funclet, cortado em ret/jmp nas duas), normaliza cada uma (endereços absolutos com relocação
    e desvios para fora da função viram zero; para dentro, deslocamento relativo ao início) e alinha as duas listas na
    ordem do link (difflib). Assinatura igual = IGUAL; nos blocos trocados, pares pela ordem: QUASE (>= 90% das
    instruções) ou DIFERENTE; o resto é SO_983 / SO_NOSSO.
 2. Alvos: nas funções IGUAL, cada chamada/endereço mascarado do 983 tem de apontar para o par do alvo do nosso.
 3. Dados: os endereços de dados citados pelo código IGUAL dão os pares dado983 <-> dado nosso; compara o conteúdo
    (ponteiros com relocação são traduzidos pelos pares; os alvos novos entram na fila: vtables, RTTI, tabelas de EH).
Saídas em DIR: funcoes.tsv, codigo_resumo.txt, alvos.txt, dados.tsv, dados_resumo.txt."""
import sys, os, struct, bisect, difflib, hashlib, collections, argparse
import capstone
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, 'tools'))
from f210_pe import PE

ap = argparse.ArgumentParser()
ap.add_argument('dll'); ap.add_argument('map'); ap.add_argument('ref'); ap.add_argument('--out', required=True)
A = ap.parse_args()
os.makedirs(A.out, exist_ok=True)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)


class Img:
    def __init__(s, path):
        s.pe = PE(path); s.d = s.pe.d; s.base = s.pe.base
        s.sec = {n: (s.base + va, vs, ro, rs) for n, va, vs, ro, rs, ch in s.pe.secs}
        s.rel = set()
        rva, sz = s.pe.dirs[5]; o = s.pe.off(rva); e = o + sz
        while o < e:
            page, bs = struct.unpack_from('<II', s.d, o)
            if not bs: break
            for i in range((bs - 8) // 2):
                w, = struct.unpack_from('<H', s.d, o + 8 + 2 * i)
                if w >> 12 == 3: s.rel.add(s.base + page + (w & 0xfff))
            o += bs
        s.rels = sorted(s.rel)
        s.imp = {}
        rva = s.pe.dirs[1][0]; o = s.pe.off(rva)
        while True:
            ilt, _, _, name, iat = struct.unpack_from('<IIIII', s.d, o)
            if not name: break
            dll = s.pe.cstr(name).lower(); t = s.pe.off(ilt or iat); k = 0
            while True:
                v, = struct.unpack_from('<I', s.d, t + 4 * k)
                if not v: break
                s.imp[s.base + iat + 4 * k] = dll + '!' + ('#%d' % (v & 0xffff) if v >> 31 else s.pe.cstr(v + 2)); k += 1
            o += 20

    def rd(s, va, n):
        """bytes de [va, va+n); o que passa do fim dos dados em arquivo (bss) vem zerado"""
        for nm, (sva, vs, ro, rs) in s.sec.items():
            if sva <= va < sva + max(vs, rs):
                k = va - sva; b = s.d[ro + k: ro + min(rs, k + n)] if k < rs else b''
                return b + bytes(n - len(b))
        return None

    def secof(s, va):
        for nm, (sva, vs, ro, rs) in s.sec.items():
            if sva <= va < sva + max(vs, rs): return nm
        return None

    def u32(s, va): return struct.unpack('<I', s.rd(va, 4))[0]

    def relin(s, a, b):
        return s.rels[bisect.bisect_left(s.rels, a): bisect.bisect_left(s.rels, b)]


N, X = Img(A.dll), Img(A.ref)

# ---------- fronteiras das funções ----------
def cut_funclets(im, a, b):
    """.text$x: um trecho por ret / jmp incondicional"""
    out = []; st = a; code = im.rd(a, b - a)
    for ins in md.disasm(code, a):
        if ins.mnemonic in ('ret', 'jmp'):
            out.append(st); st = ins.address + ins.size
        elif ins.mnemonic == 'int3' and st == ins.address:
            st = ins.address + 1
    return out

n_syms = {}  # va -> (nome, obj)
tx = {}
for l in open(A.map, errors='replace'):
    p = l.split()
    if len(p) >= 4 and p[0].startswith('0001:') and p[1].endswith('H') and p[2].startswith('.text'):
        tx[p[2]] = (N.base + 0x1000 + int(p[0][5:], 16), int(p[1][:-1], 16))
    if len(p) >= 4 and p[0].startswith('0001:') and len(p[2]) == 8 and not p[1].endswith('H'):
        try: va = int(p[2], 16)
        except ValueError: continue
        n_syms.setdefault(va, (p[1], p[-1]))
n_x0, n_x1 = tx['.text$x'][0], tx['.text$x'][0] + tx['.text$x'][1]
n_end = N.sec['.text'][0] + N.sec['.text'][1]
n_starts = sorted(v for v in n_syms if not n_x0 <= v < n_x1)
n_starts = sorted(v for v in set(n_starts) | set(cut_funclets(N, n_x0, n_x1)) if N.sec['.text'][0] <= v < n_end)

x_names = {}
for l in open(os.path.join(R, 'map', 'wangreal.tsv')):
    p = l.rstrip('\n').split('\t')
    if len(p) >= 2 and not l.startswith('#'):
        for a, b in ((p[0], p[1]), (p[1], p[0])):
            try: x_names.setdefault(int(a, 16), b); break
            except ValueError: pass
x_items = []; x_obj = {}
for fn, col in (('wangreal_funcs.tsv', 10), ('wangreal_gaps.tsv', 2)):
    for l in open(os.path.join(R, 'map', fn)):
        p = l.rstrip('\n').split('\t')
        if l[0] in '#v': continue
        x_obj[int(p[0], 16)] = p[col]
        # os vãos não viram fronteira: muitos são a cauda (ret, tabela de salto) da função anterior
        if fn == 'wangreal_funcs.tsv' or p[col] == 'text$yc_yd': x_items.append(int(p[0], 16))
        if fn == 'wangreal_funcs.tsv' and p[14] not in ('-', ''): x_names.setdefault(int(p[0], 16), p[14])
x_end = X.sec['.text'][0] + X.sec['.text'][1]
# .text$x do 983: de 1005ee10 (out/F1.3) até a primeira função de text$yc_yd
x_x0 = 0x1005ee10
x_x1 = min(v for v in x_items if x_obj[v] == 'text$yc_yd')
x_starts = sorted(v for v in set(v for v in x_items if not x_x0 <= v < x_x1) | set(cut_funclets(X, x_x0, x_x1)) if X.sec['.text'][0] <= v < x_end)


# ---------- normalização ----------
class Fn: pass

def build(im, starts, end, x0, x1):
    fs = []
    for i, st in enumerate(starts):
        en = starts[i + 1] if i + 1 < len(starts) else end
        code = im.rd(st, en - st)
        k = len(code)
        while k and code[k - 1] in (0xcc, 0x00) and not im.relin(st + k - 4, st + k): k -= 1
        # zeros finais só são enchimento no fim da seção; dentro da .text o enchimento é CC
        if any(c == 0 for c in code[k:]) and en != end: k = len(code.rstrip(b'\xcc'))
        f = Fn(); f.va = st; f.size = k; f.pad = len(code) - k; f.funclet = x0 <= st < x1
        code = code[:k]; rel = set(im.relin(st, st + k))
        toks = []; refs = []; pos = 0
        while pos < k:
            # relocação no primeiro byte = dword de tabela de salto (nenhuma instrução começa pelo endereço)
            ins = None if (st + pos) in rel else next(md.disasm(code[pos:pos + 16], st + pos, 1), None)
            if ins is None or pos + ins.size > k:
                # dados dentro da .text (tabelas de salto, GUIDs do dinput8.lib): uma "instrução" por dword/byte
                n = 4 if (st + pos) in rel and pos + 4 <= k else 1
                b = bytearray(code[pos:pos + n])
            else:
                n = ins.size; b = bytearray(ins.bytes)
            for r in range(st + pos, st + pos + n):
                if r in rel and r + 4 <= st + pos + n:
                    t, = struct.unpack_from('<I', code, r - st)
                    if st <= t < st + k: v = t - st
                    else: v = 0; refs.append(('abs', r - st, t))
                    struct.pack_into('<I', b, r - st - pos, v)
            if ins is not None and pos + ins.size <= k:
                op = code[pos]
                if op in (0xe8, 0xe9) or (op == 0x0f and n == 6 and 0x80 <= code[pos + 1] <= 0x8f):
                    t = (st + pos + n + struct.unpack_from('<i', code, pos + n - 4)[0]) & 0xffffffff
                    if not st <= t < st + k:
                        refs.append(('rel', pos + n - 4, t)); b[n - 4:n] = b'\0\0\0\0'
            toks.append(bytes(b)); pos += n
        f.thunk = im.imp.get(im.u32(st + 2)) if k == 6 and code[:2] == b'\xff\x25' else None
        if f.thunk: toks = [f.thunk.encode()]; refs = []
        f.toks = toks; f.refs = refs; f.sig = hashlib.md5(b'|'.join(toks)).digest() if k else b''
        fs.append(f)
    return fs

def refine(im, starts, end, x0, x1):
    """corte igual nas duas dlls: além das fronteiras conhecidas, todo enchimento CC que termina em endereço múltiplo
    de 16 começa um trecho novo (o Ghidra não criou função para as cópias em linha sem chamador)"""
    s = set(starts); t0 = im.sec['.text'][0]; code = im.rd(t0, end - t0)
    for r in im.relin(t0, end):                      # thunks de import: jmp [iat]
        if code[r - t0 - 2: r - t0] == b'\xff\x25' and im.u32(r) in im.imp: s.add(r - 2); s.add(r + 4)
    s.discard(end)
    for a in range(t0 + 16, end, 16):
        if x0 <= a < x1: continue
        if code[a - t0 - 1] == 0xcc and code[a - t0] != 0xcc: s.add(a)
    return sorted(s)
n_starts = refine(N, n_starts, n_end, n_x0, n_x1); x_starts = refine(X, x_starts, x_end, x_x0, x_x1)
NF = build(N, n_starts, n_end, n_x0, n_x1)
XF = build(X, x_starts, x_end, x_x0, x_x1)
NF = [f for f in NF if f.size]; XF = [f for f in XF if f.size]

# ---------- alinhamento ----------
# assinatura com vizinhança (só para desempatar cópias idênticas, p.ex. `call X; ret` de cada instância de modelo):
# a própria + a dos trechos chamados/citados, duas voltas
def deep(fs, t0, t1):
    va = [f.va for f in fs]
    def callee(t, key):
        i = bisect.bisect_right(va, t) - 1
        return key(fs[i]) + struct.pack('<I', t - va[i]) if i >= 0 and t0 <= t < t1 else b'D'
    for f in fs: f.sig2 = hashlib.md5(f.sig + b''.join(callee(t, lambda g: g.sig) for k_, o_, t in f.refs)).digest()
    for f in fs: f.sig3 = hashlib.md5(f.sig + b''.join(callee(t, lambda g: g.sig2) for k_, o_, t in f.refs)).digest()
deep(XF, X.sec['.text'][0], x_end); deep(NF, N.sec['.text'][0], n_end)
def opcodes():
    sm = difflib.SequenceMatcher(None, [f.sig3 for f in XF], [f.sig3 for f in NF], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal': yield tag, XF[i1:i2], NF[j1:j2]; continue
        xs, ns = XF[i1:i2], NF[j1:j2]
        s2 = difflib.SequenceMatcher(None, [f.sig for f in xs], [f.sig for f in ns], autojunk=False)
        for tag2, a1, a2, b1, b2 in s2.get_opcodes(): yield tag2, xs[a1:a2], ns[b1:b2]
pairs = []   # (classe, fx, fn, pct)
def pct(a, b):
    if not a or not b: return 0.0
    m = difflib.SequenceMatcher(None, a.toks, b.toks, autojunk=False)
    return sum(t.size for t in m.get_matching_blocks()) / max(len(a.toks), len(b.toks))
for tag, xs, ns in opcodes():
    if tag == 'equal':
        for fa_, fb_ in zip(xs, ns): pairs.append(['IGUAL', fa_, fb_, 1.0])
        continue
    # dentro de um bloco trocado: pares pelo melhor casamento em ordem (programação dinâmica pequena)
    if xs and ns and len(xs) * len(ns) <= 20000:
        sc = [[pct(a, b) for b in ns] for a in xs]
        D = [[0.0] * (len(ns) + 1) for _ in range(len(xs) + 1)]
        for i in range(len(xs) - 1, -1, -1):
            for j in range(len(ns) - 1, -1, -1):
                D[i][j] = max(D[i + 1][j], D[i][j + 1], D[i + 1][j + 1] + (sc[i][j] if sc[i][j] >= 0.3 else -1))
        i = j = 0
        while i < len(xs) and j < len(ns):
            if sc[i][j] >= 0.3 and D[i][j] == D[i + 1][j + 1] + sc[i][j]:
                pairs.append(['QUASE' if sc[i][j] >= 0.9 else 'DIFERENTE', xs[i], ns[j], sc[i][j]]); i += 1; j += 1
            elif D[i][j] == D[i + 1][j]: pairs.append(['SO_983', xs[i], None, 0.0]); i += 1
            else: pairs.append(['SO_NOSSO', None, ns[j], 0.0]); j += 1
        for a in xs[i:]: pairs.append(['SO_983', a, None, 0.0])
        for b in ns[j:]: pairs.append(['SO_NOSSO', None, b, 0.0])
    else:
        for a in xs: pairs.append(['SO_983', a, None, 0.0])
        for b in ns: pairs.append(['SO_NOSSO', None, b, 0.0])

# fora de ordem: o que sobrou e tem a mesma assinatura do outro lado (ordem dos .obj/libs no link; cópias idênticas)
amb = set()
for key in (lambda f: f.sig3, lambda f: f.sig):
    lx = collections.defaultdict(list); ln = collections.defaultdict(list)
    for p in pairs:
        if p[0] == 'SO_983': lx[key(p[1])].append(p)
        elif p[0] == 'SO_NOSSO': ln[key(p[2])].append(p)
    drop = set()
    for sg, L in lx.items():
        M = ln.get(sg, [])
        for pa, pb in zip(L, M):
            drop.add(id(pa)); drop.add(id(pb))
            q = ['IGUAL', pa[1], pb[2], 1.0]; pairs.append(q)
            if len(L) > 1 or len(M) > 1: amb.add(id(q))
    pairs = [p for p in pairs if id(p) not in drop]
n_fora = sum(1 for p in pairs if id(p) in amb)
# o resto: melhor par por semelhança entre trechos de tamanho parecido (funções reescritas que mudaram de lugar)
rx = [p for p in pairs if p[0] == 'SO_983' and p[1].size >= 24]; rn = [p for p in pairs if p[0] == 'SO_NOSSO' and p[2].size >= 24]
cand = []
for pa in rx:
    for pb in rn:
        a, b = pa[1], pb[2]
        if a.funclet != b.funclet or not 0.6 <= a.size / b.size <= 1.67: continue
        ta, tb = collections.Counter(a.toks), collections.Counter(b.toks)
        if sum((ta & tb).values()) / max(len(a.toks), len(b.toks)) < 0.5: continue
        cand.append((pct(a, b), a.va, b.va, pa, pb))
cand.sort(key=lambda c: (-c[0], c[1], c[2])); drop = set()
for sc_, _, _, pa, pb in cand:
    if sc_ < 0.5 or id(pa) in drop or id(pb) in drop: continue
    drop.add(id(pa)); drop.add(id(pb)); pairs.append(['QUASE' if sc_ >= 0.9 else 'DIFERENTE', pa[1], pb[2], sc_])
pairs = [p for p in pairs if id(p) not in drop]
pairs.sort(key=lambda p: (p[1].va if p[1] else F_ORD.get(p[2].va, 0), 0 if p[1] else 1)) if False else None
x_sorted = [f.va for f in XF]; n_sorted = [f.va for f in NF]
x_by = {f.va: f for f in XF}; n_by = {f.va: f for f in NF}
F = {p[1].va: p[2].va for p in pairs if p[1] and p[2] and id(p) not in amb}   # função 983 -> nossa (todas as classes)
FE = {p[1].va: p[2].va for p in pairs if p[0] == 'IGUAL' and id(p) not in amb}
def same_copy(t1, t2):
    """os dois alvos caem em cópias de código idêntico, no mesmo deslocamento"""
    i = bisect.bisect_right(x_sorted, t1) - 1; j = bisect.bisect_right(n_sorted, t2) - 1
    if i < 0 or j < 0: return False
    a, b = x_by[x_sorted[i]], n_by[n_sorted[j]]
    return a.sig == b.sig and t1 - a.va == t2 - b.va and t1 - a.va < a.size + a.pad

def code_map(t):
    """endereço de código do 983 -> nosso, pelo par da função que o contém (só funções IGUAL dão deslocamento certo)"""
    i = bisect.bisect_right(x_sorted, t) - 1
    if i < 0: return None, None
    fa = x_sorted[i]
    if t >= fa + x_by[fa].size + x_by[fa].pad or fa not in F: return None, None
    return F[fa] + (t - fa), fa in FE

# ---------- alvos + pares de dados ----------
xt0, xt1 = X.sec['.text'][0], x_end
nt0, nt1 = N.sec['.text'][0], n_end
D = {}; Dr = {}; conflict = []; tg = collections.Counter(); bad = []
def add_data(a, b, src):
    if a in D and D[a] != b: conflict.append((a, D[a], b, src)); return False
    if b in Dr and Dr[b] != a: conflict.append((a, Dr[b], b, src)); return False
    new = a not in D
    D[a] = b; Dr[b] = a
    return new
def name_n(va):
    i = bisect.bisect_right(n_sorted, va) - 1
    s = n_syms.get(n_sorted[i], ('?', '?')) if i >= 0 else ('?', '?')
    return s[0]
for cl, fx, fn, pc in pairs:
    if cl != 'IGUAL': continue
    for (k1, o1, t1), (k2, o2, t2) in zip(fx.refs, fn.refs):
        if xt0 <= t1 < xt1:
            m, exact = code_map(t1)
            if m == t2: tg['codigo_ok'] += 1
            elif same_copy(t1, t2): tg['codigo_ok_copia_identica'] += 1
            elif m is None and not nt0 <= t2 < nt1: tg['codigo_x_dado'] += 1; bad.append((fx.va, fn.va, t1, t2, 'código × dado'))
            elif m is None: tg['codigo_sem_par'] += 1; bad.append((fx.va, fn.va, t1, t2, 'alvo sem par'))
            elif not exact: tg['codigo_par_nao_igual'] += 1
            else:
                tg['codigo_outro_alvo'] += 1; i = bisect.bisect_right(x_sorted, t1) - 1; j = bisect.bisect_right(n_sorted, t2) - 1
                bad.append((fx.va, fn.va, t1, t2, 'outro alvo (par do alvo = %08x); alvo983 %08x+%x %dB, alvo nosso %08x+%x %dB %s' % (
                    m, x_sorted[i], t1 - x_sorted[i], x_by[x_sorted[i]].size, n_sorted[j], t2 - n_sorted[j], n_by[n_sorted[j]].size, name_n(t2)[:60])))
        elif t1 in X.imp or t2 in N.imp:
            if X.imp.get(t1) == N.imp.get(t2): tg['import_ok'] += 1
            else: tg['import_outro'] += 1; bad.append((fx.va, fn.va, t1, t2, 'import %s × %s' % (X.imp.get(t1), N.imp.get(t2))))
        else:
            if X.secof(t1) != N.secof(t2): tg['dado_outra_secao'] += 1; bad.append((fx.va, fn.va, t1, t2, 'seção %s × %s' % (X.secof(t1), N.secof(t2))))
            elif add_data(t1, t2, fx.va) or D.get(t1) == t2: tg['dado_ok'] += 1
            else: tg['dado_conflito'] += 1; bad.append((fx.va, fn.va, t1, t2, 'dado já pareado com outro endereço'))

# ---------- dados ----------
def bounds(im, extra):
    s = set(extra)
    for r in im.rels:
        s.add(im.u32(r))
    for nm, (sva, vs, ro, rs) in im.sec.items(): s.add(sva); s.add(sva + vs)
    for i in range(16):
        rva, sz = im.pe.dirs[i]
        if rva: s.add(im.base + rva); s.add(im.base + rva + sz)
    return sorted(s)
done = {}; rows = []
for rnd in range(40):
    xb = bounds(X, D.keys()); nb = bounds(N, Dr.keys())
    todo = [a for a in sorted(D) if a not in done]
    if not todo: break
    for a in todo:
        b = D[a]
        la = xb[bisect.bisect_right(xb, a)] - a if bisect.bisect_right(xb, a) < len(xb) else 0
        lb = nb[bisect.bisect_right(nb, b)] - b if bisect.bisect_right(nb, b) < len(nb) else 0
        n = min(la, lb); sec = X.secof(a)
        if n <= 0 or n > 0x40000 or sec is None: done[a] = ('?', 0, 0, ''); continue
        sva, vs, ro, rs = X.sec[sec]
        ini = max(0, min(n, sva + rs - a))            # parte com conteúdo em arquivo
        da, db = X.rd(a, n), N.rd(b, n)
        ra = {r - a for r in X.relin(a, a + n) if r + 4 <= a + n}; rb = {r - b for r in N.relin(b, b + n) if r + 4 <= b + n}
        diff = 0; note = []; i = 0; ptr_ok = ptr_bad = 0
        while i < n:
            if i in ra or i in rb:
                if not (i in ra and i in rb):
                    diff += 4; note.append('+%x relocação só de um lado' % i); i += 4; continue
                p, = struct.unpack_from('<I', da, i); q, = struct.unpack_from('<I', db, i)
                if xt0 <= p < xt1:
                    m, exact = code_map(p)
                    ok = m == q or same_copy(p, q)
                elif p in X.imp or q in N.imp: ok = X.imp.get(p) == N.imp.get(q)
                else:
                    ok = X.secof(p) == N.secof(q) and (D.get(p, q) == q) and (Dr.get(q, p) == p)
                    if ok: add_data(p, q, a)
                if ok: ptr_ok += 1
                else: ptr_bad += 1; diff += 4; note.append('+%x ponteiro %08x × %08x' % (i, p, q))
                i += 4
            else:
                if da[i] != db[i]:
                    diff += 1
                    if len(note) < 6: note.append('+%x %02x × %02x' % (i, da[i], db[i]))
                i += 1
        st = 'IGUAL' if not diff else 'DIFERENTE'
        if la != lb: note.insert(0, 'tamanho %d × %d' % (la, lb))
        done[a] = (st, n, diff, '; '.join(note[:8]))
        rows.append((a, b, sec, n, la, lb, st, diff, ptr_ok, ptr_bad, '; '.join(note[:8])))

# ---------- saídas ----------
def objn(f):
    s = n_syms.get(f.va)
    if f.funclet: return '(funclets .text$x)'
    if not s:
        i = bisect.bisect_right(n_sorted, f.va) - 1; s = n_syms.get(n_sorted[i], ('?', '?'))
    o = s[1]
    return o if o.endswith('.obj') and ':' not in o else 'lib:' + o.split(':')[0]
x_known = sorted(x_obj)
def objx(f):
    if f.funclet: return '(funclets .text$x)'
    i = bisect.bisect_right(x_known, f.va) - 1
    return x_obj[x_known[i]] if i >= 0 else '?'
with open(os.path.join(A.out, 'funcoes.tsv'), 'w') as o:
    o.write('classe\tpct\tva983\tbytes983\tva_nosso\tbytes_nosso\tobj_nosso\tunidade983\tnome\n')
    for cl, fx, fn, pc in pairs:
        nm = n_syms.get(fn.va, ('', ''))[0] if fn else ''
        if not nm and fx: nm = x_names.get(fx.va, '')
        o.write('%s\t%.1f\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (cl, pc * 100, '%08x' % fx.va if fx else '-', fx.size if fx else '-',
                '%08x' % fn.va if fn else '-', fn.size if fn else '-', objn(fn) if fn else '-', objx(fx) if fx else '-', nm))
with open(os.path.join(A.out, 'codigo_resumo.txt'), 'w') as o:
    def P(*a):
        s = ' '.join(str(x) for x in a); print(s); o.write(s + '\n')
    P('# código: %s × %s' % (A.dll, A.ref))
    xtot = sum(f.size for f in XF); ntot = sum(f.size for f in NF)
    P('.text 983: %d B em %d trechos (+%d B de enchimento); nossa: %d B em %d trechos (+%d B)' % (
        xtot, len(XF), sum(f.pad for f in XF), ntot, len(NF), sum(f.pad for f in NF)))
    c = collections.Counter(); bx = collections.Counter(); bn = collections.Counter()
    for cl, fx, fn, pc in pairs:
        c[cl] += 1; bx[cl] += fx.size if fx else 0; bn[cl] += fn.size if fn else 0
    P('%-10s %7s %10s %7s %10s %7s' % ('classe', 'trechos', 'bytes 983', '%', 'bytes nosso', '%'))
    for cl in ('IGUAL', 'QUASE', 'DIFERENTE', 'SO_983', 'SO_NOSSO'):
        P('%-10s %7d %10d %6.2f%% %10d %6.2f%%' % (cl, c[cl], bx[cl], 100 * bx[cl] / xtot, bn[cl], 100 * bn[cl] / ntot))
    P('dos IGUAL, %d são cópias idênticas pareadas fora de ordem (assinatura repetida)' % n_fora)
    P('mesmo endereço nas duas dlls: %d de %d pares' % (sum(1 for p in pairs if p[1] and p[2] and p[1].va == p[2].va),
                                                       sum(1 for p in pairs if p[1] and p[2])))
    P(''); P('## por unidade (bytes do 983; a unidade é a do nosso .map, ou a do mapa do 983 para SO_983)')
    g = collections.defaultdict(collections.Counter)
    for cl, fx, fn, pc in pairs:
        u = objn(fn) if fn else objx(fx) + ' [983]'
        g[u][cl] += 1; g[u]['B_' + cl] += fx.size if fx else fn.size
    P('%-28s %s' % ('unidade', '  '.join('%-16s' % x for x in ('IGUAL', 'QUASE', 'DIFERENTE', 'SO_983', 'SO_NOSSO'))))
    for u in sorted(g, key=lambda u: -sum(v for k, v in g[u].items() if k.startswith('B_'))):
        P('%-28s %s' % (u, '  '.join('%5d %8d B ' % (g[u][x], g[u]['B_' + x]) for x in ('IGUAL', 'QUASE', 'DIFERENTE', 'SO_983', 'SO_NOSSO'))))
    P(''); P('## trechos não iguais (classe, %, 983, bytes, nosso, bytes, unidade, nome)')
    for cl, fx, fn, pc in pairs:
        if cl == 'IGUAL': continue
        nm = n_syms.get(fn.va, ('', ''))[0] if fn else x_names.get(fx.va, '')
        P('%-9s %5.1f %s %5s %s %5s %-22s %s' % (cl, pc * 100, '%08x' % fx.va if fx else '-       ', fx.size if fx else '-',
          '%08x' % fn.va if fn else '-       ', fn.size if fn else '-', objn(fn) if fn else objx(fx), nm[:110]))
with open(os.path.join(A.out, 'alvos.txt'), 'w') as o:
    def P(*a):
        s = ' '.join(str(x) for x in a); print(s); o.write(s + '\n')
    P('# alvos das funções IGUAL (chamadas e endereços absolutos mascarados na assinatura)')
    for k, v in sorted(tg.items()): P('%-22s %d' % (k, v))
    P('pares de dados vindos do código e dos próprios dados: %d; conflitos: %d' % (len(D), len(conflict)))
    for fa, fb, t1, t2, why in bad: o.write('%08x/%08x  alvo %08x × %08x  %s  [%s]\n' % (fa, fb, t1, t2, why, name_n(fb)[:80]))
    for a, b0, b1, src in conflict: o.write('conflito: %08x já com %08x, agora %08x (em %08x)\n' % (a, b0, b1, src))
rows.sort()
with open(os.path.join(A.out, 'dados.tsv'), 'w') as o:
    o.write('va983\tva_nosso\tsecao\tbytes\ttam983\ttam_nosso\tclasse\tbytes_dif\tponteiros_ok\tponteiros_dif\tnota\n')
    for r in rows: o.write('%08x\t%08x\t%s\t%d\t%d\t%d\t%s\t%d\t%d\t%d\t%s\n' % r)
with open(os.path.join(A.out, 'dados_resumo.txt'), 'w') as o:
    def P(*a):
        s = ' '.join(str(x) for x in a); print(s); o.write(s + '\n')
    P('# dados: itens pareados a partir do código IGUAL e dos ponteiros dentro dos próprios dados')
    P('%-8s %6s %9s %9s | %6s %9s | %6s %9s %9s | %s' % ('seção', 'itens', 'bytes', '% seção', 'iguais', 'bytes', 'difer.', 'bytes', 'B difer.', 'ponteiros ok/dif'))
    for sec in ('.text', '.rdata', '.data'):
        rr = [r for r in rows if r[2] == sec]
        if not rr: continue
        tot = X.sec[sec][1]; cov = sum(r[3] for r in rr)
        eq = [r for r in rr if r[6] == 'IGUAL']; df = [r for r in rr if r[6] != 'IGUAL']
        P('%-8s %6d %9d %8.1f%% | %6d %9d | %6d %9d %9d | %d/%d' % (sec, len(rr), cov, 100 * cov / tot, len(eq), sum(r[3] for r in eq),
          len(df), sum(r[3] for r in df), sum(r[7] for r in df), sum(r[8] for r in rr), sum(r[9] for r in rr)))
    P('itens com tamanho diferente (até o próximo endereço citado): %d' % sum(1 for r in rows if r[4] != r[5]))
    P('mesmo endereço nas duas dlls: %d de %d itens' % (sum(1 for r in rows if r[0] == r[1]), len(rows)))
