#!/usr/bin/env python3
"""rivaloffs.py [--aplica] ARQ — sRivalData cru do KR 645 (0x190 = 400 bytes) → 983 (0x1b8) nos registros de m_rivalList, e o
CGolfDoc cru lido por `Doc()->m_pGolfDoc + c` (faixas do golfdocoffs.py). Sessão 95 (scoreboard.cpp). Formas (texto inteiro, com
quebras de linha):
  X * 400 + <primeiro do vector> [+ c]     (primeiro = SDOC(int, 0x1042c) / SHAREDDOC_ULONG(0x1042c), já no 983)
  c + X * 400 + <primeiro>                  <primeiro> + X * 400      (<último> - <primeiro>) / 400
  `rec + c` nas funções que fazem `int rec = ... 400 ... <primeiro>`
--golfdoc liga a parte do CGolfDoc, que NÃO é idempotente (0x168 → 0x17c → 0x190 se rodar duas vezes): só uma vez por arquivo
(scoreboard.cpp já passou na s95). Tabelas: out/F3.5/s95/tabelas/srivaldata_{645,983}_achatado.txt (tools/f35/achata.py 645|983 sRivalData)."""
import re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.argv, args = sys.argv[:1], sys.argv[1:]
T = ROOT + '/out/F3.5/s95/tabelas/srivaldata_%s_achatado.txt'
def load(f):
    return [(int(p[0], 16), int(p[1]), p[2]) for p in (l.split() for l in open(f)) if len(p) == 4]
A = load(T % '645'); B = {c: o for o, t, c in load(T % '983')}
def rv(x):
    f = [q for q in A if q[0] <= x < q[0] + max(q[1], 1)]
    if not f or f[-1][2] not in B: return None
    o, t, c = f[-1]; return B[c] + x - o, c
FA = [(0x0, 0x14, 0), (0x58, 0x164, 0x10), (0x168, 0x196, 0x14), (0x198, 0x3ac, 0x18), (0x440, 0x46e, 0x1c), (0x46e, 0x8c0, 0x20)]
def gd(o):
    for a, b, d in FA:
        if a <= o < b: return o + d
    return None
ap = '--aplica' in args; fn = [x for x in args if not x.startswith('--')][0]
s = open(fn, encoding='latin-1').read(); log = []
PRIM = r'(?:SDOC\(int, 0x1042c\)|SHAREDDOC_ULONG\(0x1042c\))'
NUM = lambda v: '0x%x' % v
def lin(pos): return s.count('\n', 0, pos) + 1
def r_a(m):  # X * 400 + PRIM [+ c]
    out = m.group(1) + '0x1b8' + m.group(2)
    if m.group(3):
        r = rv(int(m.group(3), 0))
        if not r: log.append(('sem', lin(m.start()), m.group(0))); return m.group(0)
        out += NUM(r[0]); log.append(('troca', lin(m.start()), r[1]))
    else: log.append(('troca', lin(m.start()), 'passo'))
    return out
s = re.sub(r'(\*\s*)400(\s*\+\s*' + PRIM + r'(?:\s*\+\s*)?)((?:0x[0-9a-f]+|\d+)(?![\w*]))?', r_a, s)
def r_b(m):  # c + X * 400 + PRIM (c antes)
    r = rv(int(m.group(1), 0))
    if not r: log.append(('sem', lin(m.start()), m.group(0))); return m.group(0)
    log.append(('troca', lin(m.start()), r[1])); return '+ ' + NUM(r[0]) + m.group(2)
s = re.sub(r'\+ (0x[0-9a-f]+)(\s*\+\s*\(unsigned int\)\w+ \* 0x1b8 \+ ' + PRIM + ')', r_b, s)
s, n1 = re.subn(r'(' + PRIM + r' \+ \(unsigned int\)\w+ \* )400\b', r'\g<1>0x1b8', s)
s, n2 = re.subn(r'(\(SDOC\(int, 0x10430\) - SDOC\(int, 0x1042c\)\) / )400\b', r'\g<1>0x1b8', s)
log += [('troca', 0, 'passo (n * 400)')] * n1 + [('troca', 0, 'passo (/ 400)')] * n2
# rec + c nas funções com `int rec = ... 0x1b8 ... PRIM`
L = s.split('\n'); i = 0
while i < len(L):
    if re.search(r'\bint rec = .*0x1b8.*1042c|\bint rec = .*1042c.*0x1b8', L[i]):
        j = i + 1; dep = 0
        while j < len(L) and not re.match(r'^\S', L[j]):  # até o fim da função (próxima linha na coluna 0)
            def r_c(m):
                r = rv(int(m.group(1), 0))
                if not r: log.append(('sem', j + 1, m.group(0))); return m.group(0)
                log.append(('troca', j + 1, r[1])); return '(rec + ' + NUM(r[0]) + ')'
            L[j] = re.sub(r'\(rec \+ (0x[0-9a-f]+|\d+)\)', r_c, L[j]); j += 1
        i = j
    i += 1
s = '\n'.join(L)
def r_g(m):
    o = int(m.group(2), 16); n = gd(o)
    if n is None: log.append(('sem', lin(m.start()), m.group(0))); return m.group(0)
    log.append(('troca', lin(m.start()), 'CGolfDoc 0x%x -> 0x%x' % (o, n))); return m.group(1) + NUM(n)
if '--golfdoc' in args: s = re.sub(r'(\((?:unsigned )?char\s*\*\)\s*Doc\(\)->m_pGolfDoc \+ )(0x[0-9a-f]+)', r_g, s)
print('%s: %d trocas, %d sem' % (fn, sum(1 for x in log if x[0] == 'troca'), sum(1 for x in log if x[0] == 'sem')))
for x in log: print('%s\t%d\t%s' % x)
for k, l in enumerate(s.split('\n')):
    if re.search(r'\b400\b', l) and not re.search(r'400\.|0x400|rb_real|_400', l): print('resta\t%d\t%s' % (k + 1, l.strip()[:140]))
if ap: open(fn, 'w', encoding='latin-1', newline='').write(s)
