#!/usr/bin/env python3
"""C103: jp983_rastro() antes de TODO `g_bQuit = true;` (quem fecha o jogo), em cópias, sem editar os arquivos da A/B.

Uso: python3 tools/v6/f4rastro/quit_rastro.py TAG_PCH_A TAG_SAIDA_A DIR_BOBJ_ORIGEM DIR_BOBJ_SAIDA
  - unidades da A: versão da revisão troca_a.REV (a mesma da build TAG_PCH_A) -> build/TAG_SAIDA_A/obj/<unidade>.obj
    (unidades que o troca_a.py já troca ficam de fora: lá o golfbg/projectg/mainframe têm o rastro C103);
  - unidades jp/ (B): fonte atual -> cópia de DIR_BOBJ_ORIGEM em DIR_BOBJ_SAIDA com as instrumentadas trocadas.
  TAG_PCH_A = '-': só as unidades jp/ (C103: a build da A sai de um worktree com o rastro já na fonte).
  Depois: make exe ... V6_PG="TAG_SAIDA_A <saída do troca_a> TAG_PCH_A" V6_BOBJ=DIR_BOBJ_SAIDA
"""
import os, re, sys, shutil, subprocess
ROOT = '/root/jp983src'
sys.path.insert(0, ROOT + '/tools/f32')
import pgbuild as P

REV = 'aa0f33dc'  # = troca_a.REV
DECL = 'extern "C" void __cdecl jp983_rastro(const char* fmt, ...);\n'
PAD = re.compile(r'\bg_bQuit\s*=\s*(true|1)\s*;')
# rflobbydesktop atual define o CheckLobbyHotKeys983 (stub no bobj-c102) e cai no AV do A173.4 (c103-2): fica a versão de DIR_BOBJ_ORIGEM
FORA = {'src/projectg/jp/rflobbydesktop.cpp'}
JA = {'src/projectg/golfbg.cpp', 'src/projectg/projectg.cpp', 'src/projectg/mainframe.cpp', 'src/projectg/lobbymain.cpp'}


def instr(txt):
    n = [0]
    def f(m):
        n[0] += 1
        return '{ jp983_rastro("C103 g_bQuit %s:%d", __FILE__, __LINE__); ' + m.group(0) + ' }'
    return DECL + PAD.sub(f, txt), n[0]


def main():
    tag_pch, tag_out, bsrc, bout = sys.argv[1:5]
    arqs = subprocess.check_output(['git', '-C', ROOT, 'grep', '-lE', r'g_bQuit\s*=\s*(true|1)\s*;', REV, '--',
                                    'src/projectg/*.cpp']).decode().split()
    arqs = sorted({a.split(':', 1)[1] for a in arqs})
    units = {u[0]: u for u in P.units()}
    class A: pass
    a = A(); a.flags = None; a.B = ROOT + '/build/' + tag_pch
    if os.path.exists(bout):
        shutil.rmtree(bout)
    shutil.copytree(bsrc, bout)
    ok = True
    for src in arqs:
        jp = src.startswith('src/projectg/jp/')
        if src in JA or src in FORA or (not jp and (src not in units or tag_pch == '-')):  # '-' = só jp/
            continue
        txt = open(ROOT + '/' + src, encoding='latin-1').read() if jp else \
            subprocess.check_output(['git', '-C', ROOT, 'show', REV + ':' + src]).decode('latin-1')
        txt, n = instr(txt)
        cp = '%s/build/%s/quit_src/%s' % (ROOT, tag_out, src)
        os.makedirs(os.path.dirname(cp), exist_ok=True)
        open(cp, 'w', encoding='latin-1').write(txt)
        if jp:
            obj = '%s/%s.obj' % (bout, os.path.basename(src)[:-4])
            args = P.OPT.split() + P.DEFS.split() + ['/I' + P.absp(i) for i in ['include/jp', 'src/projectg/jp'] + P.INC] + \
                ['/I' + ROOT + '/' + os.path.dirname(src), '/FIstdafx.h']
        else:
            _, _, pch, fi, einc = units[src]
            args = P.base_args(a, einc, src) + fi + ['/I' + ROOT + '/' + os.path.dirname(src)]
            if pch: args += ['/Yu' + os.path.basename(pch)[:-4] + '.h', '/Fp' + P.pch_file(a, pch)]
            obj = '%s/build/%s/obj/%s.obj' % (ROOT, tag_out, src[:-4])
        os.makedirs(os.path.dirname(obj), exist_ok=True)
        if os.path.exists(obj):
            os.unlink(obj)
        rc = P.cl(args + ['/Fo' + obj, cp], obj[:-4] + '.log')
        print(src, n, 'rc=%d' % rc, '' if rc == 0 else open(obj[:-4] + '.log', errors='replace').read()[-600:])
        ok = ok and rc == 0
    sys.exit(0 if ok else 1)

main()
