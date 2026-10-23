#!/bin/bash
# k2l_todas.sh CMPDIR OUTDIR [--aplica [--todos]] — roda tools/f35/k2l.py em cada unidade de CMPDIR/compila.tsv (funcs.tsv em
# CMPDIR/cmp/<unidade>/), com o lock por arquivo (lock/<arquivo>.lock); OUTDIR/<unidade>.txt + OUTDIR/resumo.tsv
R=$(cd "$(dirname "$0")/../.." && pwd); C=$1; O=$2; shift 2; mkdir -p "$O"; : > "$O/resumo.tsv"
cd "$R"
awk -F'\t' 'NR>1 && $2=="sim" {print $1}' "$C/compila.tsv" | while read u; do
  d=$(echo "${u%.cpp}" | tr '/' '_'); f="$C/cmp/$d/funcs.tsv"; [ -f "$f" ] || continue
  flock "lock/$(basename "$u").lock" python3 tools/f35/k2l.py "$u" "$f" "$@" > "$O/$d.txt" 2>&1
  printf '%s\t%s\n' "$u" "$(tail -1 "$O/$d.txt")" >> "$O/resumo.tsv"
done
