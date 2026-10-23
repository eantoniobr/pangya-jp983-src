#!/usr/bin/env python3
"""V6/F4 (frente C): o exe LIGA? Confere a tabela de símbolos dos .obj do exe sem rodar o link.

Junta os .obj das 498 unidades da A (pgbuild.units(): o .obj mais novo e sem erro entre build/pg*/obj) e os das unidades
novas da B (src/projectg/jp/units.txt -> build/B/obj), e as .lib do link do rebang (VC10: msvcrt/msvcprt/oldnames;
SDK Aug2002; VC7.1 atls; mss32/NPGameLib; import lib da wangreal em build/wangreal-full). Para cada símbolo externo citado:
  ok        definido num .obj ou numa .lib
  terceiro  só nas .lib de terceiros que o rebang compila à parte (lua, freetype, zlib, libpng, ijl15)
  FALTA     ninguém define -> LNK2001/LNK2019 no link (lista por símbolo, com quem cita e a frente dona de quem cita)
E os símbolos definidos fora de COMDAT em dois .obj (LNK2005).
Saída: out/V6/link/{resumo.txt,falta.tsv,duplicados.tsv,objs.tsv}. Só leitura (não compila nada). ~20 s.
"""
import os, sys, re, glob, struct, collections, subprocess
R = '/root/jp983src'
sys.path.insert(0, R + '/tools/f32')
import pgbuild

OUT = os.environ.get('V6_OUT') or R + '/out/V6/link'  # V6_OUT: outra pasta (rodadas "e se" com V6_EXTRA)
VS = '/root/kr839/local/vs2010'
SDK = '/root/rebang/tools/PlatformSDK-Aug2002/lib'
LIBS = [VS + '/VC10/lib/msvcrt.lib', VS + '/VC10/lib/msvcprt.lib', VS + '/VC10/lib/oldnames.lib',
        '/root/rebang/tools/VC7.1/lib/atls.lib',
        '/root/rebang/source/client/ProjectG/lib/mss32.lib', '/root/rebang/source/client/ProjectG/lib/NPGameLib.lib',
        R + '/build/wangreal-full/wangreal.lib', R + '/build/C/f4/mss32x.lib'] + \
       [SDK + '/' + x for x in ('kernel32.lib', 'winmm.lib', 'user32.lib', 'gdi32.lib', 'comdlg32.lib', 'advapi32.lib',
                                'shell32.lib', 'ole32.lib', 'oleaut32.lib', 'uuid.lib', 'shlwapi.lib', 'comctl32.lib',
                                'vfw32.lib', 'ws2_32.lib', 'wininet.lib', 'dbghelp.lib', 'iphlpapi.lib', 'msimg32.lib',
                                'opengl32.lib', 'imm32.lib', 'version.lib')]
# símbolos que o próprio link.exe fabrica
LINKER = {'___ImageBase', '__ImageBase', '___safe_se_handler_table', '___safe_se_handler_count', '__load_config_used'}
# bibliotecas de terceiros que o rebang compila à parte (VC7.1; o nosso build ainda não as compila): resolvem o link
# se a F4 usar as do rebang (ou compilar os .tar.gz)
TERCEIROS = ['/root/rebang/build/projectg/source/shared/LuaSystem/Lua/lib/lua51_Release_MD_fastcall.lib',
             '/root/rebang/build/projectg/source/client/Wangreal/lib/freetype221MT.lib',
             '/root/rebang/source/client/Fresh/lib/zlib.lib', '/root/rebang/source/client/Fresh/lib/libpng.lib',
             '/root/rebang/source/client/Wangreal/lib/ijl15.lib']


