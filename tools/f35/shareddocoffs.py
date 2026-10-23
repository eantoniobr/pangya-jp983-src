#!/usr/bin/env python3
"""shareddocoffs.py [--aplica] [--ref ARQ_645] ARQ — troca deslocamentos crus do KR 645 no CSharedDoc pelo layout do 983 (s95).
Mesma regra do golfdocoffs.py: só mexe nas linhas iguais às do fonte do 645 (M983(x) lido como x); linha nova sai em "fora".
Tabelas: out/F3.5/s95/tabelas/cshareddoc_{645,983}_achatado.txt (tools/f35/achata.py 645|983 CSharedDoc): cada folha com caminho;
o 645 → caminho → 983. Formas:
  SHAREDDOC_{UCHAR,ULONG}(c)                → Doc()->caminho quando o tipo da folha é o do acesso; senão SHAREDDOC_X(novo)
  SHAREDDOC_{UCHAR,ULONG}(I * 0xb92 + c)    → Doc()->m_userInfo[I].caminho (sUserInfo 0xb92 → 0x31c6) ou I * 0x31c6 + novo
  SHAREDDOC_{UCHAR,ULONG}(I * 0xeb + c)     → Doc()->m_holeStatistics[I].caminho (0xeb → 0x109) ou I * 0x109 + novo
  (char*)/(unsigned char*)Doc() + c, Doc() + I * 0xb92 + c, `E + c` / `c + E` dentro do SHAREDDOC_*  → só o número
list/vector: +4/+8 do VC7.1 viram +0/+4 do VS2010. Número fora de folha mas 1 antes de um array (`idx + 0x45f1` = m_holeOrder[idx - 1]) traduz pelo array. Saída: contagens + listas
"fora" (não tocadas) e "sem" (não traduzidas)."""
import re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T = ROOT + '/out/F3.5/s95/tabelas/cshareddoc_%s_achatado.txt'
def load(f):
    L = []
    for l in open(f):
        p = l.split()
        if len(p) == 4 and p[0].startswith('0x'): L.append((int(p[0], 16), int(p[1]), p[2], p[3].replace('_', ' ')))
    return L
A = load(T % '645'); B = load(T % '983'); BD = {c: (o, t, ti) for o, t, c, ti in B}
import bisect
AO = [f[0] for f in A]
def folha(x):
    i = bisect.bisect_right(AO, x) - 1
    while i >= 0 and A[i][0] == AO[i] and not (A[i][0] <= x < A[i][0] + max(A[i][1], 1)):
        if A[i][0] < x - 0x40: break
        i -= 1
    if i >= 0 and A[i][0] <= x < A[i][0] + max(A[i][1], 1): return A[i]
    return None
def novo(x):
    """(novo, caminho, resto, tipo983, tamanho983) ou None"""
    f = folha(x)
    if f and f[2] in BD:
        o, t, c, ti = f; bo, bt, bti = BD[c]
        r = x - o
        # VC7.1 (645): list/vector com o alocador ANTES (cabeça/_Myfirst em +4, tamanho/_Mylast em +8); VS2010 (983): em +0/+4 (sonda s95)
        if r in (4, 8) and re.match(r'std::(list|vector)<', ti) and re.match(r'std::(list|vector)<', bti): r -= 4
        if r < max(bt, 1): return (bo + r, c, r, bti, bt)
    f = folha(x + 1)  # 1 antes de um array: base - 1
    if f and f[0] == x + 1 and re.search(r'\[0\]$', f[2]) and f[2] in BD:
        return (BD[f[2]][0] - 1, None, -1, None, None)
    return None
# membros que no 983 saíram do objeto e ficaram estáticos no nosso cabeçalho (PROVISÓRIO lá): (char*)Doc() + c -> (char*)&CSharedDoc::m_x
EST = set(re.findall(r'^\s*static [\w ]+?\b(m_\w+);', open(ROOT + '/src/projectg/shareddoc.h', encoding='latin-1').read(), re.M))
def estatico(x):
    f = folha(x)
    if f and f[2] in EST and f[0] == x: return f[2]
    return None
U0 = BD['m_userInfo[0].roomIndex'][0]; U0_645 = 0x12d0; H0 = BD['m_holeStatistics[0].dwDrive'][0]; H0_645 = 0x4118
PASSO = {'0xb92': ('m_userInfo', U0_645, 0xb92, U0, 0x31c6), '0xeb': ('m_holeStatistics', H0_645, 0xeb, H0, 0x109)}
TIPO = {'UCHAR': ('unsigned char',), 'ULONG': ('unsigned long', 'DWORD')}

