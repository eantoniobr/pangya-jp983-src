#!/usr/bin/env python3
"""Confere a fila do robô (out/F4/fila_teste/pedidos) antes de rodar: o que a C deve cancelar ou avisar.
Uso: python3 tools/v6/fila.py [pasta]   (padrão = a fila; saída = uma linha por pedido, código 1 se houver BLOQUEIO)
BLOQUEIO: Practice/sala/tacada (REGRAS 5); entrega sem exe ou com stub [fatal] no FALTA.md (d326-1, e178-1: fecha no arranque).
AVISO: frente com mais de 2 pendentes; pedido com as mesmas ações e a mesma entrega de outro.
ORDEM (C460): a ordem prevista do robô (robo_teste.ps1 LerPedido: mais antigo por mtime, vez alternada entre frentes) e AVISO se
um original que deve FICAR na sala ("LOGO DEPOIS" no comentário) tem outro pedido do original antes dos nossos do mesmo de= ou que citam o id dele."""
import collections, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out/F4/fila_teste/pedidos')
# 160 869 = Practice; criar sala/Start/barra de tacada também proibidos (REGRAS 5)
PROIBIDO = re.compile(r'^acao=(clique 160 869\b|barra\b|tacada\b)', re.M)

ruim, por_frente, roteiros = 0, collections.Counter(), collections.defaultdict(list)
for nome in sorted(os.listdir(FILA)):
    txt = open(os.path.join(FILA, nome), encoding='utf-8', errors='replace').read()
    kv = dict(l.split('=', 1) for l in txt.splitlines() if '=' in l and not l.startswith('acao='))
    probs = []
    m = PROIBIDO.search(txt)
    if m: probs.append('PROIBIDO ' + m.group(1))
    ent = kv.get('entrega')
    if ent and kv.get('exe') != 'original':
        d = os.path.join(ROOT, ent)
        if not os.path.isfile(os.path.join(d, 'ProjectG_nosso.exe')): probs.append('entrega sem ProjectG_nosso.exe')
        falta = os.path.join(d, 'FALTA.md')
        if os.path.isfile(falta):
            fatais = [l.split('`')[1] for l in open(falta, encoding='utf-8', errors='replace') if '| fatal |' in l and '`' in l]
            if fatais: probs.append('stub fatal ' + ', '.join(fatais[:3]))
    frente = re.match(r'(?:orig-)?([a-z]+)', nome).group(1)
    por_frente[frente] += 1
    roteiros[(kv.get('exe', 'nosso'), ent, tuple(re.findall(r'^acao=.*', txt, re.M)))].append(nome)
    ruim += bool(probs)
    print(f"{nome}\t{'BLOQUEIO: ' + '; '.join(probs) if probs else 'ok'}")
for f, n in por_frente.items():
    if n > 2: print(f'AVISO: frente {f} com {n} pendentes (limite 2)')
for nomes in roteiros.values():
    if len(nomes) > 1: print('AVISO: mesmas ações em ' + ', '.join(nomes))
# ordem prevista: igual ao LerPedido (ls -1tr; frente servida há mais tempo; empate = a primeira da lista)
lista = sorted(os.listdir(FILA), key=lambda n: (os.path.getmtime(os.path.join(FILA, n)), n))
servida, ordem = {}, []
while lista:
    arq = min(lista, key=lambda n: servida.get(re.match(r'(?:orig-)?([a-z]+)', n).group(1), -1))
    servida[re.match(r'(?:orig-)?([a-z]+)', arq).group(1)] = len(ordem)
    ordem.append(arq); lista.remove(arq)
print('ORDEM: ' + ' > '.join(n[:-4] for n in ordem))
info = {}
for n in ordem:
    txt = open(os.path.join(FILA, n), encoding='utf-8', errors='replace').read()
    info[n] = (re.search(r'^exe=original', txt, re.M) is not None, (re.search(r'^de=(\S+)', txt, re.M) or [None, ''])[1], 'LOGO DEPOIS' in txt, txt)
for i, n in enumerate(ordem):
    orig, de, fica, _ = info[n]
    if not (orig and fica): continue
    nossos = [j for j, m in enumerate(ordem) if j > i and not info[m][0] and (info[m][1] == de or n[:-4] in info[m][3])]
    outro = next((j for j, m in enumerate(ordem) if j > i and info[m][0]), None)
    if nossos and outro is not None and outro < max(nossos):
        print(f'AVISO: {ordem[outro]} (original) roda antes de {ordem[max(nossos)]}: o {n} sai da sala')
    # C534: pedido alheio no meio = original parado na sala (servidor pode derrubar por inatividade) e sala a mais nas fotos dele
    meio = [ordem[j][:-4] for j in range(i + 1, max(nossos)) if j not in nossos] if nossos else []
    if meio: print(f'AVISO: {", ".join(meio)} roda(m) entre {n[:-4]} e {ordem[max(nossos)][:-4]}: o original fica na sala esse tempo')
sys.exit(1 if ruim else 0)
