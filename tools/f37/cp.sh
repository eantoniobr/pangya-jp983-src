#!/bin/bash
# f37/cp.sh <arquivo .enx/.txt do dz> <faixa awk, ex.: '$1>="00b45590" && $1<"00b45a30"'> — listagem compacta (sem os 4 dígitos altos, d[]/b[]/w[])
awk "$2" "$1" | sed 's/  ; f=.*//;s/dword ptr /d/;s/byte ptr /b/;s/word ptr /w/;s/?\([A-Za-z0-9_]*\)@[^ ]*/\1/' | awk '{a=$1; $1=""; printf "%s%s\n", substr(a,5), $0}' | cut -c1-100
