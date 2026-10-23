#!/usr/bin/env python3
"""Frente C, V4 — pacotes RECEBIDOS: ids tratados por cada despachante (OnPacket) do exe 983 × `case` do nosso fonte.

  rx.py   -> out/V4/pacotes_recebe_983.tsv (despachante, id, endereço do caso, leituras no trecho do caso)
             out/V4/rx_cmp.tsv (id a id: 983 × fonte) + rx_resumo.txt
983: segue o código depois do 1º Decode2 (tipo do pacote) pela árvore de comparações do switch do MSVC
(cmp/sub/dec + je/ja/jg…, `jmp [reg*4+tabela]` com tabela de bytes opcional) guardando "reg = tipo − k".
Fonte: `case` do 1º nível do `switch (type)` da função (por profundidade de chaves). Só leitura.
Estado `difere_bloco` (lote 9 da C-PKT): mesma sequência de leituras, mas um DecodeBuffer do fonte tem tamanho diferente do
983. O tamanho do fonte vem do literal, dos V3_SIZE/C_ASSERT ou de out/V4/sizeof_fonte.tsv (`make pkt-sizeof`, que compila
uma sonda por unidade); sem isso o bloco sai `DB(?)` e não é conferido."""
import sys, os, re, struct, collections, bisect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import R, PE, Funcs, cs
import pk
import capstone
from capstone import x86 as X

OUT = os.path.join(R, 'out', 'V4')
# despachante do 983 -> (arquivo do fonte, função)
DISP = [
    (0x009c20a0, 'src/projectg/taskmanager.cpp', 'CTask::OnPacketCommon'),
    (0x00ac03a0, 'src/projectg/lobbytask.cpp', 'CLobbyTask::OnPacket'),
    (0x0069eef0, 'src/projectg/golftask.cpp', 'CGolfTask::OnPacket'),
    (0x005a8360, 'src/projectg/realmyroomtask.cpp', 'CMyRoomWidget::OnPacket'),  # C46: era CRealMyRoomTask (não existe no 983)
    (0x007b5a20, 'src/projectg/avatar_task.cpp', 'ntAvatarChatTask::OnPacket'),
    (0x005e0ff0, 'src/projectg/jp/shopwidget.cpp', 'CShopWidget::OnPacket'),  # C50: era CShopTask (não existe no 983; B109)
    (0x006b2ee0, 'src/projectg/jp/tutorialwidget.cpp', 'CTutorialWidget::OnPacket'),  # C63: tutorialtask.cpp fora do build (A127)
    (0x0082c830, 'src/projectg/ghosttask.cpp', 'CGhostTask::OnPacket'),
    (0x00b1c5d0, 'src/projectg/familytask.cpp', 'CFamilyTask::OnPacket'),
    (0x00813a70, 'src/projectg/itembuffactor.cpp', 'CItemBuff::ProcessPacket', 'D4'),  # C63: sub-switch do Decode4 depois do id 0x181
    (0x009b9080, '', ''), (0x00910b80, '', ''),
]
JCC_EQ = ('je',)
JCC = ('ja', 'jae', 'jb', 'jbe', 'jg', 'jge', 'jl', 'jle', 'jne', 'je')
REGS = {X.X86_REG_EAX: 'a', X.X86_REG_AX: 'a', X.X86_REG_ECX: 'c', X.X86_REG_CX: 'c', X.X86_REG_EDX: 'd',
        X.X86_REG_DX: 'd', X.X86_REG_EBX: 'b', X.X86_REG_BX: 'b', X.X86_REG_ESI: 'S', X.X86_REG_SI: 'S',
        X.X86_REG_EDI: 'D', X.X86_REG_DI: 'D'}


