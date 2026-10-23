#!/bin/sh
# robo.sh ID [modo] [segundos] [acao...] — frente C, F4: grava out/F4/fila_teste/PEDIDO.txt (só se a entrega for nova e completa),
# espera o robô do PC (ESTADO != rodando, até 10 min) e resume o resultado (eventos, stubs, exceção simbolizada pelo map).
# C94 (C-ROBO): grava na FILA (fila_teste/pedidos/<id>.txt); ENTREGA=out/F4/entregas/<id> usa a entrega de um
# `make exe ENTREGA=...` (o .map vem de build/f4e/<id>/); sem ENTREGA = out/F4/entrega da C. Ex.: ENTREGA=out/F4/entregas/a168-1 tools/v6/robo.sh a168-1
cd "$(dirname "$0")/../.." || exit 1
id=$1; modo=${2:-continuar}; seg=${3:-150}; shift 3 2>/dev/null
R=out/F4/resultados; F=out/F4/fila_teste; ENT=${ENTREGA:-out/F4/entrega}; ENT=${ENT%/}
MAP=build/C/f4/ProjectG_983.map; [ "$ENT" = out/F4/entrega ] || MAP=build/f4e/$(basename $ENT)/ProjectG_983.map
[ -n "$id" ] || { echo "uso: robo.sh ID [modo] [segundos] [acao...]"; exit 2; }
[ -e "$R/$id" ] && { echo "id $id já usado"; exit 2; }
e=$(cat $R/*/eventos.txt 2>/dev/null | grep -o 'ok ProjectG_nosso.exe [0-9a-f]*' | awk '{print $3}' | tail -1)
m=$(awk '/ProjectG_nosso.exe/{print $1}' $ENT/MD5.txt)
[ "$m" = "$(md5sum $ENT/ProjectG_nosso.exe | cut -d' ' -f1)" ] || { echo "MD5.txt não bate com o exe da entrega"; exit 3; }
# C190: stub [fatal] no FALTA.md = o exe fecha no arranque (e178-1: bobj-e178 sem taskwidget.obj -> FrFormFactory983::Instance983)
grep -q '| fatal |' $ENT/FALTA.md 2>/dev/null && { echo "FALTA.md da entrega tem stub fatal (o exe fecha no arranque):"; grep '| fatal |' $ENT/FALTA.md | head -5; exit 4; }
[ "$m" = "$e" ] && echo "AVISO: mesmo exe do último teste ($m)"
{ echo "id=$id"; echo "de=${id%%-*}"; echo "entrega=$ENT"; echo "modo=$modo"; echo "segundos=$seg"; echo "wangreal=original"; for a in "$@"; do echo "acao=$a"; done; } > $F/pedidos/.$id.tmp && mv $F/pedidos/.$id.tmp $F/pedidos/$id.txt
echo "pedido $id na fila (exe $m, $ENT; à frente: $(ls $F/pedidos | grep -vc "^$id.txt$")); robô vivo: $(cat $F/ROBO_VIVO)"
n=0; while :; do s=$(cat $R/$id/ESTADO 2>/dev/null); [ -n "$s" ] && [ "$s" != rodando ] && break; n=$((n+1)); [ $n -gt 90 ] && { echo "sem resultado em 15 min"; exit 5; }; sleep 10; done
d=$R/$id; echo "ESTADO=$s"; ls $d | tr '\n' ' '; echo; cat $d/eventos.txt
sort $d/jp983_stubs.log 2>/dev/null | uniq -c
grep -E 'Exception|instruction|could not' $d/exception.log 2>/dev/null
grep 'Address=' $d/exception.log 2>/dev/null | head -20 | awk -F= '{print $2}' | xargs -r python3 tools/v6/symmap.py $MAP
