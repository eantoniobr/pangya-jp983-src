#!/bin/bash
# wl.sh unidade...: compila cada uma (--tag w; antes: pgbuild.py pch --tag w) e mostra 1 linha com a contagem do comparador. T=pasta de trabalho
cd /root/jp983src; mkdir -p ${T:-/tmp/wl}
for u in "$@"; do
  python3 tools/f32/pgbuild.py obj "$u" --tag w --force --out ${T:-/tmp/wl}/o >${T:-/tmp/wl}/build.log 2>&1
  if grep -q 'compilam 1 de 1' ${T:-/tmp/wl}/build.log; then
    tools/cmpfunc build/pg-w/obj/src/${u%.cpp}.obj --no-build --ref ref/ProjectG_983_dump.exe --map map/projectg.tsv --seed map/projectg_seed.tsv --funcs map/projectg_funcs.tsv --out ${T:-/tmp/wl}/c/$(basename $u .cpp) >/dev/null 2>&1
    echo "$u OK $(awk -F'\t' 'NR>1 && $3==1{c[$4]++} END{for(k in c) printf "%s=%d ",k,c[k]}' ${T:-/tmp/wl}/c/$(basename $u .cpp)/funcs.tsv)"
  else
    echo "$u FALHA $(grep -c ' error ' build/pg-w/obj/src/${u%.cpp}.log) erros: $(grep -m1 ' error ' build/pg-w/obj/src/${u%.cpp}.log | cut -c1-200)"
  fi
done
