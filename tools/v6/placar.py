#!/usr/bin/env python3
# C184: placar por sistema calculado do out/F5/TELAS.tsv (coluna estado começando por "igual", sem caixa).
# Uso: tools/v6/placar.py            -> mostra a tabela e a linha PLACAR (não grava)
#      tools/v6/placar.py --grava    -> atualiza a coluna "telas" do out/F5/SISTEMAS.tsv (rodar sob flock out/F5/SISTEMAS.lock)
# Sistemas sem tela no TELAS.tsv (quedas, mapa de layouts) ficam como estão.
import os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TELAS = os.path.join(RAIZ, 'out/F5/TELAS.tsv')
SIST = os.path.join(RAIZ, 'out/F5/SISTEMAS.tsv')


def ler(p):
    with open(p, encoding='utf-8') as f:
        return [l.rstrip('\n').split('\t') for l in f if l.strip()]


def main():
    tot, ig = {}, {}
    for c in ler(TELAS)[1:]:
        s = c[0]
        tot[s] = tot.get(s, 0) + 1
        if len(c) > 6 and c[6].strip().lower().startswith('igual'):
            ig[s] = ig.get(s, 0) + 1
    linhas = ler(SIST)
    pronto = 0
    for c in linhas[1:]:
        s = c[0]
        if s in tot:
            i, t = ig.get(s, 0), tot[s]
            c[3] = '%d/%d %d%%' % (i, t, 100 * i // t)
        if c[2].split(' ')[0] == 'PRONTO':  # C283: 'PRONTO (C275: ...)' também conta
            pronto += 1
        print('%-45s %-2s %-13s %s' % (s, c[1], c[2], c[3]))
    sem = sorted(set(tot) - set(c[0] for c in linhas[1:]))
    if sem:
        print('AVISO: sistema do TELAS.tsv sem linha no SISTEMAS.tsv:', ', '.join(sem))
    ti, tt = sum(ig.values()), sum(tot.values())
    print('PLACAR PARA O DONO: %d de %d sistemas PRONTO · telas iguais %d/%d = %d%% (tools/v6/placar.py, out/F5/TELAS.tsv)'
          % (pronto, len(linhas) - 1, ti, tt, 100 * ti // tt))
    if '--grava' in sys.argv[1:]:
        with open(SIST, 'w', encoding='utf-8') as f:
            for c in linhas:
                f.write('\t'.join(c) + '\n')


main()