a = sys.argv[1:]; ap = '--aplica' in a; a = [x for x in a if x != '--aplica']
ref = None
if '--ref' in a: i = a.index('--ref'); ref = a[i + 1]; del a[i:i + 2]
fn = a[0]; ref = ref or '/root/rebang/source/client/ProjectG/' + os.path.basename(fn)
NORM = lambda l: re.sub(r'M983\((0x[0-9a-f]+|\d+)\)', r'\1', l.strip())
# a s94 (golfdocoffs.py) já trocou o CGolfDoc nestas linhas: GOLFDOC()->m_x / GOLFDOC_T(0x..) / doc->m_x contam como iguais
GD = re.compile(r'GOLFDOC(?:\(\)->[\w.]+|_\w+\(0x[0-9a-f]+\))|\bdoc->m_\w+')
NORM0 = NORM; NORM = lambda l: GD.sub('G', NORM0(l))
L645 = set(NORM(l) for l in open(ref, encoding='latin-1'))
IDX = r'(?:[\w.]+(?:\(\))?(?:->\w+)?)'
P_MC = re.compile(r'SHAREDDOC_(UCHAR|ULONG)\((0x[0-9a-f]+|\d+)\)')
P_MI = re.compile(r'SHAREDDOC_(UCHAR|ULONG)\((%s) \* (0xb92|0xeb) \+ (0x[0-9a-f]+)\)' % IDX)
P_ME = re.compile(r'SHAREDDOC_(UCHAR|ULONG)\(((?:[^()]|\([^()]*\))*?) \+ (0x[0-9a-f]+)\)|SHAREDDOC_(UCHAR|ULONG)\((0x[0-9a-f]+) \+ ([^()]+)\)')
# s95: `CSharedDoc* shared = Doc();` (e `pDoc`, quando o arquivo só tem pDoc do tipo CSharedDoc) é usado do mesmo jeito
_tp = set(re.findall(r'(\w+)\* *pDoc *=', open(fn, encoding='latin-1').read()))
D = r'(?:Doc\(\)|shared|pDoc|CSharedDoc::Instance\(\))' if _tp == {'CSharedDoc'} else r'(?:Doc\(\)|shared|CSharedDoc::Instance\(\))'  # s96: Instance()
P_PI = re.compile(r'(Doc\(\) \+ (?:\(?)%s \* )(0xb92|0xeb)( \+ )(0x[0-9a-f]+)' % IDX)
P_PC = re.compile(r'(\((?:const )?(?:(?:unsigned )?char|bool)\s*\*\)\s*' + D + r' \+ )(0x[0-9a-f]+)\b(?! \*)')
P_PE = re.compile(r'(\((?:const )?(?:unsigned )?char\s*\*\)\s*' + D + r' \+ [\w.]+(?:\([^()]*\))? \+ )(0x[0-9a-f]+)\b')
P_PR = re.compile(r'(\((?:const )?(?:unsigned )?char\s*\*\)\s*' + D + r' \+ )(0x[0-9a-f]+)( \+ \w+ \* )(0xb92|0xeb)\b')
# invólucros locais (s95): o deslocamento é o último argumento; PlayerCard* = Doc() + jogador * 0xb92 + off (sUserInfo)
W1 = re.compile(r'\b(DOC_AT|SDOC)\(([\w:<> *]+), (0x[0-9a-f]+)\)')
W2 = re.compile(r'\b(DocInt|DocByte|DOC_I64|DOC_U32|DOC_U8|SD_BYTE|SD_INT)\((0x[0-9a-f]+)\)')
# argumento com expressão: SDOC(T, a + b * 0xb92) / DocInt(i * 0xb92 + c) / DocByte(c + i) ...
W4 = re.compile(r'\b(DOC_AT\([\w:<> *]+, |SDOC\([\w:<> *]+, |DocInt\(|DocByte\(|DOC_I64\(|DOC_U32\(|DOC_U8\()((?:[^()]|\((?:[^()]|\([^()]*\))*\))+?)\)')
TXT = open(fn, encoding='latin-1').read()
VU = set(re.findall(r'\b(\w+) \+= 0xb92;', TXT))  # variáveis que andam de sUserInfo em sUserInfo (expOfs, off...)
def passo(c, p6):
    """array do 645 com elemento de p6 bytes que contém c: (passo 983, base 983 do elemento 0 + resto) ou None"""
    f = folha(c)
    if not f: return None
    cam = f[2]
    for m in re.finditer(r'\[0\]', cam):
        pre = cam[:m.start()]
        a0 = [x for x in A if x[2].startswith(pre + '[0]')][:1]; a1 = [x for x in A if x[2].startswith(pre + '[1]')][:1]
        if a0 and a1 and a1[0][0] - a0[0][0] == p6:
            b0 = [x for x in B if x[2].startswith(pre + '[0]')][:1]; b1 = [x for x in B if x[2].startswith(pre + '[1]')][:1]
            r = novo(c)
            if b0 and b1 and r: return (b1[0][0] - b0[0][0], r[0])
    return None
