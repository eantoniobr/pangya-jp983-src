#!/usr/bin/env python3
"""achata.py 645|983 Tipo [Tipo...] [--onde OFF...] — achata structs: cada campo-folha com deslocamento absoluto, tamanho e caminho
(`a.b[3].c`), no layout DO 645 (cl do VC7.1 do rebang, como o campos645.py) ou DO 983 (nosso cl/pch, como o campos.py). Lê as
definições de struct dos cabeçalhos (645: rebang/source/shared/globalgamedefine.h + client/ProjectG/shareddoc.h; 983: src/shared/
globalgamedefine.h + src/projectg/shareddoc.h), sonda só os campos diretos de cada struct (offsetof, sizeof do campo e do elemento)
e expande em Python (bases, arrays, structs aninhados). Campo de bits sai como `nome:bits` no deslocamento do campo anterior + tamanho.
--onde OFF: em vez da lista, diz que folha contém cada deslocamento (OFF relativo ao 1º tipo). Sessão 95 (CSharedDoc cru em golfrule.cpp).
Saída da lista: off_hex tamanho caminho tipo (espaços do tipo viram _)."""
import sys, re, os, subprocess, types, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RB = '/root/rebang'
HDR = {'645': [RB + '/source/shared/globalgamedefine.h', RB + '/source/client/ProjectG/shareddoc.h',
               RB + '/source/client/ProjectG/golfdoc.h'],  # s96: sPlayerData
       '983': [ROOT + '/src/shared/globalgamedefine.h', ROOT + '/src/projectg/shareddoc.h', ROOT + '/src/projectg/golfdoc.h']}

def structs(files):
    """nome -> (bases, [(tipo, nome, dims, bits)]) só com campos de dados no nível 0 do corpo"""
    d = {}
    for f in files:
        s = open(f, encoding='latin-1').read()
        s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
        for m in re.finditer(r'\n(?:struct|class)\s+(\w+)\s*(:[^{;]*)?\{', s):
            nome = m.group(1); i = m.end(); depth = 1; j = i
            while depth and j < len(s):
                depth += {'{': 1, '}': -1}.get(s[j], 0); j += 1
            corpo = s[i:j - 1]; campos = []; dep = 0; buf = ''
            for l in corpo.split('\n'):
                l = l.split('//')[0]; d0 = dep; dep += l.count('{') - l.count('}')
                ma = re.match(r'\s*\}\s*(\w+)\s*((?:\[[^\]]*\])*)\s*;', l)
                if d0 and not dep and ma:  # `struct { ... } m_x[2];` anônimo: folha opaca (s95: m_teamResult)
                    campos.append(('anon', ma.group(1), re.findall(r'\[([^\]]*)\]', ma.group(2)), None)); continue
                if d0 or dep or '(' in l or 'static ' in l or 'typedef' in l or l.strip().startswith('#'): continue
                for decl in l.split(';')[:-1]:
                    decl = decl.strip()
                    if not decl or decl.endswith(':') or decl in ('public', 'private', 'protected'): continue
                    decl = re.sub(r'^(public|private|protected)\s*:\s*', '', decl)
                    mm = re.match(r'(.+?)\s*\b(\w+)\s*((?:\[[^\]]*\])*)\s*(?::\s*(\d+))?$', decl)
                    if not mm: continue
                    tipo = mm.group(1).strip();
                    if tipo in ('', 'return', 'friend') or tipo.startswith('friend'): continue
                    dims = [x for x in re.findall(r'\[([^\]]*)\]', mm.group(3))]
                    campos.append((tipo.rstrip('*').strip() + ('*' if '*' in tipo else ''), mm.group(2), dims, mm.group(4)))
            bases = [b.strip().split()[-1] for b in (m.group(2) or ':')[1:].split(',') if b.strip()]
            if campos or bases: d.setdefault(nome, (bases, campos))
    return d

