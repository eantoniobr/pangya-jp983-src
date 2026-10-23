#!/bin/bash
# decompexe983.sh <saida.txt> <va>... — pseudo-C do Ghidra (/root/jp983/proj, ProjectG_983_dump.exe, só leitura) das funções do EXE 983
R=/root/jp983src; out=$1; shift
/opt/ghidra_12.1.4_PUBLIC/support/analyzeHeadless /root/jp983/proj jp983 -process ProjectG_983_dump.exe -readOnly -noanalysis \
  -max-cpu 6 -scriptPath /root/jp983/scripts -postScript J4Decomp.java "$R/$out" "$@" > $R/build/f12/decomp.log 2>&1
grep -c '^####' "$R/$out"
