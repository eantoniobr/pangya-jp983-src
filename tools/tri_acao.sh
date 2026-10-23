#!/bin/bash
# Fotos _acao EM ORDEM (C431): tools/tri_acao.sh <reg_nova> <reg_ref> <dir_saida>
# As fotos _jogo (periódicas) desalinham pela duração; as _acao seguem o roteiro. Pareia a i-ésima _acao da nova com a
# j-ésima da ref; se RMSE > 0,05 e uma das 3 seguintes da NOVA casar (<= 0,05) com a da ref, conta as puladas como
# INSERIDA (bloco novo no roteiro). Saída: acao_ordem.txt (i nova ref rmse | INSERIDA nova) e a linha final RESUMO.
R=/root/jp983src/out/F4/resultados
A=$R/$1; B=$R/$2; O=$3; mkdir -p "$O"
rm() { compare -metric RMSE "$1" "$2" null: 2>&1 | sed -n 's/.*(\(.*\)).*/\1/p'; }
gt() { awk -v v="$1" 'BEGIN{exit !(v>0.05)}'; }
# C463: a pasta pode trazer sobra de rodada anterior (C438: 001-072 = 2a rodada, 073-130 = 1a). Cada rodada abre com
# "pedido:" no eventos.txt; só valem as fotos numeradas até o total de fotos depois do último "pedido:".
acoes() {
  local n; n=$(awk '/ pedido: /{c=0} / foto [0-9]+,| acao: foto/{c++} END{print c+0}' "$1/eventos.txt" 2>/dev/null)
  (cd "$1"; ls *_acao.png 2>/dev/null) | awk -v n="${n:-0}" -v d="$1" '
    { if (n == 0 || $0 + 0 <= n) print; else s++ }
    END { if (s) printf "AVISO %s: %d foto(s) _acao de rodada anterior ignoradas (ultima rodada = %d fotos)\n", d, s, n > "/dev/stderr" }'
}
mapfile -t NA < <(acoes "$A")
mapfile -t NB < <(acoes "$B")
i=0; j=0; k=0; ins=0; mx=0; acima=0; : > "$O/acao_ordem.txt"
while [ $i -lt ${#NA[@]} ] && [ $j -lt ${#NB[@]} ]; do
  v=$(rm "$A/${NA[$i]}" "$B/${NB[$j]}")
  if gt "$v"; then
    pul=0
    for d in 1 2 3; do
      [ $((i+d)) -lt ${#NA[@]} ] || break
      w=$(rm "$A/${NA[$((i+d))]}" "$B/${NB[$j]}")
      gt "$w" || { pul=$d; break; }
    done
    if [ $pul -gt 0 ]; then
      for d in $(seq 0 $((pul-1))); do echo "INSERIDA ${NA[$((i+d))]}" >> "$O/acao_ordem.txt"; done
      ins=$((ins+pul)); i=$((i+pul)); continue
    fi
    acima=$((acima+1))
  fi
  echo "$k ${NA[$i]} ${NB[$j]} $v" >> "$O/acao_ordem.txt"
  mx=$(awk -v a="$mx" -v b="$v" 'BEGIN{print (b>a)?b:a}')
  i=$((i+1)); j=$((j+1)); k=$((k+1))
done
echo "RESUMO pares=$k inseridas=$ins acima_0,05=$acima max=$mx sobra_nova=$((${#NA[@]}-i)) sobra_ref=$((${#NB[@]}-j))" | tee -a "$O/acao_ordem.txt"
