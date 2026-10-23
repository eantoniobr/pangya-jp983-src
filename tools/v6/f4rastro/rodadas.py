#!/usr/bin/env python3
"""C108: resumo de rodadas do robô: id, campo (byte 2 do 0x52 enviado), fim (FECHOU/código/encerrou) e EIP da exceção.
Uso: rodadas.py c108-1 c108-2 ...   (lê out/F4/resultados/<id>/)"""
import sys, re, glob, os
R = os.path.dirname(os.path.abspath(__file__)) + '/../../../out/F4/resultados/'
for i in sys.argv[1:]:
    d = R + i + '/'
    if not os.path.exists(d + 'eventos.txt'): print(i, '\t(rodando ou sem resultado)'); continue
    campo = '-'
    for f in glob.glob(d + 'pacotes/*GAME*.log'):
        m = re.search(r'-> 0x0052 \d+ 5200(..)', open(f, errors='replace').read())
        if m: campo = '0x' + m.group(1)
    ev = open(d + 'eventos.txt', errors='replace').read()
    fim = re.search(r'jogo FECHOU[^\n]*|encerrando cedo aos \d+s|tempo esgotado[^\n]*', ev)
    eip = re.search(r'Exception: (\w+) .*? at 0023:(\w+)', open(d + 'exception.log', errors='replace').read()) \
        if os.path.exists(d + 'exception.log') else None
    print(i, campo, fim.group(0) if fim else '?', ('%s @%s' % eip.groups()) if eip else '', sep='\t')
