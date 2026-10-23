#!/usr/bin/env python3
"""F3.2: compila as unidades do ProjectG.exe (fontes em src/, vindos do rebang) com o VS2010 sob Wine.

  pgbuild.py list                      unidades e configuração (de /root/rebang/build-projectg.json, só leitura)
  pgbuild.py pch                       compila os .pch (build/pg/pch)
  pgbuild.py obj [-j N] [filtro...]    compila as unidades (build/pg/obj/<caminho>.obj; log ao lado); resumo em --out
  pgbuild.py cmp [-j N] [filtro...]    cmpfunc de cada .obj contra o exe 983 -> <out>/cmp/<unidade>/ e <out>/base.tsv
Opções: --out DIR (padrão out/pg-base)  --flags "..." (troca as flags de otimização, para variantes)  --tag NOME (build/pg-NOME)
"""
import os, sys, json, subprocess, argparse, collections, concurrent.futures as cf
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RB = '/root/rebang'; VS = os.environ.get('VS', '/root/kr839/local/vs2010')
# Flags do exe 983: ver out/F3.2/variantes.txt. /Zm200 e /DREBANG_SEMANTIC_ONLY (versão em C das funções que o rebang
# tem em `naked` para igualar o VC7.1) são deste build.
OPT = '/MD /W3 /EHsc /Z7 /O2 /Ob1 /GF- /Gr /GS /Oy-'
# A352: /DJP983_POSTEFFECT = pos-efeito do 983 (CPostEffect983: HDR/DOF/FXAA) no CTask::Display; a351-1 sem queda, 32 alvos fp16 = original
DEFS = '/DNDEBUG /DWIN32 /D_WINDOWS /D_MBCS /Zm200 /DREBANG_SEMANTIC_ONLY /DJP983_POSTEFFECT'
INC = ['include', 'include/engine', 'src/engine/lib/freetype-2.2.1/include', 'src/fresh/include',
       'src/projectg', 'src/shared/thirties', VS + '/VC10/include', VS + '/compat', 'build/atl71', RB + '/tools/WTL75/include',
       RB + '/tools/PlatformSDK-Aug2002/include', RB + '/tools/DirectX9/include']
MAP = [('source/client/ProjectG/', 'src/projectg/'), ('source/client/Fresh/', 'src/fresh/'),
       ('source/client/Wangreal/source/', 'src/engine/'), ('source/client/Wangreal/include/', 'include/engine/'),
       ('source/shared/', 'src/shared/')]
def here(p):
    for a, b in MAP:
        if (p + '/').startswith(a): return (b + (p + '/')[len(a):]).rstrip('/')
    return p if p.startswith('/') else RB + '/' + p

# Unidades do 645 que o 983 não tem: ficam fora do build do exe (o fonte continua em src/ só para consulta).
# tutorialtask.cpp — o 983 não tem CTutorialTask (sem RTTI/nome/fábrica; s125); o último uso compilado
# (IS_EXACTKINDOF no caso 0xce do CTaskMain::HandleMsgCommon) saiu na s127 e o da taskmanager.cpp no C-PKT lote 54.
# fxinterpreter.cpp — o FxInterpreter do 983 é a unidade da B (src/projectg/jp/fxinterpreter.cpp); a da A (layout do 645) dava
# LNK2005/ODR no link (pedido C64.2, s131); fxinterpreter.h agora inclui o jp/fxinterpreter983.h.
FORA_983 = {'src/projectg/tutorialtask.cpp', 'src/projectg/fxinterpreter.cpp'}
# Unidades que o 983 liga no exe e o 645 não tinha: (unidade aqui, depois de qual unidade na ordem de link).
# langtable.cpp — o exe 983 tem cópia própria (WLangTable: Find 00b4df40, ctor 00b4e6b0, Load 00b4e980,
# K2L_Compatibility 00b4ec60, entre wmath e wboneset); o fonte é o da wangreal.dll (src/wangreal, frente W). Pedido C64.1.
# wxshadermtl.cpp — o exe 983 tem a unidade inteira do material de shader (00bb1be0–00bb83d0, entre wtextureview e bitmap;
# s150): mesmo fonte da dll (src/engine, frente W). O .pet do 983 cria os materiais (WPuppet +0x1fc).
# itemcursor983.cpp — unidade própria do cursor de artefatos no 983 (00478cc2-0047a060; A594: no changeroominfodlg.cpp
# o ~FrChangeRoomInfoDlg perdia o frame de exceção).
# lua983_ltable/lua983_lapi.cpp — ltable.c/lapi.c do Lua com o lua_number2int do 983 (fld/fistp; A222), no lugar dos membros
# da lua51_Release_MD_fastcall.lib do rebang (truque da soma, errado com a FPU em _PC_24).
EXTRA_983 = [('src/wangreal/langtable.cpp', 'src/engine/wmath.cpp'), ('src/engine/wxshadermtl.cpp', 'src/engine/w3danispr.cpp'),
             ('src/shared/LuaSystem/lua983_ltable.cpp', 'src/shared/LuaSystem/lua_tinker/lua_tinker.cpp'),
             ('src/shared/LuaSystem/lua983_lapi.cpp', 'src/shared/LuaSystem/lua983_ltable.cpp'),
             ('src/projectg/itemcursor983.cpp', 'src/projectg/changeroominfodlg.cpp')]

