#!/usr/bin/env python3
"""C-F4.2: confere os portões A1–A4 do out/V6/ROTEIRO.md (Parte A) -> out/F4/portoes.tsv e out/F4/portoes.txt.

  A1  o exe liga: build/C/f4/ProjectG_983.exe (make exe, C-F4.4) ou, enquanto não existe, o exe de PROVA do make f4-link
      (liga só com /FORCE: portão fechado enquanto houver símbolo não resolvido).
  A2  GameGuard desligado por chave de compilação: compila src/projectg/ggc_wrapper.cpp com CL=/DJP983_SEM_GAMEGUARD (pch da
      tag c) e confere que o _GGC_Init vira `mov eax,1; ret` (2 instruções) e que o .obj não cita o construtor do CNPGameLib;
      sem a chave o _GGC_Init tem de continuar IGUAL ao 983 (00a5cf80). O .obj com a chave vai para build/C/f4/gg/ — FORA de
      build/pg*/obj, para o make v6-link/f4-link não o pegar sem querer (é o make exe que o usa).
  A3  importa ijl15.dll com os mesmos nomes do 983 (out/F4/link/imports.tsv e imports_so_*.tsv do make f4-link).
  A4  constantes de partida do 983 (login, portas, PANGYA_ARG, nome do GameGuard): out/V5/constantes.tsv sem DIFERE (make v5).
  A5  (C-F4.5, pedido do dono após o teste 1) todo import de dll que NÃO é do Windows existe nos exports da dll real que vai
      junto do jogo: mss32 (Mss32.dll do cliente JP 983), ijl15 (rugburn), msvcr100/msvcp100 (redistribuível do VS2010) —
      listas em tools/v6/f4dll/<dll>.txt. Dll fora dessas e fora da lista do sistema (SISTEMA) também fecha o portão.
      O teste 1 parou no carregador: "_AIL_set_DirectSound_HWND@8" não existe no Mss32.dll do cliente. -> out/F4/exe/imports_a5.tsv
  A6  (C-F4.6, pedido do dono após o teste 2) o ijl15 que vai junto é o DE TESTE: build/C/f4/ijl15teste/ijl15_teste.dll
      (rugburn público, tools/v6/ijl15teste/build.sh) existe, exporta todo ijl* que o exe importa, não tem os patches de
      endereço fixo (nem textos "Patched ...", nem o PatchAddress do json), é diferente do ijl15 de terceiro do cliente
      (out/F4/ijl15_rugburn_terceiro.dll), e os .bat da entrega (out/V6/bat) trocam o ijl15.dll e conferem com `fc /b`.
  A7  (C-F4.10, teste 5: "fechou no carregamento", WFile("chat.bin") lançou) valores do 645 QA/KR que o 983 trocou não estão no
      exe e os do 983 estão: chave XTEA da tabela dos .pak (OpenPAKFILE2 00bad6d0 = chave da updatelist 00d3d60c; com a do 645
      nenhum arquivo dos projectg*.pak é achado), chave da updatelist, textos do QA (Pangya_QA, ProjectG_ReleaseQA.exe,
      patch.pangya.ntreev.com). Controle: o dump do 983 passa (mesma conferência).

Uso: make f4-portoes  (= make v5 + python3 tools/v6/portoes.py; ~30 s)
"""
import os, sys, re, glob, shutil, hashlib, subprocess
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, R + '/tools/v6'); import f4cfg
# C94 (C-ROBO): F4_BUILD/F4_OUT (ENTREGA=); a tag provisória do A2 ganha o nome da rodada para duas frentes não se pisarem
TAG = 'f4gg' + ('-' + os.path.basename(f4cfg.B4) if f4cfg.PROPRIO else '')
OUT = f4cfg.O4; GG = f4cfg.B4 + '/gg'; TMP = R + '/build/pg-' + TAG
U = 'projectg/ggc_wrapper.cpp'


