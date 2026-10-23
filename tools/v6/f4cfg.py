"""C-ROBO (C94): pastas do `make exe`, parametrizáveis para A e B gerarem o próprio exe de teste sem pisar no da C.

Padrão (C): build/C/f4, out/F4, out/V6/link, out/F4/entrega — igual ao de antes.
Com ENTREGA=out/F4/entregas/<id> (make exe ENTREGA=...; ver Makefile.C), o Makefile exporta:
  F4_BUILD = build/f4e/<id>        link, stubs, gg, res, exe e .map  (PRIVADO da rodada)
  F4_OUT   = build/f4e/<id>/out     relatórios (link/, link_stubs/, exe/, stubs.tsv, FALTA.md, portoes.tsv)
  V6_OUT   = build/f4e/<id>/out/v6link   objs.tsv/falta.tsv do v6-link
(a pasta ENTREGA vai inteira para o PC por scp: só o exe, a ijl15, a updatelist, os .bat, MD5.txt e 3 resumos pequenos)
Entradas COMPARTILHADAS (só leitura nas rodadas com ENTREGA=; quem as refaz é o make exe da C): build/C/f4/terc,
build/C/f4/ijl15teste, build/C/f4/mss32x.lib, build/C/f4/ws2_32.lib, out/F4/updatelist_web_local_original.
"""
import os
R = '/root/jp983src'
C4 = R + '/build/C/f4'                                       # compartilhado
B4 = os.path.abspath(os.environ.get('F4_BUILD') or C4)       # saída do link
O4 = os.path.abspath(os.environ.get('F4_OUT') or R + '/out/F4')
V6 = os.path.abspath(os.environ.get('V6_OUT') or R + '/out/V6/link')
ENT = os.path.abspath(os.environ.get('ENTREGA') or R + '/out/F4/entrega')
PROPRIO = B4 != C4                                           # rodada de outra frente (ENTREGA=)


def rel(p): return os.path.relpath(p, R)
