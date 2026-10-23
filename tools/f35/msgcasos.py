#!/usr/bin/env python3
"""msgcasos.py SAIDA [-j N] [--cmp DIR] [--pares msg_pares.tsv] [filtro ...] — votos para os números de mensagem ABERTOS [--extra vthandle.tsv] pelos
`case` das funções que recebem MsgObject (HandleMsg e afins), lendo o switch dos dois lados (nosso .obj × exe 983).
Em cada função com par: acha as cargas `mov R,[X+4]` (MsgObject::message), executa o despacho (cmp/sub/add/dec/jcc/tabelas) para
cada número possível e anota para onde vai (alvo = endereço depois do último desvio decidido só pelo número). Número cujo alvo é
diferente do alvo de um número absurdo = tratado. Do nosso lado o número aberto aparece como 0x40000000 + n (msg983.h).
Pareamento: os tratados nos dois lados com o mesmo valor são âncoras; cada aberto n só pode casar com um tratado do 983 que
sobrou, dentro do intervalo que a tabela permite (entre as âncoras vizinhas de msg_pares.tsv), em ordem crescente.
  exato = só existe uma atribuição crescente possível;  sim = escolhida pela semelhança do corpo do caso (anotada).
Saída: casos_funcs.tsv (por switch), casos_votos.tsv (n645 → n983 por função), casos_resumo.tsv (por número)."""
import sys, os, re, csv, glob, struct, collections, difflib, bisect, importlib.machinery, importlib.util
import concurrent.futures as cf
import capstone
from capstone import x86 as X
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ld = importlib.machinery.SourceFileLoader('cmpfunc', R + '/tools/cmpfunc')
sp = importlib.util.spec_from_loader('cmpfunc', ld); cm = importlib.util.module_from_spec(sp); ld.exec_module(cm)
md = cm.md
M32 = 0xffffffff
PROV = 0x40000000
ABS = 0x7ffffff3        # número absurdo: o alvo dele é o "não tratado"
_c = None
def cmp_():
    global _c
    if _c is None:
        pe = cm.PE(R + '/ref/ProjectG_983_dump.exe')
        _c = cm.Cmp(pe, {}, cm.load_starts(R + '/map/projectg_funcs.tsv'))
    return _c
def obj_code(ob, sec, a, b):
    """bytes da função do .obj com os rótulos internos resolvidos em OBJBASE (como cm.obj_tokens)"""
    data, rel, ch = ob.secs[sec - 1]
    buf = bytearray(data[a:b]); internal = set()
    for off, (typ, si) in rel.items():
        if not (a <= off < b): continue
        nm, val, ssec, cls, styp = ob.syms[si]
        add = struct.unpack_from('<i', data, off)[0]
        if ssec == sec and a <= val + (add if typ == 6 else 0) < b and typ in (6, 0x14):
            if typ == 6:
                struct.pack_into('<I', buf, off - a, cm.OBJBASE + val + add - a); internal.add(off - a)
            else:
                struct.pack_into('<i', buf, off - a, val + add - a - (off - a + 4))
    return bytes(buf), cm.OBJBASE, (lambda o, v: 'A' if o in internal else None)
def sgn(x): return x - (1 << 32) if x & 0x80000000 else x
def cond(cc, fl):
    """fl = ('sub', a, b) | ('res', r, carry); devolve True/False ou None se não dá para decidir"""
    if fl is None: return None
    if fl[0] == 'sub':
        a, b = fl[1], fl[2]; r = (a - b) & M32; zf = r == 0; cf_ = a < b; sa, sb = sgn(a), sgn(b); lt = sa < sb
        t = {'e': zf, 'ne': not zf, 'b': cf_, 'ae': not cf_, 'be': cf_ or zf, 'a': not cf_ and not zf, 'l': lt, 'ge': not lt,
             'le': lt or zf, 'g': not lt and not zf, 's': bool(r & 0x80000000), 'ns': not r & 0x80000000}
    else:
        r, c = fl[1], fl[2]; zf = r == 0
        t = {'e': zf, 'ne': not zf, 's': bool(r & 0x80000000), 'ns': not r & 0x80000000}
        if c is not None: t.update({'b': c, 'ae': not c, 'be': c or zf, 'a': not c and not zf})
    return t.get(cc)
