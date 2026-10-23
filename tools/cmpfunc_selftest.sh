#!/bin/bash
# Autoteste do tools/cmpfunc (rodar depois de mexer nele). Usa a device do 645 (/root/rebang, só leitura) como
# corpus: compila 8 .cpp + bitmap, linka numa dll (build/f03/self.dll) e compara cada .obj com ela.
#  1) com o .map do linker como mapa: toda função presente na dll tem de dar IGUAL (0 QUASE, 0 DIFERENTE);
#  2) sem mapa: nenhum endereço achado pode divergir do .map;
#  3) negativo: bitmap.cpp com 3 funções alteradas -> exatamente essas 3 deixam de ser IGUAL (+ Save, que já difere);
#  4) negativo: literais do wd3d8.obj com 1 bit trocado -> funções que os usam caem para QUASE (alvo:literal).
# Saída em out/F0.3/. Código de saída 0 = passou.
set -e
R=$(cd "$(dirname "$0")/.." && pwd); cd "$R"
S=${REBANG:-/root/rebang}; VS=${VS:-/root/kr839/local/vs2010}; B=$R/build/f03; O=$R/out/F0.3
mkdir -p $B/neg $O
CF="/nologo /c /MD /W3 /EHsc /Z7 /O2 /Ob1 /Gr /GS /Oy- /DNDEBUG /DWIN32 /D_WINDOWS /D_MBCS /DWANGREAL_DEVICE"
INC="/I$S/source/rebang /I$VS/VC10/include /I$VS/compat /I$S/tools/PlatformSDK-Aug2002/include /I$S/tools/DirectX9/include /I$S/source/client/Wangreal/include /I$S/source/client/device"
if [ ! -f $B/self.dll ] || [ "$1" = rebuild ]; then
  for f in client/device/wd3d client/device/wd3d8 client/device/wdinput/directinput client/device/wdinput/dikeyboard \
           client/device/wdinput/dimouse client/device/wime/wime client/device/device client/Wangreal/source/wdxtc \
           client/Wangreal/source/bitmap; do
    b=$(basename $f); tools/vs.sh cl $CF $INC /Fo$B/$b.obj $S/source/$f.cpp > $B/$b.log 2>&1 || { echo "FALHOU $b"; exit 1; }
  done
  L=$S/tools
  (cd $B && $R/tools/vs.sh link /NOLOGO /DLL /SUBSYSTEM:WINDOWS /MACHINE:X86 /BASE:0x10000000 /INCREMENTAL:NO /OPT:REF /OPT:ICF \
    /NODEFAULTLIB /DEF:$S/source/client/device/device.def /OUT:$B/self.dll /MAP:$B/self.map *.obj \
    $L/DirectX9/lib/d3dx9.lib $L/DirectX9/lib/d3d9.lib $L/DirectX9/lib/dxguid.lib $L/DirectX9/lib/dinput8.lib $VS/sdklib/kernel32.lib \
    $L/PlatformSDK-Aug2002/lib/imm32.lib $L/PlatformSDK-Aug2002/lib/winmm.lib $L/PlatformSDK-Aug2002/lib/user32.lib \
    $L/PlatformSDK-Aug2002/lib/gdi32.lib $VS/VC10/lib/msvcprt.lib $VS/VC10/lib/msvcrt.lib $VS/VC10/lib/oldnames.lib > link.log 2>&1) \
    || { tail $B/link.log; exit 1; }
fi
python3 - $B/self.map $B/self.tsv <<'P'
import re, sys
rx = re.compile(r'^\s*[0-9a-f]{4}:[0-9a-f]{8}\s+(\S+)\s+([0-9a-f]{8})\s+(f\s+i?|\s+)\s*(\S+)\s*$')
with open(sys.argv[2], 'w') as o:
    for l in open(sys.argv[1], errors='replace'):
        m = rx.match(l.rstrip('\r\n'))
        if m and int(m.group(2), 16) >= 0x10001000 and m.group(4).endswith('.obj'):
            o.write('%s\t%s\n' % (m.group(1), m.group(2)))
