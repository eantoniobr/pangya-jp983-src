#!/usr/bin/env python3
"""F4 (frente C, C-F4.1): link de PROVA do ProjectG 983 com /FORCE — o que só aparece no link de verdade.

Liga os .obj do out/V6/link/objs.tsv (o `make v6-link` escolhe: A = .obj mais novo sem erro de cada unidade; B = build/B/obj)
com o link.exe do VS2010 SP1 (o mesmo linker 10.0 do exe 983), as .lib do VC10 (msvcrt -> msvcr100.dll, msvcprt ->
msvcp100.dll, como o 983), o SDK Aug2002 do rebang e as .lib de terceiros do rebang (lua, freetype, zlib, libpng, ijl15).
/FORCE:MULTIPLE,UNRESOLVED: o exe sai mesmo com símbolo faltando (NÃO roda: cada símbolo que falta vira chamada a 0).
Saída: build/C/f4/ProjectG_983_prova.exe (+ .map, .log) e out/F4/link/:
  resumo.txt        contagens por código LNK, tamanho das seções, imports do nosso exe × imports do 983
  avisos.tsv        cada aviso/erro do link (código, símbolo, quem cita)
  imports.tsv       dll × nº de funções importadas (nosso × 983)
  xcu.tsv           inicializadores dinâmicos (??__E) por .obj na ordem do link (+ xcu983.tsv/xcu_ordem.tsv do xcu983.py)
  nao_resolvidos.tsv  cada símbolo que falta, se o `make v6-link` previa, frente e VA do 983
  imports_so_983.tsv / imports_so_nosso.tsv / imports_so_983_quem.tsv (impusers.py: quem usa no 983)
  recursos.tsv      tipo/id/língua × bytes, nosso × 983
Uso: make f4-link  (= python3 tools/v6/linkprova.py [--sem-terceiros] [--opt] [--stubs | --exe]; ~1 min; não compila .cpp, só o .rc e as\n     import libs por nome; pede um `make v6-link` antes para a lista de .obj estar em dia)
"""
import os, sys, re, subprocess, collections, time
R = '/root/jp983src'
VS = os.environ.get('VS', '/root/kr839/local/vs2010')
SDK = '/root/rebang/tools/PlatformSDK-Aug2002/lib'
sys.path.insert(0, R + '/tools/v6')
import f4cfg
B = f4cfg.B4                 # C94 (C-ROBO): build/C/f4 ou F4_BUILD
OUT = f4cfg.O4 + '/link'
EXE = B + '/ProjectG_983_prova.exe'
sys.path.insert(0, R + '/tools/v6')
CRT = [VS + '/VC10/lib/' + x for x in ('msvcrt.lib', 'msvcprt.lib', 'oldnames.lib')]
SYS = [VS + '/sdklib/kernel32.lib'] + [SDK + '/' + x + '.lib' for x in (
    'user32', 'gdi32', 'comdlg32', 'advapi32', 'shell32', 'ole32', 'oleaut32', 'uuid', 'shlwapi', 'comctl32', 'vfw32',
    'ws2_32', 'wininet', 'dbghelp', 'iphlpapi', 'msimg32', 'imm32', 'winmm')]
OUTRAS = ['/root/rebang/tools/VC7.1/lib/atls.lib', '/root/rebang/source/client/ProjectG/lib/mss32.lib',
          '/root/rebang/source/client/ProjectG/lib/NPGameLib.lib', B + '/mss32x.lib']
TERCEIROS = ['/root/rebang/build/projectg/source/shared/LuaSystem/Lua/lib/lua51_Release_MD_fastcall.lib',
             '/root/rebang/build/projectg/source/client/Wangreal/lib/freetype221MT.lib',
             '/root/rebang/source/client/Fresh/lib/zlib.lib', '/root/rebang/source/client/Fresh/lib/libpng.lib',
             '/root/rebang/source/client/Wangreal/lib/ijl15.lib']
