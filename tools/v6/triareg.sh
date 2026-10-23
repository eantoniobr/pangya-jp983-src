#!/bin/bash
# Triagem de uma regressão contra a anterior (C412).
# uso: tools/v6/triareg.sh <reg-nova> <reg-base> <pasta-saida>
# Gera na pasta: opcodes.diff (contagem por opcode/direção, GAME e RANK),
# fotos.txt (RMSE normalizado foto a foto, mesmo índice), resumo.txt (queda/PANIC/PARTIDA, nº de fotos).
set -u
R=out/F4/resultados
NOVA=$1; BASE=$2; OUT=$3
mkdir -p "$OUT"
conta() { # <pasta> <SERVIDOR>
  cat "$R/$1"/pacotes/*-"$2"-*.log 2>/dev/null | awk '$2=="->"||$2=="<-"{print $2, $3}' | sort | uniq -c | awk '{print $2, $3, $1}'
}
: > "$OUT/opcodes.diff"
for s in GAME RANK; do
  echo "## $s" >> "$OUT/opcodes.diff"
  diff <(conta "$BASE" $s) <(conta "$NOVA" $s) >> "$OUT/opcodes.diff"
done
: > "$OUT/fotos.txt"
for f in "$R/$NOVA"/*.png; do
  b=$(basename "$f")
  [ -f "$R/$BASE/$b" ] || { echo "$b sem_base" >> "$OUT/fotos.txt"; continue; }
  v=$(compare -metric RMSE "$f" "$R/$BASE/$b" null: 2>&1 | sed -n 's/.*(\(.*\)).*/\1/p')
  echo "$b ${v:-erro}" >> "$OUT/fotos.txt"
done
{
  echo "nova=$NOVA base=$BASE"
  echo "ESTADO: $(cat "$R/$NOVA/ESTADO" 2>/dev/null)"
  echo "fotos: $(ls "$R/$NOVA"/*.png 2>/dev/null | wc -l) (base $(ls "$R/$BASE"/*.png 2>/dev/null | wc -l))"
  echo "queda/PANIC/PARTIDA em eventos.txt:"
  grep -niE "queda|crash|panic|partida detectada|AV |exce" "$R/$NOVA/eventos.txt" 2>/dev/null | head -10
  echo "fotos com RMSE > 0.09:"
  awk '$2+0>0.09' "$OUT/fotos.txt"
} > "$OUT/resumo.txt"
cat "$OUT/resumo.txt"
