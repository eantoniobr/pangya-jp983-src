#!/usr/bin/env python3
"""C-F4.4: relatório do que falta no build/C/f4/ProjectG_983.exe (make exe) -> out/F4/FALTA.md e out/F4/falta_exe.tsv.

Para cada stub de função (out/F4/stubs.tsv, make f4-stubs) diz quem o chama no EXE LIGADO, pelo grafo de chamadas DIRETAS
(call/jmp rel32; capstone) a partir de dois pontos:
  - os inicializadores estáticos (.CRT$XCU, entre ___xc_a e ___xc_z): rodam ANTES do WinMain — um stub alcançado daqui
    mostra a caixa (ou fecha o jogo, se fatal) já ao abrir, em qualquer modo;
  - o _WinMain@16: profundidade mínima (nº de chamadas) até o stub. Profundidade pequena = chance de aparecer cedo.
Chamadas indiretas (vtable, ponteiro de função) NÃO são seguidas: "não alcançado" não quer dizer "nunca chamado".
Também agrupa os stubs por frente (coluna frentes do stubs.tsv) e por passo do roteiro (tools/v6/prontidao.py: passo_da do
.obj que cita; vale o menor passo entre os que citam).
Uso: python3 tools/v6/falta_exe.py [exe]   (make exe chama; ~20 s; só leitura)
"""
import os, sys, re, struct, collections, hashlib
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, R + '/tools/v6')
from pe import PE                       # noqa: E402
from prontidao import passo_da, PASSOS, RESTO   # noqa: E402

import f4cfg
EXE = sys.argv[1] if len(sys.argv) > 1 else f4cfg.B4 + '/ProjectG_983.exe'   # C94: F4_BUILD/F4_OUT
OUT = f4cfg.O4


def ler_map(mp):
    """símbolos de código (seção 0001): va -> (nome, obj); e os de dados que interessam"""
    cod, dados, nomes = {}, {}, {}
    for l in open(mp, encoding='latin1'):
        c = l.split()
        if len(c) < 4 or ':' not in c[0] or not re.match(r'^[0-9a-f]{8}$', c[2]): continue
        va = int(c[2], 16)
        if c[0].startswith('0001:'): cod.setdefault(va, (c[1], c[-1])); nomes[c[1]] = va
        else: dados[c[1]] = va
    return cod, dados, nomes


