#!/usr/bin/env python3
"""Frente C, V4 — pacotes de rede: sequência de chamadas da API de pacote (WSendPacket/WReceivedPacket) por função.

  pk.py 983            -> out/V4/pk983_funcs.tsv (toda função do exe 983 que monta/lê pacote) + pacotes_envio_983.tsv
  pk.py nosso          -> out/V4/pk_nosso_funcs.tsv (o mesmo nos nossos .obj, pareado pelo va983 do comparador)
  pk.py cmp            -> out/V4/pk_cmp.tsv + pk_cmp_resumo.txt (assinatura 983 × nossa, função a função)

Assinatura = chamadas em ordem de endereço: P(id) cria pacote; E1 E2 E4 E8 ES(texto) EX(texto cifrado) EB(n) (bloco de n
bytes) ED; >dest envia; D1 D2 D4 D8 DS DX DB(n) lê. `?` = argumento que não é constante na instrução `push`.
Só leitura do exe e dos .obj; não compila nada."""
import sys, os, re, glob, struct, collections, importlib.machinery, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import R, PE, Funcs, cs

OUT = os.path.join(R, 'out', 'V4')
# API no exe 983: implementação (packet.cpp, 005ab…) e embrulhos do pimpl (00a4d…/00a4e…)
API983 = {
    0x5ab3f0: 'E1', 0xa4dd50: 'E1', 0x5ab420: 'E2', 0xa4dd60: 'E2', 0x5ab450: 'E4', 0xa4dd70: 'E4',
    0x5ab490: 'E8', 0xa4dd80: 'E8', 0x5ab950: 'ES', 0xa4dda0: 'ES', 0x5ab9b0: 'EX', 0xa4ddb0: 'EX',
    0x5ab540: 'EB', 0xa4ddc0: 'EB', 0x5ab100: 'ED', 0xa4ddd0: 'ED',
    0x5ab890: 'P', 0xa4dde0: 'P', 0xa4e800: 'P', 0xa4e8a0: 'P',
    0xa4dab0: '>',
    0x5ab140: 'D1', 0xa4deb0: 'D1', 0x5ab150: 'D2', 0xa4dec0: 'D2', 0x5ab180: 'D4', 0xa4ded0: 'D4',
    0x5ab1a0: 'D8', 0xa4dee0: 'D8', 0x5abce0: 'DS', 0xa4def0: 'DS', 0x5abbc0: 'DS', 0xa4e1f0: 'DS', 0x5abd60: 'DX',
    0x5ab1c0: 'DB', 0xa4df00: 'DB',
}
# API nos nossos .obj: nome decorado
APIOBJ = [(re.compile(p), op) for p, op in (
    (r'^\?Encode1@WSendPacket@@', 'E1'), (r'^\?Encode2@WSendPacket@@', 'E2'), (r'^\?Encode4@WSendPacket@@', 'E4'),
    (r'^\?Encode8@WSendPacket@@', 'E8'), (r'^\?EncodeStr@WSendPacket@@', 'ES'),
    (r'^\?EncodeEncryptedStr@WSendPacket@@', 'EX'), (r'^\?EncodeBuffer@WSendPacket@@', 'EB'),
    (r'^\?EncodeData@WSendPacket@@', 'ED'), (r'^\?InitPacket@WSendPacket@@', 'P'),
    (r'^\?\?0WSendPacket@@QAE@(H|W4enumClientPacket@@)@Z', 'P'), (r'^\?Send@WSendPacket@@', '>'),
    (r'^\?Decode1@WReceivedPacket@@', 'D1'), (r'^\?Decode2@WReceivedPacket@@', 'D2'),
    (r'^\?Decode4@WReceivedPacket@@', 'D4'), (r'^\?Decode8@WReceivedPacket@@', 'D8'),
    (r'^\?DecodeStr@WReceivedPacket@@', 'DS'), (r'^\?DecodeEncryptedStr@WReceivedPacket@@', 'DX'),
    (r'^\?DecodeBuffer@WReceivedPacket@@', 'DB'))]
DEST = {0: 'GAME', 1: 'MSN', 2: 'SHOP', 3: 'LOGIN', 4: 'RANK'}
md = cs()