def tsv(p):
    if not os.path.exists(p): return []
    return [l.rstrip('\n').split('\t') for l in open(p, encoding='utf-8', errors='replace')]


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def cmpfunc(obj, out):
    mp = out + '/map.tsv'; os.makedirs(out, exist_ok=True)
    with open(mp, 'w') as f:
        for m in ('projectg.tsv', 'pkt_c.tsv'): f.write(open(R + '/map/' + m, encoding='latin1').read())
    subprocess.run([R + '/tools/cmpfunc', obj, '--no-build', '--ref', R + '/ref/ProjectG_983_dump.exe', '--map', mp,
                    '--seed', R + '/map/projectg_seed.tsv', '--funcs', R + '/map/projectg_funcs.tsv', '--out', out],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {c[1]: c for c in tsv(out + '/funcs.tsv')[1:] if len(c) > 8}


def a1():
    exe = f4cfg.B4 + '/ProjectG_983.exe'
    if os.path.exists(exe):
        res = open(OUT + '/exe/resumo.txt').read() if os.path.exists(OUT + '/exe/resumo.txt') else ''
        m = re.search(r'não resolvidos distintos[^:]*: (\d+)', res)
        f = re.search(r'opções: (.*)', res)
        # C92: /FORCE:MULTIPLE só é aceito quando vem do V6_DUP_OK (duplicatas conhecidas, listadas no resumo)
        d = re.search(r'V6_DUP_OK \(.*?\): (\S.*?); LNK2005 no link', res)
        fl = f.group(1).replace('/FORCE:MULTIPLE', '') if f and d else (f.group(1) if f else '')
        ok = bool(m and m.group(1) == '0' and f and '/FORCE' not in fl and 'ggc_wrapper.obj sem GameGuard' in res)
        return ('ok' if ok else 'FECHADO'), 'make exe: %s, %d bytes, md5 %s; %s não resolvidos, %s /FORCE, ggc_wrapper.obj de %s%s' % (
            os.path.relpath(exe, R), os.path.getsize(exe), md5(exe), m.group(1) if m else '?',
            'com' if '/FORCE' in fl else 'sem', f4cfg.rel(GG), ('; /FORCE:MULTIPLE só para ' + d.group(1)) if d else '')
    prova = f4cfg.B4 + '/ProjectG_983_prova.exe'
    res = open(OUT + '/link/resumo.txt').read() if os.path.exists(OUT + '/link/resumo.txt') else ''
    m = re.search(r'não resolvidos distintos[^:]*: (\d+)', res)
    if os.path.exists(prova):
        return 'FECHADO', 'só o exe de prova (/FORCE; %s não resolvidos; md5 %s) — falta o make exe (C-F4.3/C-F4.4)' % (
            m.group(1) if m else '?', md5(prova))
    return 'FECHADO', 'nenhum exe (rodar make f4-link)'


def a2():
    # sem a chave: o .obj da tag c (pgbuild obj --tag c) tem de seguir IGUAL ao 983
    base = R + '/build/pg-c/obj/src/' + U[:-4] + '.obj'
    # C108 (A180): a pg-c já sumiu numa limpeza -> recriar (pch + ggc_wrapper) em vez de fechar o portão
    if not os.path.exists(base) or not os.path.isdir(R + '/build/pg-c/pch'):
        for a in (['pch'], ['obj', U]):
            subprocess.run(['python3', R + '/tools/f32/pgbuild.py'] + a + ['--tag', 'c', '--out', GG + '/pgc'], cwd=R,
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    det = []; ok = True
    if os.path.exists(base):
        f = cmpfunc(base, GG + '/cmp_sem')
        g = f.get('?_GGC_Init@@YIHXZ')
        det.append('sem a chave: _GGC_Init %s %s' % (g[3], g[5]) if g else 'sem a chave: _GGC_Init não achado')
        ok &= bool(g and g[3] == 'IGUAL' and g[5] == '00a5cf80')
    else:
        det.append('sem a chave: %s não existe (rodar tools/pkt/wl.sh %s)' % (os.path.relpath(base, R), U)); ok = False
    # com a chave: compila numa tag provisória que usa o pch da tag c e tira o .obj de build/pg*
    shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP)
    os.symlink('../pg-c/pch', TMP + '/pch')
    env = dict(os.environ, CL='/DJP983_SEM_GAMEGUARD')
    p = subprocess.run(['python3', R + '/tools/f32/pgbuild.py', 'obj', U, '--tag', TAG, '--force', '--out', GG + '/pg'],
                       cwd=R, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    obj = TMP + '/obj/src/' + U[:-4] + '.obj'
    os.makedirs(GG, exist_ok=True)
    if not os.path.exists(obj):
        shutil.rmtree(TMP, ignore_errors=True)
        return 'FECHADO', '; '.join(det + ['com a chave: não compila (%s)' % p.stdout.strip().splitlines()[-1:]])
    dst = GG + '/ggc_wrapper.obj'; shutil.copy2(obj, dst)
    shutil.copy2(obj[:-4] + '.log', GG + '/ggc_wrapper.log')
    shutil.rmtree(TMP, ignore_errors=True)
    f = cmpfunc(dst, GG + '/cmp_com')
    g = f.get('?_GGC_Init@@YIHXZ')
    ctor = b'??0CNPGameLib@@' in open(dst, 'rb').read()
    det.append('com a chave: _GGC_Init %s instruções%s; construtor do CNPGameLib %s no .obj (%s)' % (
        g[7] if g else '?', ' (mov eax,1; ret)' if g and g[7] == '2' else '', 'CITADO' if ctor else 'não citado',
        os.path.relpath(dst, R)))
    ok &= bool(g and g[7] == '2' and not ctor)
    return ('ok' if ok else 'FECHADO'), '; '.join(det)


def a3():
    L = OUT + ('/exe' if os.path.exists(OUT + '/exe/imports.tsv') else '/link')   # o do make exe, se houver
    imp = {c[0]: c for c in tsv(L + '/imports.tsv')[1:] if len(c) >= 3}
    so = [c for n in ('imports_so_983.tsv', 'imports_so_nosso.tsv') for c in tsv(L + '/' + n)
          if c and c[0].lower() == 'ijl15.dll']
    i = imp.get('ijl15.dll')
    if not i: return 'FECHADO', 'ijl15.dll não está nas importações do exe (rodar make f4-link)'
    ok = i[1] == i[2] and i[1] != '0' and not so
    return ('ok' if ok else 'FECHADO'), 'ijl15.dll: %s nomes no nosso × %s no 983; %d diferentes por nome (%s/imports*.tsv)' % (
        i[1], i[2], len(so), os.path.relpath(L, R))


def a4():
    t = tsv(R + '/out/V5/constantes.tsv')[1:]
    dif = [c[0] for c in t if c and c[-1] != 'igual']
    if not t: return 'FECHADO', 'out/V5/constantes.tsv não existe (rodar make v5)'
    return ('ok' if not dif else 'FECHADO'), '%d constantes, %d iguais%s (out/V5/constantes.tsv)' % (
        len(t), len(t) - len(dif), '; DIFERE: ' + ', '.join(dif) if dif else '')


SISTEMA = {'advapi32', 'avifil32', 'comctl32', 'comdlg32', 'dbghelp', 'gdi32', 'imm32', 'iphlpapi', 'kernel32', 'msvfw32',
           'netapi32', 'ole32', 'oleaut32', 'shell32', 'shlwapi', 'user32', 'wininet', 'winmm', 'ws2_32'}


def a5(exe=None):
    sys.path.insert(0, R + '/tools/v6'); from pe import PE
    exe = exe or f4cfg.B4 + '/ProjectG_983.exe'
    if not os.path.exists(exe): return 'FECHADO', '%s não existe (rodar make exe)' % os.path.relpath(exe, R)
    imp = sorted(PE(exe).imports())
    ruins, n, porDll = [], 0, {}
    for dll, nm in imp:
        b = dll[:-4] if dll.endswith('.dll') else dll
        ref = R + '/tools/v6/f4dll/%s.txt' % b
        if os.path.exists(ref):
            if b not in porDll: porDll[b] = {l.strip() for l in open(ref) if l.strip() and not l.startswith('#')}
            n += 1
            if nm not in porDll[b]: ruins.append((dll, nm, 'não exportado pela dll real'))
        elif b not in SISTEMA: ruins.append((dll, nm, 'dll desconhecida (nem do Windows nem em tools/v6/f4dll)'))
    os.makedirs(OUT + '/exe', exist_ok=True)
    with open(OUT + '/exe/imports_a5.tsv', 'w') as f:
        f.write('dll\tnome\tproblema\n')
        for r in ruins: f.write('\t'.join(r) + '\n')
    det = '%d imports de %s conferidos com os exports reais (tools/v6/f4dll); %d com problema%s (out/F4/exe/imports_a5.tsv)' % (
        n, '/'.join(sorted(porDll)), len(ruins), ': ' + ', '.join('%s!%s' % r[:2] for r in ruins[:6]) if ruins else '')
    return ('ok' if not ruins else 'FECHADO'), det


def a6(exe=None):
    sys.path.insert(0, R + '/tools/v6'); from pe import PE
    exe = exe or f4cfg.B4 + '/ProjectG_983.exe'
    dll = f4cfg.C4 + '/ijl15teste/ijl15_teste.dll'
    terc = R + '/out/F4/ijl15_rugburn_terceiro.dll'
    if not os.path.exists(dll): return 'FECHADO', 'falta build/C/f4/ijl15teste/ijl15_teste.dll (tools/v6/ijl15teste/build.sh)'
    prob = []
    ex = PE(dll).exports()
    pede = sorted(n for d, n in PE(exe).imports() if d == 'ijl15.dll') if os.path.exists(exe) else []
    if not pede: prob.append('exe sem imports de ijl15.dll?')
    prob += ['não exporta ' + n for n in pede if n not in ex]
    b = open(dll, 'rb').read()
    if b'Patched ' in b: prob.append('tem texto "Patched ..." (patch de endereço fixo)')
    if b'sem patches de endereco fixo' not in b: prob.append('sem a marca do sem_endereco.c')
    mp = dll[:-4] + '.map'
    if os.path.exists(mp) and re.search(r'\?PatchAddress@@YAXXZ|PatchGG_|ranking', open(mp, errors='replace').read()):
        prob.append('.map com PatchAddress/PatchGG_/ranking ligados')
    if os.path.exists(terc) and md5(terc) == md5(dll): prob.append('igual ao ijl15 de terceiro')
    for bat, deve in (('USAR_EXE_NOSSO.bat', ('ijl15.dll.orig', 'ijl15_teste.dll', 'fc /b')),
                      ('VOLTAR_EXE_ORIGINAL.bat', ('ijl15.dll.orig', 'jp983_stub_continuar.txt')),
                      ('ABRIR_COM_STUBS.bat', ('fc /b', 'jp983_stub_continuar.txt', 'PORTAO A6'))):
        t = open(R + '/out/V6/bat/' + bat, encoding='ascii', errors='replace').read() if os.path.exists(R + '/out/V6/bat/' + bat) else ''
        prob += ['%s sem %r' % (bat, x) for x in deve if x not in t]
    det = 'ijl15_teste.dll md5 %s; exporta %d/%d ijl* do exe; %s' % (
        md5(dll), len(pede) - sum(n not in ex for n in pede), len(pede), '; '.join(prob) if prob else 'sem patch de endereço; .bat trocam e conferem')
    return ('ok' if not prob else 'FECHADO'), det


KEY983 = (0x020a5fd4, 0x01eebdff, 0x02b3c6a0, 0x04f6a3e1)   # .pak (00bad6d0) e updatelist (00d3d60c) do 983
KEY645 = (0x0485b576, 0x05148e02, 0x05141d96, 0x028fa9d6)   # .pak e updatelist do 645 QA
QA645 = (b'Pangya_QA', b'ProjectG_ReleaseQA.exe', b'patch.pangya.ntreev.com')


def a7(exe=None):
    import struct
    exe = exe or f4cfg.B4 + '/ProjectG_983.exe'
    if not os.path.exists(exe): return 'FECHADO', '%s não existe (rodar make exe)' % os.path.relpath(exe, R)
    b = open(exe, 'rb').read(); prob = []
    # código: as 4 palavras como imediato de `mov [ebp-0x14..-8], imm32` (c7 45 ec/f0/f4/f8), como no OpenPAKFILE2 do 983
    cod = b''.join(b'\xc7\x45' + bytes([d]) + struct.pack('<I', k) for d, k in zip((0xec, 0xf0, 0xf4, 0xf8), KEY983))
    npak = b.count(cod)
    if npak != 1: prob.append('chave do 983 no OpenPAKFILE2: %d lugar(es) (esperado 1)' % npak)
    ndado = b.count(b''.join(struct.pack('<I', k) for k in KEY983))
    if ndado < 1: prob.append('chave da updatelist do 983 ausente como dado')
    for k in KEY645:
        if struct.pack('<I', k) in b: prob.append('palavra da chave do 645 0x%08x presente' % k)
    for t in QA645:
        if t.lower() in b.lower(): prob.append('texto do 645 QA %r presente' % t.decode())
    det = 'chave .pak do 983 no código %dx, chave updatelist como dado %dx; %s' % (
        npak, ndado, '; '.join(prob) if prob else '0 valores do 645 QA (chaves, Pangya_QA, ReleaseQA, ntreev)')
    return ('ok' if not prob else 'FECHADO'), det


def a8(exe=None):
    # C92 (revisor 14/10 17:05): manifesto de ID 1 requireAdministrator como o 983 (com asInvoker, c91-1, o jogo dá "파일 에러")
    exe = exe or f4cfg.B4 + '/ProjectG_983.exe'
    if not os.path.exists(exe): return 'FECHADO', '%s não existe (rodar make exe)' % os.path.relpath(exe, R)
    b = open(exe, 'rb').read()
    ni, na = b.count(b'level="asInvoker"'), b.count(b'level="requireAdministrator"')
    return ('ok' if na >= 1 and ni == 0 else 'FECHADO'), 'manifestos no exe: asInvoker %dx, requireAdministrator %dx (o de nome MANIFEST_RESOURCE_ID não é lido pelo Windows)' % (ni, na)


if __name__ == '__main__':
    if '--a7' in sys.argv:             # conferência avulsa: portoes.py --a7 EXE
        e, d = a7(sys.argv[sys.argv.index('--a7') + 1]); print('A7', e, d); sys.exit(0 if e == 'ok' else 1)
    os.makedirs(OUT, exist_ok=True)
    if '--so-a2' in sys.argv:          # make exe: só (re)compila o build/C/f4/gg/ggc_wrapper.obj antes do link
        e, d = a2(); print('A2', e, d); sys.exit(0 if e == 'ok' else 1)
    linhas = [('A1', 'o exe liga', *a1()), ('A2', 'GameGuard desligado por chave (JP983_SEM_GAMEGUARD)', *a2()),
              ('A3', 'importa ijl15.dll (rugburn)', *a3()), ('A4', 'constantes de login/PANGYA_ARG do 983', *a4()),
              ('A5', 'imports existem nas dlls reais do cliente', *a5()),
              ('A6', 'ijl15 de teste (rugburn público, sem patch de endereço)', *a6()),
              ('A7', 'valores do 983 (chave dos .pak/updatelist), nada do 645 QA', *a7()),
              ('A8', 'manifesto requireAdministrator do 983 (asInvoker quebra o arranque)', *a8())]
    with open(OUT + '/portoes.tsv', 'w') as f:
        f.write('portao\to_que\testado\tdetalhe\n')
        for l in linhas: f.write('\t'.join(l) + '\n')
    txt = ['%s %-55s %-8s %s' % l for l in linhas]
    txt.append('portões A1–A8: %d de %d ok' % (sum(l[2] == 'ok' for l in linhas), len(linhas)))
    open(OUT + '/portoes.txt', 'w').write('\n'.join(txt) + '\n')
    print('\n'.join(txt))
    sys.exit(0 if all(l[2] == 'ok' for l in linhas) else 1)
