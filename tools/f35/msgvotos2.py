#!/usr/bin/env python3
"""msgvotos2.py SAIDA [-j N] [--cmp DIR] [filtro ...] — votos para a renumeração das mensagens entre atores (645 → 983) em TODAS
as funções com par (não só o despachante comum, que é o msgvotos.py da s66).
Pares função do .obj × VA do 983: os funcs.tsv de uma comparação completa (padrão out/F3.5/s65/depois/cmp).
(E) envios: em cada lado, a sequência dos números passados ao construtor MsgObject(IActor*, int msg, ...) (0046e780) — o 2º push
    antes do call. Só vota quando os dois lados têm a mesma quantidade de construções (par posição a posição).
(R) recebimentos: só nas funções cuja assinatura recebe MsgObject; alinha as instruções pela forma (imediato mascarado) e colhe os
    pares de imediato de cmp/sub/add (os testes do switch). Mais fraco que (E): a árvore do switch muda quando entram casos.
Saída: env_funcs.tsv, env_votos.tsv, rec_votos.tsv, rec_locais.tsv."""
import sys, os, re, csv, glob, collections, difflib, importlib.machinery, importlib.util
import concurrent.futures as cf
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ld = importlib.machinery.SourceFileLoader('cmpfunc', R + '/tools/cmpfunc')
sp = importlib.util.spec_from_loader('cmpfunc', ld); cm = importlib.util.module_from_spec(sp); ld.exec_module(cm)
CTOR_N = '??0MsgObject@@QAE@PBVIActor@@HHHHHH@Z'; CTOR_V = 0x46e780
HEX = re.compile(r'[0-9a-f]+$')
_c = None
def cmp_():
    global _c
    if _c is None:
        pe = cm.PE(R + '/ref/ProjectG_983_dump.exe')
        _c = cm.Cmp(pe, {}, cm.load_starts(R + '/map/projectg_funcs.tsv'))
    return _c
def isctor(ref):
    return bool(ref) and ((ref[0][0] == 'S' and ref[0][1] == CTOR_N and not ref[0][2]) or (ref[0][0] == 'V' and ref[0][2] == CTOR_V))
POSTS = {'?SendMsg@IActor@@QAEHPBV1@PBDHHHHK@Z': 3, '?PostMsg@IActor@@QAEHPBV1@PBDHHHHK@Z': 3, '?AfxPostMsg@@YIHPBVIActor@@PBDHHHHK@Z': 1}
POSTV = {0xa46580: 3, 0xa46940: 3, 0x47d200: 1}
SLOT = 0x2c     # IActor::HandleMsg na vtable (operator<< do 983, 0046e7c0: call [vtbl+0x2c])
LEA = re.compile(r'lea (\w+),\[(\w+)\+\*1\+([0-9a-f]+)\]$')
STO = re.compile(r'mov \[(\w+)\+\*1\+([0-9a-f]+)\],([0-9a-f]+)$')
VCALL = re.compile(r'call \[\w+\+\*1\+%x\]$' % SLOT)
def npush(t, i, n):
    """n-ésimo push antes da instrução i (1 = o último), sem cruzar call/salto; imediato -> int, senão None"""
    k = 0
    for j in range(i - 1, max(i - 40, -1), -1):
        mj = t.m[j]
        if mj == 'call' or mj.startswith('j') or mj.startswith('ret') or mj.startswith('.'): return None
        if mj == 'push':
            k += 1
            if k == n:
                o = t.s[j][5:]
                return int(o, 16) if HEX.match(o) else None
    return None