def objop(nm):
    for rx, op in APIOBJ:
        if rx.match(nm):
            return op
    return None


def scan(code, va, target_op):
    """code = bytes da função; target_op(endereço da instrução call/jmp, alvo ou None) -> op ou None.
    Devolve [(endereço, op, argumento)]."""
    ev = []
    pushes = []
    o = 0
    n = len(code)
    while o < n:
        got = False
        for a, size, mn, ops in md.disasm_lite(code[o:], va + o):
            got = True
            o = a - va + size
            if mn == 'push':
                try:
                    pushes.append(int(ops, 16) & 0xffffffff)
                except ValueError:
                    pushes.append(None)
            elif mn in ('call', 'jmp'):
                tgt = None
                if ops.startswith('0x'):
                    tgt = int(ops, 16)
                op = target_op(a, tgt)
                if op:
                    arg = ''
                    if op == 'P':
                        v = pushes[-1] if pushes else None
                        arg = '(%s)' % ('?' if v is None else '0x%x' % v)
                    elif op in ('EB', 'DB'):
                        v = pushes[-2] if len(pushes) > 1 else None
                        arg = '(%s)' % ('?' if v is None else '0x%x' % v)
                    elif op == '>':
                        v = pushes[-1] if pushes else None
                        arg = DEST.get(v, '?')
                    ev.append((a, op, arg))
                if mn == 'call':
                    pushes = []
        if not got or o < n:
            if not got:
                o += 1      # dado no meio do código (tabela de switch): anda 1 byte
    return ev


def sig(ev):
    return ' '.join(op + arg for _, op, arg in ev)


def hits983(pe):
    """endereços de `call/jmp rel32` do .text cujo alvo é da API."""
    name, v, sz, ro, rs = pe.secs[0]
    d = pe.d[ro:ro + min(sz, rs)]
    out = []
    for opc in (b'\xe8', b'\xe9'):
        p = d.find(opc)
        while p >= 0:
            if p + 5 <= len(d):
                t = (v + p + 5 + struct.unpack_from('<i', d, p + 1)[0]) & 0xffffffff
                if t in API983:
                    out.append(v + p)
            p = d.find(opc, p + 1)
    return sorted(out)


def run983():
    pe = PE()
    F = Funcs()
    hs = hits983(pe)
    porf = collections.defaultdict(list)
    fora = 0
    for h in hs:
        i = __import__('bisect').bisect_right(F.vas, h) - 1
        if i < 0:
            fora += 1
            continue
        porf[i].append(h)
    rows = []
    for i in sorted(porf):
        va, tam, uni, n645, n983 = F.l[i]
        if va in API983 or 0x5ab000 <= va < 0x5abe00 or 0xa4da00 <= va < 0xa4ecd0:
            continue        # a própria API
        fim = F.vas[i + 1] if i + 1 < len(F.vas) else va + tam
        fim = min(fim, max(porf[i]) + 5)
        code = pe.bytes(va, fim - va)
        hset = set(porf[i])
        ev = scan(code, va, lambda a, t: API983.get(t) if a in hset else None)
        perd = len(hset) - len(ev)
        rows.append((va, n645 or n983, uni, len(ev), perd, sig(ev), ev))
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'pk983_funcs.tsv'), 'w') as f:
        f.write('va983\tnome\tunidade\tn\tperdidas\tassinatura\n')
        for va, nm, uni, n, perd, s, ev in rows:
            f.write('%08x\t%s\t%s\t%d\t%d\t%s\n' % (va, nm, uni, n, perd, s))
    # pacotes enviados: cada P até o próximo P
    env = []
    for va, nm, uni, n, perd, s, ev in rows:
        cur = None
        for a, op, arg in ev:
            if op == 'P':
                cur = [a, arg[1:-1], [], '']
                env.append((va, nm, uni, cur))
            elif cur is not None and op[0] == 'E':
                cur[2].append(op + arg)
            elif cur is not None and op == '>':
                if not cur[3]:
                    cur[3] = arg
    with open(os.path.join(OUT, 'pacotes_envio_983.tsv'), 'w') as f:
        f.write('id\tdestino\tcampos\tonde\tva_func\tfuncao\tunidade\n')
        for va, nm, uni, (a, pid, campos, dest) in sorted(env, key=lambda e: (e[3][1] == '?', int(e[3][1], 16) if e[3][1] != '?' else 0, e[3][0])):
            f.write('%s\t%s\t%s\t%08x\t%08x\t%s\t%s\n' % (pid, dest, ' '.join(campos), a, va, nm, uni))
    ids = collections.Counter(e[3][1] for e in env)
    print('983: %d chamadas da API em %d funções (%d fora de função); %d montagens de pacote, %d ids distintos, %d sem id constante'
          % (len(hs), len(rows), fora, len(env), len([k for k in ids if k != '?']), ids.get('?', 0)))
    print('983: chamadas não alcançadas pelo desmonte linear: %d' % sum(r[4] for r in rows))
    return rows


