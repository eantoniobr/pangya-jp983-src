#!/usr/bin/env python3
# C186: diferença byte a byte do 0x0044 grande (dados do jogador) entre dois resultados do robô.
# Uso: tools/v6/diff0044.py out/F4/resultados/<A> out/F4/resultados/<B>  -> "offset hexA hexB" por trecho.
# Serve para separar estado da conta (caddie/itens equipados) de defeito nosso antes de comparar telas.
import glob, sys

def player_data(run):
    for line in open(glob.glob(run + '/pacotes/*GAME*')[0], errors='replace'):
        p = line.split()
        if len(p) > 4 and p[1] == '->' and p[2] == '0x0044' and int(p[3]) > 1000:
            return bytes.fromhex(p[4])

a, b = player_data(sys.argv[1]), player_data(sys.argv[2])
diff = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
i = 0
while i < len(diff):
    j = i
    while j + 1 < len(diff) and diff[j + 1] - diff[j] < 8:  # junta trechos próximos
        j += 1
    s, e = diff[i], diff[j] + 1
    print(hex(s), a[s:e].hex(), b[s:e].hex())
    i = j + 1