def main():
    mp = EXE[:-4] + '.map'
    pe = PE(EXE)
    cod, dados, nome_va = ler_map(mp)
    ini = sorted(cod)
    fim = {a: (ini[i + 1] if i + 1 < len(ini) else a + 0x1000) for i, a in enumerate(ini)}
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    cache = {}

    def chamadas(a):
        """alvos de call/jmp rel32 da função que começa em a (só para fora dela, ou começo de função)"""
        if a in cache: return cache[a]
        r = set()
        e = fim.get(a)
        if e is None: cache[a] = r; return r
        try: code = pe.d[pe.off(a - pe.base): pe.off(a - pe.base) + min(e - a, 0x20000)]
        except Exception: cache[a] = r; return r
        for i in md.disasm(code, a):
            if i.mnemonic in ('call', 'jmp') and i.op_str.startswith('0x'):
                t = int(i.op_str, 16)
                if t in cod and (t < a or t >= e): r.add(t)
            if i.mnemonic == 'int3' and i.address > a: break
        cache[a] = r
        return r

    def bfs(raizes):
        prof, pai = {}, {}
        fila = collections.deque()
        for x in raizes: prof[x] = 0; fila.append(x)
        while fila:
            a = fila.popleft()
            for t in chamadas(a):
                if t not in prof: prof[t] = prof[a] + 1; pai[t] = a; fila.append(t)
        return prof, pai

    # .CRT$XCU
    xa, xz = dados['___xc_a'], dados['___xc_z']
    xcu = [pe.u32(v) for v in range(xa, xz, 4)]
    xcu = [v for v in xcu if v]
    # um inicializador por vez, na ordem do .CRT$XCU (a ordem em que o CRT os chama): cada função fica com o PRIMEIRO
    # inicializador que a alcança (ordem_xcu) — é essa a ordem em que os stubs aparecem ao abrir o exe
    p_xcu, pai_xcu, ordem_xcu = {}, {}, {}
    for k, x in enumerate(xcu):
        if x in p_xcu: continue
        p1, pai1 = bfs([x])
        for t, d in p1.items():
            if t not in p_xcu:
                p_xcu[t] = d; ordem_xcu[t] = k
                if t in pai1: pai_xcu[t] = pai1[t]
    wm = nome_va.get('_WinMain@16')
    p_wm, _ = bfs([wm]) if wm else ({}, {})

    st = [l.rstrip('\n').split('\t') for l in open(OUT + '/stubs.tsv', encoding='utf-8')]
    h, st = st[0], st[1:]
    ix = {k: i for i, k in enumerate(h)}
    linhas = []
    for c in st:
        if c[ix['tipo']] != 'função': continue
        rot = c[ix['stub_nota']].split(';')[0].strip()
        va = nome_va.get('_' + rot) or nome_va.get(rot)
        objs = c[ix['quem_cita']].split()
        passo = min((passo_da(re.sub(r'\.obj$', '', o.lower())) for o in objs), default=RESTO[0])
        caminho = ''
        if va in p_xcu:
            passo = '1'   # sobe pelo .CRT$XCU: roda ao abrir, antes do WinMain
            x, cam = va, []
            while x in pai_xcu: x = pai_xcu[x]; cam.append(cod[x][0])
            caminho = ' <- '.join(cam[:4]) + (' <- ...' if len(cam) > 4 else '')
        linhas.append(dict(simbolo=c[0], modo=c[ix['modo']], frentes=c[ix['frentes']], va983=c[ix['va983']], passo=passo,
                           va='%08x' % va if va else '-', xcu='sim' if va in p_xcu else 'não',
                           ordem_xcu=str(ordem_xcu[va]) if va in ordem_xcu else '-',
                           prof_winmain=str(p_wm[va]) if va in p_wm else '-', caminho_xcu=caminho, quem=c[ix['quem_cita']]))
    cols = ['simbolo', 'modo', 'frentes', 'passo', 'va983', 'va', 'xcu', 'ordem_xcu', 'prof_winmain', 'caminho_xcu', 'quem']
    with open(OUT + '/falta_exe.tsv', 'w') as f:
        f.write('\t'.join(cols) + '\n')
        for d in sorted(linhas, key=lambda d: (d['xcu'] != 'sim', int(d['ordem_xcu']) if d['ordem_xcu'] != '-' else 0,
                                               int(d['prof_winmain']) if d['prof_winmain'] != '-' else 99, d['simbolo'])):
            f.write('\t'.join(d[k] for k in cols) + '\n')

    tit = {p: t for p, t, *_ in PASSOS}; tit[RESTO[0]] = 'Comum / resto'
    md5 = hashlib.md5(open(EXE, 'rb').read()).hexdigest()
    sem_va = [d for d in linhas if d['va'] == '-']
    w = []
    w.append('# O que falta no exe (C-F4.4, `make exe`)\n')
    w.append('Exe: `%s`, %d bytes, md5 `%s`. Gerado por `tools/v6/falta_exe.py` (grafo de chamadas DIRETAS no exe ligado; '
             'chamadas por vtable/ponteiro não entram).\n' % (os.path.relpath(EXE, R), os.path.getsize(EXE), md5))
    w.append('- stubs de função: %d (fatais: %d; os demais voltam 0 com `JP983_STUB=continuar`); dados: valores do 983 (não param o jogo)'
             % (len(linhas), sum(d['modo'] == 'fatal' for d in linhas)))
    w.append('- inicializadores estáticos (.CRT$XCU): %d; funções alcançadas a partir deles: %d; **stubs alcançados antes do WinMain: %d**'
             % (len(xcu), len(p_xcu), sum(d['xcu'] == 'sim' for d in linhas)))
    w.append('- _WinMain@16 em %s; funções alcançadas por chamada direta: %d; stubs alcançados: %d' % (
        '%08x' % wm if wm else '?', len(p_wm), sum(d['prof_winmain'] != '-' for d in linhas)))
    if sem_va: w.append('- stubs sem endereço no .map (conferir): %d' % len(sem_va))
    w.append('\n## Stubs alcançados pelos inicializadores estáticos (aparecem ao abrir, antes da janela)\n')
    xs = sorted((d for d in linhas if d['xcu'] == 'sim'), key=lambda d: (int(d['ordem_xcu']), int(d['prof_winmain']) if d['prof_winmain'] != '-' else 99))
    if not xs: w.append('Nenhum (por chamada direta).')
    else:
        w.append('Na ordem do .CRT$XCU (nº do inicializador na tabela; o 1º da lista é a 1ª caixa do modo padrão).\n')
        w.append('| ordem | stub | modo | frente | caminho (de quem chama até o inicializador) |\n|---|---|---|---|---|')
        for d in xs: w.append('| %s | `%s` | %s | %s | %s |' % (d['ordem_xcu'], d['simbolo'], d['modo'], d['frentes'], d['caminho_xcu']))
    w.append('\n## Por passo do roteiro (out/V6/ROTEIRO.md) × frente\n')
    fr = sorted({d['frentes'] for d in linhas})
    w.append('| passo | ' + ' | '.join(fr) + ' | total | fatais | alcançados do WinMain (prof. ≤ 3) |')
    w.append('|---|' + '---|' * (len(fr) + 3))
    por = collections.defaultdict(list)
    for d in linhas: por[d['passo']].append(d)
    for p in sorted(por):
        L = por[p]
        w.append('| %s %s | ' % (p, tit.get(p, '')) + ' | '.join(str(sum(d['frentes'] == x for d in L)) for x in fr) +
                 ' | %d | %d | %d |' % (len(L), sum(d['modo'] == 'fatal' for d in L),
                                         sum(d['prof_winmain'] != '-' and int(d['prof_winmain']) <= 3 for d in L)))
    w.append('\n## Os mais perto do WinMain (chamada direta; até 30)\n')
    w.append('| prof. | stub | modo | frente | passo | VA 983 |\n|---|---|---|---|---|---|')
    perto = sorted((d for d in linhas if d['prof_winmain'] != '-'), key=lambda d: (int(d['prof_winmain']), d['simbolo']))
    for d in perto[:30]:
        w.append('| %s | `%s` | %s | %s | %s | %s |' % (d['prof_winmain'], d['simbolo'][:110], d['modo'], d['frentes'], d['passo'], d['va983']))
    w.append('\n## Fatais (não voltam nem com JP983_STUB=continuar)\n')
    w.append('| stub | frente | passo | VA 983 | prof. WinMain |\n|---|---|---|---|---|')
    for d in sorted((d for d in linhas if d['modo'] == 'fatal'), key=lambda d: d['simbolo']):
        w.append('| `%s` | %s | %s | %s | %s |' % (d['simbolo'][:110], d['frentes'], d['passo'], d['va983'], d['prof_winmain']))
    w.append('\nTabela completa: `out/F4/falta_exe.tsv` (uma linha por stub de função).')
    open(OUT + '/FALTA.md', 'w').write('\n'.join(w) + '\n')
    print('\n'.join(w[:8]))


if __name__ == '__main__':
    main()
