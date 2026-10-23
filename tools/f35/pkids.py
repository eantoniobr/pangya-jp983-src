#!/usr/bin/env python3
"""Ids de pacote ENVIADO: troca no fonte a numeração do KR 645 pela do JP 983 (pedido C→A da V4).
  pkids.py plano  [OUT]  -> OUT/pkids_envio.tsv (cada `WSendPacket x(N)` do fonte: id, id novo, prova)
                            (só faz sentido ANTES do `aplica`; o plano usado está em out/F3.5/s61/antes)
  pkids.py aplica [OUT]  -> edita os arquivos (só as linhas com prova `par` ou `faixa`) e regrava o plano
Prova:  par     = a função do lugar tem par no 983 com a mesma assinatura de pacote (out/V4/pk_cmp.tsv)
        faixa   = os vizinhos alinhados de baixo e de cima têm o mesmo salto (out/V4/ids_cliente.tsv, só `faixa`)
        lacuna  = id entre duas faixas de salto diferente (ou acima da última): não mexe
        nao983  = o id novo não aparece em nenhum pacote montado pelo exe 983 (pacotes_envio_983.tsv): não mexe
A tabela usada fica congelada em map/pacotes_ids_envio.tsv (id do 645 -> id do 983), porque depois da troca o
out/V4 da frente C deixa de mostrar a diferença.
"""
import sys, os, re, csv, glob, collections
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V4 = os.path.join(R, 'out', 'V4')
MAPA = os.path.join(R, 'map', 'pacotes_ids_envio.tsv')
SITE = re.compile(r'((?:WSendPacket|RbSendPacketExtern)\s*&?\s*\w+\s*(?:=\s*\*\s*new\s+WSendPacket\s*)?\(\s*|=\s*new\s+WSendPacket\s*\(\s*)'
                  r'((?:\(enumClientPacket\)\s*)?)(0[xX][0-9a-fA-F]+|\d+)(\s*\))')
DEF = re.compile(r'^[A-Za-z_].*?(?:\b(\w+)::)?(~?\w+)\s*\([^;]*$')


def fontes():
    for base in ('src/projectg', 'src/shared', 'src/fresh', 'src/engine'):
        for d, _, fs in os.walk(os.path.join(R, base)):
            if os.sep + 'jp' in d[len(R):] and 'src/projectg/jp' in d:
                continue
            for f in sorted(fs):
                if f.endswith(('.cpp', '.h', '.inl')):
                    yield os.path.join(d, f)


def pids(sig):
    return [int(x, 16) for x in re.findall(r'P\((0x[0-9a-f]+)\)', sig)]


def forma(sig):
    return re.sub(r'P\(0x[0-9a-f]+\)', 'P', re.sub(r'B\(0x[0-9a-f]+\)', 'B', sig))


def tabela_global():
    """id645 -> id983 das linhas `faixa` de ids_cliente.tsv (ou do mapa congelado, se existir)."""
    t = {}
    if os.path.exists(MAPA):
        for r in csv.DictReader(open(MAPA), delimiter='\t'):
            t[int(r['id_645'], 16)] = int(r['id_983'], 16)
        return t
    for r in csv.DictReader(open(os.path.join(V4, 'ids_cliente.tsv')), delimiter='\t'):
        if r['certeza'] == 'faixa':
            t[int(r['id_nosso'], 16)] = int(r['id_983'], 16)
    return t


def por_funcao():
    """(unidade, classe, metodo) -> {id645: id983} das funções com par e a mesma forma de assinatura."""
    m = {}
    for r in csv.DictReader(open(os.path.join(V4, 'pk_cmp.tsv')), delimiter='\t'):
        if r['estado'] not in ('igual', 'difere_id', 'difere_id_bloco', 'difere_bloco'):
            continue
        a, b = pids(r['assinatura_nossa']), pids(r['assinatura_983'])
        if len(a) != len(b) or forma(r['assinatura_nossa']) != forma(r['assinatura_983']):
            continue
        d, ok = {}, True
        for x, y in zip(a, b):
            if d.setdefault(x, y) != y:
                ok = False
        if not ok:
            continue
        f = r['funcao']
        mm = re.match(r'\?\?([01])(\w+?)@@', f)
        if mm:
            cls = mm.group(2); met = ('~' if mm.group(1) == '1' else '') + cls
        else:
            mm = re.match(r'\?(\w+?)@(?:(\w+?)@)?', f)
            if not mm:
                continue
            met, cls = mm.group(1), mm.group(2) or ''
        m.setdefault((r['unidade'], cls, met), []).append(d)
    return m


