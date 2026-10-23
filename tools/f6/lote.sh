#!/bin/bash
# (C404) uso: [TIRA_FORCA=1] tools/f6/lote.sh unidade fn1 fn2...  (tira todas as sobrecargas naked; reverte se objeq != IGUAL)
cd /root/jp983src
u=$1; shift; F=src/projectg/$u.cpp; O=build/pg-${PG_TAG:-c464}/obj/src/projectg/$u.obj; D=out/F6/tmp/${LOTE_DIR:-lote}
exec 9>lock/$u.cpp.lock; flock -n 9 || { echo "$u TRAVADO"; exit; }
[ -z "$(git status --short -- $F)" ] || { echo "$u SUJO"; exit; }
mkdir -p $D/a $D/b
python3 tools/f32/pgbuild.py obj $F --tag ${PG_TAG:-c464} --out $D/a >/dev/null 2>&1; cp $O $D/a/
for fn in "$@"; do python3 tools/f6/tira_naked.py $F $fn todas || echo "$u $fn MAO"; done
python3 tools/f32/pgbuild.py obj $F --tag ${PG_TAG:-c464} --out $D/b 2>&1 | grep -q "falham 0" || { echo "$u NAO COMPILA"; git checkout -- $F; exit; }; cp $O $D/b/
r=$(python3 tools/f6/objeq.py $D/{a,b}/$u.obj | tail -1); echo "$u: $r"
case "$r" in IGUAL*) ;; *) git checkout -- $F;; esac