def coff(path):
    """(definidos, indefinidos, definidos_fora_comdat, alternatename) de um .obj (COFF comum ou bigobj)"""
    d = open(path, 'rb').read()
    if len(d) < 20: return None
    big = struct.unpack_from('<HH', d, 0) == (0, 0xffff)
    if big:
        nsec, symoff, nsym = struct.unpack_from('<I', d, 44)[0], *struct.unpack_from('<II', d, 48)
        sh, ssz, opt = 56, 20, 0
    else:
        mach, nsec, _, symoff, nsym, opt, _ = struct.unpack_from('<HHIIIHH', d, 0)
        if mach != 0x14c: return None
        sh, ssz = 20 + opt, 18
    stroff = symoff + nsym * ssz
    secs = [struct.unpack_from('<8sIIIIIIHHI', d, sh + i * 40) for i in range(nsec)]
    def nm(o):
        raw = d[o:o + 8]
        if raw[:4] == b'\0\0\0\0':
            s = stroff + struct.unpack_from('<I', raw, 4)[0]
            return d[s:d.index(b'\0', s)].decode('latin1')
        return raw.rstrip(b'\0').decode('latin1')
    de, un, strong, alt, sel = set(), set(), set(), {}, {}
    i = 0
    while i < nsym:
        o = symoff + i * ssz
        name = nm(o)
        if big:
            val, sec = struct.unpack_from('<Ii', d, o + 8); _, cls, naux = struct.unpack_from('<HBB', d, o + 16)
        else:
            val, sec = struct.unpack_from('<Ih', d, o + 8); _, cls, naux = struct.unpack_from('<HBB', d, o + 14)
        if cls == 3 and naux and 0 < sec <= nsec and secs[sec - 1][9] & 0x1000 and name == secs[sec - 1][0].rstrip(b'\0').decode('latin1'):
            sel[sec] = d[o + ssz + 14]  # aux de definição de seção: seleção do COMDAT
        if cls == 2:
            if sec > 0:
                de.add(name)
                if not secs[sec - 1][9] & 0x1000 or sel.get(sec) == 1: strong.add(name)
            elif sec == 0:
                (de if val else un).add(name)  # val != 0: COMMON
        elif cls == 105:  # weak external: tem um padrão, conta como definido
            de.add(name)
        i += 1 + naux
    for s in secs:  # /alternatename:A=B na .drectve
        if s[0].rstrip(b'\0') == b'.drectve':
            txt = d[s[4]:s[4] + s[3]].decode('latin1', 'replace')
            for a, b in re.findall(r'/alternatename:([^=\s]+)=(\S+)', txt, re.I): alt[a.strip('"')] = b.strip('"')
    return de, un - de, strong, alt


def libsyms(path):
    """nomes do 1º membro de ligação ("/") de uma .lib"""
    d = open(path, 'rb').read()
    if not d.startswith(b'!<arch>\n'): return set()
    o = 8
    size = int(d[o + 48:o + 58].split()[0]); body = d[o + 60:o + 60 + size]
    n = struct.unpack_from('>I', body, 0)[0]
    names = body[4 + 4 * n:].split(b'\0')[:n]
    return {x.decode('latin1') for x in names}


def newest_obj(rel):
    """.obj mais novo da unidade entre build/pg*/obj, que não esteja vazio e cujo .log não tenha erro"""
    best = None
    # C84: build/C/f4/troca/obj/ = .obj da C com as linhas do F4 (lock por arquivo) — vale enquanto for o mais novo;
    # V6_SEM="pg-a154 ..." ignora builds da A em andamento (headers/pch diferentes dos .obj da build fechada)
    sem = [os.path.basename(t.rstrip('/')) for t in os.environ.get('V6_SEM', '').split()]   # C108: aceita build/pg-x
    # C94 (C-ROBO): V6_PG="pg-a168 ..." = a(s) build(s) da A desta rodada: as OUTRAS build/pg-a* saem da disputa; os .obj
    # provisórios da C (build/pg-c*, troca) continuam valendo pela data (c94-1: o wbone.obj da pg-a167 é anterior ao wbone.h da C88)
    pg = os.environ.get('V6_PG', '').split()
    if pg: sem = sem + [t for t in (os.path.basename(os.path.dirname(d)) for d in glob.glob(f'{R}/build/pg-a*/obj'))
                        if t not in pg]
    for f in glob.glob(f'{R}/build/pg*/obj/{rel[:-4]}.obj') + glob.glob(f'{R}/build/C/f4/troca/obj/{rel[:-4]}.obj'):
        if any(f'/build/{t}/' in f for t in sem): continue
        if os.path.getsize(f) < 100: continue
        lg = f[:-4] + '.log'
        if os.path.exists(lg) and ' error ' in open(lg, errors='replace').read(): continue
        m = os.path.getmtime(f)
        if not best or m > best[0]: best = (m, f)
    return best[1] if best else None