def units():
    """[(unidade aqui, unidade no rebang, pch aqui|None, [/FI...], [includes extras])] na ordem de link do rebang"""
    d = json.load(open(RB + '/build-projectg.json')); out = []
    def add(e, inherit):
        if isinstance(e, str): e = {'path': e}
        p = e['path']
        if not p.endswith(('.cpp',)) or here(p) in FORA_983: return
        ef = [f for f in e.get('extra_flags', []) if f.startswith('/FI')]
        out.append((here(p), p, here(e['pch']) if e.get('pch') else None, ef, [here(i) for i in e.get('includes', [])]))
    for e in d['inputs']:
        if isinstance(e, dict) and 'library' in e:
            if 'Fresh_ReleaseQA' in e['library']:
                for m in e['members']: add(m, e)
        else: add(e, None)
    for u, depois in EXTRA_983:
        i = [x[0] for x in out].index(depois)
        out.insert(i + 1, (u, u, None, [], []))
    return out

def pchs(us):
    return sorted({u[2] for u in us if u[2]})

def cl(args, log):
    env = dict(os.environ, VS=VS)
    p = subprocess.run([ROOT + '/tools/vs.sh', 'cl', '/nologo', '/c'] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=ROOT, env=env)
    open(log, 'wb').write(p.stdout)
    return p.returncode

def absp(p): return p if p.startswith('/') else ROOT + '/' + p
# F3.5 (sessão 38): a biblioteca Fresh do 983 é /Ob2 (29 unidades: IGUAL 378 com /Ob1 × 436 com /Ob2; a engine e o
# ProjectG seguem /Ob1 — out/F3.5/s38/ob2_fresh.txt).
def opt_for(src): return OPT.replace('/Ob1', '/Ob2') if src.startswith('src/fresh/') else OPT
def base_args(a, extra_inc=(), src=''):
    return (a.flags or opt_for(src)).split() + DEFS.split() + ['/I' + absp(i) for i in list(extra_inc) + INC]
def pch_file(a, src): return '%s/pch/%s.pch' % (a.B, src[:-4].replace('/', '_'))

def do_pch(a, src):
    out = pch_file(a, src); os.makedirs(os.path.dirname(out), exist_ok=True)
    h = os.path.basename(src)[:-4] + '.h'
    rc = cl(base_args(a, src=src) + ['/Yc' + h, '/Fp' + out, '/Fo' + out[:-4] + '.obj', absp(src)], out[:-4] + '.log')
    return src, rc

def do_obj(a, u):
    src, rb, pch, fi, einc = u
    obj = '%s/obj/%s.obj' % (a.B, src[:-4]); os.makedirs(os.path.dirname(obj), exist_ok=True)
    args = base_args(a, einc, src) + fi
    if pch: args += ['/Yu' + os.path.basename(pch)[:-4] + '.h', '/Fp' + pch_file(a, pch)]
    # em dia = mais novo que a fonte E que o pch (cabeçalho mudado refaz o pch; sem isso o .obj velho era reaproveitado)
    new = os.path.exists(obj) and os.path.getmtime(obj) > os.path.getmtime(absp(src))
    # (s47) pch que falhou/não existe: o .obj velho NÃO está em dia (antes passava como bom e a linha de base saía com objs velhos)
    if new and pch: new = os.path.exists(pch_file(a, pch)) and os.path.getmtime(obj) > os.path.getmtime(pch_file(a, pch))
    if new and not a.force: return src, 0
    rc = cl(args + ['/Fo' + obj, absp(src)], obj[:-4] + '.log')
    if rc and os.path.exists(obj): os.remove(obj)
    return src, rc

