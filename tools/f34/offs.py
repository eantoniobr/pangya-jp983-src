#!/usr/bin/env python3
"""offs.py Classe [cabeçalho] [-e expr ...] — deslocamento de cada campo m_* da classe como o pch do exe a vê (sem depender do
/d1reportSingleClassLayout, que deixou de imprimir para o CSharedDoc): gera um .cpp com offsetof de cada campo num vetor,
compila com /FA e lê os DD da listagem. Com cabeçalho dado, ele é incluído (com protected/private abertos). -e acrescenta expressões inteiras (ex.: 'sizeof(sRoomInfo)'). Saída: off_hex nome."""
import sys, os, re, types
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT + '/tools/f32'); import pgbuild as pb
OPEN = False
def fields(cls, hdr):
    s = open(hdr, encoding='latin-1').read()
    i = re.search(r'\nclass %s\b[^;{]*\{' % cls, s).end(); j = s.index('\n};', i); out = []
    depth = 0
    for l in s[i:j].split('\n'):
        l = l.split('//')[0]
        d0 = depth; depth += l.count('{') - l.count('}')
        if d0 or '(' in l or 'static ' in l: continue
        m = re.search(r'\b(m_\w+)(\[[^;]*\])?(\s*:\s*\d+)?;', l)
        if m and not m.group(3) and m.group(1) not in out: out.append(m.group(1))
    return out
def measure(cls, names, exprs=(), inc=None):
    a = types.SimpleNamespace(flags=None, B=ROOT + '/build/pg'); os.makedirs(ROOT + '/build/f34', exist_ok=True)
    src = ROOT + '/build/f34/offs.cpp'
    ex = ['offsetof(%s, %s)' % (cls, n) for n in names] + list(exprs) + ['sizeof(%s)' % cls]
    open(src, 'w').write('#include <stddef.h>\n' + ('#define protected public\n#define private public\n#include "%s"\n' % inc if inc else '') + 'extern const unsigned int rb_offs[] = {0x5eed0001,\n' + ',\n'.join(ex) + '\n};\n')
    pch = 'src/projectg/stdafx.cpp'
    # --aberto: sem pch e com private/protected trocados por public (classe do pch com campos fechados; ~20 s)
    use = ['/FIstdafx.h', '/Dprivate=public', '/Dprotected=public'] if OPEN else ['/FIstdafx.h', '/Yustdafx.h', '/Fp' + pb.pch_file(a, pch)]
    rc = pb.cl(pb.base_args(a) + use + ['/FA', '/Fa' + src[:-4] + '.asm',
               '/Fo' + src[:-4] + '.obj', src], src[:-4] + '.log')
    if rc: sys.exit(open(src[:-4] + '.log', errors='replace').read()[-3000:])
    t = open(src[:-4] + '.asm', errors='replace').read(); t = t[t.index('05eed0001H'):]
    v = [int(x.rstrip('H'), 16) for x in re.findall(r'DD\s+([0-9a-fA-F]+H?)', t)][:len(ex)]
    return list(zip(names + list(exprs) + ['sizeof'], v))
if __name__ == '__main__':
    av = sys.argv[1:]; exprs = []
    OPEN = '--aberto' in av
    if OPEN: av.remove('--aberto')
    while '-e' in av: k = av.index('-e'); exprs.append(av[k + 1]); del av[k:k + 2]
    cls = av[0]; hdr = av[1] if len(av) > 1 else ROOT + '/src/projectg/shareddoc.h'
    for n, v in measure(cls, fields(cls, hdr), exprs, os.path.abspath(hdr).replace('/', '\\\\').join(['Z:', '']) if len(av) > 1 else None): print('0x%05x %s' % (v, n))
