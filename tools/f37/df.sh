#!/bin/bash
# f37/df.sh <unidade> <nome> — lado a lado (cmpfunc --diff) da(s) função(ões) da unidade cujo nome contém <nome>
cd /root/jp983src && tools/cmpfunc build/B/obj/$1.obj --no-build --ref ref/ProjectG_983_dump.exe --map build/B/mapa.tsv --funcs map/projectg_funcs.tsv --diff "$2" 2>&1 | awk '/^--- /{p=1} p' | cut -c1-140