def casos983(pe, va, fim, chave='D2'):
    """{id: endereço do caso} do switch sobre o tipo (1º Decode2 da função; `chave`='D4' = sub-switch sobre o 1º Decode4,
    como o `CItemBuff::ProcessPacket`, que confere o id e despacha pelo subtipo)."""
    md = cs(True)
    code = pe.bytes(va, fim - va)
    ins = {}
    o = 0
    while o < len(code):
        ok = False
        for i in md.disasm(code[o:], va + o):
            ins[i.address] = i
            o = i.address - va + i.size
            ok = True
        if not ok:
            o += 1
    # início: logo depois do 1º call a Decode2
    ini = None
    for a in sorted(ins):
        i = ins[a]
        if i.mnemonic == 'call' and i.op_str.startswith('0x') and pk.API983.get(int(i.op_str, 16)) == chave:
            ini = a + i.size
            break
    if ini is None:
        return {}, 0
    casos = {}
    vistos = set()
    glob = {}       # endereço de memória -> k (variável global/local com o tipo)
    pilha = [(ini, (('a', 0),), None, None)]     # (endereço, regs com tipo-k, último cmp (k_do_reg, imm), limite de tabela)
    nlim = 0
    while pilha:
        a, regs, lastcmp, lim = pilha.pop()
        regs = dict(regs)
        const = {}      # C63: registro -> constante (`mov ecx,0x181; cmp ax,cx`; `xor ebx,ebx; sub eax,ebx`)
        while True:
            key = (a, tuple(sorted(regs.items())))
            if key in vistos or a not in ins:
                break
            vistos.add(key)
            i = ins[a]
            mn = i.mnemonic
            ops = i.operands
            nxt = a + i.size
            r0 = REGS.get(ops[0].reg) if ops and ops[0].type == X.X86_OP_REG else None
            r1c = const.get(REGS.get(ops[1].reg)) if len(ops) == 2 and ops[1].type == X.X86_OP_REG else None
            if r0 and r0 not in regs:
                if mn == 'mov' and ops[1].type == X.X86_OP_IMM:
                    const[r0] = ops[1].imm & 0xffffffff
                    a = nxt
                    continue
                if mn == 'xor' and len(ops) == 2 and ops[1].type == X.X86_OP_REG and ops[0].reg == ops[1].reg:
                    const[r0] = 0
                    a = nxt
                    continue
                const.pop(r0, None)
            if mn in ('movzx', 'mov') and len(ops) == 2:
                src = ops[1]
                if src.type == X.X86_OP_REG and REGS.get(src.reg) in regs and r0:
                    regs[r0] = regs[REGS[src.reg]]
                elif ops[0].type == X.X86_OP_MEM and src.type == X.X86_OP_REG and REGS.get(src.reg) in regs:
                    glob[(ops[0].mem.base, ops[0].mem.disp)] = regs[REGS[src.reg]]
                elif r0 and src.type == X.X86_OP_MEM and (src.mem.base, src.mem.disp) in glob and src.mem.index == 0:
                    regs[r0] = glob[(src.mem.base, src.mem.disp)]
                elif r0 and src.type == X.X86_OP_MEM and mn == 'movzx' and src.size == 1 and lastcmp and lastcmp[0] == 'c' \
                        and REGS.get(src.mem.base or src.mem.index) in regs and not (src.mem.base and src.mem.index) \
                        and not isinstance(regs[REGS[src.mem.base or src.mem.index]], tuple):
                    # tabela de bytes: reg = idx[tipo-k]
                    regs = {r0: ('idx', src.mem.disp & 0xffffffff, regs[REGS[src.mem.base or src.mem.index]], lastcmp[1])}
                elif r0 in regs:
                    del regs[r0]
                elif r0 is None and ops[0].type == X.X86_OP_MEM:
                    pass
                else:
                    if not r0:
                        break
            elif mn in ('sub', 'add') and r0 in regs and (ops[1].type == X.X86_OP_IMM or r1c is not None) \
                    and not isinstance(regs[r0], tuple):
                v = ops[1].imm if ops[1].type == X.X86_OP_IMM else r1c
                if v >= 0x80000000:
                    v -= 0x100000000
                k = regs[r0] + (v if mn == 'sub' else -v)
                regs[r0] = k
                lastcmp = ('z', r0, k)       # ZF: tipo == k
            elif mn == 'dec' and r0 in regs and not isinstance(regs[r0], tuple):
                regs[r0] += 1
                lastcmp = ('z', r0, regs[r0])
            elif mn == 'lea' and len(ops) == 2 and ops[1].type == X.X86_OP_MEM and REGS.get(ops[1].mem.base) in regs \
                    and ops[1].mem.index == 0 and r0:
                regs[r0] = regs[REGS[ops[1].mem.base]] - ops[1].mem.disp
            elif mn == 'cmp' and r0 in regs and ops[1].type == X.X86_OP_IMM and not isinstance(regs[r0], tuple):
                lastcmp = ('c', ops[1].imm, regs[r0] + ops[1].imm)       # igual quando tipo == k+imm
            elif mn == 'cmp' and r0 in regs and r1c is not None and not isinstance(regs[r0], tuple):
                lastcmp = ('c', r1c, regs[r0] + r1c)
            elif mn == 'cmp' and ops[0].type == X.X86_OP_MEM and (ops[0].mem.base, ops[0].mem.disp) in glob \
                    and ops[1].type == X.X86_OP_IMM:
                lastcmp = ('c', ops[1].imm, glob[(ops[0].mem.base, ops[0].mem.disp)] + ops[1].imm)
            elif mn in JCC and ops[0].type == X.X86_OP_IMM:
                t = ops[0].imm
                if lastcmp is None:
                    break
                if mn == 'je':
                    casos.setdefault(lastcmp[2], t)
                elif mn == 'jne':
                    casos.setdefault(lastcmp[2], nxt)
                    pilha.append((t, tuple(regs.items()), None, None))
                    break
                else:
                    pilha.append((t, tuple(regs.items()), lastcmp, None))
                    if mn == 'ja':
                        lim = t          # destino do `default` da tabela que vem a seguir
            elif mn == 'jmp' and ops[0].type == X.X86_OP_IMM:
                a = ops[0].imm
                continue
            elif mn == 'jmp' and ops[0].type == X.X86_OP_MEM and ops[0].mem.scale == 4 and REGS.get(ops[0].mem.index) in regs \
                    and lastcmp and lastcmp[0] == 'c':
                st = regs[REGS[ops[0].mem.index]]
                tab = ops[0].mem.disp & 0xffffffff
                if isinstance(st, tuple):
                    _, idx, k, n = st
                    for j in range(n + 1):
                        b = pe.bytes(idx + j, 1)
                        t = pe.u32(tab + 4 * b[0])
                        if t != lim:
                            casos.setdefault(k + j, t)
                else:
                    n = lastcmp[1]
                    for j in range(n + 1):
                        if pe.u32(tab + 4 * j) != lim:
                            casos.setdefault(st + j, pe.u32(tab + 4 * j))
                nlim += 1
                break
            elif mn in ('push', 'pop', 'test', 'xor', 'nop') or (mn == 'mov' and False):
                if mn == 'test':
                    lastcmp = None
                if mn in ('xor',) and r0 in regs:
                    del regs[r0]
            else:
                break
            a = nxt
    return casos, nlim


