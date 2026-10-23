#!/usr/bin/env python3
"""Ids de pacote RECEBIDO: troca nos `case` dos despachantes a numeração do KR 645 pela do JP 983 (pedido C→A da V4).
  rxids.py plano  [OUT] -> OUT/rxids_recebe.tsv (cada `case N:` de 1º nível de cada despachante: id, id novo, prova)
  rxids.py aplica [OUT] -> edita os .cpp (só prova `faixa` cujo id novo é caso do MESMO despachante no exe 983)
Prova:  faixa   = vizinhos alinhados de baixo e de cima com o mesmo salto (out/V4/ids_servidor.tsv, só `faixa`)
        lacuna  = entre faixas de salto diferente: não mexe
        lacuna:lo|hi = id em lacuna que fica com o salto do vizinho de baixo/cima: o id novo é caso do despachante no 983
                  e a lacuna tem um ponto de virada só (ver lacunas())
        lacuna  = entre faixas de salto diferente, sem decisão
        nao983  = o id novo não é caso desse despachante no 983 (out/V4/pacotes_recebe_983.tsv)
        choque  = ficaria igual a outro `case` do mesmo switch
      Os três últimos viram `case PKT645_SEM_983(0xNN):` (valor fora da faixa de ids; o tratador fica desligado até
      alguém achar o id do 983): com o id do 645 ele trataria OUTRO pacote do 983.
A tabela usada fica congelada em map/pacotes_ids_recebe.tsv. Lista de despachantes = a de tools/v4/rx.py.
"""
import sys, os, re, csv, collections
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V4 = os.path.join(R, 'out', 'V4')
MAPA = os.path.join(R, 'map', 'pacotes_ids_recebe.tsv')
DESP = [(0x009c20a0, 'src/projectg/taskmanager.cpp', 'CTask::OnPacketCommon'),
        (0x00ac03a0, 'src/projectg/lobbytask.cpp', 'CLobbyTask::OnPacket'),
        (0x0069eef0, 'src/projectg/golftask.cpp', 'CGolfTask::OnPacket'),
        (0x005a8360, 'src/projectg/realmyroomtask.cpp', 'CRealMyRoomTask::OnPacket'),
        (0x007b5a20, 'src/projectg/avatar_task.cpp', 'ntAvatarChatTask::OnPacket'),
        (0x005e0ff0, 'src/projectg/shoptask.cpp', 'CShopTask::OnPacket'),
        (0x006b2ee0, 'src/projectg/tutorialtask.cpp', 'CTutorialTask::OnPacket'),
        (0x0082c830, 'src/projectg/ghosttask.cpp', 'CGhostTask::OnPacket'),
        (0x00b1c5d0, 'src/projectg/familytask.cpp', 'CFamilyTask::OnPacket')]
LAB = re.compile(r'([ \t]*case\s+)((?:\(\w+\)\s*)?)(0[xX][0-9a-fA-F]+|\d+)(\s*:)')


def tabela():
    t = {}
    if os.path.exists(MAPA):
        for r in csv.DictReader(open(MAPA), delimiter='\t'):
            t[int(r['id_645'], 16)] = int(r['id_983'], 16)
        return t
    for r in csv.DictReader(open(os.path.join(V4, 'ids_servidor.tsv')), delimiter='\t'):
        if r['certeza'] == 'faixa':
            t[int(r['id_fonte'], 16)] = int(r['id_983'], 16)
    return t


def casos983():
    d = collections.defaultdict(set)
    for r in csv.DictReader(open(os.path.join(V4, 'pacotes_recebe_983.tsv')), delimiter='\t'):
        d[int(r['despachante983'], 16)].add(int(r['id'], 16))
    return d


def interp(t, n):
    if n in t:
        return t[n], 'faixa'
    ks = sorted(t)
    lo = [k for k in ks if k < n]; hi = [k for k in ks if k > n]
    if lo and hi and t[lo[-1]] - lo[-1] == t[hi[0]] - hi[0]:
        return n + t[lo[-1]] - lo[-1], 'faixa'
    return None, 'lacuna'


def labels(txt, func):
    """[(posição do match, match)] dos `case` de 1º nível do 1º switch da função (mesma regra do rx.py)."""
    m = re.search(r'^[\w \*]*\b%s\(WReceivedPacket\s*&\s*\w+\)\s*\{' % re.escape(func), txt, re.M)
    if not m:
        return None
    sw = re.compile(r'switch\s*\(\s*\w*[tT]ype\w*\s*\)').search(txt, m.end()) or re.compile(r'switch\s*\(').search(txt, m.end())
    j = txt.index('{', sw.end())
    depth, k, res = 0, j, []
    while k < len(txt):
        c = txt[k]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
        elif c == '\n' and depth == 1:
            mm = LAB.match(txt, k + 1)
            while mm:                       # vários `case` na mesma linha
                res.append(mm)
                mm = LAB.match(txt, mm.end())
        k += 1
    return res


def vizinhos(t, n):
    ks = sorted(t)
    lo = [k for k in ks if k < n]; hi = [k for k in ks if k > n]
    return (lo[-1] if lo else None), (hi[0] if hi else None)


def candidatos(t, c, prop, p):
    """saltos possíveis de um `case` em lacuna: [(lado, id novo)] cujo id novo é caso do despachante e está livre."""
    tomados = {q[2] for q in prop if q[3] == 'faixa'}
    lo, hi = vizinhos(t, p[1])
    r = []
    if lo is not None and p[1] + t[lo] - lo in c and p[1] + t[lo] - lo not in tomados:
        r.append(('lo', p[1] + t[lo] - lo))
    if hi is not None and p[1] + t[hi] - hi in c and p[1] + t[hi] - hi not in tomados:
        r.append(('hi', p[1] + t[hi] - hi))
    return r


