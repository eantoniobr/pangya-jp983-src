#!/usr/bin/env python3
"""F4 (frente C, C-F4.3): zlib e libpng recompiladas com o VS2010 (cl 16, /MD -> msvcr100.dll, como o 983).

As .lib do rebang (source/client/Fresh/lib/{zlib,libpng}.lib) são do VC7.1 e a libpng cita `__iob` (o FILE[] do msvcr71),
que o msvcr100 não exporta com esse nome -> 1 não resolvido no link (out/F4/link/nao_resolvidos.tsv). Compilamos as mesmas
fontes do rebang (libpng 1.2.8 = a do 983; zlib 1.2.2 — o 983 tem a 1.2.6, mesma API) com as opções do exe: /Gr (fastcall
por padrão: o rebang também; os nomes ficam iguais, ex. `@inflate@8`, `_png_create_read_struct`), /O2 /MD.
Mesmos membros das .lib do rebang (lib /list). Saída: build/C/f4/terc/{zlib,libpng}.lib (+ .log).
Uso: make f4-terc  (= python3 tools/v6/terc.py; ~20 s)
"""
import os, sys, subprocess, glob
R = '/root/jp983src'
VS = os.environ.get('VS', '/root/kr839/local/vs2010')
TP = '/root/rebang/source/client/Fresh/third_party'
B = R + '/build/C/f4/terc'
OPT = ['/nologo', '/c', '/MD', '/O2', '/Gr', '/GS', '/W0', '/DNDEBUG', '/DWIN32', '/D_WINDOWS', '/D_CRT_SECURE_NO_WARNINGS',
       '/I' + VS + '/VC10/include', '/I' + VS + '/compat', '/I/root/rebang/tools/PlatformSDK-Aug2002/include']
LIBS = {
    'zlib': (TP + '/zlib-1.2.2', 'adler32 compress crc32 deflate gzio infback inffast inflate inftrees trees uncompr zutil'),
    'libpng': (TP + '/libpng-1.2.8', 'png pngerror pngget pngmem pngpread pngread pngrio pngrtran pngrutil pngset pngtrans '
                                     'pngwio pngwrite pngwtran pngwutil'),
}


def vs(*a):
    p = subprocess.run([R + '/tools/vs.sh'] + list(a), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=dict(os.environ, VS=VS))
    return p.returncode, p.stdout.decode('latin1').replace('\r', '')


def main():
    ok = True
    for nome, (src, us) in LIBS.items():
        od = '%s/%s' % (B, nome); os.makedirs(od, exist_ok=True)
        for f in glob.glob(od + '/*.obj'): os.remove(f)
        fontes = ['%s/%s.c' % (src, u) for u in us.split()]
        rc, log = vs('cl', *OPT, '/I' + TP + '/zlib-1.2.2', '/Fo' + od + '/', *fontes)
        objs = ['%s/%s.obj' % (od, u) for u in us.split()]
        falta = [o for o in objs if not os.path.exists(o)]
        if not falta:
            rc2, log2 = vs('lib', '/nologo', '/OUT:%s/%s.lib' % (B, nome), *objs); log += log2; rc = rc or rc2
        open('%s/%s.log' % (B, nome), 'w').write(log)
        okn = rc == 0 and not falta and os.path.exists('%s/%s.lib' % (B, nome))
        print('%-7s %s: %d fontes, %d .obj%s' % (nome, 'ok' if okn else 'ERRO', len(fontes), len(objs) - len(falta),
              '' if okn else ' (ver %s/%s.log)' % (os.path.relpath(B, R), nome)))
        ok &= okn
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
