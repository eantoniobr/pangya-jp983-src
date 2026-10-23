#!/usr/bin/env python3
"""initcmp.py Classe cabeçalho fonte.cpp VA_INI [prefixo] — confere o layout de uma tela Fresh com herança múltipla contra o 983:
para cada ON_FRESH_*(nome, FRCMD_INIT, Classe::Handler) do fonte, pega o campo que o handler grava no nosso código
(1º `m_x =` do corpo) e o deslocamento dele no nosso build (offs.py --aberto), e compara com o deslocamento que o handler
do mesmo nome de controle grava no 983 (msgmap.py VA_INI = inicializador estático do mapa). Saída: nome, campo, nosso,
983, delta; no fim os nomes de controle com Init só no 983 (campo novo) e só no nosso fonte (campo que saiu)."""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import msgmap as M, offs as O
cls, hdr, cpp, va = sys.argv[1:5]; pre = sys.argv[5] if len(sys.argv) > 5 else ''
src = open(cpp, encoding='latin-1').read()
O.OPEN = True
mine = dict((n, v) for n, v in O.measure(cls, O.fields(cls, hdr), (), os.path.abspath(hdr).replace('/', '\\\\').join(['Z:', ''])))
def field(h):
    m = re.search(r'\n\w[^\n;]*\b%s::%s\s*\([^)]*\)\s*\{(.*?)\n\}' % (cls, h), src, re.S)
    f = re.search(r'\b(m_\w+)\s*=[^=]', m.group(1)) if m else None
    return f.group(1) if f else None
ini = {}
for m in re.finditer(r'ON_FRESH_\w+\(\s*"([^"]+)",\s*FRCMD_INIT,\s*(\w+)::(\w+)\)', src):
    if m.group(2) == cls and m.group(1).startswith(pre): ini.setdefault(m.group(1), m.group(3))
new = {}
for slot, h in M.entries(int(va, 16), 0x8000):
    import struct
    name, cmd = struct.unpack_from('<II', M.P.d, M.P.off(slot) + 16); nm = M.P.cstr(name) if name else None
    if nm and cmd == 1 and nm.startswith(pre) and nm not in new: new[nm] = (h, M.stores(h))
bad = 0
for nm, h in ini.items():
    f = field(h); o = mine.get(f); n = new.get(nm)
    n0 = int(n[1][0], 16) if n and n[1] else None
    st = 'sem Init no 983' if not n else ('?' if o is None or n0 is None else ('=' if o == n0 else '%+d' % (n0 - o)))
    if st != '=': bad += 1
    print('%-40s %-28s nosso %-6s 983 %-6s %s' % (nm, f or '(%s)' % h, '0x%x' % o if o is not None else '-', '0x%x' % n0 if n0 is not None else '-', st))
for nm, (h, w) in new.items():
    if nm not in ini: print('%-40s %-28s nosso %-6s 983 %-6s só no 983 (handler %08x)' % (nm, '-', '-', w[0] if w else '-', h))
print('%d controles com Init no fonte, %d não conferem' % (len(ini), bad))
