#!/bin/bash
# decomp983.sh <saida.txt> <va>... — pseudo-C do Ghidra (proj/wr983, só leitura) das funções pedidas
R=/root/jp983src; out=$1; shift
/opt/ghidra_12.1.4_PUBLIC/support/analyzeHeadless $R/proj wr983 -process wangreal_983.dll -readOnly -noanalysis \
  -max-cpu 6 -scriptPath /root/jp983/scripts -postScript J4Decomp.java "$out" "$@" > $R/build/f12/decomp.log 2>&1
grep -c '^####' "$out"
