#!/usr/bin/env python3
"""F6: tira o ramo naked MORTO de uma funcao (o exe compila com /DREBANG_SEMANTIC_ONLY: so o #else em C++ entra).
Uso: tira_naked.py ARQUIVO.cpp Classe::Funcao [N]  -> apaga '#ifndef REBANG_SEMANTIC_ONLY'..'#else' e o '#endif' casado.
N (C404) = qual sobrecarga (1 = a primeira naked do nome no arquivo, 'todas' = todas, de baixo para cima).
Recusa se o bloco tiver mais de uma funcao, funclets de EH ou nao tiver #else."""
import re, sys
arq, nome = sys.argv[1], sys.argv[2]
L = open(arq, encoding='latin-1', newline='').read().split('\n')
alvo = [i for i, l in enumerate(L) if re.search(r'__declspec\(naked\)\s+[^(]*?\b' + re.escape(nome) + r'\s*\(', l)]
qual = sys.argv[3] if len(sys.argv) > 3 else None
if qual == 'todas' and len(alvo) > 1:
    import subprocess
    for k in range(len(alvo), 0, -1):
        r = subprocess.call([sys.executable, sys.argv[0], arq, nome, str(k)])
        if r: sys.exit(r)
    sys.exit(0)
if qual and qual != 'todas':
    if not 1 <= int(qual) <= len(alvo): sys.exit('naked de %s: so %d ocorrencias' % (nome, len(alvo)))
    alvo = [alvo[int(qual) - 1]]
if len(alvo) != 1: sys.exit('naked de %s: %d ocorrencias (use N ou todas)' % (nome, len(alvo)))
n = alvo[0]
# (C396) o bloco pode abrir com varios '#pragma comment(linker, ...)' entre o #ifndef e o naked
# (C404) e tambem '#define'/'#undef' (RB_XDATA, macros locais do naked)
ini = next(i for i in range(n, max(n - 400, 0), -1) if L[i].startswith('#') and not L[i].startswith(('#pragma', '#define', '#undef')))
if not re.match(r'#ifndef\s+REBANG_SEMANTIC_ONLY\s*$', L[ini]): sys.exit('antes do naked: %r' % L[ini])
d, els, fim = 0, None, None
for i in range(ini + 1, len(L)):
    t = L[i].strip()
    if t.startswith('#if'): d += 1
    elif t.startswith('#endif'):
        if d == 0: fim = i; break
        d -= 1
    elif t.startswith('#else') and d == 0: els = i
if els is None or fim is None: sys.exit('sem #else/#endif')
corpo = '\n'.join(L[ini:els])
# (C404) TIRA_FORCA=1 aceita bloco com funclets/varias naked: o lote so mantem se o .obj sair igual (objeq)
import os
if os.environ.get('TIRA_FORCA') != '1' and (len(re.findall(r'__declspec\(naked\)', corpo)) != 1 or 'Funclets' in corpo or 'ehfunclets' in corpo):
    sys.exit('bloco com mais de uma funcao ou funclets: tratar a mao')
print('%s: apaga %d..%d (naked, %d linhas) e %d (#endif)' % (nome, ini + 1, els + 1, els - ini + 1, fim + 1))
del L[fim]
del L[ini:els + 1]
open(arq, 'w', encoding='latin-1', newline='').write('\n'.join(L))