def envios(t):
    """sequência de (tipo, número): C = construtor fora de linha, P = SendMsg/PostMsg/AfxPostMsg, V = HandleMsg virtual com o
    MsgObject montado em linha (número = imediato gravado em objeto+4)"""
    seq = []
    for i, m in enumerate(t.m):
        if m != 'call': continue
        ref = t.refs[i]
        if isctor(ref): seq.append(('C', npush(t, i, 2))); continue
        if ref:
            n = POSTS.get(ref[0][1]) if ref[0][0] == 'S' and not ref[0][2] else POSTV.get(ref[0][2]) if ref[0][0] == 'V' else None
            if n: seq.append(('P', npush(t, i, n))); continue
        if not VCALL.match(t.s[i]):
            # `mov R,[vtbl+0x2c]` ... `call R`
            q = re.match(r'call (e[a-ds][xi])$', t.s[i]); ok = False
            if q:
                for j in range(i - 1, max(i - 8, -1), -1):
                    if t.m[j] == 'call' or t.m[j].startswith('j'): break
                    if re.match(r'mov %s,\[\w+\+\*1\+%x\]$' % (q.group(1), SLOT), t.s[j]): ok = True; break
            if not ok: continue
        # o argumento: push R logo antes, com R = lea [B+D]
        reg = None; slot = None
        for j in range(i - 1, max(i - 8, -1), -1):
            if t.m[j] == 'call' or t.m[j].startswith('j'): break
            if reg is None and t.m[j] == 'push': reg = t.s[j][5:]; continue
            if reg is not None:
                q = LEA.match(t.s[j])
                if q and q.group(1) == reg: slot = (q.group(2), (int(q.group(3), 16) + 4) & 0xffffffff); break
        if slot is None: continue
        val = None; achou = False
        for j in range(i - 1, max(i - 120, -1), -1):
            q = STO.match(t.s[j])
            if q and q.group(1) == slot[0] and int(q.group(2), 16) == slot[1]: val = int(q.group(3), 16); achou = True; break
            if t.s[j].startswith('mov [%s+*1+%x],' % slot): achou = True; break      # número vindo de registrador
        if achou: seq.append(('V', val))
    return seq
def imm(s):
    p = s.split(' ', 1)
    if len(p) < 2: return None
    o = p[1].split(',')
    return int(o[-1], 16) if len(o) == 2 and HEX.match(o[-1]) else None
