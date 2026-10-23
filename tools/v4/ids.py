#!/usr/bin/env python3
"""Frente C, V4 — tabela de conversão dos ids de pacote: nosso fonte (numeração do 645) -> exe 983.

  ids.py -> out/V4/ids_servidor.tsv (recebidos; de rx_cmp.tsv) e out/V4/ids_cliente.tsv (enviados; de pk_cmp.tsv)
Recebidos: em cada despachante, alinha a lista de casos do fonte com a do 983 (ordem crescente de id) pela sequência de
leituras de cada caso (difflib, só casos com >= 2 leituras) e vota no par id_fonte -> id_983.
Enviados: nas funções pareadas pelo comparador, o n-ésimo pacote criado no nosso .obj × o n-ésimo no 983, quando a
quantidade de pacotes e os campos (E1 E4 ES …) são iguais."""
import os, sys, csv, re, collections, difflib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(R, 'out', 'V4')


def letras(s):
    return ' '.join(x.split('(')[0] for x in s.split() if x[0] == 'D')


def servidor():
    por = collections.defaultdict(lambda: ([], []))
    for r in csv.DictReader(open(os.path.join(OUT, 'rx_cmp.tsv')), delimiter='\t'):
        i = int(r['id'], 16)
        if r['estado'] in ('so_983', 'igual', 'difere'):
            por[r['despachante']][0].append((i, letras(r['leituras_983'])))
        if r['estado'] in ('so_fonte', 'igual', 'difere'):
            por[r['despachante']][1].append((i, r['leituras_fonte']))
    votos = collections.defaultdict(collections.Counter)
    for d, (l9, lf) in por.items():
        l9.sort()
        lf.sort()
        a = [s if len(s.split()) >= 2 else 'f%d' % k for k, (i, s) in enumerate(lf)]
        b = [s if len(s.split()) >= 2 else 'n%d' % k for k, (i, s) in enumerate(l9)]
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        for blk in sm.get_matching_blocks():
            for k in range(blk.size):
                votos[lf[blk.a + k][0]][(l9[blk.b + k][0], d)] += 1
    rows = []
    for f in sorted(votos):
        c = collections.Counter()
        for (i9, d), n in votos[f].items():
            c[i9] += n
        melhor, n = c.most_common(1)[0]
        rows.append((f, melhor, n, sum(c.values()), ' '.join('0x%x:%d' % kv for kv in c.most_common()),
                     ','.join(sorted({d for (i9, d) in votos[f] if i9 == melhor}))))
    with open(os.path.join(OUT, 'ids_servidor.tsv'), 'w') as fo:
        fo.write('id_fonte\tid_983\tdelta\tcerteza\tvotos\ttotal\ttodos\tdespachantes\n')
        for (f, m, n, t, todos, ds), c in zip(rows, certeza(rows)):
            fo.write('0x%x\t0x%x\t%+d\t%s\t%d\t%d\t%s\t%s\n' % (f, m, m - f, c, n, t, todos, ds))
    faixas(rows, 'recebidos')
    return rows


def certeza(rows):
    """'faixa' se o id vizinho (anterior ou seguinte com par) tem o mesmo delta; senão 'isolado' (conferir à mão)."""
    out = []
    for k, r in enumerate(rows):
        d = r[1] - r[0]
        viz = [rows[j][1] - rows[j][0] for j in (k - 1, k + 1) if 0 <= j < len(rows)]
        out.append('faixa' if d in viz else 'isolado')
    return out


def faixas(rows, titulo):
    """resumo: trechos consecutivos de ids com o mesmo delta."""
    out = []
    for f, m, n, t, *_ in rows:
        d = m - f
        if out and out[-1][2] == d:
            out[-1][1] = f
            out[-1][3] += 1
        else:
            out.append([f, f, d, 1])
    print('%s: %d ids com par; por faixa (id_fonte de–até, delta, nº de ids):' % (titulo, len(rows)))
    print('  ' + '; '.join('0x%x–0x%x %+d (%d)' % tuple(x) for x in out))


def cliente():
    votos = collections.defaultdict(collections.Counter)
    onde = collections.defaultdict(set)
    for r in csv.DictReader(open(os.path.join(OUT, 'pk_cmp.tsv')), delimiter='\t'):
        if r['estado'] not in ('igual', 'igual_curinga') and not r['estado'].startswith('difere'):
            continue
        def pac(s):
            res = []
            for x in s.split():
                if x.startswith('P('):
                    res.append([x[2:-1], []])
                elif res and x[0] == 'E':
                    res[-1][1].append(x.split('(')[0])
            return res
        a, b = pac(r['assinatura_nossa']), pac(r['assinatura_983'])
        if len(a) != len(b):
            continue
        for (ia, ca), (ib, cb) in zip(a, b):
            if '?' in ia or '?' in ib or ca != cb:
                continue
            votos[int(ia, 16)][int(ib, 16)] += 1
            onde[int(ia, 16)].add(r['unidade'].replace('src_projectg_', ''))
    rows = []
    for f in sorted(votos):
        c = votos[f]
        m, n = c.most_common(1)[0]
        rows.append((f, m, n, sum(c.values()), ' '.join('0x%x:%d' % kv for kv in c.most_common()), ','.join(sorted(onde[f]))[:120]))
    with open(os.path.join(OUT, 'ids_cliente.tsv'), 'w') as fo:
        fo.write('id_nosso\tid_983\tdelta\tcerteza\tvotos\ttotal\ttodos\tunidades\n')
        for (f, m, n, t, todos, us), c in zip(rows, certeza(rows)):
            fo.write('0x%x\t0x%x\t%+d\t%s\t%d\t%d\t%s\t%s\n' % (f, m, m - f, c, n, t, todos, us))
    faixas(rows, 'enviados')
    amb = [r for r in rows if r[2] != r[3]]
    print('enviados: %d ids do nosso fonte com mais de um id do 983 (fonte já adaptado em parte, ou par errado)' % len(amb))
    return rows


if __name__ == '__main__':
    servidor()
    cliente()
