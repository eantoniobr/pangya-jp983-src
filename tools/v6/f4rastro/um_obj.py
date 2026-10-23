#!/usr/bin/env python3
"""C96: compila unidades do jeito do pgbuild (pch da TAG_PCH) para build/TAG_SAIDA/obj/<unidade>.obj, sem cópia.

Uso: python3 tools/v6/f4rastro/um_obj.py TAG_PCH TAG_SAIDA unidade [...]   (ex.: pg-a169 pg-c96 src/projectg/inputmanager.cpp)
Para testar com o robô uma correção da C num arquivo da A antes da A recompilar: make exe com V6_PG="TAG_SAIDA TAG_PCH".
"""
import os, sys
ROOT = '/root/jp983src'
sys.path.insert(0, ROOT + '/tools/f32')
import pgbuild as P


def main():
    tag_pch, tag_out = sys.argv[1], sys.argv[2]
    units = {u[0]: u for u in P.units()}
    class A: pass
    a = A(); a.flags = None; a.B = ROOT + '/build/' + tag_pch
    ok = True
    for src in sys.argv[3:]:
        _, _, pch, fi, einc = units[src]
        args = P.base_args(a, einc, src) + fi + ['/I' + ROOT + '/' + os.path.dirname(src)]
        if pch: args += ['/Yu' + os.path.basename(pch)[:-4] + '.h', '/Fp' + P.pch_file(a, pch)]
        obj = '%s/build/%s/obj/%s.obj' % (ROOT, tag_out, src[:-4])
        os.makedirs(os.path.dirname(obj), exist_ok=True)
        rc = P.cl(args + ['/Fo' + obj, ROOT + '/' + src], obj[:-4] + '.log')
        print(src, 'rc=%d' % rc, obj if rc == 0 else open(obj[:-4] + '.log', errors='replace').read()[-800:])
        ok = ok and rc == 0
    sys.exit(0 if ok else 1)

main()
