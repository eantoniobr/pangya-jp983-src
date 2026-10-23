#!/bin/bash
# C108: espera os pedidos do robô terminarem (ESTADO feito/erro_robo/cancelado; a fila roda fora de ordem) e resume com rodadas.py.
# Uso: tools/v6/f4rastro/espera.sh c108-1 c108-2 ...   (rodar em segundo plano)
R=$(cd "$(dirname "$0")/../../.." && pwd)
while :; do ok=1; for i in "$@"; do grep -qs 'feito\|erro\|cancel' "$R/out/F4/resultados/$i/ESTADO" || ok=0; done; [ $ok = 1 ] && break; sleep 30; done
python3 "$R/tools/v6/f4rastro/rodadas.py" "$@"
