#!/bin/bash
# caso.sh VA [despachante]: desmonta o caso de pacote que começa em VA até o início do caso seguinte do mesmo despachante
# (inícios tirados de out/V4/pacotes_recebe_983.tsv; padrão: 009c20a0 = CTask::OnPacketCommon). Saída enxuta (sem f=, sem iteradores).
cd /root/jp983src; d=${2:-009c20a0}
n=$(awk -F'\t' -v d=$d -v v=$1 '$1==d{print $4}' out/V4/pacotes_recebe_983.tsv | sort -u | awk -v v=$1 '$1>v{print;exit}')
python3 tools/f37/dz.py $1 $n | sed -E 's/  ; f=.*//; s/\?\$_Tree_iterator.*//' | cut -c11-130