# o 983 é /BASE:0x400000, sem ASLR nem SafeSEH (cabeçalho do ref/ProjectG_983_dump.exe)
FLAGS = ['/NOLOGO', '/MACHINE:X86', '/SUBSYSTEM:WINDOWS', '/BASE:0x400000', '/DYNAMICBASE:NO', '/NXCOMPAT:NO',
         '/SAFESEH:NO', '/INCREMENTAL:NO', '/NODEFAULTLIB', '/FORCE:MULTIPLE', '/FORCE:UNRESOLVED', '/ERRORREPORT:NONE']


# importação POR NOME como no 983 (dumpbin /imports do ref: 0 por ordinal). As .lib do SDK Aug2002 (ws2_32, oleaut32) e a
# ijl15.lib do rebang importam por ORDINAL; o rugburn é carregado como ijl15.dll e não sabemos os ordinais dele -> import
# libs nossas a partir de tools/v6/f4def/<dll>.def (nomes decorados tirados das .lib originais). `lib /DEF` com `f@N` daria
# importação do nome DECORADO (a dll não exporta "connect@12"); por isso ligamos uma dll-stub (funções __stdcall vazias com
# N/4 argumentos) com um .def SEM decoração: o link gera a import lib com "Name type: undecorate", como as do SDK novo.
DEFS = {'ws2_32.lib': 'ws2_32', 'oleaut32.lib': 'oleaut32', 'ijl15.lib': 'ijl15'}


