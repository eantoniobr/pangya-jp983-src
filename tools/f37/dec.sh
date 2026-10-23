#!/bin/bash
# f37/dec.sh <saida.txt> <va>... — pseudo-C do Ghidra das funções do exe 983 (projeto /root/jp983/proj, só leitura, sob ghidra.lock)
out=$1; shift
flock /root/jp983/ghidra.lock /opt/ghidra_12.1.4_PUBLIC/support/analyzeHeadless /root/jp983/proj jp983 -process ProjectG_983_dump.exe \
  -readOnly -noanalysis -max-cpu 6 -scriptPath /root/jp983/scripts -postScript J4Decomp.java "$out" "$@" > /root/jp983src/build/B/dec.log 2>&1
grep -c '^####' "$out"