def front(path):
    bo = os.environ.get('V6_BOBJ', '').strip('/')
    return 'B' if '/build/B/' in path or (bo and f'/{bo}/' in path) else 'C' if '/build/C/' in path else 'A'


def main():
    os.makedirs(OUT, exist_ok=True)
    objs, faltam = [], []
    for u in pgbuild.units():
        f = newest_obj(u[0])
        (objs if f else faltam).append(f or u[0])
    for l in open(R + '/src/projectg/jp/units.txt'):
        l = l.split('#')[0].strip()
        if not l: continue
        f = f'{R}/{os.environ.get("V6_BOBJ") or "build/B/obj"}/{os.path.basename(l)[:-4]}.obj'  # C94: V6_BOBJ = outra pasta da B
        if os.path.exists(f) and os.path.getsize(f) > 100: objs.append(f)
        else: faltam.append('src/projectg/jp/' + l)
    for f in os.environ.get('V6_EXTRA', '').split():  # "e se": .obj a mais (ex.: unidade nova ainda fora do units.txt)
        objs.append(os.path.abspath(f))
    defs = collections.defaultdict(list); strong = collections.defaultdict(list); refs = collections.defaultdict(list)
    alt = {}
    for f in objs:
        r = coff(f)
        if r is None: faltam.append(f + ' (não é COFF i386)'); continue
        de, un, st, al = r
        for s in de: defs[s].append(f)
        for s in st: strong[s].append(f)
        for s in un: refs[s].append(f)
        alt.update(al)
    lib = {}
    for L in LIBS:
        if os.path.exists(L):
            for s in libsyms(L): lib.setdefault(s, os.path.basename(L))
    terc = {}
    for L in TERCEIROS:
        if os.path.exists(L):
            for x in libsyms(L): terc.setdefault(x, os.path.basename(L))
    contagem = collections.Counter(); falta = []; usoterc = collections.Counter()
    for s, quem in sorted(refs.items()):
        if s in defs or s in LINKER: contagem['ok_obj'] += 1; continue
        if s in lib: contagem['ok_lib'] += 1; continue
        if s in alt and (alt[s] in defs or alt[s] in lib): contagem['ok_alt'] += 1; continue
        if s in terc: contagem['terceiro'] += 1; usoterc[terc[s]] += 1; continue
        contagem['FALTA'] += 1; falta.append((s, quem))
    dup = [(s, fs) for s, fs in sorted(strong.items()) if len(set(fs)) > 1]
    rel = lambda f: f.replace(R + '/', '')
    dem = demangle([s for s, _ in falta] + [s for s, _ in dup])
    va = {}; porva = collections.defaultdict(set)
    for m in ('map/projectg.tsv', 'map/pkt_c.tsv', 'src/projectg/jp/jp.tsv', 'map/wangreal.tsv'):
        for l in open(f'{R}/{m}', errors='replace'):
            c = l.rstrip('\n').split('\t')
            if len(c) > 1 and re.fullmatch(r'[0-9a-f]{8}', c[1]):
                va.setdefault(c[0], ('w:' if 'wangreal' in m else '') + c[1])
                if 'wangreal' not in m and c[0] in defs: porva[c[1]].add(c[0])
    # visão sem corpo cujo endereço do 983 já tem função/dado DEFINIDO com outro nome: basta trocar a declaração
    gemeo = {x: sorted(porva.get(va.get(x, '-'), ())) for x, _ in falta}
    dem.update(demangle(sorted({g for v in gemeo.values() for g in v})))
    porcl = collections.defaultdict(list)
    with open(OUT + '/falta.tsv', 'w') as o:
        o.write('simbolo\tnome\tfrentes\tn_citam\tva983\tclasse\tdefinido_como\tquem_cita\n')
        for s, quem in falta:
            fr = ''.join(sorted({front(q) for q in quem})); cl = classe(s)
            porcl[(cl, fr)].append(len(quem))
            o.write(f'{s}\t{dem.get(s, s)}\t{fr}\t{len(quem)}\t{va.get(s, "-")}\t{cl}\t{" | ".join(dem.get(g, g) for g in gemeo[s]) or "-"}\t{" ".join(rel(q) for q in quem[:6])}\n')
    with open(OUT + '/falta_classes.tsv', 'w') as o:
        o.write('classe\tfrentes\tsimbolos\tcitacoes\n')
        for (cl, fr), v in sorted(porcl.items(), key=lambda x: (-sum(x[1]), x[0])):
            o.write(f'{cl}\t{fr}\t{len(v)}\t{sum(v)}\n')
    with open(OUT + '/duplicados.tsv', 'w') as o:
        o.write('simbolo\tnome\tobjs\n')
        for s, fs in dup: o.write(f'{s}\t{dem.get(s, s)}\t{" ".join(rel(q) for q in sorted(set(fs)))}\n')
    with open(OUT + '/objs.tsv', 'w') as o:
        for f in objs: o.write(f'{front(f)}\t{rel(f)}\n')
        for f in faltam: o.write(f'SEM_OBJ\t{f}\n')
    porfr = collections.Counter(''.join(sorted({front(q) for q in quem})) for _, quem in falta)
    txt = [f'.obj lidos: {len(objs)} (A {sum(front(f)=="A" for f in objs)}, B {sum(front(f)=="B" for f in objs)}); '
           f'unidades sem .obj utilizável: {len(faltam)}',
           f'.lib lidas: {sum(os.path.exists(L) for L in LIBS)} de {len(LIBS)} ({len(lib)} símbolos)',
           f'símbolos externos citados: {len(refs)}',
           f'  resolvidos por .obj: {contagem["ok_obj"]}; por .lib: {contagem["ok_lib"]}; por /alternatename: {contagem["ok_alt"]}',
           f'  só nas bibliotecas de terceiros do rebang (fora do nosso build): {contagem["terceiro"]} — '
           + ', '.join(f'{k} {v}' for k, v in sorted(usoterc.items())),
           f'  FALTA (ninguém define; o link pararia): {contagem["FALTA"]} — citados por frente: '
           + ', '.join(f'{k}={v}' for k, v in sorted(porfr.items())),
           f'  das FALTA, com o mesmo endereço do 983 já DEFINIDO sob outro nome (trocar a visão pelo nome real): '
           f'{sum(1 for v in gemeo.values() if v)}',
           f'definidos fora de COMDAT em mais de um .obj (LNK2005): {len(dup)}']
    open(OUT + '/resumo.txt', 'w').write('\n'.join(txt) + '\n')
    print('\n'.join(txt))