def implibs():
    vs = R + '/tools/vs.sh'
    for n in DEFS.values():
        d, o = R + '/tools/v6/f4def/%s.def' % n, B + '/%s.lib' % n
        if os.path.exists(o) and os.path.getmtime(o) >= os.path.getmtime(d): continue
        lib, nomes = None, []
        for l in open(d):
            l = l.split(';')[0].strip()
            if l.startswith('LIBRARY'): lib = l.split()[1]
            elif l and l != 'EXPORTS': nomes.append(l.split()[0])
        t = B + '/stub_' + n
        os.makedirs(t, exist_ok=True)
        with open(t + '/s.c', 'w') as f, open(t + '/s.def', 'w') as g:
            g.write('LIBRARY %s\nEXPORTS\n' % lib)
            for x in nomes:
                nm, _, k = x.partition('@')
                args = ', '.join('int a%d' % i for i in range(int(k or 0) // 4)) or 'void'
                f.write('int %s %s(%s) { return 0; }\n' % ('__stdcall' if k else '__cdecl', nm, args))
                g.write('  %s\n' % nm)
        run = lambda *a: subprocess.run([vs] + list(a), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
        run('cl', '/nologo', '/c', '/Fo' + t + '/s.obj', t + '/s.c')
        run('link', '/NOLOGO', '/DLL', '/NOENTRY', '/NODEFAULTLIB', '/MACHINE:X86', '/DEF:' + t + '/s.def',
            '/OUT:' + t + '/s.dll', '/IMPLIB:' + o, t + '/s.obj')


# C-F4.6: o mss32.lib do rebang é do Miles do 645; o miles.cpp do 983 (C82.1 da A) importa funções do Miles novo que o Mss32.dll
# do cliente exporta (tools/v6/f4dll/mss32.txt) e a .lib velha não tem. Import lib complementar com o nome DECORADO exato
# (como no 983 e na .lib velha: "Name type: name"): dll-stub + .def `nome=nome` (o `lib /DEF` sozinho daria o símbolo __imp___AIL…).
MSS32X = ['_AIL_file_size_info@12', '_AIL_file_read_info@16']


def mss32x():
    o, d = B + '/mss32x.lib', R + '/tools/v6/linkprova.py'
    if os.path.exists(o) and os.path.getmtime(o) >= os.path.getmtime(d): return
    t = B + '/stub_mss32x'
    os.makedirs(t, exist_ok=True)
    with open(t + '/s.c', 'w') as f, open(t + '/s.def', 'w') as g:
        g.write('LIBRARY Mss32\nEXPORTS\n')
        for x in MSS32X:
            nm, _, k = x[1:].partition('@')
            f.write('int __stdcall %s(%s) { return 0; }\n' % (nm, ', '.join('int a%d' % i for i in range(int(k) // 4)) or 'void'))
            g.write('  %s=%s\n' % (x, x))
    run = lambda *a: subprocess.run([R + '/tools/vs.sh'] + list(a), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    run('cl', '/nologo', '/c', '/Fo' + t + '/s.obj', t + '/s.c')
    run('link', '/NOLOGO', '/DLL', '/NOENTRY', '/NODEFAULTLIB', '/MACHINE:X86', '/DEF:' + t + '/s.def',
        '/OUT:' + t + '/s.dll', '/IMPLIB:' + o, t + '/s.obj')


RES = B + '/projectg_f4.res'


def recursos_rc():
    """src/projectg/ProjectG.rc + tools/v6/f4res/projectg_f4.rc -> build/C/f4/res/projectg_f4.rc (UTF-16) -> projectg_f4.res"""
    d = B + '/res'; os.makedirs(d, exist_ok=True)
    src = open(R + '/src/projectg/ProjectG.rc', encoding='utf-8-sig').read().replace('#pragma code_page(65001)', '')
    extra = open(R + '/tools/v6/f4res/projectg_f4.rc', encoding='utf-8').read()
    open(d + '/projectg_f4.rc', 'w', encoding='utf-16').write((src + '\n' + extra).replace('\r\n', '\n').replace('\n', '\r\n'))
    p = subprocess.run([R + '/tools/vs.sh', 'run', '/root/rebang/tools/VC7.1/bin/rc.exe', '/i', R + '/src/projectg',
                        '/i', R + '/tools/v6/f4res', '/fo', RES, d + '/projectg_f4.rc'], cwd=R + '/tools/v6/f4res',
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    open(d + '/rc.log', 'wb').write(p.stdout)
    return p.returncode == 0 and os.path.exists(RES)


def z(p): return 'Z:' + p.replace('/', '\\')


def objs():
    o = []
    for l in open(f4cfg.V6 + '/objs.tsv'):
        c = l.rstrip('\n').split('\t')
        if len(c) >= 2 and c[1].endswith('.obj'): o.append((c[0], R + '/' + c[1] if not c[1].startswith('/') else c[1]))
    return o


def imports(exe):
    p = subprocess.run([R + '/tools/vs.sh', 'dumpbin', '/imports', exe], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    n, d = collections.Counter(), None
    for l in p.stdout.decode('latin1').replace('\r', '').split('\n'):
        m = re.match(r'^    ([A-Za-z0-9_.\-]+\.(?:dll|DLL))$', l)
        if m: d = m.group(1).lower(); continue
        if d and (re.match(r'^ +[0-9A-F]+ \S+$', l) or re.match(r'^ +Ordinal +\d+$', l)): n[d] += 1
        if d and re.match(r'^ +Ordinal +\d+$', l): n['(por ordinal)'] += 1
        elif d and l.strip().startswith('Summary'): d = None
    return n


def main():
    global EXE, OUT, TERCEIROS
    terc = '--sem-terceiros' not in sys.argv
    flags = FLAGS + (['/OPT:REF', '/OPT:ICF'] if '--opt' in sys.argv else ['/OPT:NOREF', '/OPT:NOICF'])
    # --stubs (C-F4.3): + build/C/f4/stubs/stubs983.obj (make f4-stubs) e zlib/libpng do VS2010 (make f4-terc), SEM /FORCE
    # -> build/C/f4/ProjectG_983_stubs.exe e out/F4/link_stubs/ (o out/F4/link/ do link de prova fica como está)
    # --exe (C-F4.4, make exe): igual ao --stubs, mas com o build/C/f4/gg/ggc_wrapper.obj (JP983_SEM_GAMEGUARD) no lugar do
    # ggc_wrapper.obj da lista -> build/C/f4/ProjectG_983.exe e out/F4/exe/
    exe = '--exe' in sys.argv
    DUP_OK = set(os.environ.get('V6_DUP_OK', '').split())
    stubs = '--stubs' in sys.argv or exe
    if stubs:
        EXE, OUT = (B + '/ProjectG_983.exe', f4cfg.O4 + '/exe') if exe else (B + '/ProjectG_983_stubs.exe', f4cfg.O4 + '/link_stubs')
        flags = [x for x in flags if not x.startswith('/FORCE')]
        # C92: V6_DUP_OK="sim1 sim2" = duplicatas (LNK2005) conhecidas, aceitas com /FORCE:MULTIPLE (fica a 1ª definição);
        # qualquer outra LNK2005 apaga o exe. Uso: contornar visão duplicada de outra frente até ela corrigir.
        if DUP_OK: flags.append('/FORCE:MULTIPLE')
        TERCEIROS = [f4cfg.C4 + '/terc/' + os.path.basename(L) if os.path.basename(L) in ('zlib.lib', 'libpng.lib') else L for L in TERCEIROS]
        if os.path.exists(EXE): os.remove(EXE)
    os.makedirs(B, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    ob = objs()
    if stubs: ob += [('C', B + '/stubs/stubs983.obj'), ('C', B + '/stubs/stubs983a.obj')]
    if exe:
        gg = [i for i, (_, q) in enumerate(ob) if os.path.basename(q) == 'ggc_wrapper.obj']
        if len(gg) != 1 or not os.path.exists(B + '/gg/ggc_wrapper.obj'):
            sys.exit('linkprova --exe: ggc_wrapper.obj na lista %d vez(es); build/C/f4/gg/ggc_wrapper.obj %s (rodar make f4-portoes)'
                     % (len(gg), 'existe' if os.path.exists(B + '/gg/ggc_wrapper.obj') else 'NÃO existe'))
        ob[gg[0]] = ('C', B + '/gg/ggc_wrapper.obj')
    implibs()
    mss32x()
    troca = lambda L: B + '/' + DEFS[os.path.basename(L)] + '.lib' if os.path.basename(L) in DEFS else L
    libs = [troca(L) for L in CRT + SYS + OUTRAS + (TERCEIROS if terc else []) if os.path.exists(L)]
    falta_lib = [L for L in CRT + SYS + OUTRAS + (TERCEIROS if terc else []) if not os.path.exists(L)]
    rsp = B + '/link.rsp'
    with open(rsp, 'w') as f:
        for x in flags + ['/OUT:' + z(EXE), '/MAP:' + z(EXE[:-4] + '.map'), '/MAPINFO:EXPORTS']: f.write(x + '\n')
        for _, p in ob: f.write('"%s"\n' % z(p))
        if recursos_rc(): f.write('"%s"\n' % z(RES))
        for L in libs: f.write('"%s"\n' % z(L))
    t = time.time()
    p = subprocess.run([R + '/tools/vs.sh', 'link', '@' + rsp], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       env=dict(os.environ, VS=VS))
    dt = time.time() - t
    log = p.stdout.decode('latin1').replace('\r', '')
    open(EXE[:-4] + '.log', 'w').write(log)
    # avisos/erros
    cod, linhas = collections.Counter(), []
    for l in log.split('\n'):
        m = re.search(r'\b(LNK\d{4})\b', l)
        if not m: continue
        cod[m.group(1)] += 1
        quem = l.split(' : ')[0].strip()
        sm = (re.search(r'unresolved external symbol "[^"]*" \((\S+)\)', l) or re.search(r'unresolved external symbol (\S+)', l)
              or re.search(r'"[^"]*" \((\S+)\) already defined', l) or re.search(r'(\S+) already defined', l))
        sym = sm.group(1) if sm else ''
        linhas.append((m.group(1), sym, quem, l.strip()[:300]))
    with open(OUT + '/avisos.tsv', 'w') as f:
        f.write('codigo\tsimbolo\tquem\tlinha\n')
        for x in linhas: f.write('\t'.join(x) + '\n')
    ok = os.path.exists(EXE) and os.path.getmtime(EXE) >= t - 1
    dup = set(sym for c, sym, _, _ in linhas if c in ('LNK2005', 'LNK4006'))
    if stubs and DUP_OK and ok and (dup - DUP_OK):
        os.remove(EXE); ok = False
        print('linkprova: LNK2005 fora do V6_DUP_OK: ' + ' '.join(sorted(dup - DUP_OK)))
    # .CRT$XCU pela .map (ordem do link = ordem dos inicializadores estáticos)
    xcu = []
    mp = EXE[:-4] + '.map'
    if ok and os.path.exists(mp):
        for l in open(mp, encoding='latin1'):
            c = l.split()
            if len(c) >= 4 and c[1].startswith('??__E') and c[-1].endswith('.obj'):
                xcu.append((c[0], c[1], c[-1]))
    # a .map não lista as entradas da .CRT$XCU por símbolo: contamos os ??__E (inicializadores dinâmicos) por .obj
    por = collections.OrderedDict()
    for _, s, o in xcu: por[o] = por.get(o, 0) + 1
    with open(OUT + '/xcu.tsv', 'w') as f:
        f.write('ordem\tobj\tinicializadores\n')
        for i, (o, n) in enumerate(por.items()): f.write('%d\t%s\t%d\n' % (i + 1, o, n))
    imp_n = imports(EXE) if ok else collections.Counter()
    imp_9 = imports(R + '/ref/ProjectG_983_dump.exe')
    # função a função (pelo leitor de PE: nomes e ordinais), para o impusers.py
    from pe import PE
    fn = lambda e: {(d_, n_) for d_, n_ in PE(e).imports()}
    if ok:
        a9, an = fn(R + '/ref/ProjectG_983_dump.exe'), fn(EXE)
        for nome, conj in (('imports_so_983.tsv', a9 - an), ('imports_so_nosso.tsv', an - a9)):
            with open(OUT + '/' + nome, 'w') as f:
                for d_, n_ in sorted(conj): f.write('%s\t%s\n' % (d_, n_))
        if not stubs: subprocess.run([sys.executable, R + '/tools/v6/impusers.py'])
    with open(OUT + '/imports.tsv', 'w') as f:
        f.write('dll\tnosso\t983\n')
        for d in sorted(set(imp_n) | set(imp_9)): f.write('%s\t%d\t%d\n' % (d, imp_n[d], imp_9[d]))
    # seções do exe
    sec = ''
    if ok:
        q = subprocess.run([R + '/tools/vs.sh', 'dumpbin', '/headers', EXE], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        h = q.stdout.decode('latin1').replace('\r', '')
        sec = ', '.join('%s 0x%s' % (n, v) for n, v in re.findall(r'SECTION HEADER #\d+\n\s*(\S+) name\n\s*([0-9A-F]+) virtual size', h))
    unres = sorted({s for c, s, _, _ in linhas if c in ('LNK2001', 'LNK2019') and s})
    # cruzamento com o out/V6/link/falta.tsv (a previsão do `make v6-link`)
    prev = {}
    for l in open(f4cfg.V6 + '/falta.tsv', encoding='utf-8'):
        c = l.rstrip('\n').split('\t')
        if len(c) > 4 and c[0] != 'simbolo': prev[c[0]] = c
    quem = collections.defaultdict(set)
    for c, s_, q, _ in linhas:
        if c in ('LNK2001', 'LNK2019') and s_: quem[s_].add(q)
    with open(OUT + '/nao_resolvidos.tsv', 'w') as f:
        f.write('simbolo\tprevisto_v6link\tfrentes\tva983\tquem_cita\n')
        for s_ in unres:
            c = prev.get(s_)
            f.write('%s\t%s\t%s\t%s\t%s\n' % (s_, 'sim' if c else 'NAO', c[2] if c else '-', c[4] if c else '-', ' '.join(sorted(quem[s_]))))
    novos = [s_ for s_ in unres if s_ not in prev]
    nao_vieram = [s_ for s_ in prev if s_ not in set(unres)]
    from pe import recursos
    r9 = {(t, i, l): n for t, i, l, n in recursos(PE(R + '/ref/ProjectG_983_dump.exe'))}
    rn = {(t, i, l): n for t, i, l, n in recursos(PE(EXE))} if ok else {}
    with open(OUT + '/recursos.tsv', 'w') as f:
        f.write('tipo\tid\tlingua\tbytes_nosso\tbytes_983\n')
        for k in sorted(set(r9) | set(rn), key=str): f.write('%s\t%s\t%s\t%s\t%s\n' % (k + (rn.get(k, '-'), r9.get(k, '-'))))
    with open(OUT + '/resumo.txt', 'w') as f:
        w = lambda s='': f.write(s + '\n')
        w(('make exe: link com os stubs e o ggc_wrapper.obj sem GameGuard (sem /FORCE)' if exe else 'link com os stubs (sem /FORCE)' if stubs else 'link de prova (/FORCE)') + ' em %.0f s; código de saída do link.exe: %d; exe gerado: %s' % (dt, p.returncode,
          ('sim, %d bytes' % os.path.getsize(EXE)) if ok else 'NÃO'))
        w('.obj: %d (%s); .lib: %d%s' % (len(ob), ', '.join('%s %d' % kv for kv in sorted(collections.Counter(a for a, _ in ob).items())),
          len(libs), (' (faltam: ' + ', '.join(os.path.basename(x) for x in falta_lib) + ')') if falta_lib else ''))
        w('opções: ' + ' '.join(flags))
        if stubs and DUP_OK: w('V6_DUP_OK (duplicatas aceitas com /FORCE:MULTIPLE): ' + ' '.join(sorted(DUP_OK)) + '; LNK2005 no link: ' + (' '.join(sorted(dup)) or 'nenhuma'))
        w('avisos/erros por código: ' + (', '.join('%s %d' % kv for kv in sorted(cod.items())) or 'nenhum'))
        w('símbolos não resolvidos distintos (LNK2001/LNK2019): %d' % len(unres))
        w('  previstos pelo make v6-link: %d de %d; só no link (o v6-link não viu): %d; previstos que o link resolveu: %d'
          % (len(unres) - len(novos), len(prev), len(novos), len(nao_vieram)))
        for s_ in novos[:40]: w('    só no link: %s (%s)' % (s_, ' '.join(sorted(quem[s_]))[:120]))
        for s_ in nao_vieram[:40]: w('    resolvido no link: %s' % s_)
        w('inicializadores dinâmicos (??__E): %d em %d .obj (ordem do link em xcu.tsv)' % (len(xcu), len(por)))
        if sec: w('seções: ' + sec)
        w('recursos (tipo/id/língua: bytes nosso × 983): ' + '; '.join('%s/%s/%s: %s×%s' % (k + (rn.get(k, '-'), r9.get(k, '-')))
          for k in sorted(set(r9) | set(rn), key=str)))
        w('imports (dll: nosso / 983):')
        for d in sorted(set(imp_n) | set(imp_9)):
            mark = '' if (imp_n[d] > 0) == (imp_9[d] > 0) else ('  <- só no nosso' if imp_n[d] else '  <- só no 983')
            w('  %-16s %4d / %4d%s' % (d, imp_n[d], imp_9[d], mark))
    if ok and not stubs:
        q = subprocess.run([sys.executable, R + '/tools/v6/xcu983.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        with open(OUT + '/resumo.txt', 'a') as f:
            f.write('inicializadores estáticos (.CRT$XCU, tools/v6/xcu983.py):\n' + ''.join('  ' + l + '\n' for l in q.stdout.decode().splitlines()))
    print(open(OUT + '/resumo.txt').read())
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
