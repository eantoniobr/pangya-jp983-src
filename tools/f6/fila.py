#!/usr/bin/env python3
"""F6: gera out/F6/EMIT_FILA.tsv (funcoes __declspec(naked) de src/projectg) com o VA do 983 pelo map/projectg.tsv.
Ordem: arquivos da partida/console primeiro, depois o resto por arquivo. Preserva o estado das linhas ja existentes."""
import os, re, glob, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PARTIDA = ['golfrule', 'camerawork', 'scoreboard', 'golfplayer', 'club', 'particleparty', 'fxspray', 'npc', 'quadtree',
           'resultdlg', 'taskmain', 'gamerule', 'ball', 'golfbg', 'hole', 'console', 'gmtoolkit']
mapa = {}
for l in open(os.path.join(R, 'map/projectg.tsv'), encoding='utf-8', errors='replace'):
    if l.startswith('#'): continue
    p = l.rstrip('\n').split('\t')
    if len(p) < 2: continue
    m = re.match(r'\?(\w+)@(\w+)@@', p[0])  # ?Func@Class@@
    if m: mapa.setdefault('%s::%s' % (m.group(2), m.group(1)), []).append(p[1])
    else:
        m = re.match(r'\?(\w+)@@', p[0])
        if m: mapa.setdefault(m.group(1), []).append(p[1])
fila = os.path.join(R, 'out/F6/EMIT_FILA.tsv')
estado = {}
if os.path.exists(fila):
    for l in open(fila, encoding='utf-8'):
        p = l.rstrip('\n').split('\t')
        if len(p) >= 5 and p[0] != 'arquivo': estado[(p[0], p[1])] = p[3:]
rx = re.compile(r'__declspec\(naked\)\s+[^(]*?([\w:~]+)\s*\(')
linhas = []
for f in sorted(glob.glob(os.path.join(R, 'src/projectg/**/*.cpp'), recursive=True)):
    rel = os.path.relpath(f, R)
    txt = open(f, encoding='latin-1').read().split('\n')
    # estado do pre-processador com /DREBANG_SEMANTIC_ONLY (flag do exe, tools/f32/pgbuild.py DEFS): 1 ativo, 0 morto, None ?
    pilha, ativo = [], []
    for l in txt:
        t = l.strip()
        if t.startswith('#if'):
            if re.match(r'#ifndef\s+REBANG_SEMANTIC_ONLY\b', t) or re.match(r'#if\s+0\b', t) or \
               re.match(r'#if\s+!\s*defined\s*\(?\s*REBANG_SEMANTIC_ONLY', t): v = 0
            elif re.match(r'#ifdef\s+REBANG_SEMANTIC_ONLY\b', t) or re.match(r'#if\s+1\b', t): v = 1
            else: v = None
            pilha.append(v)
        elif t.startswith('#else') and pilha:
            pilha[-1] = None if pilha[-1] is None else 1 - pilha[-1]
        elif t.startswith('#elif') and pilha:
            pilha[-1] = None if pilha[-1] != 1 else 0
        elif t.startswith('#endif') and pilha:
            pilha.pop()
        ativo.append(0 if 0 in pilha else (None if None in pilha else 1))
    for i, l in enumerate(txt):
        m = rx.search(l)
        if not m: continue
        nome = m.group(1)
        if nome.endswith('Funclets'): continue  # dados de EH: saem junto com a funcao
        ctx = '\n'.join(txt[max(0, i - 6):i])
        tem_c = 'C version is in the #else' in ctx
        a = ativo[i]
        vas = mapa.get(nome, [])
        va = vas[0] if len(vas) == 1 else ('?' if not vas else 'ambiguo:' + ','.join(vas[:3]))
        base = os.path.splitext(os.path.basename(f))[0]
        pri = PARTIDA.index(base) if base in PARTIDA else 99
        linhas.append((pri, rel, i + 1, nome, va, ('MORTO' if a == 0 else ('ATIVO' if a == 1 else 'ATIVO?'))))
linhas.sort(key=lambda x: (x[0], x[1], x[2]))
with open(fila, 'w', encoding='utf-8') as o:
    o.write('arquivo\tfuncao\tVA983\testado\tlinha\tobs\n')
    for pri, rel, ln, nome, va, ob in linhas:
        st = estado.get((rel, nome), ['pendente'])
        o.write('%s\t%s\t%s\t%s\t%d\t%s\n' % (rel, nome, va, st[0], ln, ob))
print(len(linhas), 'funcoes')
