#!/usr/bin/env python3
"""C-F4.5: `make exe` (último passo) — copia o build/C/f4/ProjectG_983.exe para out/F4/entrega/ProjectG_nosso.exe e grava o
MD5.txt SÓ se todos os portões do out/F4/portoes.tsv estão ok (A5 = imports existem nas dlls reais do cliente; pedido do dono
após o teste 1, em que o exe nem carregou). Portão fechado = não entrega (sai com 1 e deixa a entrega anterior como está).
C-F4.6: leva junto o build/C/f4/ijl15teste/ijl15_teste.dll (portão A6) e os .bat de out/V6/bat (fonte única dos .bat).
C-F4.8 (pedido C85): + www_teste/patch/updatelist = out/F4/updatelist_web_local_original com a linha ProjectG.exe trocada
(fcrc = CRC_32 do jogo via crc983.py — C86 — e fsize do exe entregue), recifrada com a chave do 983 e conferida decifrando de volta (tools/v6/updatelist.py).
O LEIAME.md da pasta é escrito à mão (diz o md5 da entrega)."""
import os, sys, shutil, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import updatelist
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
import f4cfg   # C94 (C-ROBO): ENTREGA=/F4_BUILD/F4_OUT (make exe ENTREGA=out/F4/entregas/<id>)
EXE, ENT = f4cfg.B4 + '/ProjectG_983.exe', f4cfg.ENT
E = f4cfg.rel(ENT)

port = [l.rstrip('\n').split('\t') for l in open(f4cfg.O4 + '/portoes.tsv')][1:]
fech = [p[0] for p in port if p[2] != 'ok']
if fech or len(port) < 7:
    sys.exit('entrega: NÃO feita — portão(ões) fechado(s): %s (%s/portoes.txt)' % (f4cfg.rel(f4cfg.O4), ', '.join(fech) or 'faltam linhas'))
os.makedirs(ENT, exist_ok=True)
shutil.copyfile(EXE, ENT + '/ProjectG_nosso.exe')
IJL = f4cfg.C4 + '/ijl15teste/ijl15_teste.dll'
shutil.copyfile(IJL, ENT + '/ijl15_teste.dll')
for b in ('USAR_EXE_NOSSO.bat', 'VOLTAR_EXE_ORIGINAL.bat', 'ABRIR_COM_STUBS.bat'):
    shutil.copyfile(R + '/out/V6/bat/' + b, ENT + '/' + b)
m = hashlib.md5(open(EXE, 'rb').read()).hexdigest()
mi = hashlib.md5(open(IJL, 'rb').read()).hexdigest()
open(ENT + '/MD5.txt', 'w').write('%s  %s/ProjectG_nosso.exe\n%s  %s/ijl15_teste.dll\n' % (m, E, mi, E))
print('entrega: %s/ProjectG_nosso.exe %d bytes md5 %s + ijl15_teste.dll md5 %s (portões %s ok)' % (
    E, os.path.getsize(EXE), m, mi, '/'.join(p[0] for p in port)))
updatelist.troca(R + '/out/F4/updatelist_web_local_original', ENT + '/ProjectG_nosso.exe',
                 ENT + '/www_teste/patch/updatelist', f4cfg.O4 + '/updatelist_resumo.txt')
open(ENT + '/MD5.txt', 'a').write('%s  %s/www_teste/patch/updatelist\n' % (hashlib.md5(
    open(ENT + '/www_teste/patch/updatelist', 'rb').read()).hexdigest(), E))
if f4cfg.PROPRIO:   # rodada de outra frente: resumos pequenos junto (a pasta vai inteira para o PC)
    for n in ('portoes.txt', 'stubs_resumo.txt', 'FALTA.md'):
        if os.path.exists(f4cfg.O4 + '/' + n): shutil.copyfile(f4cfg.O4 + '/' + n, ENT + '/' + n)
    open(ENT + '/ORIGEM.txt', 'w').write('build %s; relatórios %s; V6_PG=%s V6_SEM=%s V6_BOBJ=%s\n' % (
        f4cfg.rel(f4cfg.B4), f4cfg.rel(f4cfg.O4), os.environ.get('V6_PG', ''), os.environ.get('V6_SEM', ''), os.environ.get('V6_BOBJ', '')))
# C99: VAs dos ganchos do uitrace no nosso exe (o gancho do PC só conhece os do 983; pedido C99.1 ao revisor)
import uitrace_end
if os.path.exists(f4cfg.B4 + '/ProjectG_983.map'):
    print('uitrace_end: %d/5 ganchos -> %s/uitrace_end.txt' % (
        uitrace_end.gera(f4cfg.B4 + '/ProjectG_983.map', ENT + '/ProjectG_nosso.exe', ENT + '/uitrace_end.txt'), E))