def casos_fonte(arq, func):
    """{id: texto do caso} do 1º switch da função (casos do 1º nível)."""
    p = os.path.join(R, arq)
    if not arq or not os.path.exists(p):
        return None
    t = open(p, encoding='latin1').read()
    # a ÚLTIMA definição do arquivo: nas unidades com híbrido do rebang (#ifndef REBANG_SEMANTIC_ONLY ... #else ... #endif)
    # a 1ª é a cópia morta dentro do híbrido e a que compila no build do 983 é a do #else (golftask.cpp; achado na C15)
    ms = list(re.finditer(r'^[\w \*]*\b%s\(WReceivedPacket\s*&\s*\w+\)\s*\{' % re.escape(func), t, re.M))
    if not ms:
        return None
    m = ms[-1]
    i = m.end()
    sw = re.compile(r'switch\s*\(\s*\w*[tT]ype\w*\s*\)').search(t, i) or re.compile(r'switch\s*\(').search(t, i)
    if not sw:
        return None
    j = t.index('{', sw.end())
    global _prologo
    _prologo = t[m.end():sw.start()]      # C63: declarações antes do switch (ex.: `sSCardAvilityPeriodInfo info;` do CItemBuff)
    depth = 0
    k = j
    res = collections.OrderedDict()
    cur = []
    start = None
    lab = re.compile(r'\s*(case\s+([^:]+?)|default)\s*:')
    line_start = j + 1
    while k < len(t):
        c = t[k]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
        elif c == '\n' and depth == 1:
            mm = lab.match(t, k + 1)
            if mm:
                if start is not None:
                    for idn in cur:
                        res[idn] = t[start:k]
                    if re.search(r'\b(break|return|goto)\b', t[start:k]):
                        cur = []
                    else:
                        cur = list(cur)
                if start is None or re.search(r'\b(break|return|goto)\b', t[start:k]):
                    cur = []
                if mm.group(2):
                    try:
                        cur.append(int(mm.group(2).strip().split()[-1].strip('()'), 0))
                    except ValueError:
                        cur.append(mm.group(2).strip())
                start = mm.end()
        k += 1
    if start is not None:
        for idn in cur:
            res[idn] = t[start:k]
    return res