class Fn:
    def __init__(self, code, base, kind_at):
        self.code, self.base, self.end, self.kind_at = code, base, base + len(code), kind_at
        self.cache = {}
    def ins(self, pc):
        it = self.cache.get(pc)
        if it is None and self.base <= pc < self.end:
            it = next(md.disasm(self.code[pc - self.base:pc - self.base + 16], pc), None)
            if it is not None:
                try: rw = it.regs_access()
                except Exception: rw = ((), ())
                it = (it, [o for o in it.operands], rw[1])
            self.cache[pc] = it or 0
        return it or None
    def heads(self):
        """(endereço, registrador) das cargas mov R,[X+4]"""
        res = []
        for kind, pos, it in cm.walk(self.code, self.base, self.end, self.kind_at, False):
            if kind != 'ins' or it.mnemonic != 'mov' or len(it.operands) != 2: continue
            d, s = it.operands
            if d.type == X.X86_OP_REG and d.size == 4 and s.type == X.X86_OP_MEM and s.mem.disp == 4 and s.mem.base and not s.mem.index \
                    and s.mem.base not in (X.X86_REG_ESP, X.X86_REG_EBP) and s.mem.segment == 0:
                res.append((pos, d.reg, pos + it.size))
        return res
    def rd(self, a, n):
        if self.base <= a and a + n <= self.end:
            return int.from_bytes(self.code[a - self.base:a - self.base + n], 'little')
        return None
    def run(self, pc, reg, val):
        """executa o despacho com reg = val; devolve o endereço depois do último desvio decidido (ou None)"""
        k = {reg: val & M32}; fl = None; last = None
        for _ in range(400):
            q = self.ins(pc)
            if q is None: break
            it, ops, wr = q; m = it.mnemonic; nxt = pc + it.size
            if m in ('call', 'ret', 'retn', 'int3', 'leave'): break
            if m == 'jmp':
                o = ops[0]
                if o.type == X.X86_OP_IMM: pc = o.imm & M32; continue      # desvio incondicional não decide nada
                if o.type == X.X86_OP_MEM and o.mem.index in k and o.mem.scale == 4 and not o.mem.base:
                    t = self.rd((o.mem.disp + k[o.mem.index] * 4) & M32, 4)
                    if t is None: break
                    pc = t; last = pc; continue
                break
            if m[0] == 'j' and len(ops) == 1 and ops[0].type == X.X86_OP_IMM:
                r = cond(m[1:], fl)
                if r is None: break
                pc = (ops[0].imm & M32) if r else nxt; last = pc; continue
            done = False
            if len(ops) == 2 and ops[0].type == X.X86_OP_REG and ops[0].size == 4:
                d, s = ops; dv = k.get(d.reg)
                sv = (s.imm & M32) if s.type == X.X86_OP_IMM else k.get(s.reg) if s.type == X.X86_OP_REG else None
                if m == 'cmp' and dv is not None and sv is not None: fl = ('sub', dv, sv); done = True
                elif m == 'sub' and dv is not None and sv is not None: fl = ('sub', dv, sv); k[d.reg] = (dv - sv) & M32; done = True
                elif m == 'add' and dv is not None and sv is not None:
                    r = dv + sv; k[d.reg] = r & M32; fl = ('res', r & M32, r > M32); done = True
                elif m == 'test' and dv is not None and sv is not None: fl = ('res', dv & sv, False); done = True
                elif m == 'mov' and s.type == X.X86_OP_REG and sv is not None: k[d.reg] = sv; done = True
                elif m == 'lea' and s.type == X.X86_OP_MEM and s.mem.base in k and not s.mem.index:
                    k[d.reg] = (k[s.mem.base] + s.mem.disp) & M32; done = True
                elif m == 'movzx' and s.type == X.X86_OP_MEM and s.size == 1 and s.mem.base in k and not s.mem.index:
                    t = self.rd((k[s.mem.base] + s.mem.disp) & M32, 1)
                    if t is not None: k[d.reg] = t; done = True
            elif len(ops) == 1 and ops[0].type == X.X86_OP_REG and ops[0].size == 4 and ops[0].reg in k and m in ('dec', 'inc'):
                dv = k[ops[0].reg]
                if m == 'dec': fl = ('sub', dv, 1); k[ops[0].reg] = (dv - 1) & M32
                else: k[ops[0].reg] = (dv + 1) & M32; fl = ('res', k[ops[0].reg], None)
                done = True
            if not done:
                # instrução alheia ao despacho: o que ela escreve deixa de ser conhecido
                for r in wr:
                    if r == X.X86_REG_EFLAGS: fl = None
                    else:
                        for kr in list(k):
                            if kr == r or md.reg_name(r) in SUB.get(kr, ()): del k[kr]
                if not k and fl is None: break
            pc = nxt
        return last
    def sig(self, pc, n=30):
        """forma das primeiras instruções do corpo do caso (mnemônico + tipos dos operandos)"""
        s = []
        for _ in range(n):
            q = self.ins(pc)
            if q is None: break
            it, ops, _w = q
            s.append(it.mnemonic + ' ' + ','.join('r' if o.type == X.X86_OP_REG else 'i' if o.type == X.X86_OP_IMM else 'm' for o in ops))
            if it.mnemonic in ('ret', 'retn', 'jmp'): break
            pc += it.size
        return s
