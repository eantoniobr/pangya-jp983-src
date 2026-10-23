#!/bin/bash
# galeria.sh — imagens ORIGINAL x NOSSO dos sistemas PRONTO (pedido do dono 17/10 21:35).
# Uso: tools/v6/galeria.sh [out/F5/galeria/pares.tsv]
# pares.tsv: NN<TAB>sistema<TAB>orig dir/foto[,foto]<TAB>nosso dir/foto[,foto]<TAB>prova<TAB>ressalva
# "foto" sem dir herda o dir da anterior; "026-039" = faixa de fotos. Uma linha da imagem por foto (antes/depois da ação).
# Colunas opcionais: 7 recorte (WxH+X+Y, na foto inteira), 8 zoom (%). Com recorte e > 2 fotos = FAIXA de quadros seguidos:
# ORIGINAL em cima x NOSSO embaixo, 7 quadros por linha (C378, revisor 17/10 23:00).
set -e
cd "$(dirname "$0")/../.."
PARES=${1:-out/F5/galeria/pares.tsv}
OUT=out/F5/galeria
RES=out/F4/resultados
W=800  # largura de cada metade -> total 1600

acha() { # dir/foto -> caminho do png
	ls "$RES/${1%/*}/${1#*/}"_*.png 2>/dev/null | head -1
}
lista() { # "a/010,012" ou "a/010,b/015" -> um dir/foto por linha
	local d="" x
	for x in ${1//,/ }; do
		case $x in */*) d=${x%/*};; *) x=$d/$x;; esac
		case ${x#*/} in *-*) local a=${x#*/}; a=${a%-*}; local b=${x##*-}
			for ((k=10#$a; k<=10#$b; k++)); do printf '%s/%03d\n' "$d" $k; done;;
		*) echo "$x";; esac
	done
}
metade() { # png rotulo saida
	convert "$1" ${REC:+-crop $REC +repage} -resize ${W}x \
		\( -size ${W}x28 xc:'#202020' -fill white -font DejaVu-Sans-Bold -pointsize 17 \
		   -gravity center -annotate +0+0 "$2" \) +swap -append "$3"
}

LEIA=$OUT/LEIAME.txt
echo "# Galeria dos sistemas PRONTO: ORIGINAL (983) à esquerda x NOSSO à direita; gerada por tools/v6/galeria.sh de $PARES" > "$LEIA"
TMP=$(mktemp -d)
grep -v '^#' "$PARES" | while IFS=$'\t' read -r nn sis orig nosso prova ress REC ZOOM; do
	[ -n "$nn" ] || continue
	[ "$REC" = "-" ] && REC=""
	mapfile -t O < <(lista "$orig")
	mapfile -t N < <(lista "$nosso")
	if [ -n "$REC" ] && [ ${#O[@]} -gt 2 ]; then  # faixa de quadros seguidos
		for lado in O N; do
			declare -n L=$lado; t=()
			for x in "${L[@]}"; do f=$(acha "$x"); [ -n "$f" ] || { echo "FALTA foto: $x" >&2; exit 1; }
				t+=("$f"); done
			[ $lado = O ] && rot="ORIGINAL 983 — $orig (quadros seguidos)" || rot="NOSSO — $nosso (quadros seguidos)"
			montage "${t[@]}" -crop $REC +repage -tile 7x -geometry $((2*W/7-4))x+2+2 -background '#202020' $TMP/m$lado.png
			convert \( -size $((2*W))x28 xc:'#202020' -fill white -font DejaVu-Sans-Bold -pointsize 17 \
				-gravity center -annotate +0+0 "$rot" \) $TMP/m$lado.png -append $TMP/f$lado.png
			unset -n L
		done
		convert $TMP/fO.png $TMP/fN.png -append +repage "$OUT/${nn}_${sis}.png"
		echo "${nn}_${sis}.png	$sis	orig ${orig} x nosso ${nosso} (recorte $REC)	$prova	ressalva: $ress" >> "$LEIA"
		echo "ok ${nn}_${sis}.png (faixa)"; continue
	fi
	linhas=()
	for i in "${!O[@]}"; do
		fo=$(acha "${O[$i]}"); fn=$(acha "${N[$i]}")
		[ -n "$fo" ] && [ -n "$fn" ] || { echo "FALTA foto: ${O[$i]} / ${N[$i]}" >&2; exit 1; }
		qual=""; [ ${#O[@]} -gt 1 ] && { [ $i -eq 0 ] && qual=" (antes)" || qual=" (depois)"; }
		metade "$fo" "ORIGINAL 983 — ${O[$i]}$qual" $TMP/o$i.png
		metade "$fn" "NOSSO — ${N[$i]}$qual" $TMP/n$i.png
		convert $TMP/o$i.png $TMP/n$i.png +append $TMP/l$i.png
		linhas+=($TMP/l$i.png)
	done
	convert "${linhas[@]}" -append +repage "$OUT/${nn}_${sis}.png"
	echo "${nn}_${sis}.png	$sis	orig ${orig} x nosso ${nosso}${REC:+ (recorte $REC${ZOOM:+, zoom $ZOOM%})}	$prova	ressalva: $ress" >> "$LEIA"
	echo "ok ${nn}_${sis}.png"
done
rm -rf "$TMP"