def targ(e):
    termos = [t.strip() for t in e.split(' + ')]
    cs = [i for i, t in enumerate(termos) if re.fullmatch(r'0x[0-9a-f]+', t) and int(t, 16) >= 0x40]
    if len(cs) != 1: return None
    c = int(termos[cs[0]], 16); out = list(termos); ps = None
    for i, t in enumerate(termos):
        m = re.fullmatch(r'(.+?) \* (0x[0-9a-f]+|\d+)', t)
        if m: ps = (i, int(m.group(2), 0), m.group(1))
    if ps and ps[1] in (0xb92, 0xeb) or any(t in VU for t in termos):
        nome, b6, p6, b9, p9 = PASSO['0x%x' % (ps[1] if ps else 0xb92)]
        r = novo(c)
        if not r or not r[1] or not r[1].startswith(nome + '[0]'): return None
        out[cs[0]] = '\x01%x' % r[0]
        if ps: out[ps[0]] = '%s * \x01%x' % (ps[2], p9)
        return ' + '.join(out), r[1]
    if ps:
        q = passo(c, ps[1])
        if not q: return None
        out[cs[0]] = '\x01%x' % q[1]; out[ps[0]] = '%s * \x01%x' % (ps[2], q[0])
        return ' + '.join(out), folha(c)[2] + ' (passo 0x%x)' % q[0]
    r = novo(c)
    if not r: return None
    out[cs[0]] = '\x01%x' % r[0]
    return ' + '.join(out), r[1] or '(1 antes do array)'
