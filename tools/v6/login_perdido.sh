#!/bin/bash
# C346: censo dos logins perdidos do robô (esperapac LOGIN 0x0002 sem o pacote) por run, nosso x original.
# Uso: tools/v6/login_perdido.sh [dir_resultados]   (padrão out/F4/resultados)
# Saída: uma linha por run "PERDIDO|ok <id> <ms foto4->clique senha> <ms clique senha->texto>" e o total.
R=${1:-out/F4/resultados}
SENHA=${SENHA_TESTE:?defina SENHA_TESTE = texto digitado no campo de senha pelo robo}   # exportacao: a senha da conta de teste saiu do script
ms() { awk -F'[:.]' '{print (($1*60+$2)*60+$3)*1000+$4}' <<<"$1"; }
no=0; nn=0; po=0; pn=0
for f in "$R"/*/eventos.txt; do
  d=$(basename "$(dirname "$f")")
  grep -q "esperapac LOGIN 0x0002" "$f" || continue
  t4=$(grep -m1 "foto 4," "$f" | cut -c1-12 | tr -d '\357\273\277')
  tc=$(grep -m1 "acao: clique 802 384" "$f" | cut -c1-12 | tr -d '\357\273\277')
  tt=$(grep -m1 "acao: texto $SENHA" "$f" | cut -c1-12 | tr -d '\357\273\277')
  a=-; b=-
  [ -n "$t4" ] && [ -n "$tc" ] && a=$(( $(ms "$tc") - $(ms "$t4") ))
  [ -n "$tc" ] && [ -n "$tt" ] && b=$(( $(ms "$tt") - $(ms "$tc") ))
  if grep -qE "pacote 0x0002 nao visto|LOGIN NAO ENTROU" "$f"; then s=PERDIDO; else s=ok; fi
  case $d in orig-*) no=$((no+1)); [ $s = PERDIDO ] && po=$((po+1));; *) nn=$((nn+1)); [ $s = PERDIDO ] && pn=$((pn+1));; esac
  echo "$s $d $a $b"
done
echo "TOTAL nosso $pn/$nn perdidos; original $po/$no perdidos"