_prologo = ''       # texto da função antes do switch do último casos_fonte() (lido por leituras_fonte)
DEC = re.compile(r'\b(Decode1|Decode2|Decode4|Decode8|DecodeStr|DecodeEncryptedStr|DecodeBuffer)\s*\(')
LET = {'Decode1': 'D1', 'Decode2': 'D2', 'Decode4': 'D4', 'Decode8': 'D8', 'DecodeStr': 'DS', 'DecodeEncryptedStr': 'DX',
       'DecodeBuffer': 'DB'}


def tamanhos():
    """tipo -> sizeof conhecido: V3_SIZE de include/asserts e C_ASSERT(sizeof(T) == N) do fonte (lote 9 da C-PKT)."""
    tz = {}
    import glob
    for p in glob.glob(os.path.join(R, 'include', 'asserts', '*.h')):
        for m in re.finditer(r'^V3_SIZE\(\s*([\w:]+)\s*,\s*(0x[0-9a-fA-F]+|\d+)\s*\)', open(p, encoding='latin1').read(), re.M):
            tz[m.group(1).split('::')[-1]] = int(m.group(2), 0)
    for base in ('src', 'include'):
        for d, _, fs in os.walk(os.path.join(R, base)):
            for f in fs:
                if f.endswith(('.cpp', '.h', '.inl')):
                    for m in re.finditer(r'C_ASSERT\(\s*sizeof\(\s*([\w:]+)\s*\)\s*==\s*(0x[0-9a-fA-F]+|\d+)',
                                         open(os.path.join(d, f), encoding='latin1').read()):
                        tz.setdefault(m.group(1).split('::')[-1], int(m.group(2), 0))
    return tz


SZF = os.path.join(OUT, 'sizeof_fonte.tsv')      # feito por tools/pkt/sz.py (compila uma sonda por unidade)


def tamanhos_sonda():
    """(arquivo, expressão de tipo) -> sizeof medido pelo compilador (tools/pkt/sz.py); vazio se a sonda não rodou."""
    tz = {}
    if os.path.exists(SZF):
        for l in open(SZF):
            c = l.rstrip('\n').split('\t')
            if len(c) >= 3 and c[2].startswith('0x'):
                tz[(c[0], c[1])] = int(c[2], 16)
    return tz


def tipo_de(arg, antes):
    """expressão de tipo (para `sizeof(...)`) do 2º argumento de um DecodeBuffer; None se não é sizeof de algo resolvível.
    `antes` = texto do caso até a chamada (para achar a declaração da variável local)."""
    s = re.match(r'^sizeof\s*\(\s*(.+?)\s*\)$', arg) or re.match(r'^sizeof\s+([\w:]+)$', arg)
    if not s:
        return None
    e = s.group(1).strip()
    if 'Doc()' in e:
        return e.replace('Doc()', '((CSharedDoc*)0)')
    if not re.match(r'^[\w:]+$', e):
        return None
    ds = list(re.finditer(r'(?:^|[;{}(\n])\s*((?:unsigned\s+|struct\s+|const\s+)*[A-Za-z_][\w:]*(?:<[^;>]*>)?)\s+%s\s*((?:\[[^\]]*\])*)\s*[;=(,]'
                          % re.escape(e), antes))
    ds = [d for d in ds if d.group(1) not in ('return', 'delete', 'new', 'case', 'goto', 'else')]
    if ds:
        d = ds[-1]
        return (d.group(1) + ' ' + d.group(2)).strip()
    return e        # nome de tipo


def leituras_fonte(txt, tz, arq='', sonda=None, pede=None):
    """leituras do texto de um caso, na ordem; DecodeBuffer leva o tamanho quando é literal, sizeof de tipo conhecido
    (asserts) ou medido pela sonda. `pede` (lista) recebe as expressões de tipo que a sonda deve medir."""
    txt = re.sub(r'//[^\n]*', '', txt)
    sonda = sonda or {}
    out = []
    for m in DEC.finditer(txt):
        op = LET[m.group(1)]
        if op == 'DB':
            k = m.end()
            d = 1
            virg = None
            while k < len(txt) and d:
                c = txt[k]
                if c == '(':
                    d += 1
                elif c == ')':
                    d -= 1
                elif c == ',' and d == 1:
                    virg = k
                k += 1
            arg = txt[virg + 1:k - 1].strip() if virg else ''
            v = None
            try:
                v = int(arg, 0)
            except ValueError:
                te = tipo_de(arg, _prologo + ';' + txt[:m.start()])
                if te:
                    if pede is not None:
                        pede.append(te)
                    v = sonda.get((arq, te))
                    if v is None and re.match(r'^[\w:]+$', te):
                        v = tz.get(te.split('::')[-1])
            op += '(?)' if v is None else '(0x%x)' % v
        out.append(op)
    return out