W3 = re.compile(r'\b(PlayerCardInt|PlayerCardByte)\(([^,()]+(?:\([^()]*\))?(?:->\w+)?), (0x[0-9a-f]+)\)')
WN = re.compile(r'\b(DOC_AT|SDOC|DocInt|DocByte|DOC_I64|DOC_U32|DOC_U8|SD_BYTE|SD_INT|PlayerCardInt|PlayerCardByte)\(')
linhas = open(fn, encoding='latin-1').read().split('\n')
nt = nm = 0; fora = []; sem = []; feitos = []
for k, l in enumerate(linhas):
    if '#define' in l or ('SHAREDDOC_' not in l and 'Doc() +' not in l and 'CSharedDoc::Instance() +' not in l and not re.search(r'char\*\)\s*(shared|pDoc) \+', l)
                          and not WN.search(l)): continue
    if NORM(l) not in L645:
        fora.append((k + 1, l.strip())); continue
    def membro(t, r):
        return r and r[2] == 0 and r[1] and r[3] in TIPO[t] and r[4] == {'UCHAR': 1, 'ULONG': 4}[t]
    def mc(m):
        global nt, nm
        t, c = m.group(1), int(m.group(2), 0); r = novo(c)
        if not r: sem.append((k + 1, m.group(0))); return m.group(0)
        nt += 1; feitos.append((k + 1, m.group(0), r[1]))
        if membro(t, r): nm += 1; return 'Doc()->' + r[1]
        return 'SHAREDDOC_%s(\x01%x)' % (t, r[0])
    def mi(m):
        global nt, nm
        t, i, ps, c = m.group(1), m.group(2), m.group(3), int(m.group(4), 16)
        nome, b6, p6, b9, p9 = PASSO[ps]; inner = c - b6
        if not 0 <= inner < p6: sem.append((k + 1, m.group(0))); return m.group(0)
        r = novo(b6 + inner)
        if not r or not r[1] or not r[1].startswith(nome + '[0]'): sem.append((k + 1, m.group(0))); return m.group(0)
        nt += 1; feitos.append((k + 1, m.group(0), r[1]))
        if membro(t, r): nm += 1; return 'Doc()->%s[%s]%s' % (nome, i, r[1][len(nome) + 3:])
        return 'SHAREDDOC_%s(%s * \x01%x + \x01%x)' % (t, i, p9, r[0])
    def me(m):
        global nt
        if m.group(1): t, e, c, pre = m.group(1), m.group(2), int(m.group(3), 16), True
        else: t, c, e, pre = m.group(4), int(m.group(5), 16), m.group(6), False
        r = novo(c)
        if not r: sem.append((k + 1, m.group(0))); return m.group(0)
        nt += 1; feitos.append((k + 1, m.group(0), r[1] or '(1 antes do array)'))
        return 'SHAREDDOC_%s(%s + \x01%x)' % (t, e, r[0]) if pre else 'SHAREDDOC_%s(\x01%x + %s)' % (t, r[0], e)
    def pi(m):
        global nt
        nome, b6, p6, b9, p9 = PASSO[m.group(2)]; inner = int(m.group(4), 16) - b6
        r = novo(b6 + inner) if 0 <= inner < p6 else None
        if not r: sem.append((k + 1, m.group(0))); return m.group(0)
        nt += 1; feitos.append((k + 1, m.group(0), r[1]))
        return m.group(1) + '\x01%x' % p9 + m.group(3) + '\x01%x' % r[0]
    def pr(m):  # Doc() + base + i * passo
        global nt
        nome, b6, p6, b9, p9 = PASSO[m.group(4)]; c = int(m.group(2), 16); r = novo(c)
        if not r or not r[1] or not r[1].startswith(nome + '[0]'): sem.append((k + 1, m.group(0))); return m.group(0)
        nt += 1; feitos.append((k + 1, m.group(0), r[1]))
        return m.group(1) + '\x01%x' % r[0] + m.group(3) + '\x01%x' % p9
    def pc(m):
        global nt
        c = int(m.group(2), 16); r = novo(c)
        e = None if r else estatico(c)
        if e and m.group(1).endswith('Doc() + '):
            nt += 1; feitos.append((k + 1, m.group(0), 'estático ' + e))
            return m.group(1)[:-len('Doc() + ')] + '&CSharedDoc::' + e
        if not r: sem.append((k + 1, m.group(0))); return m.group(0)
        nt += 1; feitos.append((k + 1, m.group(0), r[1] or '(1 antes do array)'))
        return m.group(1) + '\x01%x' % r[0]
    WT = {'SD_BYTE': 'unsigned char', 'SD_INT': 'int', 'DocInt': 'int', 'DocByte': 'unsigned char', 'DOC_I64': '__int64', 'DOC_U32': 'unsigned int', 'DOC_U8': 'unsigned char'}
    def west(m, tipo, c):
        global nt
        e = estatico(c)
        if not e: return None
        nt += 1; feitos.append((k + 1, m.group(0), 'estático ' + e))
        return '(*(%s*)&CSharedDoc::%s)' % (tipo, e)
    def w1(m):
        global nt
        c = int(m.group(3), 16); r = novo(c)
        if not r: x = west(m, m.group(2), c); 
        if not r and x: return x
        if not r: sem.append((k + 1, m.group(0))); return m.group(0)
        nt += 1; feitos.append((k + 1, m.group(0), r[1] or '(1 antes do array)'))
        return '%s(%s, \x01%x)' % (m.group(1), m.group(2), r[0])
    def w2(m):
        global nt
        c = int(m.group(2), 16); r = novo(c)
        if not r: x = west(m, WT[m.group(1)], c)
        if not r and x: return x
        if not r: sem.append((k + 1, m.group(0))); return m.group(0)
        nt += 1; feitos.append((k + 1, m.group(0), r[1] or '(1 antes do array)'))
        return '%s(\x01%x)' % (m.group(1), r[0])
    def w3(m):
        global nt
        c = int(m.group(3), 16); r = novo(c)
        if not r or not r[1] or not r[1].startswith('m_userInfo[0]'): sem.append((k + 1, m.group(0))); return m.group(0)
        nt += 1; feitos.append((k + 1, m.group(0), r[1]))
        return '%s(%s, \x01%x)' % (m.group(1), m.group(2), r[0])
    def w4(m):
        global nt
        if re.fullmatch(r'0x[0-9a-f]+', m.group(2)) or '\x01' in m.group(2): return m.group(0)
        r = targ(m.group(2))
        if not r: sem.append((k + 1, m.group(0))); return m.group(0)
        nt += 1; feitos.append((k + 1, m.group(0), r[1]))
        return m.group(1) + r[0] + ')'
    l = W3.sub(w3, W2.sub(w2, W1.sub(w1, l)))
    l = W4.sub(w4, l)
    if VU: l = re.sub(r'\b(%s) \+= 0xb92;' % '|'.join(VU), r'\1 += 0x31c6;', l)
    l = l.replace('\x01', '0x')
    l2 = P_MI.sub(mi, l); l2 = P_MC.sub(mc, l2); l2 = P_ME.sub(me, l2)
    l2 = P_PR.sub(pr, l2); l2 = P_PI.sub(pi, l2); l2 = P_PE.sub(pc, l2); l2 = P_PC.sub(pc, l2)
    l2 = l2.replace('\x01', '0x')
    if l2 != linhas[k]: linhas[k] = l2
    elif 'SHAREDDOC_' in l or re.search(r'(Doc\(\)|shared) \+ ', l) or WN.search(l): sem.append((k + 1, 'linha: ' + l.strip()[:140]))
print('%s: %d trocas (%d por membro); %d fora do 645 (não mexidas); %d sem tradução' % (fn, nt, nm, len(fora), len(sem)))
for k, s, c in feitos: print('troca\t%d\t%s\t%s' % (k, s, c))
for k, s in fora: print('fora\t%d\t%s' % (k, s[:150]))
for k, s in sem: print('sem\t%d\t%s' % (k, s))
if ap: open(fn, 'w', encoding='latin-1', newline='').write('\n'.join(linhas))
