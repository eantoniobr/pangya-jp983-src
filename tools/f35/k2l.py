#!/usr/bin/env python3
"""k2l.py FONTE.cpp FUNCS.tsv [--aplica] — textos que o exe 983 passa por K2L_Compatibility (00b4ec60) em cada função
própria com par (FUNCS.tsv = saída do cmpfunc) e o estado do mesmo literal na cópia viva da função no fonte:
ok (já embrulhado, direto ou dentro de um K2L(c ? a : b)), cru (literal sem K2L), falta (literal não achado). --aplica embrulha os crus quando a contagem
de usos bate (nº de usos com K2L no 983 == nº de literais iguais na função). --todos: com --aplica, embrulha também quando
a contagem não bate (todo uso cru de um texto que o 983 embrulha naquela função; texto vazio fica de fora)."""
import sys, os, re, struct, capstone
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = open(os.path.join(R, 'ref', 'ProjectG_983_dump.exe'), 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
def off(va):
    r = va - base
    for i in range(ns):
        vs, v, rs, ro = struct.unpack_from('<IIII', d, st + 40 * i + 8)
        if v <= r < v + max(vs, rs): return ro + r - v
tam = {}
for l in open(os.path.join(R, 'map', 'projectg_funcs.tsv')):
    p = l.split('\t')
    if len(p) > 1 and re.fullmatch('[0-9a-f]{8}', p[0]): tam[int(p[0], 16)] = int(p[1])
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
K2L = 0xb4ec60
def textos983(va):
    """lista dos textos (bytes) cujo endereço vai em ecx logo antes de um call K2L"""
    out = []; ecx = []
    for i in md.disasm(d[off(va):off(va) + tam.get(va, 0)], va):
        if i.mnemonic == 'mov' and i.op_str.startswith('ecx, 0x'):
            ecx.append(int(i.op_str[5:], 16))       # um salto pode juntar dois textos no mesmo call
        elif i.mnemonic == 'call' and i.op_str == hex(K2L):
            for a in ecx:
                o = off(a)
                if o: out.append(d[o:d.index(b'\0', o)])
            ecx = []
        elif i.mnemonic == 'call' or (i.mnemonic in ('mov', 'lea', 'xor', 'pop', 'or') and i.op_str.split(',')[0] == 'ecx'):
            ecx = []                                 # outro call ou ecx regravado: o texto não foi para o K2L
    return out
def dec(s):
    b = bytearray(); i = 0
    while i < len(s):
        c = s[i]
        if c != '\\': b += c.encode('latin-1'); i += 1; continue
        n = s[i + 1]
        if n == 'x':
            m = re.match('[0-9a-fA-F]+', s[i + 2:]); b.append(int(m.group(0), 16) & 255); i += 2 + len(m.group(0))
        elif n in '01234567':
            m = re.match('[0-7]{1,3}', s[i + 1:]); b.append(int(m.group(0), 8) & 255); i += 1 + len(m.group(0))
        else:
            b += {'n': b'\n', 't': b'\t', 'r': b'\r', '0': b'\0'}.get(n, n.encode('latin-1')); i += 2
    return bytes(b)
LIT = re.compile(r'"((?:[^"\\\n]|\\.)*)"(?:\s*"((?:[^"\\\n]|\\.)*)")*')
ONE = re.compile(r'"((?:[^"\\\n]|\\.)*)"')
def corpo(src, nome):
    cls, _, fn = nome.rpartition('::')
    pat = re.compile(r'^(?![ \t#/]).*\b' + re.escape(nome) + r'\([^;]*$', re.M)
    ms = [m for m in pat.finditer(src) if not src[m.start():m.end()].lstrip().startswith(('extern', 'inline __declspec'))]
    if not ms:                                       # approachdesc.cpp: Mission_N::BuildDesc vem da macro MISSION(N)
        mm = re.fullmatch(r'Mission_(\d+)::BuildDesc', nome)
        ms = list(re.finditer(r'^MISSION\(%s\)[ \t]*$' % mm.group(1), src, re.M)) if mm else []
    if not ms:                                       # definição recuada dentro de `namespace X {`
        pi = re.compile(r'^([ \t]+)(?![ \t#/]).*(?<![\w:~])' + re.escape(nome) + r'\([^;]*$', re.M)
        mi = [m for m in pi.finditer(src) if '=' not in src[m.start():m.end()].split('(')[0]
              and not src[m.start():m.end()].lstrip().startswith(('return', 'if', 'else', 'extern', 'inline __declspec'))]
        if mi:
            m = mi[-1]; ind = m.group(1); a = src.find('\n' + ind + '{', m.start()); b = src.find('\n' + ind + '}\n', a)
            if a >= 0 and b >= 0: return (a, b + len(ind) + 3)
    if not ms: return None
    m = ms[-1]; a = src.find('\n{', m.start()); b = src.find('\n}\n', a)
    return (a, b + 3) if a >= 0 and b >= 0 else None
def demangle(n):
    """Classe::Método (classe = a mais interna; namespaces caem), construtor/destrutor, função livre ou de namespace anônimo"""
    m = re.match(r'\?\?([01])(\w+)@', n)
    if m: return m.group(2) + '::' + ('~' if m.group(1) == '1' else '') + m.group(2)
    m = re.match(r'\?(\w+)@(?:\?A0x[0-9a-f]+@)?@Y', n)
    if m: return m.group(1)
    m = re.match(r'\?(\w+)@(\w+)@', n)
    if m: return m.group(2) + '::' + m.group(1)
    m = re.match(r'_(\w+)@\d+$', n)
    return m.group(1) if m else None
def dentro(body, pos):
    """o literal em pos está dentro dos parênteses de um K2L_Compatibility( (direto ou em `K2L(c ? a : b)`)"""
    n = 0; i = pos - 1; fim = max(0, pos - 600)
    while i >= fim:
        c = body[i]
        if c in ';{}': return False
        if c == ')': n += 1
        elif c == '(':
            if n: n -= 1
            elif re.search(r'(?:K2L_Compatibility|Translate983)\s*$', body[:i]): return True  # Translate983 = nome da B/C
        i -= 1
    return False
fonte, funcs = sys.argv[1], sys.argv[2]; aplica = '--aplica' in sys.argv; todos = '--todos' in sys.argv
src = open(fonte, encoding='latin-1').read()
edits = []; tot = {'ok': 0, 'cru': 0, 'falta': 0}
for l in open(funcs):
    p = l.rstrip('\n').split('\t')
    if len(p) < 6 or p[2] != '1' or not re.fullmatch('[0-9a-f]{8}', p[5]): continue
    ts = textos983(int(p[5], 16))
    if not ts: continue
    nome = demangle(p[1]); rg = corpo(src, nome) if nome else None
    if not rg: print('SEM_CORPO\t%s\t%d textos' % (p[1], len(ts))); continue
    body = src[rg[0]:rg[1]]
    lits = [(m.start(), m.end(), b''.join(dec(x) for x in ONE.findall(m.group(0)))) for m in LIT.finditer(body)]
    for t in sorted(set(ts)):
        n983 = ts.count(t); ach = [x for x in lits if x[2] == t]
        emb = [x for x in ach if dentro(body, x[0])]
        cru = [x for x in ach if x not in emb]
        est = 'ok' if len(emb) >= n983 else ('cru' if cru else 'falta')
        tot[est] += 1
        if est != 'ok':
            print('%s\t%s\t%s\t983=%d emb=%d cru=%d\t%s' % (est, p[5], nome, n983, len(emb), len(cru), t.decode('cp949', 'replace')))
        if est == 'cru' and aplica and (len(emb) + len(cru) == n983 or (todos and t)):
            for x in cru: edits.append((rg[0] + x[0], rg[0] + x[1]))
print('total: %s; a embrulhar: %d' % (tot, len(edits)))
if aplica and edits:
    for a, b in sorted(set(edits), reverse=True):
        src = src[:a] + 'K2L_Compatibility(' + src[a:b] + ')' + src[b:]
    open(fonte, 'w', encoding='latin-1').write(src)
