#!/usr/bin/env python3
"""C99 (C-F4.21): endereços dos 5 ganchos do uitrace (robô do PC) no NOSSO exe. O gancho do PC só conhece os VAs do 983
original (sprite 00BEC720, texto 00BECC00, textura 00BE9C70, evento 00BE9550, arquivo 00B59D00) e no nosso exe recusa
("imagem diferente do IDB"). Grava <entrega>/uitrace_end.txt: gancho, VA no 983, VA no nosso, 16 primeiros bytes (para o
trampolim conferir/copiar o prólogo), símbolo. Mesmas assinaturas/convenções do 983 (args nos mesmos lugares da pilha).
Uso: uitrace_end.py MAPA EXE SAIDA"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe as pemod

G = [('sprite', 0x00BEC720, '?DrawTexture@FrGraphicInterface@@QBEXPBVBitmap@@ABVWRect@@KH@Z'),
     ('texto', 0x00BECC00, '?PrintText11@FrGraphicInterface@@QAEXABVWPoint@@KABVFrTEXT@@@Z'),   # 645 frgraphicinterface.cpp:349
     ('textura', 0x00BE9C70, '?GetBitmap@Fresh@@QAEPBVBitmap@@PBD@Z'),
     ('evento', 0x00BE9550, '?SendCmdToOwnerTarget@FrWnd@@QAE_NW4eFrCmd@@HPAUsFRESH_HANDLER@@@Z'),  # 983: 44 bytes (o curto)
     ('arquivo', 0x00B59D00, '?GetCFile@WResourceManager@@QAEPAVcFile@@PBDH@Z')]


def gera(mapa, exe, saida):
    va = {}
    for l in open(mapa, errors='replace'):
        p = l.split()
        if len(p) >= 3 and ':' in p[0] and len(p[2]) == 8 and all(c in '0123456789abcdef' for c in p[2]): va.setdefault(p[1], int(p[2], 16))
    img = pemod.PE(exe)
    out = ['# gancho\tva_983\tva_nosso\tbytes16\tsimbolo   (C99; uitrace_end.py; ver out/PEDIDOS.md C99.1)']
    for g, v983, sym in G:
        v = va.get(sym)
        if v is None: out.append('%s\t%08X\t-\t-\t%s (ausente no .map)' % (g, v983, sym)); continue
        o = img.off(v - img.base)
        out.append('%s\t%08X\t%08X\t%s\t%s' % (g, v983, v, img.d[o:o + 16].hex().upper(), sym))
    open(saida, 'w').write('\n'.join(out) + '\n')
    return sum(1 for l in out[1:] if '\t-\t' not in l)


if __name__ == '__main__':
    n = gera(*sys.argv[1:4])
    print('uitrace_end: %d/%d ganchos -> %s' % (n, len(G), sys.argv[3]))