def ids983():
    s = set()
    for r in csv.DictReader(open(os.path.join(V4, 'pacotes_envio_983.tsv')), delimiter='\t'):
        v = r.get('id') or list(r.values())[0]
        try:
            s.add(int(v, 16))
        except (ValueError, TypeError):
            pass
    return s


def interp(t, n):
    if n in t:
        return t[n], 'faixa'
    ks = sorted(t)
    lo = [k for k in ks if k < n]; hi = [k for k in ks if k > n]
    if lo and hi and t[lo[-1]] - lo[-1] == t[hi[0]] - hi[0]:
        return n + t[lo[-1]] - lo[-1], 'faixa'
    return None, 'lacuna'


def plano():
    t, pf, s983 = tabela_global(), por_funcao(), ids983()
    linhas = []
    for p in fontes():
        rel = os.path.relpath(p, R)
        un = re.sub(r'\.\w+$', '', rel).replace('/', '_')
        cls = met = ''
        asm = 0
        for i, l in enumerate(open(p, encoding='latin-1'), 1):
            d = DEF.match(l)
            if d and not l.startswith(('return', 'else', 'if', 'for', 'while', 'switch', 'case', 'typedef', 'extern', 'static const')):
                cls, met = d.group(1) or '', d.group(2)
            for mm in SITE.finditer(l):
                n = int(mm.group(3), 0)
                novo, prova = None, ''
                for dd in pf.get((un, cls, met), []):
                    if n in dd and t.get(n, dd[n]) == dd[n]:   # par que contradiz a tabela = par errado do comparador
                        novo, prova = dd[n], 'par'
                if novo is None:
                    novo, prova = interp(t, n)
                    if novo is not None and novo not in s983:
                        prova = 'nao983'
                linhas.append([rel, i, cls + '::' + met if cls else met, '0x%x' % n,
                               '0x%x' % novo if novo is not None else '', prova, mm.group(3)])
    return linhas


def grava(linhas, out):
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'pkids_envio.tsv'), 'w') as f:
        f.write('arquivo\tlinha\tfuncao\tid_645\tid_983\tprova\ttexto\n')
        for r in linhas:
            f.write('\t'.join(map(str, r)) + '\n')
    c = collections.Counter((r[5], 'muda' if r[4] and r[4] != r[3] else 'igual' if r[4] else '-') for r in linhas)
    for k in sorted(c):
        print('%-8s %-6s %d' % (k[0], k[1], c[k]))
    print('total', len(linhas))


def aplica(linhas):
    por = collections.defaultdict(dict)
    for r in linhas:
        if r[5] in ('par', 'faixa') and r[4] != r[3]:
            por[r[0]].setdefault(r[1], []).append((r[6], r[4]))
    n = 0
    for rel, d in sorted(por.items()):
        p = os.path.join(R, rel)
        ls = open(p, encoding='latin-1', newline='').read().split('\n')
        for i, tro in d.items():
            it = iter(tro)
            def sub(mm):
                nonlocal n
                try:
                    velho, novo = next(it)
                except StopIteration:
                    return mm.group(0)
                if mm.group(3) != velho:
                    return mm.group(0)
                n += 1
                return mm.group(1) + mm.group(2) + novo + mm.group(4)
            # todos os lugares da linha entram no plano na ordem; os que não mudam ficam fora de `tro`
            todos = [mm.group(3) for mm in SITE.finditer(ls[i - 1])]
            if len(todos) != 1:
                print('linha com mais de um pacote, à mão:', rel, i); continue
            ls[i - 1] = SITE.sub(sub, ls[i - 1])
        open(p, 'w', encoding='latin-1', newline='').write('\n'.join(ls))
    print('trocados', n, 'em', len(por), 'arquivos')


def congela():
    t = tabela_global()
    with open(MAPA, 'w') as f:
        f.write('id_645\tid_983\n')
        for k in sorted(t):
            f.write('0x%x\t0x%x\n' % (k, t[k]))


if __name__ == '__main__':
    modo = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(R, 'out', 'F3.5', 'pkids')
    L = plano()
    if modo == 'aplica':
        if os.path.exists(MAPA):
            sys.exit('map/pacotes_ids_envio.tsv já existe: a troca já foi aplicada (rodar de novo somaria o salto duas vezes)')
        aplica(L)
        congela()
    grava(L, out)