SUB = {X.X86_REG_EAX: ('ax', 'al', 'ah'), X.X86_REG_EBX: ('bx', 'bl', 'bh'), X.X86_REG_ECX: ('cx', 'cl', 'ch'),
       X.X86_REG_EDX: ('dx', 'dl', 'dh'), X.X86_REG_ESI: ('si',), X.X86_REG_EDI: ('di',)}
def switches(fn, vals):
    """[(endereço da carga, {valor: alvo tratado})] — só cargas que distinguem pelo menos um número"""
    res = []
    for pos, reg, nxt in fn.heads():
        dflt = set(fn.run(nxt, reg, x) for x in (ABS, 0x3ff5, 0xfffffff0))
        mp = {}
        for v in vals:
            t = fn.run(nxt, reg, v)
            if t is not None and t not in dflt: mp[v] = t
        # alvo comum a mais de 16 números = faixa/saída da árvore (não é corpo de caso)
        ct = collections.Counter(mp.values())
        mp = {v: t for v, t in mp.items() if ct[t] <= 16}
        if mp and len(mp) < len(vals) // 2: res.append((pos, mp))
    return res
VO = VR = None
def um(arg):
    obj, pares = arg
    out = []
    try: ob = cm.Obj(R + '/' + obj)
    except Exception as e: return obj, out, 'erro: %s' % e
    C = cmp_()
    pe = C.pe
    def ref(va):
        tr, size = C.ref_tokens(va)
        if tr is None or not size: return None
        return Fn(pe.read(va, size), va, lambda o, v, va=va: 'A' if pe.isaddr(va + o, v) else None)
    for nm, sec, a, b, own in ob.funcs():
        if nm not in pares: continue
        if 'MsgObject@@' not in nm.split('@@', 1)[-1] or nm.startswith('??'): continue
        va, cls = pares[nm]
        fo = Fn(*obj_code(ob, sec, a, b)); so = switches(fo, VO)
        if isinstance(va, tuple):
            # SEM_PAR: candidatos da vtable (vthandle.py); fica o que tiver mais âncoras em comum (>= 2, e mais que o segundo)
            pts = []
            for c in va:
                fr = ref(c)
                if fr is None: continue
                sr = switches(fr, VR)
                sc = max([len(set(v for v in mo if v < PROV) & set(mr)) for _p, mo in so for _q, mr in sr] or [0])
                pts.append((sc, c, fr, sr))
            pts.sort(key=lambda x: -x[0])
            if not pts or pts[0][0] < 2 or (len(pts) > 1 and pts[1][0] == pts[0][0]): continue
            _sc, va, fr, sr = pts[0]; cls = 'VTABLE'
        else:
            fr = ref(va)
            if fr is None: continue
            sr = switches(fr, VR)
        so = [(p, mp, {v: fo.sig(t) for v, t in mp.items()}) for p, mp in so]
        sr = [(p, mp, {v: fr.sig(t) for v, t in mp.items()}) for p, mp in sr]
        out.append((nm, va, cls, [(p - fo.base, mp, sg) for p, mp, sg in so], [(p - va, mp, sg) for p, mp, sg in sr]))
    return obj, out, ''
