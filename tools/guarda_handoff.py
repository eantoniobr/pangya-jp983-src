#!/usr/bin/env python3
# Depois de cada sessão (run-frente.sh): o HANDOFF.md deve ter os 5 blocos "### A".."### E" e nenhuma seção "## ".
# Bloco de outra frente que sumiu/encolheu muito volta da cópia de antes da sessão; seções "## " acrescentadas saem
# (as regras vivem em REGRAS.md). Uso: guarda_handoff.py <frente> <copia_antes>. Log: runs/handoff_guarda.log
import re, sys, datetime
X, antes_p = sys.argv[1], sys.argv[2]
R = '/root/jp983src/HANDOFF.md'
def blocos(t):
    cab = t.split('\n### ', 1)[0]
    d = {}
    for m in re.finditer(r'(?ms)^### ([A-E])\n(.*?)(?=^### [A-E]\n|\Z)', t):
        d[m.group(1)] = m.group(2)
    return cab, d
try:
    antes = open(antes_p, encoding='utf-8').read(); agora = open(R, encoding='utf-8').read()
except Exception:
    sys.exit(0)
cab_a, ba = blocos(antes); cab_n, bn = blocos(agora)
log = []
for f, txt in ba.items():
    if f == X: continue
    # só bloco SUMIDO volta: encolher pode ser a própria frente atualizando (set_handoff_block.py) durante a sessão de X
    if f not in bn:
        bn[f] = txt; log.append(f'bloco {f} restaurado (sumiu depois da sessão de {X})')
for f in bn:
    bn[f] = re.sub(r'(?m)^## .*', '', bn[f]) if re.search(r'(?m)^## ', bn[f]) else bn[f]
if re.search(r'(?m)^## ', agora) or log:
    novo = cab_a.rstrip('\n') + '\n\n' + ''.join(f'### {f}\n{bn[f].rstrip()}\n\n' for f in 'ABCDE' if f in bn)
    open(R, 'w', encoding='utf-8').write(novo)
    if re.search(r'(?m)^## ', agora): log.append(f'seção "## " acrescentada por {X} retirada (regras ficam em REGRAS.md)')
if log:
    with open('/root/jp983src/runs/handoff_guarda.log', 'a') as L:
        for l in log: L.write(f'{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')}Z {l}\n')
