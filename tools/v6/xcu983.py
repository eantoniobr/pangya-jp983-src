#!/usr/bin/env python3
"""F4 (frente C): ordem dos inicializadores estáticos (.CRT$XCU) do 983 × a do nosso exe de prova.

983: _initterm(0x00cfcd24, 0x00cfe3b0) em 00c3cc45 (__tmainCRTStartup). Cada entrada é um ??__E (inicializador dinâmico);
a unidade dela sai dos call/jmp/push que ele faz para dentro das faixas de map/projectg_units.tsv (ini983..fim983)
-- o próprio ??__E fica num bloco à parte (.text$yc), fora das faixas.
Nosso: a .map do build/C/f4/ProjectG_983_prova.exe (símbolos 0002:<.CRT$XCU> não aparecem: usamos a ordem dos ??__E na
.text$yc, que é a mesma do .CRT$XCU porque o link junta os dois na ordem dos .obj).
Saída: out/F4/link/xcu983.tsv (ordem, va, unidade 983), out/F4/link/xcu_ordem.tsv (unidade, posição 983, posição nossa)
e um resumo na tela: unidades com inicializador nos dois, inversões de ordem (pares fora de ordem).
"""
import sys, struct, bisect, collections, os
R = '/root/jp983src'
sys.path.insert(0, R + '/tools/v6')
from pe import PE
p = PE(R + '/ref/ProjectG_983_dump.exe')
U = []
for l in open(R + '/map/projectg_units.tsv'):
    c = l.rstrip('\n').split('\t')
    if c[0] == 'unidade' or len(c) < 12 or not c[10] or not c[11]: continue
    try: U.append((int(c[10], 16), int(c[11], 16), os.path.basename(c[0]).rsplit('.', 1)[0].lower()))
    except ValueError: pass
U.sort(); INI = [u[0] for u in U]


def unidade(va):
    i = bisect.bisect_right(INI, va) - 1
    return U[i][2] if i >= 0 and U[i][0] <= va <= U[i][1] else None


def alvos(va, n=80):
    """unidades citadas pelos primeiros n bytes do inicializador (call/jmp rel32, push/mov imm32)"""
    o, r = p.off(va - p.base), []
    d = p.d[o:o + n]
    for i in range(len(d) - 4):
        if d[i] in (0xe8, 0xe9):
            t = va + i + 5 + struct.unpack_from('<i', d, i + 1)[0]
            u = unidade(t)
            if u: r.append(u)
        if d[i] == 0xc3: break
    return r


xs = [p.u32(a) for a in range(0x00cfcd24, 0x00cfe3b0, 4)]
ordem983 = []
with open(R + '/out/F4/link/xcu983.tsv', 'w') as f:
    f.write('ordem\tva\tunidade\n')
    for i, v in enumerate(xs):
        if not v: continue
        a = alvos(v); u = collections.Counter(a).most_common(1)[0][0] if a else '-'
        f.write('%d\t%08x\t%s\n' % (i, v, u))
        if u != '-' and u not in ordem983: ordem983.append(u)
# nosso: ??__E na ordem de endereço, .obj da .map
nosso = []
mp = R + '/build/C/f4/ProjectG_983_prova.map'
ev = []
for l in open(mp, encoding='latin1'):
    c = l.split()
    if len(c) >= 4 and c[1].startswith('??__E') and c[-1].endswith('.obj') and c[0].startswith('0001:'):
        ev.append((int(c[2], 16), c[-1][:-4].lower()))
for _, o in sorted(ev):
    if o not in nosso: nosso.append(o)
pos9 = {u: i for i, u in enumerate(ordem983)}; posn = {u: i for i, u in enumerate(nosso)}
amb = [u for u in ordem983 if u in posn]
inv = 0
seq = [posn[u] for u in amb]
for i in range(len(seq)):
    for j in range(i + 1, len(seq)):
        if seq[i] > seq[j]: inv += 1
with open(R + '/out/F4/link/xcu_ordem.tsv', 'w') as f:
    f.write('unidade\tpos983\tpos_nosso\n')
    for u in sorted(set(ordem983) | set(nosso), key=lambda u: (pos9.get(u, 9999), posn.get(u, 9999))):
        f.write('%s\t%s\t%s\n' % (u, pos9.get(u, '-'), posn.get(u, '-')))
tot = len(amb) * (len(amb) - 1) // 2
print('983: %d entradas no .CRT$XCU (%d nulas), %d com unidade achada, %d unidades distintas'
      % (len(xs), xs.count(0), sum(1 for l in open(R + '/out/F4/link/xcu983.tsv') if not l.rstrip().endswith('-')) - 1, len(ordem983)))
print('nosso: %d ??__E em %d .obj' % (len(ev), len(nosso)))
print('unidades com inicializador nos dois: %d; pares fora de ordem: %d de %d (%.1f%%)' % (len(amb), inv, tot, 100.0 * inv / max(tot, 1)))
# nº de entradas do .CRT$XCU do nosso exe (pela .map) e quantas chamam K2L_Compatibility (nos dois)
import re
tam = 0; k2l_n = None
for l in open(mp, encoding='latin1'):
    m = re.match(r'^ 0002:([0-9a-f]{8}) ([0-9a-f]{8})H \.CRT\$XCU ', l)
    if m: ini, tam = int(m.group(1), 16), int(m.group(2), 16)
    c = l.split()
    if len(c) >= 3 and c[1] == '?K2L_Compatibility@@YIPBDPBD@Z' and c[0].startswith('0001:'): k2l_n = int(c[2], 16)
pn = PE(R + '/build/C/f4/ProjectG_983_prova.exe')
rd = [s_ for s_ in pn.secs if s_[0] == '.rdata'][0][1] + pn.base
xn = [pn.u32(rd + ini + 4 * i) for i in range(tam // 4)] if tam else []


def chama(pe_, v, alvo):
    o = pe_.off(v - pe_.base); d_ = pe_.d[o:o + 40]
    return any(d_[i] == 0xe8 and v + i + 5 + struct.unpack_from('<i', d_, i + 1)[0] == alvo for i in range(len(d_) - 4))
k9 = sum(1 for v in xs if v and chama(p, v, 0x00b4ec60))
kn = sum(1 for v in xn if v and k2l_n and chama(pn, v, k2l_n))
print('entradas não nulas do .CRT$XCU: nosso %d × 983 %d; das quais chamam K2L_Compatibility: nosso %d × 983 %d '
      '(fora essas: %d × %d)' % (sum(1 for v in xn if v), len(xs) - xs.count(0), kn, k9,
                                sum(1 for v in xn if v) - kn, len(xs) - xs.count(0) - k9))
