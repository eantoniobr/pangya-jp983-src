#!/bin/bash
# Triagem de regressão (C355): tools/tri_reg.sh <reg_nova> <reg_ref> <dir_saida>
# - opcodes.diff: contagem por direção/opcode das conexões GAME (e RANK) nova x ref (diff vazio = mesmos pacotes)
# - fotos.txt: RMSE normalizado (ImageMagick) foto a foto, mesmo nome; FALTA_A/FALTA_B
# - vizinho.txt: para RMSE > 0,05, o menor RMSE contra as fotos ±6 da ref (defasagem de tempo)
R=/root/jp983src/out/F4/resultados
A=$R/$1; B=$R/$2; O=$3; mkdir -p "$O"
cnt() { cat "$1"/pacotes/*-"$2"-*.log 2>/dev/null | awk '{print $2, $3}' | sort | uniq -c | awk '{print $2, $3, $1}'; }
for t in GAME RANK; do
  echo "## $t"; diff <(cnt "$B" $t) <(cnt "$A" $t) | grep '^[<>]'
done > "$O/opcodes.diff"
: > "$O/fotos.txt"; : > "$O/vizinho.txt"
for f in $(cd "$A"; ls [0-9]*.png) $(cd "$B"; ls [0-9]*.png); do echo $f; done | sort -u | while read f; do
  [ -f "$A/$f" ] || { echo "$f FALTA_A" >> "$O/fotos.txt"; continue; }
  [ -f "$B/$f" ] || { echo "$f FALTA_B" >> "$O/fotos.txt"; continue; }
  v=$(compare -metric RMSE "$A/$f" "$B/$f" null: 2>&1 | sed -n 's/.*(\(.*\)).*/\1/p')
  echo "$f $v" >> "$O/fotos.txt"
  if awk -v v="$v" 'BEGIN{exit !(v>0.05)}'; then
    n=$((10#${f:0:3})); best=9; bn=-
    for d in $(seq -6 6); do
      m=$((n+d)); g=$(cd "$B"; ls $(printf %03d $m)_*.png 2>/dev/null | head -1); [ -n "$g" ] || continue
      w=$(compare -metric RMSE "$A/$f" "$B/$g" null: 2>&1 | sed -n 's/.*(\(.*\)).*/\1/p')
      awk -v w="$w" -v b="$best" 'BEGIN{exit !(w<b)}' && { best=$w; bn=${g:0:3}; }
    done
    echo "$f $best $bn" >> "$O/vizinho.txt"
  fi
done
echo "fotos A=$(ls "$A"/[0-9]*.png | wc -l) B=$(ls "$B"/[0-9]*.png | wc -l); >0,05: $(wc -l < "$O/vizinho.txt"); vizinho >0,09:"
awk '$2>0.09' "$O/vizinho.txt"
grep -iE "queda|panic|crash|nao chegou|NAO ENTROU" "$A/eventos.txt" 2>/dev/null | head
