#!/usr/bin/env python3
"""F4 (frente C): imports que só o 983 tem -> quem usa no 983 (função e unidade) e se a função existe no nosso exe.
Entrada: out/F4/link/imports_so_983.tsv (dll<TAB>nome) feito pelo linkprova.py. Saída: out/F4/link/imports_so_983_quem.tsv
"""
import sys, struct, re, bisect, os
R = '/root/jp983src'
sys.path.insert(0, R + '/tools/v6')
from pe import PE
p = PE(R + '/ref/ProjectG_983_dump.exe')
im = p.imports()
# funções do 983 (map/projectg_funcs.tsv: início, tamanho, unidade, nome do Ghidra) e nomes decorados (projectg.tsv etc.)
FN = []
for l in open(R + '/map/projectg_funcs.tsv', encoding='latin1'):
    c = l.rstrip('\n').split('\t')
    if c[0] == 'f983': continue
    try: FN.append((int(c[0], 16), int(c[1]), c[3] or '-', c[10] if len(c) > 10 else '-'))
    except (ValueError, IndexError): pass
FN.sort(); FS = [x[0] for x in FN]
DEC = {}
for m in ('map/projectg.tsv', 'map/pkt_c.tsv', 'src/projectg/jp/jp.tsv'):
    for l in open(R + '/' + m, encoding='latin1'):
        c = l.rstrip('\n').split('\t')
        if len(c) >= 2 and re.match(r'^[0-9a-fA-F]{8}$', c[1]): DEC.setdefault(int(c[1], 16), c[0])
nosso = set()
for l in open(R + '/build/C/f4/ProjectG_983_prova.map', encoding='latin1'):
    c = l.split()
    if len(c) >= 3 and c[0].startswith('0001:'): nosso.add(c[1])
text = p.secs[0]; base_t = p.base + text[1]; d = p.d[text[3]:text[3] + text[4]]
so = [l.rstrip('\n').split('\t') for l in open(R + '/out/F4/link/imports_so_983.tsv')]
with open(R + '/out/F4/link/imports_so_983_quem.tsv', 'w') as f:
    f.write('dll\tapi\tva_983\tfuncao_983\tunidade_983\tno_nosso_exe\n')
    for dll, nm in so:
        slot = im.get((dll, nm))
        if not slot: f.write('%s\t%s\t-\t(slot não achado)\t-\t-\n' % (dll, nm)); continue
        pat = struct.pack('<I', slot); vis = set()
        for m in re.finditer(re.escape(pat), d):
            va = base_t + m.start()
            i = bisect.bisect_right(FS, va) - 1
            if i < 0 or va >= FN[i][0] + FN[i][1]: continue   # fora de função conhecida (dado/tabela)
            fn = FN[i]
            if fn[0] in vis: continue
            vis.add(fn[0])
            dec = DEC.get(fn[0], '-')
            f.write('%s\t%s\t%08x\t%s\t%s\t%s\n' % (dll, nm, fn[0], dec if dec != '-' else fn[3], fn[2],
                    'sim' if dec in nosso else ('NAO' if dec != '-' else 'sem nome')))
        if not vis: f.write('%s\t%s\t-\t(sem referência no .text)\t-\t-\n' % (dll, nm))
