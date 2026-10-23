#!/usr/bin/env python3
# Troca só o bloco "### X" do HANDOFF.md, sob trava, lendo o texto novo da entrada padrão.
# Uso: tools/set_handoff_block.py X < bloco.txt   (sem a linha "### X"; as outras frentes ficam intactas)
import fcntl, re, sys

lane = sys.argv[1].upper()
body = sys.stdin.read().strip('\n')
path = "/root/jp983src/HANDOFF.md"
with open('/root/jp983src/HANDOFF.lock', 'w') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)  # serializa as frentes: sem isto a última gravação apagava o bloco das outras
    text = open(path, encoding='utf-8').read()
    pattern = re.compile(rf'(?ms)^### {lane}\n.*?(?=^### [A-E]\n|\Z)')
    block = f'### {lane}\n{body}\n\n'
    text = pattern.sub(lambda _: block, text, count=1) if pattern.search(text) else text.rstrip('\n') + '\n\n' + block
    open(path, 'w', encoding='utf-8').write(text)