def recebe(to, tr):
    res = []
    sm = difflib.SequenceMatcher(None, to.r, tr.r, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != 'equal': continue
        for k in range(i2 - i1):
            m = to.m[i1 + k]
            if m not in ('cmp', 'sub', 'add'): continue
            x, y = imm(to.s[i1 + k]), imm(tr.s[j1 + k])
            if x is None or y is None: continue
            if 'esp' in to.s[i1 + k]: continue
            res.append((m, x, y))
    return res
def um(arg):
    obj, pares = arg
    out_e, out_r = [], []
    try: ob = cm.Obj(R + '/' + obj)
    except Exception as e: return obj, out_e, out_r, 'erro: %s' % e
    C = cmp_()
    for nm, sec, a, b, own in ob.funcs():
        if nm not in pares: continue
        va, cls = pares[nm]
        to = cm.obj_tokens(ob, sec, a, b)
        eo = envios(to); temctor = bool(eo)
        rx = 'MsgObject@@' in nm.split('@@', 1)[-1] and not nm.startswith('??')
        if not temctor and not rx: continue
        tr, _ = C.ref_tokens(va)
        if tr is None: continue
        if temctor:
            out_e.append((nm, '%08x' % va, cls, eo, envios(tr)))
        if rx:
            for m, x, y in recebe(to, tr): out_r.append((nm, '%08x' % va, cls, m, x, y))
    return obj, out_e, out_r, ''
def fx(s): return ' '.join(k + ('%x' % x if x is not None else '?') for k, x in s)
def main():
    a = sys.argv[1:]; out = a[0]; j = 8; cmpdir = R + '/out/F3.5/s65/depois/cmp'; filt = []
    i = 1
    while i < len(a):
        if a[i] == '-j': j = int(a[i + 1]); i += 2
        elif a[i] == '--cmp': cmpdir = a[i + 1]; i += 2
        elif a[i] == '--inv': i += 1
        else: filt.append(a[i]); i += 1
    jobs = []; visto = set()
    for f in sorted(glob.glob(cmpdir + '/*/funcs.tsv')):
        pares = {}; obj = None
        for r in csv.DictReader(open(f, errors='replace'), delimiter='\t'):
            obj = r['arquivo']
            if r['va983'] in ('-', '') or r['classe'] == 'SEM_PAR' or r['funcao'] in visto: continue
            pares[r['funcao']] = (int(r['va983'], 16), r['classe'])
        visto |= set(pares)
        if obj and pares and (not filt or any(x in obj for x in filt)): jobs.append((obj, pares))
    os.makedirs(out, exist_ok=True)
    # --inv: o fonte já está em M983(n); desfaz pelo msg983.h (valor -> número do 645) para os votos continuarem em números do 645.
    # Valor que não está no cabeçalho (número do 983 escrito direto) não vota.
    inv = None
    if '--inv' in a:
        inv = {}
        for l in open(R + '/src/projectg/msg983.h', encoding='latin1'):
            m = re.match(r'#define MSG645_(0x[0-9a-f]+) (0x[0-9a-f]+)', l)
            if m: inv[int(m.group(2), 16)] = int(m.group(1), 16)
    def volta(x):
        if inv is None or x is None or x == 0 or 0x2710 <= x < 0x40000000: return x
        return inv.get(x)
    E = []; Rc = []; erros = []
    with cf.ProcessPoolExecutor(j) as ex:
        for obj, e, r, err in ex.map(um, jobs):
            u = re.sub(r'^build/[^/]+/obj/', '', obj)
            if err: erros.append((u, err))
            E += [(u, nm, va, cls, [(k, volta(x)) for k, x in sq], q) for nm, va, cls, sq, q in e]
            Rc += [(u, nm, va, cls, m, volta(x), y) for nm, va, cls, m, x, y in r if volta(x) is not None]
    votos = collections.defaultdict(lambda: collections.defaultdict(list)); est = collections.Counter()
    with open(out + '/env_funcs.tsv', 'w') as f:
        f.write('unidade\tfuncao\tva983\tclasse\tmsgs_nosso\tmsgs_983\testado\n')
        for u, nm, va, cls, s, q in sorted(E):
            ok = len(s) == len(q) and all(x[0] == y[0] for x, y in zip(s, q))
            e = 'vota' if ok else 'tamanho'; est[e] += 1
            f.write('\t'.join((u, nm, va, cls, fx(s), fx(q), e)) + '\n')
            if ok:
                for (k, x), (_, y) in zip(s, q):
                    if x is not None and y is not None: votos[x][y].append((cls, u, nm))
    ig = mud = disp = 0
    with open(out + '/env_votos.tsv', 'w') as f:
        f.write('msg_645\tmsg_983\tvotos\tvotos_contra\tIGUAL\tQUASE\tDIFERENTE\tunidades\texemplos\n')
        for x in sorted(votos):
            tot = sum(len(v) for v in votos[x].values())
            best = max(votos[x], key=lambda y: len(votos[x][y]))
            ig += best == x; mud += best != x; disp += len(votos[x]) > 1
            for y, l in sorted(votos[x].items(), key=lambda kv: -len(kv[1])):
                c = collections.Counter(v[0] for v in l); us = sorted(set(os.path.basename(v[1])[:-4] for v in l))
                f.write('0x%x\t0x%x\t%d\t%d\t%d\t%d\t%d\t%d\t%s\n' % (x, y, len(l), tot - len(l), c['IGUAL'], c['QUASE'], c['DIFERENTE'],
                        len(us), ' '.join(us[:6])))
    rv = collections.defaultdict(lambda: collections.defaultdict(set))
    with open(out + '/rec_locais.tsv', 'w') as f:
        f.write('unidade\tfuncao\tva983\tclasse\tmnem\tnosso\t983\n')
        for u, nm, va, cls, m, x, y in sorted(Rc):
            f.write('%s\t%s\t%s\t%s\t%s\t0x%x\t0x%x\n' % (u, nm, va, cls, m, x, y))
            if m == 'cmp': rv[x][y].add(nm)
    with open(out + '/rec_votos.tsv', 'w') as f:
        f.write('imediato_nosso\timediato_983\tfuncoes\tfuncoes_contra\texemplos\n')
        for x in sorted(rv):
            tot = sum(len(v) for v in rv[x].values())
            for y, l in sorted(rv[x].items(), key=lambda kv: -len(kv[1])):
                f.write('0x%x\t0x%x\t%d\t%d\t%s\n' % (x, y, len(l), tot - len(l), ' '.join(sorted(l)[:3])))
    print('objs %d (erros %d) | funções com envio %d: %s | mensagens do 645 com voto %d: maioria igual %d, maioria diferente %d, disputadas %d'
          % (len(jobs), len(erros), len(E), dict(est), len(votos), ig, mud, disp))
    print('funções que recebem MsgObject com par: %d | pares de imediato (cmp) distintos: %d' % (len(set(x[1] for x in Rc)), sum(len(v) for v in rv.values())))
    for e in erros[:10]: print('ERRO', e)
if __name__ == '__main__': main()