def do_cmp(a, u):
    src = u[0]; obj = '%s/obj/%s.obj' % (a.B, src[:-4])
    if not os.path.exists(obj): return src, None
    od = '%s/cmp/%s' % (a.out, src[:-4].replace('/', '_'))
    cmd = [ROOT + '/tools/cmpfunc', obj, '--no-build', '--ref', ROOT + '/ref/ProjectG_983_dump.exe', '--map', a.map,
           '--funcs', ROOT + '/map/projectg_funcs.tsv', '--out', od] + (['--seed', a.seed] if a.seed else [])
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=ROOT)
    return src, (p.returncode, od, p.stdout[-400:] if p.returncode else '')

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd'); ap.add_argument('filt', nargs='*'); ap.add_argument('-j', type=int, default=8)
    ap.add_argument('--out', default='out/pg-base'); ap.add_argument('--flags'); ap.add_argument('--tag'); ap.add_argument('--force', action='store_true')
    ap.add_argument('--map', default=ROOT + '/map/projectg.tsv'); ap.add_argument('--seed', default=ROOT + '/map/projectg_seed.tsv')
    a = ap.parse_args(); a.B = ROOT + '/build/pg' + ('-' + a.tag if a.tag else ''); a.out = absp(a.out)
    if a.seed and not os.path.exists(a.seed): a.seed = None
    us = units()
    if a.filt: us = [u for u in us if any(f in u[0] for f in a.filt)]
    if a.cmd == 'list':
        for u in us: print('\t'.join([u[0], u[1], u[2] or '-', ' '.join(u[3]) or '-', ' '.join(u[4]) or '-']))
        return
    os.makedirs(a.out, exist_ok=True)
    with cf.ThreadPoolExecutor(a.j) as ex:
        if a.cmd == 'pch':
            bad = 0
            for src, rc in ex.map(lambda s: do_pch(a, s), pchs(units())):
                print('pch  %-45s %s' % (src, 'ok' if rc == 0 else 'FALHOU')); bad += rc != 0
            sys.exit(1 if bad else 0)
        if a.cmd == 'obj':
            res = list(ex.map(lambda u: do_obj(a, u), us))
            ok = [s for s, rc in res if rc == 0]; bad = [s for s, rc in res if rc != 0]
            with open(a.out + '/compila.tsv', 'w') as f:
                f.write('unidade\tcompila\tprimeiro_erro\n')
                for s, rc in res:
                    err = ''
                    if rc:
                        lg = open('%s/obj/%s.log' % (a.B, s[:-4]), errors='replace').read().split('\n')
                        err = next((l.strip() for l in lg if ' error ' in l), lg[-2] if len(lg) > 1 else '')[:300]
                    f.write('%s\t%s\t%s\n' % (s, 'sim' if rc == 0 else 'nao', err))
            print('compilam %d de %d; falham %d -> %s/compila.tsv' % (len(ok), len(res), len(bad), a.out))
        if a.cmd == 'cmp':
            CL = ('IGUAL', 'QUASE', 'DIFERENTE', 'SEM_PAR'); tot = collections.Counter(); totb = collections.Counter(); rows = []
            for src, r in ex.map(lambda u: do_cmp(a, u), us):
                if r is None: rows.append((src, 'nao_compila') + ('',) * 9); continue
                if r[0]: rows.append((src, 'cmp_falhou') + ('',) * 9); print('cmp falhou', src, r[2]); continue
                c = collections.Counter(); b = collections.Counter(); wi = [0.0, 0]
                for l in open(r[1] + '/funcs.tsv').read().split('\n')[1:]:
                    p = l.split('\t')
                    if len(p) > 9 and p[2] == '1':
                        c[p[3]] += 1; b[p[3]] += int(p[9]); wi[0] += float(p[4]) * int(p[7]); wi[1] += int(p[7])
                tot.update(c); totb.update(b)
                rows.append((src, 'ok', sum(c[k] for k in CL)) + tuple(c[k] for k in CL) + tuple(b[k] for k in CL) + ('%.1f' % (100 * wi[0] / max(wi[1], 1)),))
            with open(a.out + '/base.tsv', 'w') as f:
                f.write('unidade\testado\tproprias\tIGUAL\tQUASE\tDIFERENTE\tSEM_PAR\tB_IGUAL\tB_QUASE\tB_DIFERENTE\tB_SEM_PAR\tpct_instr\n')
                for r in rows: f.write('\t'.join(map(str, r)) + '\n')
            n = sum(tot[k] for k in CL); nb = sum(totb[k] for k in CL)
            s = 'pg-base: %d unidades comparadas, %d funções próprias (%d B): ' % (sum(1 for r in rows if r[1] == 'ok'), n, nb) + \
                '; '.join('%s %d (%.1f%% das funções, %d B = %.1f%%)' % (k, tot[k], 100 * tot[k] / max(n, 1), totb[k], 100 * totb[k] / max(nb, 1)) for k in CL)
            open(a.out + '/base_resumo.txt', 'w').write(s + '\n'); print(s)

if __name__ == '__main__':
    main()