def sonda(lado, tipos, S):
    body = '#include <stddef.h>\n#pragma warning(disable:4003)\n'; k = 0; chaves = []
    for t in tipos:
        bases, campos = S[t]
        body += 'extern const unsigned int rb_s_%s[] = {0x5eed0002, sizeof(%s)};\n' % (t, t)
        for b in [x for x in bases if x in S]:
            body += 'extern const unsigned int rb_b_%s_%s[] = {0x5eed0002, (unsigned int)(char*)static_cast<%s*>((%s*)0x1000) - 0x1000};\n' % (t, b, b, t)
        for tipo, n, dims, bits in campos:
            if bits: continue
            idx = '[0]' * len(dims)
            body += ('__if_exists(%s::%s){\nextern const unsigned int rb_c_%s_%s[] = {0x5eed0002, offsetof(%s,%s), sizeof(((%s*)0)->%s), '
                     'sizeof(((%s*)0)->%s%s)};\n}\n') % (t, n, t, n, t, n, t, n, t, n, idx)
    W = ROOT + '/build/f35/achata'; os.makedirs(W, exist_ok=True); src = W + '/a%s.cpp' % lado
    if lado == '645':
        body = '#define private public\n#define protected public\n#include "stdafx.h"\n#include "shareddoc.h"\n#include "golfdoc.h"\n' + body
        open(src, 'w').write(body)
        z = lambda p: 'Z:' + p.replace('/', '\\')
        inc = [RB + '/source/rebang', RB + '/tools/VC7.1/include', RB + '/tools/VC7.1/atlmfc/include', RB + '/tools/WTL75/include',
               RB + '/tools/PlatformSDK-Aug2002/include', RB + '/source/client/Wangreal/include',
               RB + '/source/client/Wangreal/lib/freetype-2.2.1/include', RB + '/source/client/Fresh/include',
               RB + '/source/client/ProjectG', RB + '/source/shared/thirties', RB + '/source/shared']
        args = ['/nologo', '/c', '/MD', '/GX', '/O2', '/G7', '/Gr', '/GS', '/Oy-', '/Zm200', '/DNDEBUG', '/DWIN32', '/D_WINDOWS', '/D_MBCS'] + \
               ['/I' + z(p) for p in inc] + ['/FA', '/Fa' + z(src[:-4] + '.asm'), '/Fo' + z(src[:-4] + '.obj'), z(src)]
        env = dict(os.environ, WINEPREFIX=os.environ.get('VS', '/root/kr839/local/vs2010') + '/wine', WINEDEBUG='-all',
                   WINEDLLOVERRIDES='mscoree,mshtml=', WINEPATH=z(RB + '/tools/VC7.1/bin'))
        p = subprocess.run(['wine', RB + '/tools/VC7.1/bin/cl.exe'] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, cwd=W)
        open(src[:-4] + '.log', 'wb').write(p.stdout); rc = p.returncode
    else:
        sys.path.insert(0, ROOT + '/tools/f32'); import pgbuild as pb
        open(src, 'w').write(body)
        a = types.SimpleNamespace(flags=None, B=ROOT + '/build/pg')
        rc = pb.cl(pb.base_args(a) + ['/FIstdafx.h', '/Dprivate=public', '/Dprotected=public', '/FI' + HDR['983'][1], '/FI' + HDR['983'][2], '/FA',
                                      '/Fa' + src[:-4] + '.asm', '/Fo' + src[:-4] + '.obj', src], src[:-4] + '.log')
    if rc: sys.exit(open(src[:-4] + '.log', errors='replace').read()[-4000:])
    t = open(src[:-4] + '.asm', errors='replace').read(); r = {}
    for m in re.finditer(r'\?rb_(\w+)@@3QBIB\s+DD\s+05eed0002H[^\n]*\n((?:\s+DD\s+[0-9a-fA-F]+H?\r?\n)+)', t):
        r[m.group(1)] = [int(x, 16) for x in re.findall(r'DD\s+0*([0-9a-fA-F]+)H?', m.group(2))]
    return r

def achata(lado, raiz):
    S = structs(HDR[lado])
    # fecho dos tipos alcançáveis
    vist = []; fila = [raiz]
    while fila:
        t = fila.pop()
        if t in vist or t not in S: continue
        vist.append(t); bases, campos = S[t]; fila += bases + [c[0] for c in campos]
    R = sonda(lado, vist, S); folhas = []
    def rec(t, base, cam):
        bases, campos = S[t]
        for b in bases:
            if b in S: rec(b, base + R.get('b_%s_%s' % (t, b), [0])[0], cam)
        ult = base
        for tipo, n, dims, bits in campos:
            if bits: folhas.append((ult, 0, cam + n + ':' + bits, tipo)); continue
            k = 'c_%s_%s' % (t, n)
            if k not in R: continue
            off, tam, el = R[k]; o = base + off; ult = o + tam
            sub = tipo if tipo in S and tipo in vist else None
            if dims:
                cnt = tam // el if el else 1; nd = len(dims)
                if nd > 1:  # arrays de várias dimensões: achatar como um só índice da 1ª dimensão
                    sub = None; folhas.append((o, tam, cam + n + '[%d]*%d' % (cnt, el), tipo)); continue
                for i in range(cnt):
                    if sub: rec(sub, o + i * el, cam + '%s[%d].' % (n, i))
                    else: folhas.append((o + i * el, el, cam + '%s[%d]' % (n, i), tipo))
            elif sub: rec(sub, o, cam + n + '.')
            else: folhas.append((o, tam, cam + n, tipo))
    rec(raiz, 0, '')
    return sorted(folhas), R.get('s_' + raiz, [0])[0]

if __name__ == '__main__':
    a = sys.argv[1:]; onde = []
    if '--onde' in a: i = a.index('--onde'); onde = [int(x, 0) for x in a[i + 1:]]; a = a[:i]
    lado, raiz = a[0], a[1]
    F, tam = achata(lado, raiz)
    if not onde:
        for o, t, c, ti in F: print('0x%05x %d %s %s' % (o, t, c, ti.replace(' ', '_')))
        print('sizeof 0x%x' % tam)
    for x in onde:
        best = [f for f in F if f[0] <= x < f[0] + max(f[1], 1)]
        print('0x%x\t%s' % (x, '; '.join('%s+0x%x' % (c, x - o) if x != o else c for o, t, c, ti in best) or '?'))
