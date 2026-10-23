#!/bin/bash
# triagem.sh: para cada caso "so_983" de $1 (padrão out/PKT/s7/faltam_onpacketcommon.tsv; precisa de /tmp/pkt/casos.tsv = id<TAB>va do
# despachante 009c20a0 tirado de out/V4/pacotes_recebe_983.tsv) desmonta o caso em /tmp/pkt/d/<id>.txt e lista tamanho,
# chamadas a funções sem nome (FUN_) e globais lidos: mostra quais casos dependem de código que ainda não existe.
cd /root/jp983src
mkdir -p /tmp/pkt/d; awk -F"\t" '$1=="009c20a0"{print $3"\t"$4}' out/V4/pacotes_recebe_983.tsv > /tmp/pkt/casos.tsv
awk -F"\t" '$2=="so_983"{print $1}' ${1:-out/PKT/s7/faltam_onpacketcommon.tsv} | while read id; do
 va=$(awk -v i=$id '$1==i{print $2}' /tmp/pkt/casos.tsv); nx=$(awk -v v=$va '$2>v{print $2}' /tmp/pkt/casos.tsv | sort | head -1)
 python3 tools/f37/dz.py $va $nx | sed -E 's/  ; f=.*//' > /tmp/pkt/d/$id.txt
 n=$(wc -l < /tmp/pkt/d/$id.txt)
 un=$(grep -o "call    0x[0-9a-f]*  ; FUN_[0-9a-f]*" /tmp/pkt/d/$id.txt | awk '{print $4}' | sort -u | grep -v "FUN_0047d230" | tr '\n' ' ')
 gl=$(grep -o "dword ptr \[0xe[0-9a-f]*\]" /tmp/pkt/d/$id.txt | sort -u | tr -d '[]' | awk '{print $3}' | tr '\n' ' ')
 echo "$id $va n=$n | $un| $gl"
done
