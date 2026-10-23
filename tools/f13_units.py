#!/usr/bin/env python3
"""f13_units — aplica as unidades (.obj) da F1.3 ao map/wangreal_funcs.tsv (coluna obj / obj_via) e gera
out/F1.3/{unidades.tsv,classes_rtti.tsv} e map/wangreal_gaps.tsv (código fora do mapa de funções).
Rodar de novo depois de tools/f04_map.py (que regrava o mapa). Evidência das fronteiras: out/F1.3/RELATORIO.md."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from f13_lib import *
# (início, fim exclusivo, unidade, fonte provisório, origem, como a fronteira foi achada)
UNITS = [
    (0x10001000, 0x100124f0, 'shparam', 'src/wangreal/wshparam.cpp (nome provisório)', 'obj do projeto device (novo no 839)',
     'escada .rdata: 10062398 (uso em 100122c0) antes de 100623e4 (uso em 10001000) => um só .obj'),
    (0x100124f0, 0x100162a0, 'wd3d', 'src/wangreal/wd3d.cpp', 'obj do projeto device', 'âncoras do 645; ~WDevice em 100124f0'),
    (0x100162a0, 0x10045030, 'wd3d8', 'src/wangreal/wd3d8.cpp', 'obj do projeto device', 'âncoras do 645; strstr é o 1º COMDAT do wd3d8.obj'),
    (0x10045030, 0x10045320, 'directinput', 'src/wangreal/wdinput/directinput.cpp', 'obj do projeto device', 'âncoras do 645'),
    (0x10045320, 0x100462f0, None, '', '', ''),      # dikeyboard/dimouse: rótulos da F0.4
    (0x100462f0, 0x10047650, None, '', '', ''),      # wime
    (0x10047650, 0x10048122, None, '', '', ''),      # device
    (0x10048122, 0x100481d0, 'thunks_import', '-', 'bibliotecas de importação', 'jmp [IAT]'),
    (0x100481d0, 0x10049310, 'lib:dinput8_dados', '-', 'dinput8.lib (c_rgodfDIKeyboard/Mouse dentro da .text)',
     'c_dfDIKeyboard 10065d04 -> 100481d0; c_dfDIMouse 10065f0c -> 100491d0'),
    (0x10049310, 0x10058350, 'wxshadermtl', 'src/engine/wxshadermtl.cpp (nome provisório)', 'obj de biblioteca (engine), novo no 839',
     'vem depois dos thunks; .data 1006d224 (TYPE_*) + RTTI WxShaderMtl; dtor 10058010/10058320'),
    (0x10058350, 0x100584a0, 'wvdshnames', 'src/engine/wvdshnames.cpp (nome provisório)', 'obj de biblioteca (engine), novo no 839',
     '.data 1006d2a4.. (3 tabelas de nomes) separada da .data do wxshadermtl pelo RTTI de WxShaderMtl'),
    (0x100584a0, 0x10059990, None, '', '', ''),      # bitmap, wdxtc: rótulos da F0.4
    (0x10059990, 0x1005bf50, 'lang', 'src/wangreal/langtable.cpp', 'obj de biblioteca (engine), novo no 983',
     'escada .rdata/.bss limpa nos dois lados; puxado pelo inicializador de g_msgD3DInitFailed (10061a60)'),
    (0x1005bf50, 0x1005e19c, 'wmath', 'src/engine/wmath.cpp (nome provisório; 1 ou 2 .obj)', 'obj(s) de biblioteca (engine)',
     'depois do lang; .rdata 10066368.., .data 1006d358.., .bss 1006e6a4..; _CIacos/_CIsin'),
    (0x1005e19c, 0x1005ee10, 'crt', '-', 'msvcrt.lib (arranque, new[], cookie, EH)', 'operator new[] 1005e1a8 em diante'),
    (0x1005ee10, 0x10061a60, 'text$x', '-', 'funclets de EH de todos os .obj (.text$x)', '1º __unwindfunclet em 1005ee10'),
    (0x10061a60, 0x10061b00 + 0x100, 'text$yc_yd', '-', 'inicializadores estáticos e atexit (.text$yc/.text$yd)',
     'tabela .CRT$XCU 10062240: 10061a60 10061a70 10061ab0 10061af0'),
]
KEEP_IN_X = ('wd3d', 'wd3d8')     # rótulos por âncora que a F0.4 deu dentro da .text$x


def unit_of(va, old):
    for lo, hi, nm, *_ in UNITS:
        if lo <= va < hi:
            if nm is None:
                return old, None
            if nm == 'text$x' and old in KEEP_IN_X:
                return old + ':text$x', 'f13'
            return nm, 'f13'
    return old, None


path = os.path.join(ROOT, 'map', 'wangreal_funcs.tsv')
L = open(path).read().split('\n')
hdr = None; out = []; cnt = collections.Counter(); byt = collections.Counter(); ch = 0
for l in L:
    if not l or l.startswith('#'):
        out.append(l); continue
    a = l.split('\t')
    if hdr is None:
        hdr = a; out.append(l); io, iv = a.index('obj'), a.index('obj_via'); continue
    va = int(a[0], 16)
    nm, via = unit_of(va, a[io])
    if via and nm != a[io]:
        a[io] = nm; a[iv] = 'f13'; ch += 1
    cnt[a[io]] += 1; byt[a[io]] += int(a[1])
    out.append('\t'.join(a))
if '--apply' in sys.argv:
    open(path, 'w').write('\n'.join(out))
print('linhas com unidade alterada:', ch)
od = os.path.join(ROOT, 'out', 'F1.3'); os.makedirs(od, exist_ok=True)
# código fora do mapa de funções (vãos que não são só int3)
gaps = []
for p, n in zip(FUNCS, FUNCS[1:]):
    e = p['va'] + p['sz']; b = pe.read(e, n['va'] - e); s = b.lstrip(b'\xcc')
    if s and not (0x100481d0 <= e < 0x10049310) and e < 0x1005ee10:
        st = e + len(b) - len(s)
        kind = 'tabela_switch?' if st in pe.fix and secof(pe.u32(st)) == '.text' else 'codigo'
        gaps.append((st, len(s.rstrip(b'\xcc')), unit_of(st, p['obj'])[0], kind, '%x' % p['va']))
with open(os.path.join(ROOT, 'map', 'wangreal_gaps.tsv'), 'w') as f:
    f.write('# trechos da .text do 983 fora de map/wangreal_funcs.tsv (o Ghidra não criou função: sem referência ou cauda)\n')
    f.write('va\tsz\tobj\ttipo\tfuncao_anterior\n')
    for g in gaps:
        f.write('%x\t%d\t%s\t%s\t%s\n' % g)
gc = collections.Counter(); gb = collections.Counter()
for g in gaps:
    gc[g[2]] += 1; gb[g[2]] += g[1]
with open(os.path.join(od, 'unidades.tsv'), 'w') as f:
    f.write('inicio\tfim\tunidade\tfuncoes_mapa\tbytes_mapa\tvaos\tbytes_vaos\tfonte\torigem\tevidencia\n')
    seen = set()
    for lo, hi, nm, src, org, ev in UNITS:
        if nm is None:
            continue
        f.write('%x\t%x\t%s\t%d\t%d\t%d\t%d\t%s\t%s\t%s\n' % (lo, hi, nm, cnt[nm], byt[nm], gc[nm], gb[nm], src, org, ev)); seen.add(nm)
    for nm in sorted(cnt):
        if nm not in seen:
            f.write('-\t-\t%s\t%d\t%d\t%d\t%d\t(rótulo da F0.4)\t\t\n' % (nm, cnt[nm], byt[nm], gc[nm], gb[nm]))
# classes com RTTI -> unidade (pela função de menor endereço que usa a vtable)
mn = {}
for f_, t in refs():
    if secof(f_) == '.text' and f_ < 0x1005ee10:
        mn[t] = min(mn.get(t, 1 << 32), f_)
vts = collections.OrderedDict()
for l in open(os.path.join(ROOT, 'build', 'f04', 'vt983w.tsv')):
    a = l.rstrip('\n').split('\t')
    vts.setdefault((a[0], a[4]), 0); vts[(a[0], a[4])] += 1
with open(os.path.join(od, 'classes_rtti.tsv'), 'w') as f:
    f.write('classe\tvtable\tslots\tprimeiro_uso\tunidade\n')
    for (c, v), n in vts.items():
        m = mn.get(int(v, 16))
        fn = func_at(m) if m else None
        f.write('%s\t%s\t%d\t%s\t%s\n' % (c, v, n, '%x' % m if m else '-', unit_of(m, fn['obj'])[0] if m else '?'))
print('vãos de código:', len(gaps), sum(g[1] for g in gaps), dict(gc))
