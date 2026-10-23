#!/bin/bash
# f37/res.sh <JPOUT> [unidade...] — resumo do make jp-cmp: só as funções próprias (ou com VA dentro da faixa do JP) que não são IGUAL + contagem
o=$1; shift; us=${@:-$(ls $o/cmp)}
for u in $us; do
  f=$o/cmp/$u/funcs.tsv
  echo "== $u: $(awk -F'\t' 'NR>1 && $3==1{c[$4]++} END{for(k in c) printf "%s=%d ",k,c[k]}' $f)"
  awk -F'\t' 'NR>1 && $3==1 && $4!="IGUAL"{printf "   %s %s %s %s\n",$4,$5,$6,substr($2,1,90)}' $f
done
