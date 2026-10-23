#!/bin/bash
# cm.sh unidade [--diff Nome]: compara o .obj de build/pg-c com o exe 983 usando map/projectg.tsv + o mapa da frente C
# (map/pkt_c.tsv: funções de pacote que a C escreveu e que ainda não estão no mapa da A). Saída em $T/c/<unidade>.
cd /root/jp983src; T=${T:-/tmp/pkt}; mkdir -p $T; u=$1; shift
cat map/projectg.tsv map/pkt_c.tsv > $T/map.tsv
if [ "$1" = "--diff" ]; then
  tools/cmpfunc build/pg-c/obj/src/${u%.cpp}.obj --no-build --ref ref/ProjectG_983_dump.exe --map $T/map.tsv --seed map/projectg_seed.tsv --funcs map/projectg_funcs.tsv --diff "$2"
else
  tools/cmpfunc build/pg-c/obj/src/${u%.cpp}.obj --no-build --ref ref/ProjectG_983_dump.exe --map $T/map.tsv --seed map/projectg_seed.tsv --funcs map/projectg_funcs.tsv --out $T/c/$(basename $u .cpp) >/dev/null 2>&1
  awk -F'\t' 'NR>1 && $3==1{printf "%-9s %5.1f%% %s %5d %5d  %s\n",$4,$5*100,$6,$8,$9,$2}' $T/c/$(basename $u .cpp)/funcs.tsv
fi