def cmpfunc_mod():
    ld = importlib.machinery.SourceFileLoader('cmpfunc', os.path.join(R, 'tools', 'cmpfunc'))
    spec = importlib.util.spec_from_loader('cmpfunc', ld)
    m = importlib.util.module_from_spec(spec)
    ld.exec_module(m)
    return m


def novos_funcs_tsv():
    """unidade -> funcs.tsv mais novo (mesma regra do painel: fora /tmp/, /antes/, /ab/).
    C25: uma entrada por FONTE (caminho do .obj depois de 'obj/'), não por nome de pasta — 'golfrule' (wl.sh da C) e
    'src_projectg_golfrule' (comparação da A) são o mesmo fonte e eram contados duas vezes, a cópia velha como sem_par."""
    best = {}
    for p in glob.glob(os.path.join(R, 'out', '**', 'cmp', '*', 'funcs.tsv'), recursive=True):
        if '/tmp/' in p or '/antes/' in p or '/ab/' in p or '/V4/' in p:
            continue
        u = os.path.basename(os.path.dirname(p))
        chave = u
        with open(p) as f:
            for l in f:
                c = l.split('\t')
                if c[0] != 'arquivo' and len(c) >= 7:
                    chave = c[0].split('/obj/', 1)[-1]
                    break
        m = os.path.getmtime(p)
        if chave not in best or m > best[chave][0]:
            best[chave] = (m, p, u)
    return {u: p for (m, p, u) in best.values()}


def run_nosso():
    cm = cmpfunc_mod()
    rows = []
    semobj = []
    vistos = set()
    # C25: pares da frente C (map/pkt_c.tsv) completam funções que a comparação mais nova deixou sem par
    pktc = {}
    for l in open(os.path.join(R, 'map', 'pkt_c.tsv')):
        c = l.rstrip('\n').split('\t')
        if len(c) >= 2 and not c[0].startswith('#'):
            pktc[c[0]] = c[1]
    for u, p in sorted(novos_funcs_tsv().items()):
        info = {}
        objp = None
        for l in open(p):
            c = l.rstrip('\n').split('\t')
            if c[0] == 'arquivo' or len(c) < 7:
                continue
            objp = c[0]
            info[c[1]] = (c[3], c[5], c[2])
        if not objp:
            continue
        ap = objp if os.path.isabs(objp) else os.path.join(R, objp)
        if not os.path.exists(ap):
            semobj.append((u, objp))
            continue
        try:
            ob = cm.Obj(ap)
        except (SystemExit, struct.error):  # .obj vazio = outra frente compilando na hora
            semobj.append((u, objp))
            continue
        for nm, sec, a, b, propria in ob.funcs():
            data, rel, ch = ob.secs[sec - 1]
            alvo = {}
            for ro, (typ, si) in rel.items():
                if a <= ro < b and typ == 0x14:
                    op = objop(ob.syms[si][0])
                    if op:
                        alvo[ro - 1 - a] = op
            if not alvo:
                continue
            ev = scan(data[a:b], 0, lambda ad, t: alvo.get(ad))
            cl, va, pr = info.get(nm, ('?', '-', '?'))
            if nm in pktc:  # C39: o par explícito da C vale também sobre par por vizinhança (ICF: Net_StartPeriodItem)
                va = pktc[nm]
            chave = (nm, va)
            if chave in vistos and not propria:
                continue
            vistos.add(chave)
            rows.append((u, nm, int(propria), cl, va, len(ev), len(alvo) - len(ev), sig(ev)))
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'pk_nosso_funcs.tsv'), 'w') as f:
        f.write('unidade\tfuncao\tpropria\tclasse_cmp\tva983\tn\tperdidas\tassinatura\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    print('nosso: %d funções com API de pacote em %d unidades; %d unidades sem .obj' % (
        len(rows), len({r[0] for r in rows}), len(semobj)))
    for u, o in semobj[:10]:
        print('  sem obj:', u, o)


