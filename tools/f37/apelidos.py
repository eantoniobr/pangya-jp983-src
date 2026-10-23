#!/usr/bin/env python3
"""f37/apelidos — B153 (pedido C90.1): apelidos de link para as visões velhas/sem corpo da frente B (RFWnd do rfscenemanager.h,
RFManager/RFRenderer velhos, CItemManagerJp, CExhibition983, CPetFrameJp…) cujo endereço do 983 já tem função/dado DEFINIDO
com outro nome decorado (na lib da RF da B ou num .obj da A). Mesmo critério do `definido_como` do tools/v6/simbolos.py:
símbolo citado e sem definição cujo VA (map/projectg.tsv, src/projectg/jp/jp.tsv) = VA de UM símbolo definido.
Gera src/projectg/jp/rfapelidos983.cpp com `#pragma comment(linker, "/ALTERNATENAME:velho=novo")` (o link só usa o apelido
quando o velho fica sem definição; o simbolos.py/stubs.py da C já os contam). ABI conferida pelo undname: mesma classe de
retorno (void/inteiro/ponto flutuante/objeto por valor; velho void aceita novo inteiro), mesmo nº de argumentos, mesma convenção.
Uso: python3 tools/f37/apelidos.py   (só lê os .obj; ~1 min; refazer depois de mudar visões)
"""
import os, sys, re, collections
R = '/root/jp983src'
sys.path.insert(0, R + '/tools/v6')
import simbolos as S

OUT = R + '/src/projectg/jp/rfapelidos983.cpp'
EXCLUI = {  # conferidos à mão (B153)
    '?GetTypeName@RFWndEx@@UAEPB_WXZ',  # velho devolve wchar_t*, a lib devolve const std::wstring&
    '?GetRow983@LuaRow983@@QAE?AULuaCell983@@H@Z',  # LuaCell983 x lua_table_helper devolvidos por valor
    '?GetByIndex@LuaTable983@_gateway@@QAEMH@Z',  # this lua_tinker::table x LuaChild983
}
CONV = ('__thiscall', '__fastcall', '__cdecl', '__stdcall')


def split_args(s):
    d = 0; parts = ['']
    for ch in s:
        if ch in '<(': d += 1
        elif ch in '>)': d -= 1
        if ch == ',' and d == 0: parts.append('')
        else: parts[-1] += ch
    return [p.strip() for p in parts if p.strip() and p.strip() != 'void']


def sig(dem):
    """(convenção, tipo de retorno, nº de args) de um nome legível; None = dado"""
    m = re.search(r'(%s)' % '|'.join(CONV), dem)
    if not m: return None
    head = re.sub(r'^(public|protected|private): ', '', dem[:m.start()]).replace('virtual ', '').replace('static ', '').strip()
    i = dem.find('(', m.end())
    j = dem.rfind(')')
    return m.group(1), head, len(split_args(dem[i + 1:j]))


def kind(t):
    t = t.strip()
    if not t: return 'ctor'
    if t == 'void': return 'void'
    if t in ('float', 'double'): return 'fp'
    if t.endswith('*') or t.endswith('&'): return 'int'
    if t.startswith('class ') or t.startswith('struct ') or t.startswith('union '): return 'obj'
    return 'int'


def compat(a, b):
    sa, sb = sig(a), sig(b)
    if sa is None or sb is None: return (sa is None and sb is None), 'dado'
    if sa[0] != sb[0]: return False, 'convenção'
    if sa[2] != sb[2]: return False, 'nº de args %d x %d' % (sa[2], sb[2])
    ka, kb = kind(sa[1]), kind(sb[1])
    # velho void só com novo inteiro (float deixa o ST(0) empilhado; objeto por valor pede o ponteiro oculto)
    if ka != kb and not (ka == 'void' and kb == 'int'): return False, 'retorno %s x %s' % (ka, kb)
    return True, ''


def main():
    objs = []
    for u in S.pgbuild.units():
        f = S.newest_obj(u[0])
        if f: objs.append(f)
    for l in open(R + '/src/projectg/jp/units.txt'):
        l = l.split('#')[0].strip()
        f = f'{R}/build/B/obj/{os.path.basename(l)[:-4]}.obj'
        if l and l != os.path.basename(OUT) and os.path.exists(f): objs.append(f)
    defs, refs = set(), set()
    for f in objs:
        r = S.coff(f)
        if r: defs |= r[0]; refs |= r[1]
    va = {}; porva = collections.defaultdict(set)
    for m in ('map/projectg.tsv', 'src/projectg/jp/jp.tsv'):
        for l in open(f'{R}/{m}', errors='replace'):
            c = l.rstrip('\n').split('\t')
            if len(c) > 1 and re.fullmatch(r'[0-9a-f]{8}', c[1]):
                va.setdefault(c[0], c[1])
                if c[0] in defs: porva[c[1]].add(c[0])
    cand = {}
    for s in sorted(refs - defs):
        g = porva.get(va.get(s, '-'), set())
        if len(g) == 1 and s not in EXCLUI: cand[s] = next(iter(g))
    dem = S.demangle(sorted(set(cand) | set(cand.values())))
    ok, fora = {}, []
    for s, t in cand.items():
        c, why = compat(dem.get(s, s), dem.get(t, t))
        if c: ok[s] = t
        else: fora.append((s, t, why))
    with open(OUT, 'w') as f:
        f.write('// JP 983 (B153, pedido C90.1): apelidos de link das visões velhas/sem corpo da frente B para o símbolo definido com o\n'
                '// mesmo endereço do 983 (gerado por tools/f37/apelidos.py; ABI conferida pelo undname). O link só usa o apelido quando\n'
                '// o nome velho fica sem definição. Somem quando as unidades passarem a declarar pelo nome real (refresh/lib/*.h…).\n')
        for s in sorted(ok, key=lambda k: (va[k], k)):
            f.write('#pragma comment(linker, "/ALTERNATENAME:%s=%s") // %s %s\n' % (s, ok[s], va[s], dem.get(ok[s], '')[:90]))
    for s, t, why in sorted(fora):
        print('FORA\t%s\t%s\t%s' % (why, dem.get(s, s)[:110], dem.get(t, t)[:110]))
    print('apelidos: %d; fora por ABI: %d; excluídos à mão: %d (%s)' % (len(ok), len(fora), len(EXCLUI), OUT))


if __name__ == '__main__':
    main()