P
OBJS=$(ls $B/*.obj)
tools/cmpfunc $OBJS --ref $B/self.dll --map $B/self.tsv --inline --out $O/autoteste > /dev/null
tools/cmpfunc $OBJS --ref $B/self.dll --map /nonexistent --inline --out $O/autoteste_semmapa > /dev/null
# negativos
sed -e '137s/255/254/' -e '273s/ReleaseDC(hwnd, hdc)/DeleteDC(hdc)/' -e '152s/{/{ if (i == 7) continue;/' \
  $S/source/client/Wangreal/source/bitmap.cpp > $B/neg/bitmap_neg.cpp
tools/vs.sh cl $CF $INC /Fo$B/neg/bitmap_neg.obj $B/neg/bitmap_neg.cpp > $B/neg/bitmap_neg.log 2>&1
rm -f $B/neg/map.tsv
tools/cmpfunc $B/bitmap.obj --map $B/neg/map.tsv --update-map > /dev/null
tools/cmpfunc $B/neg/bitmap_neg.obj --map $B/neg/map.tsv --out $O/negativo > /dev/null
python3 - $B/wd3d8.obj $B/neg/wd3d8_lit.obj <<'P'
import struct, sys
d = bytearray(open(sys.argv[1], 'rb').read())
mach, nsec, _, symoff, nsym, opt, _ = struct.unpack_from('<HHIIIHH', d, 0)
stroff = symoff + nsym * 18
i = 0
while i < nsym:
    raw, val, sec, typ, cls, naux = struct.unpack_from('<8sIhHBB', d, symoff + i * 18)
    if raw[:4] == b'\0\0\0\0':
        o = stroff + struct.unpack_from('<I', raw, 4)[0]
        if d[o:o + 5] == b'??_C@' and sec > 0:
            d[struct.unpack_from('<I', d, 20 + (sec - 1) * 40 + 20)[0] + val] ^= 1
    i += 1 + naux
open(sys.argv[2], 'wb').write(d)
P
tools/cmpfunc $B/neg/wd3d8_lit.obj --ref $B/self.dll --map $B/self.tsv --inline --out $O/negativo_literal > /dev/null
python3 - $B/self.tsv $O <<'P'
import csv, sys, collections
m = dict(l.rstrip('\n').split('\t') for l in open(sys.argv[1])); O = sys.argv[2]
rd = lambda d: list(csv.DictReader(open('%s/%s/funcs.tsv' % (O, d)), delimiter='\t', quoting=csv.QUOTE_NONE))
ok = True
def chk(name, cond, txt):
    global ok
    ok &= bool(cond); print('%-4s %s: %s' % ('OK' if cond else 'ERRO', name, txt))
c = collections.Counter(r['classe'] for r in rd('autoteste'))
chk('1 autoteste com mapa', c['QUASE'] == 0 and c['DIFERENTE'] == 0 and c['IGUAL'] > 1000, dict(c))
c = collections.Counter()
for r in rd('autoteste_semmapa'):
    if r['funcao'] in m:
        c['certo' if r['va983'] == m[r['funcao']] else 'indeterminado' if r['va983'] == '-' else 'ERRADO'] += 1
    if r['classe'] in ('QUASE', 'DIFERENTE'): c['falsa diferença'] += 1
chk('2 autoteste sem mapa', c['ERRADO'] == 0 and c['falsa diferença'] == 0 and c['certo'] > 800, dict(c))
bad = sorted(r['funcao'].split('@')[0] + ':' + r['classe'] for r in rd('negativo') if r['classe'] != 'IGUAL')
chk('3 negativo (fonte alterado)', bad == ['?GetAlpha:QUASE', '?PaintStretch:QUASE', '?Save:DIFERENTE', '?SetPalette:DIFERENTE'], bad)
n = [r for r in rd('negativo_literal') if r['classe'] == 'QUASE']
chk('4 negativo (literais)', len(n) > 50 and all('alvo:literal' in r['nota'] for r in n), '%d funções rebaixadas para QUASE' % len(n))
print('AUTOTESTE', 'PASSOU' if ok else 'FALHOU'); sys.exit(0 if ok else 1)
P
