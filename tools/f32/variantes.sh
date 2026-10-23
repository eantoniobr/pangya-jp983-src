#!/bin/bash
# F3.2: confere as flags do exe 983 por variantes (como na F0.2): recompila pch + unidades de teste com cada conjunto
# e mede com o cmpfunc. Uso: variantes.sh <saida.txt> unidade...   (build em build/pg-v_<nome>, apagado no fim)
cd "$(dirname "$0")/../.."; out=$1; shift
B='/MD /W3 /EHsc /Z7 /O2 /Ob1 /GF- /Gr /GS /Oy-'
run() { # nome flags
  rm -rf build/pg-v_$1 build/pg-v_$1.out
  python3 tools/f32/pgbuild.py pch --tag v_$1 --flags "$2" > /dev/null 2>&1
  python3 tools/f32/pgbuild.py obj "${U[@]}" -j3 --tag v_$1 --flags "$2" --out build/pg-v_$1.out > /dev/null 2>&1
  r=$(python3 tools/f32/pgbuild.py cmp "${U[@]}" -j3 --tag v_$1 --out build/pg-v_$1.out | tail -1)
  printf '%-10s %-52s %s\n' "$1" "$2" "$r" | tee -a $out
  rm -rf build/pg-v_$1 build/pg-v_$1.out
}
U=("$@"); : > $out
run base  "$B"
run Ob2   "${B/\/Ob1/\/Ob2}"
run Ob0   "${B/\/Ob1/\/Ob0}"
run GF    "${B/\/GF-/\/GF}"
run GSoff "${B/\/GS/\/GS-}"
run Oy    "${B/ \/Oy-/}"
run O1    "${B/\/O2/\/O1}"
run Gy    "$B /Gy"
run fpfast "$B /fp:fast"
run sse   "$B /arch:SSE"
run Gd    "${B/\/Gr/\/Gd}"