def classe(s):
    """escopo de um nome decorado (classe/namespace mais interno), '(livre)' para função/dado global, '(C)' para nome C"""
    if not s.startswith('?'): return '(C)'
    m = re.match(r'\?\?(?:_[0-9A-Z]|[0-9A-Z])([^@?]+)@', s) or re.match(r'\?\?\$[^@]+@[^@]*@([^@]+)@', s) \
        or re.match(r'\?[^@?]+@([^@?]+)@', s)
    if re.match(r'\?[^@?]+@@[0-9YZ]', s): return '(livre)'
    return m.group(1) if m else '?'


def demangle(names):
    """nomes legíveis pelo undname do VS2010 sob Wine (se falhar, fica o nome cru)"""
    names = [n for n in names if n.startswith('?')]
    if not names: return {}
    und = VS + '/VC10/bin/undname.exe'
    if not os.path.exists(und): return {}
    out = {}
    for i in range(0, len(names), 200):
        part = names[i:i + 200]
        try:
            p = subprocess.run(['wine', und] + part, capture_output=True, text=True, timeout=120,
                               env=dict(os.environ, WINEDEBUG='-all'))
        except Exception:
            return out
        for m in re.finditer(r'Undecoration of :- "(.*?)"\s*is :- "(.*?)"', p.stdout, re.S):
            out[m.group(1)] = m.group(2)
    return out


if __name__ == '__main__':
    main()
