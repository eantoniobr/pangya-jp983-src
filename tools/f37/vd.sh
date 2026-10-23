#!/bin/bash
# f37/vd.sh <dec.txt> <va ini> <va fim> — mostra o pseudo-C (saída do dec.sh) das funções com VA em [ini, fim), sem linhas vazias
awk -v a="$2" -v b="$3" '/^####/{v=substr($2,3); on=(v>=a && v<b)} on && NF' "$1"