def main():
    global VO, VR
    a = sys.argv[1:]; out = a[0]; j = 8; cmpdir = R + '/out/F3.5/s67/depois2/cmp'; pares_f = R + '/out/F3.5/s67/msg2/msg_pares.tsv'; filt = []; extra_f = None
    i = 1
    while i < len(a):
        if a[i] == '-j': j = int(a[i + 1]); i += 2
        elif a[i] == '--cmp': cmpdir = a[i + 1]; i += 2
        elif a[i] == '--pares': pares_f = a[i + 1]; i += 2
        elif a[i] == '--extra': extra_f = a[i + 1]; i += 2
        else: filt.append(a[i]); i += 1
    hdr = {}        # valor no msg983.h -> número do 645
    for l in open(R + '/src/projectg/msg983.h', encoding='latin1'):
        m = re.match(r'#define MSG645_(0x[0-9a-f]+) (0x[0-9a-f]+)', l)
        if m: hdr[int(m.group(2), 16)] = int(m.group(1), 16)
    VR = list(range(1, 0x480)) + list(range(0x2710, 0x2740))
    VO = sorted(set(VR) | set(hdr))
    anc = sorted((int(r['msg_645'], 16), int(r['msg_983'], 16)) for r in csv.DictReader(open(pares_f), delimiter='\t') if r['decisao'] == 'ancora')
    xs = [x for x, _ in anc]
    def faixa(n):
        i = bisect.bisect_left(xs, n)
        lo = anc[i - 1][1] if i > 0 else 0
        hi = anc[i][1] if i < len(xs) else 0x480
        return lo, hi       # exclusivos
    extra = collections.defaultdict(list)
    if extra_f:
        for r in csv.DictReader(open(extra_f), delimiter='\t'):
            v = int(r['va983'], 16)
            if v not in extra[r['funcao']]: extra[r['funcao']].append(v)
    jobs = []; visto = set()
    for f in sorted(glob.glob(cmpdir + '/*/funcs.tsv')):
        pares = {}; obj = None
        for r in csv.DictReader(open(f, errors='replace'), delimiter='\t'):
            obj = r['arquivo']
            if r['funcao'] in visto or 'MsgObject@@' not in r['funcao']: continue
            if r['va983'] in ('-', '') or r['classe'] == 'SEM_PAR':
                if r['propria'] == '1' and r['funcao'] in extra: pares[r['funcao']] = (tuple(extra[r['funcao']]), 'SEM_PAR')
                continue
            pares[r['funcao']] = (int(r['va983'], 16), r['classe'])
        visto |= set(pares)
        if obj and pares and (not filt or any(x in obj for x in filt)): jobs.append((obj, pares))
    os.makedirs(out, exist_ok=True)
    res = []; erros = []
    with cf.ProcessPoolExecutor(j, initializer=_ini, initargs=(VO, VR)) as ex:
        for obj, o, err in ex.map(um, jobs):
            u = os.path.basename(obj)[:-4]
            if err: erros.append((u, err))
            res += [(u,) + x for x in o]
    votos = collections.defaultdict(lambda: collections.defaultdict(list))
    ff = open(out + '/casos_funcs.tsv', 'w'); fv = open(out + '/casos_votos.tsv', 'w')
    ff.write('unidade\tfuncao\tva983\tclasse\tcarga_nosso\tcarga_983\tancoras\tabertos\tsobram_983\tso_nosso\testado\tabertos_645\tsobram\tso_nosso(983:645)\n')
    fv.write('unidade\tfuncao\tva983\tclasse\tmsg_645\tmsg_983\tmodo\tsim\tcandidatos\n')
    nsw = 0; est = collections.Counter()
    for u, nm, va, cls, so, sr in sorted(res):
        usados = set()
        for po, mo, sgo in so:
            ab = sorted(v - PROV for v in mo if v >= PROV)
            rs = set(v for v in mo if v < PROV)
            # a carga do 983 com mais âncoras em comum; sem âncora nenhuma, só se há uma carga de cada lado
            best = None
            for k, (pr, mr, sgr) in enumerate(sr):
                if k in usados: continue
                c = len(rs & set(mr))
                if best is None or c > best[0]: best = (c, k)
            if best is None or (best[0] == 0 and not (len(so) == 1 and len(sr) == 1)):
                if ab:
                    ff.write('%s\t%s\t%08x\t%s\t+%x\t-\t0\t%d\t-\t%d\tsem_carga_983\t%s\t\n' % (u, nm, va, cls, po, len(ab), len(rs), ' '.join('%x' % x for x in ab)))
                    est['sem_carga_983'] += 1
                continue
            k = best[1]; usados.add(k); pr, mr, sgr = sr[k]; nsw += 1
            sobra = sorted(set(mr) - rs); so_nosso = sorted(rs - set(mr))
            def sim(n, y):
                return difflib.SequenceMatcher(None, sgo[n + PROV], sgr[y], autojunk=False).ratio()
            cand = {n: [y for y in sobra if faixa(n)[0] < y < faixa(n)[1]] for n in ab}
            # atribuições crescentes: conta (até 2) as que casam TODOS os abertos; se só há uma -> exato
            def conta(i, miny):
                if i == len(ab): return 1
                t = 0
                for y in cand[ab[i]]:
                    if y > miny:
                        t += conta(i + 1, y)
                        if t > 1: return t
                return t
            modo = '-'; atr = {}
            if ab:
                tot = conta(0, -1) if len(ab) <= 40 else 2
                # melhor atribuição crescente pela semelhança (pode pular aberto: caso que o 983 não tem mais)
                S = {(n, y): sim(n, y) for n in ab for y in cand[n]}
                B = [[0.0] * (len(sobra) + 1) for _ in range(len(ab) + 1)]
                for i2 in range(len(ab) - 1, -1, -1):
                    for k2 in range(len(sobra) - 1, -1, -1):
                        v = max(B[i2 + 1][k2], B[i2][k2 + 1])
                        s = S.get((ab[i2], sobra[k2]))
                        if s is not None: v = max(v, B[i2 + 1][k2 + 1] + s + 0.01)
                        B[i2][k2] = v
                i2 = k2 = 0
                while i2 < len(ab) and k2 < len(sobra):
                    s = S.get((ab[i2], sobra[k2]))
                    if s is not None and abs(B[i2][k2] - (B[i2 + 1][k2 + 1] + s + 0.01)) < 1e-9: atr[ab[i2]] = sobra[k2]; i2 += 1; k2 += 1
                    elif B[i2 + 1][k2] >= B[i2][k2 + 1]: i2 += 1
                    else: k2 += 1
                modo = 'exato' if tot == 1 and len(atr) == len(ab) else 'sim' if atr else 'nada'
                for n in ab:
                    if n in atr:
                        y = atr[n]; s = S[(n, y)]
                        fv.write('%s\t%s\t%08x\t%s\t0x%x\t0x%x\t%s\t%.2f\t%s\n' % (u, nm, va, cls, n, y, modo, s, ' '.join('%x' % c for c in cand[n])))
                        votos[n][y].append((modo, s, cls, u, nm))
                    else:
                        fv.write('%s\t%s\t%08x\t%s\t0x%x\t-\tsem\t-\t%s\n' % (u, nm, va, cls, n, ' '.join('%x' % c for c in cand[n])))
            est[modo] += 1
            ff.write('%s\t%s\t%08x\t%s\t+%x\t+%x\t%d\t%d\t%d\t%d\t%s\t%s\t%s\t%s\n' % (u, nm, va, cls, po, pr, len(rs & set(mr)), len(ab), len(sobra), len(so_nosso), modo,
                     ' '.join('%x' % x for x in ab), ' '.join('%x' % x for x in sobra[:80]),
                     ' '.join('%x:%s' % (x, '%x' % hdr[x] if x in hdr else '?') for x in so_nosso[:80])))
    ff.close(); fv.close()
    with open(out + '/casos_resumo.tsv', 'w') as f:
        f.write('msg_645\tmsg_983\tfuncoes\texato\tsim_alta\tsim_baixa\tcontra\tsim_media\texemplos\n')
        for n in sorted(votos):
            tot = sum(len(l) for l in votos[n].values())
            for y, l in sorted(votos[n].items(), key=lambda kv: -len(kv[1])):
                ex = sum(1 for v in l if v[0] == 'exato'); sa = sum(1 for v in l if v[0] == 'sim' and v[1] >= 0.8)
                f.write('0x%x\t0x%x\t%d\t%d\t%d\t%d\t%d\t%.2f\t%s\n' % (n, y, len(l), ex, sa, len(l) - ex - sa, tot - len(l), sum(v[1] for v in l) / len(l),
                        ' '.join(sorted(set(v[3] for v in l))[:5])))
    print('objs %d (erros %d) | funções com MsgObject e par: %d | switches pareados %d: %s | números abertos com voto: %d'
          % (len(jobs), len(erros), len(res), nsw, dict(est), len(votos)))
    for e in erros[:10]: print('ERRO', e)
def _ini(vo, vr):
    global VO, VR
    VO, VR = vo, vr
if __name__ == '__main__': main()
