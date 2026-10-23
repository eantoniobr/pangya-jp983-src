#!/usr/bin/env python3
"""Frente C (C351) — par nosso × original: opcodes do GAME por foto, lado a lado.

  parops.py NOSSO ORIG [--de N] [--ate M] [--desloca K] [--todos]
NOSSO/ORIG = id do resultado (out/F4/resultados/<id>) ou caminho. Cada pacote do GAME-JP cai no trecho da última foto
anterior a ele (horas de eventos.txt); repetições seguidas viram "0xID*n". Trecho compara como multiconjunto (a ordem
da rajada do servidor varia; --ordem exige a mesma ordem). --desloca K compara a foto N do NOSSO com a N+K do ORIG. Sem
--todos só imprime os trechos DIFERENTES. No fim: sequência inteira do cliente ('<-' = enviado pelo jogo) com difflib
(pega pacote que caiu uma foto antes/depois) e opcodes exclusivos de cada lado."""
import os, re, sys, glob, argparse, difflib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(R, 'out', 'F4', 'resultados')


def seg(h):
    a, b, c = h.split(':')
    return int(a) * 3600 + int(b) * 60 + float(c)


def le(rid):
    d = rid if os.path.isdir(rid) else os.path.join(RES, rid)
    if not os.path.isfile(os.path.join(d, 'eventos.txt')):
        sys.exit('%s: sem resultado (eventos.txt) — pedido ainda na fila?' % rid)
    fotos = []
    for ln in open(os.path.join(d, 'eventos.txt'), encoding='utf-8', errors='replace'):
        m = re.match(r'(\d\d:\d\d:\d\d\.\d+) foto (\d+)', ln)
        if m:
            fotos.append((seg(m.group(1)), int(m.group(2))))
    pk = []
    for f in sorted(glob.glob(os.path.join(d, 'pacotes', '*GAME*.log'))):
        for ln in open(f, encoding='utf-8', errors='replace'):
            p = ln.split()
            if len(p) >= 3 and p[1] in ('->', '<-') and p[2].startswith('0x'):
                pk.append((seg(p[0]), p[1] + p[2]))
    trechos = {}
    for t, op in sorted(pk, key=lambda x: x[0]):
        n = 0
        for tf, nf in fotos:
            if tf <= t:
                n = nf
        trechos.setdefault(n, []).append(op)
    return trechos


def junta(ops):
    out = []
    for op in ops:
        if out and out[-1][0] == op:
            out[-1][1] += 1
        else:
            out.append([op, 1])
    return ' '.join(o if n == 1 else '%s*%d' % (o, n) for o, n in out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('nosso'); ap.add_argument('orig')
    ap.add_argument('--de', type=int, default=0); ap.add_argument('--ate', type=int, default=999)
    ap.add_argument('--desloca', type=int, default=0); ap.add_argument('--todos', action='store_true')
    ap.add_argument('--ordem', action='store_true')
    a = ap.parse_args()
    n, o = le(a.nosso), le(a.orig)
    dif = 0
    for k in sorted(set(n) | {x - a.desloca for x in o}):
        if not a.de <= k <= a.ate:
            continue
        ln, lo = n.get(k, []), o.get(k + a.desloca, [])
        sn, so = junta(ln), junta(lo)
        ig = sn == so if a.ordem else sorted(ln) == sorted(lo)
        if not ig:
            dif += 1
        if not ig or a.todos:
            print('%s foto %03d/%03d' % ('IGUAL' if ig else 'DIFER', k, k + a.desloca))
            print('  nosso: ' + (sn or '-'))
            if sn != so:
                print('  orig : ' + (so or '-'))
    cn = {op for v in n.values() for op in v}
    co = {op for v in o.values() for op in v}
    print('trechos diferentes: %d' % dif)
    cli = lambda t: [op for k in sorted(t) for op in t[k] if op.startswith('<-')]
    qn, qo = cli(n), cli(o)
    print('cliente inteiro: %s (%d x %d pacotes)' % ('IGUAL' if qn == qo else 'DIFER', len(qn), len(qo)))
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, qn, qo, autojunk=False).get_opcodes():
        if tag != 'equal':
            print('  %s nosso[%d:%d] %s | orig[%d:%d] %s' % (tag, i1, i2, junta(qn[i1:i2]) or '-', j1, j2, junta(qo[j1:j2]) or '-'))
    print('so no nosso: ' + (' '.join(sorted(cn - co)) or '-'))
    print('so no orig : ' + (' '.join(sorted(co - cn)) or '-'))


if __name__ == '__main__':
    sys.exit(main())
