#!/usr/bin/env python3
"""campos645.py Classe [cabeçalho_do_rebang] — deslocamento de cada campo (m_*, unk*) da classe NO LAYOUT DO KR 645: compila um
probe de offsetof com o cl do VC7.1 do rebang (só leitura: /root/rebang/tools/VC7.1, cabeçalhos de /root/rebang/source) sob o
prefixo Wine do nosso VS2010 (tools/vs.sh); saída em build/f35/c645/. Mesma ideia do campos.py (que mede o layout do 983).
Serve para traduzir deslocamentos crus do 645 que ficaram no fonte (s94: CSharedDoc/CGolfDoc em golfrule.cpp).
Saída: off_hex nome (sizeof no fim)."""
import sys, re, os, subprocess
RB = '/root/rebang'; ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFS = [a for a in sys.argv[1:] if a.startswith('/D')]; sys.argv = [a for a in sys.argv if not a.startswith('/D')]  # s96: /DREBANG_GOLFRULE_PCH
cls = sys.argv[1]; hdr = sys.argv[2] if len(sys.argv) > 2 else RB + '/source/client/ProjectG/' + cls[1:].lower() + '.h'
s = open(hdr, encoding='latin-1').read()
i = re.search(r'\n(?:class|struct) %s\b[^;{]*\{' % cls, s).end(); j = s.index('\n};', i); names = []; depth = 0
for l in s[i:j].split('\n'):
    l = l.split('//')[0]; d0 = depth; depth += l.count('{') - l.count('}')
    if d0 or '(' in l or 'static ' in l: continue
    m = re.search(r'\b((?:m_|unk|rb_)\w+)(\[[^;]*\])?(\s*:\s*\d+)?;', l)
    if m and not m.group(3) and m.group(1) not in names: names.append(m.group(1))
W = ROOT + '/build/f35/c645'; os.makedirs(W, exist_ok=True)
src = W + '/c645_%s.cpp' % cls
body = '#define private public\n#define protected public\n#include "stdafx.h"\n#include "%s"\n#include <stddef.h>\n' % os.path.basename(hdr)
for n in names:
    body += '__if_exists(%s::%s){\nextern const unsigned int rb_o_%s[] = {0x5eed0001, offsetof(%s,%s)};\n}\n' % (cls, n, n, cls, n)
body += 'extern const unsigned int rb_o_sizeof[] = {0x5eed0001, sizeof(%s)};\n' % cls
open(src, 'w').write(body)
z = lambda p: 'Z:' + p.replace('/', '\\')
inc = [RB + '/source/rebang', RB + '/tools/VC7.1/include', RB + '/tools/VC7.1/atlmfc/include', RB + '/tools/WTL75/include',
       RB + '/tools/PlatformSDK-Aug2002/include', RB + '/source/client/Wangreal/include',
       RB + '/source/client/Wangreal/lib/freetype-2.2.1/include', RB + '/source/client/Fresh/include', os.path.dirname(hdr),
       RB + '/source/client/ProjectG', RB + '/source/shared/thirties']
args = ['/nologo', '/c', '/MD', '/GX', '/O2', '/G7', '/Gr', '/GS', '/Oy-', '/Zm200', '/DNDEBUG', '/DWIN32', '/D_WINDOWS', '/D_MBCS'] + DEFS + ['/I' + z(p) for p in inc] + \
       ['/FA', '/Fa' + z(src[:-4] + '.asm'), '/Fo' + z(src[:-4] + '.obj'), z(src)]
env = dict(os.environ, WINEPREFIX=os.environ.get('VS', '/root/kr839/local/vs2010') + '/wine', WINEDEBUG='-all',
           WINEDLLOVERRIDES='mscoree,mshtml=', WINEPATH=z(RB + '/tools/VC7.1/bin'))
p = subprocess.run(['wine', RB + '/tools/VC7.1/bin/cl.exe'] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, cwd=W)
open(src[:-4] + '.log', 'wb').write(p.stdout)
if p.returncode: sys.exit(p.stdout.decode('latin-1')[-3000:])
t = open(src[:-4] + '.asm', errors='replace').read(); r = []
for m in re.finditer(r'\?rb_o_(\w+)@@3QBIB\s+DD\s+05eed0001H[^\n]*\n\s+DD\s+0*([0-9a-fA-F]+)H?\r?\n', t): r.append((int(m.group(2), 16), m.group(1)))
for v, n in sorted(r, key=lambda x: (x[1] == 'sizeof', x[0])): print('0x%04x %s' % (v, n))
