#!/bin/bash
# C103: build INTEIRA e coerente de uma revisão (PCH + 499 .obj, ~3 min com -j 8) num git worktree, sem misturar .obj de
# revisões diferentes (c102-11/c103-1: pg-a172 + .obj novos da B/D -> saída falsa na carga da partida).
# Uso: tools/v6/f4rastro/wt_build.sh TAG [REV] [PATCH_PY]
#   REV padrão = HEAD. PATCH_PY (opcional) = script python rodado DENTRO do worktree antes de compilar (rastro/correção
#   provisória só na cópia; os arquivos da A/D/E no repositório não mudam).
#   DEFS="/DJP983_SHOT_PREDICTION ..." (ambiente, opcional): defines a mais no PCH e nos .obj, só na cópia do pgbuild.py
#   do worktree (C105; ex.: previsão de tacada do 645, decisão do dono 15/10 03:25 — exe sem ele = HUD do 983).
#   C468: ponha também "pg" no V6_SEM (build/pg em recompilação por outra frente -> .obj pela metade, LNK2001 fatal sem nome);
#         o ani_overlay.obj (sem fonte) vem de build/pg: copie-o antes para build/pg-TAG.
#   C108: sem V6_SEM (nomes ou caminhos) o simbolos.py pega o .obj mais NOVO de qualquer pg-* (pg-w/pg-d*/pg-e* em compilação -> LNK1000/1181).
#   Saída: build/pg-TAG (no repositório principal). Depois:
#   make exe ENTREGA=out/F4/entregas/<id> V6_PG="pg-TAG" V6_SEM="<NOMES de todas as outras build/pg-*: pg-w pg-d9 ...>" V6_BOBJ=<cópia dos .obj da B>
set -e
TAG=$1; REV=${2:-HEAD}; PATCH=$3
R=/root/jp983src; W=/root/jp983-$TAG
[ -n "$PATCH" ] && PATCH=$(readlink -f "$PATCH")   # C104: antes do cd (relativo ao worktree não existe)
[ -n "$TAG" ] || { echo "uso: $0 TAG [REV] [PATCH_PY]"; exit 2; }
[ -e $R/build/pg-$TAG ] && { echo "build/pg-$TAG já existe"; exit 2; }
[ -d $W ] || flock $R/git.lock git -C $R worktree add --detach $W $REV >/dev/null
mkdir -p $W/build; [ -e $W/build/atl71 ] || ln -s $R/build/atl71 $W/build/atl71   # fora do git, o pgbuild precisa
if [ -n "$PATCH" ]; then (cd $W && python3 -I "$PATCH") || { echo "PATCH falhou"; exit 1; }; fi
cd $W
[ -n "$DEFS" ] && sed -i "s|^DEFS = '\(.*\)'|DEFS = '\1 $DEFS'|" tools/f32/pgbuild.py && grep -m1 '^DEFS' tools/f32/pgbuild.py
python3 tools/f32/pgbuild.py pch --tag $TAG --out out/${TAG}pch > /tmp/wt_$TAG.pch.log 2>&1
grep -c FALHOU /tmp/wt_$TAG.pch.log && { echo "PCH falhou: /tmp/wt_$TAG.pch.log"; exit 1; } || true
python3 tools/f32/pgbuild.py obj -j 8 --tag $TAG --out out/${TAG}obj > /tmp/wt_$TAG.obj.log 2>&1 || true
tail -n 1 /tmp/wt_$TAG.obj.log
mv $W/build/pg-$TAG $R/build/pg-$TAG
echo "ok: build/pg-$TAG (worktree $W: apagar com git worktree remove --force $W)"