def lacunas(t, c, prop, GL):
    """Uma lacuna (lo, hi) tem um ponto de virada só: ids com um único candidato o delimitam (GL junta os de todos
    os despachantes); id com os dois candidatos fica do lado que a virada mandar. Lacuna com votos fora de ordem,
    acima do último id alinhado, ou abaixo do primeiro com salto != 0: não decide."""
    for p in prop:
        if p[3] != 'lacuna':
            continue
        lo, hi = vizinhos(t, p[1])
        if hi is None or (lo is None and t[hi] != hi):
            continue
        g = GL.get((lo, hi))
        if g is None or g['ruim']:
            continue
        cs = dict(candidatos(t, c, prop, p))
        lado = None
        if lo is None:
            lado = 'hi'
        elif g['lo'] and p[1] <= max(g['lo']):
            lado = 'lo'
        elif g['hi'] and p[1] >= min(g['hi']):
            lado = 'hi'
        if lado in cs:
            p[2], p[3] = cs[lado], 'faixa'
            p.append('lacuna:' + lado)


def votos_lacunas(t, c983, todos):
    GL = {}
    for va, prop in todos:
        for p in prop:
            if p[3] != 'lacuna':
                continue
            lo, hi = vizinhos(t, p[1])
            g = GL.setdefault((lo, hi), {'lo': [], 'hi': [], 'ruim': False})
            cs = candidatos(t, c983[va], prop, p)
            if len(cs) == 1:
                g[cs[0][0]].append(p[1])
    for g in GL.values():
        if g['lo'] and g['hi'] and max(g['lo']) > min(g['hi']):
            g['ruim'] = True
    return GL


def plano():
    t, c983 = tabela(), casos983()
    todos = []
    for va, arq, func in DESP:
        txt = open(os.path.join(R, arq), encoding='latin-1', newline='').read()
        ms = labels(txt, func) or []
        prop = []
        for mm in ms:
            n = int(mm.group(3), 0)
            novo, prova = interp(t, n)
            if novo is not None and novo not in c983[va]:
                prova = 'nao983'
            prop.append([mm, n, novo, prova])
        todos.append((va, prop))
    GL = votos_lacunas(t, c983, todos)
    L, edits = [], collections.defaultdict(list)
    for va, arq, func in DESP:
        txt = open(os.path.join(R, arq), encoding='latin-1', newline='').read()
        ms = labels(txt, func)
        if ms is None:
            print('não achei', func); continue
        prop = []
        for mm in ms:
            n = int(mm.group(3), 0)
            novo, prova = interp(t, n)
            if novo is not None and novo not in c983[va]:
                prova = 'nao983'
            prop.append([mm, n, novo, prova])
        # lacuna: fica com o salto do vizinho de baixo ou de cima quando o exe 983 decide (ver lacunas())
        lacunas(t, c983[va], prop, GL)
        # choque: id final repetido dentro do mesmo switch
        # (só entre os que ficam ativos: os sem id do 983 saem do caminho)
        final = collections.Counter(p[2] for p in prop if p[3] == 'faixa')
        for p in prop:
            if p[3] == 'faixa' and final[p[2]] > 1:
                p[3] = 'choque'
        for p in prop:
            mm, n, novo, prova = p[:4]
            if len(p) > 4 and prova == 'faixa':
                prova = p[4]
            ok = prova == 'faixa' or prova.startswith('lacuna:')
            L.append([func, arq, txt.count('\n', 0, mm.start(3)) + 1, '0x%x' % n, '0x%x' % novo if novo is not None else '', prova])
            if ok and novo != n:
                edits[arq].append((mm.start(3), mm.end(3), '0x%x' % novo))
            elif not ok:
                # sem id do 983 conhecido: o `case` sai do caminho (packet.h: PKT645_SEM_983) em vez de tratar outro pacote
                edits[arq].append((mm.start(2), mm.end(3), 'PKT645_SEM_983(0x%x)' % n))
    return L, edits


def grava(L, out):
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'rxids_recebe.tsv'), 'w') as f:
        f.write('despachante\tarquivo\tlinha\tid_645\tid_983\tprova\n')
        for r in L:
            f.write('\t'.join(map(str, r)) + '\n')
    c = collections.Counter((r[0], r[5].split(':')[0] + ('_vizinho' if ':' in r[5] else '') if r[5] != 'faixa' else ('faixa_muda' if r[4] != r[3] else 'faixa_igual')) for r in L)
    cols = sorted({k[1] for k in c})
    print('%-30s' % 'despachante' + ''.join('%14s' % x for x in cols))
    for d in dict.fromkeys(r[0] for r in L):
        print('%-30s' % d + ''.join('%14d' % c[(d, x)] for x in cols))


if __name__ == '__main__':
    modo = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(R, 'out', 'F3.5', 'rxids')
    L, edits = plano()
    if modo == 'aplica':
        if os.path.exists(MAPA):
            sys.exit('map/pacotes_ids_recebe.tsv já existe: a troca já foi aplicada')
        for arq, es in edits.items():
            p = os.path.join(R, arq)
            txt = open(p, encoding='latin-1', newline='').read()
            for a, b, s in sorted(es, reverse=True):
                txt = txt[:a] + s + txt[b:]
            open(p, 'w', encoding='latin-1', newline='').write(txt)
            print('trocados', len(es), 'em', arq)
        t = tabela()
        with open(MAPA, 'w') as f:
            f.write('id_645\tid_983\n')
            for k in sorted(t):
                f.write('0x%x\t0x%x\n' % (k, t[k]))
    grava(L, out)