def casa(a, b):
    """assinaturas iguais, aceitando `?` como curinga de argumento."""
    x, y = a.split(), b.split()
    if len(x) != len(y):
        return False
    for p, q in zip(x, y):
        if p == q:
            continue
        pp, qq = p.split('(')[0].rstrip('?'), q.split('(')[0].rstrip('?')
        if p[0] == '>' and q[0] == '>' and ('?' in p or '?' in q):
            continue
        if pp == qq and ('?' in p or '?' in q):
            continue
        return False
    return True


def tipo_dif(a, b):
    """difere_id = só o id do pacote; difere_bloco = só o tamanho de um bloco (EB/DB); difere_id_bloco; senão difere_campos."""
    x, y = a.split(), b.split()
    if len(x) != len(y) or [p.split('(')[0] for p in x] != [q.split('(')[0] for q in y]:
        return 'difere_campos'
    d = {p[0] for p, q in zip(x, y) if p != q and '?' not in p and '?' not in q}
    if d == {'P'}:
        return 'difere_id'
    if d and d <= {'E', 'D'}:
        return 'difere_bloco'
    if d and d <= {'P', 'E', 'D'}:
        return 'difere_id_bloco'
    return 'difere_campos'


def run_cmp():
    r983 = {}
    for l in open(os.path.join(OUT, 'pk983_funcs.tsv')):
        c = l.rstrip('\n').split('\t')
        if c[0] != 'va983':
            r983[c[0]] = c
    out = []
    usados = set()
    cont = collections.Counter()
    for l in open(os.path.join(OUT, 'pk_nosso_funcs.tsv')):
        c = l.rstrip('\n').split('\t')
        if c[0] == 'unidade':
            continue
        u, nm, pr, cl, va, n, perd, s = c
        if va in ('-', ''):
            est = 'sem_par'
            s9 = ''
        else:
            va = va.split(',')[0].lower().zfill(8)
            usados.add(va)
            if va not in r983:
                est = 'so_nosso'      # o 983 não chama a API nesse endereço
                s9 = ''
            else:
                s9 = r983[va][5]
                est = 'igual' if s9 == s else ('igual_curinga' if casa(s9, s) else tipo_dif(s9, s))
        cont[est] += 1
        out.append((est, u, nm, pr, cl, va, s9, s))
    falt = [(va, c) for va, c in sorted(r983.items()) if va not in usados]
    with open(os.path.join(OUT, 'pk_cmp.tsv'), 'w') as f:
        f.write('estado\tunidade\tfuncao\tpropria\tclasse_cmp\tva983\tassinatura_983\tassinatura_nossa\n')
        for r in sorted(out):
            f.write('\t'.join(r) + '\n')
    with open(os.path.join(OUT, 'pk_983_sem_fonte.tsv'), 'w') as f:
        f.write('va983\tnome\tunidade\tn\tassinatura\n')
        for va, c in falt:
            f.write('%s\t%s\t%s\t%s\t%s\n' % (va, c[1], c[2], c[3], c[5]))
    with open(os.path.join(OUT, 'pk_cmp_resumo.txt'), 'w') as f:
        t = 'funções nossas com API de pacote: %d\n' % len(out)
        for k in ('igual', 'igual_curinga', 'difere_id', 'difere_bloco', 'difere_id_bloco', 'difere_campos', 'so_nosso', 'sem_par'):
            t += '  %-14s %d\n' % (k, cont[k])
        t += 'funções do 983 com API de pacote: %d; sem função nossa pareada: %d\n' % (len(r983), len(falt))
        f.write(t)
        print(t, end='')


if __name__ == '__main__':
    for a in sys.argv[1:] or ['983', 'nosso', 'cmp']:
        {'983': run983, 'nosso': run_nosso, 'cmp': run_cmp}[a]()
