#!/bin/bash
# F0.4: exporta funções (hashes J3), vtables e características (ExportFeat) das três wangreal.dll.
# 983 = projeto próprio (proj/wr983); 839 e 645 = projetos do kr839, sempre em -readOnly. Um Ghidra por vez.
G=/opt/ghidra_12.1.4_PUBLIC/support/analyzeHeadless
O=/root/jp983src/build/f04; mkdir -p $O
SP="/root/jp983/scripts;/root/kr839/scripts"
run() { # projdir projname programa sufixo
  $G $1 $2 -process $3 -noanalysis -readOnly -max-cpu 6 -scriptPath "$SP" \
    -postScript J3Export.java $O/f$4.jsonl -postScript ExportVtables.java $O/vt$4.tsv \
    -postScript ExportFeat.java $O/x$4.jsonl > $O/export$4.log 2>&1 < /dev/null
}
run /root/jp983src/proj wr983 wangreal_983.dll 983w
run /root/kr839/proj kr839 wangreal.dll 839w
run /root/kr839/proj645w wr645 wangreal_ReleaseQA.dll 645w
wc -l $O/*.jsonl $O/*.tsv
