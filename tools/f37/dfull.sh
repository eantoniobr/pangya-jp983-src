#!/bin/bash
# f37/dfull.sh <unidade> <nome> — como o df.sh, mas sem resumir os trechos iguais e sem cortar a linha (para listar `call` e
# deslocamentos dos dois lados). Usa build/B/cmpfull.py = cópia do tools/cmpfunc com o resumo desligado (refeita a cada chamada).
cd /root/jp983src && sed 's/if i2 - i1 > 6 and not dif:/if False:/;s/%-46s/%-100s/g;s/\[:46\]/[:100]/g' tools/cmpfunc > build/B/cmpfull.py && python3 build/B/cmpfull.py build/B/obj/$1.obj --no-build --ref ref/ProjectG_983_dump.exe --map build/B/mapa.tsv --funcs map/projectg_funcs.tsv --diff "$2" 2>&1 | awk '/^--- /{p=1} p'