def main():
    pe = PE()
    tz = tamanhos()
    sonda = tamanhos_sonda()
    F = Funcs()
    ev983 = {}
    for l in open(os.path.join(OUT, 'pk983_funcs.tsv')):
        pass
    rows = []
    cmp_rows = []
    res = []
    for va, arq, func, *chave in DISP:
        i = F.vas.index(va)
        fim = F.vas[i + 1]
        # o corpo vai além do 1º pedaço quando a função seguinte é rótulo interno; usa o tamanho do mapa se maior
        fim = max(fim, va + F.l[i][1])
        cas, nt = casos983(pe, va, fim, *chave)
        code = pe.bytes(va, fim - va)
        ev = pk.scan(code, va, lambda a, t: pk.API983.get(t))
        alvos = sorted(set(cas.values()))
        porid = {}
        for idn, t in sorted(cas.items()):
            k = bisect.bisect_right(alvos, t)
            lim = alvos[k] if k < len(alvos) else fim
            s = ' '.join(op + arg for a, op, arg in ev if t <= a < lim)
            porid[idn] = (t, s)
            rows.append(('%08x' % va, F.nome(va), '0x%x' % idn, '%08x' % t, s))
        fonte = casos_fonte(arq, func)
        nome = func or F.nome(va)
        if fonte is None:
            res.append((nome, len(cas), None, 0, 0, 0, 0, 0))
            for idn in sorted(porid):
                cmp_rows.append((nome, '0x%x' % idn, 'sem_fonte', porid[idn][1], ''))
            continue
        fid = {k: v for k, v in fonte.items() if isinstance(k, int)}
        so9 = sorted(set(porid) - set(fid))
        sof = sorted(set(fid) - set(porid))
        ig = df = db = 0
        for idn in sorted(set(porid) | set(fid)):
            s9 = porid[idn][1] if idn in porid else ''
            lf = leituras_fonte(fid[idn], tz, arq, sonda) if idn in fid else []
            sf = ' '.join(lf)
            if idn not in fid:
                est = 'so_983'
            elif idn not in porid:
                est = 'so_fonte'
            else:
                l9 = [x for x in s9.split() if x[0] == 'D']
                est = 'igual' if [x.split('(')[0] for x in l9] == [x.split('(')[0] for x in lf] else 'difere'
                # lote 9: mesma sequência, mas um bloco de tamanho conhecido no fonte difere do 983
                if est == 'igual' and any(a != b and '?' not in b for a, b in zip(l9, lf)):
                    est = 'difere_bloco'
                ig += est == 'igual'
                df += est == 'difere'
                db += est == 'difere_bloco'
            cmp_rows.append((nome, '0x%x' % idn, est, s9, sf))
        res.append((nome, len(cas), len(fid), len(so9), len(sof), ig, df, db))
    with open(os.path.join(OUT, 'pacotes_recebe_983.tsv'), 'w') as f:
        f.write('despachante983\tnome\tid\tva_caso\tleituras_no_trecho\n')
        for r in rows:
            f.write('\t'.join(r) + '\n')
    with open(os.path.join(OUT, 'rx_cmp.tsv'), 'w') as f:
        f.write('despachante\tid\testado\tleituras_983\tleituras_fonte\n')
        for r in cmp_rows:
            f.write('\t'.join(r) + '\n')
    with open(os.path.join(OUT, 'rx_resumo.txt'), 'w') as f:
        t = '%-30s %7s %7s %7s %8s %6s %6s %6s\n' % ('despachante', 'ids983', 'idsfonte', 'so_983', 'so_fonte', 'igual', 'difere', 'bloco')
        for nome, n9, nf, a, b, c, d, e in res:
            t += '%-30s %7d %7s %7d %8d %6d %6d %6d\n' % (nome[:30], n9, '-' if nf is None else nf, a, b, c, d, e)
        f.write(t)
        print(t, end='')


if __name__ == '__main__':
    main()
