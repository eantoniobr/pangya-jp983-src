#!/bin/bash
# Limpeza automática de build/ do jp983src (revisor 15/10): por frente, mantém as 3 pastas mais novas e nunca apaga
# pasta mexida nos últimos 45 min (pode estar em uso). Roda de hora em hora pelo cron; log em runs/limpeza.log.
cd /root/jp983src/build || exit 0
L=/root/jp983src/runs/limpeza.log
antes=$(df --output=avail -BG /root | tail -1 | tr -dc 0-9)
for pre in pg-a pg-c pg-d pg-e pg-b f4e/; do
  ls -dt ${pre}* 2>/dev/null | grep -E "^${pre}[0-9]" | tail -n +4 | while read d; do
    [ -n "$(find "$d" -maxdepth 2 -newermt '-10 minutes' -print -quit)" ] && continue
    rm -rf -- "$d" && echo "$(date -Is) apagado build/$d" >> $L
  done
done
# entregas por pedido do robô com mais de 1 dia
# bobj-* (objetos) e pg-reg* (regressão) ficavam de fora (16/10: 38 GB); mantém as 3 mais novas por família, as mexidas há < 3 h
# e as usadas como base (V6_BOBJ/V6_PG/V6_SEM) por alguma entrega das últimas 6 h
usadas=$(find /root/jp983src/out/F4/entregas -maxdepth 2 -name ORIGEM.txt -newermt "-2 hours" -exec grep -hoE "V6_PG=pg-[A-Za-z0-9_-]+|V6_BOBJ=build/bobj-[A-Za-z0-9_-]+" {} + 2>/dev/null | sed -E "s/^V6_PG=//; s/^V6_BOBJ=build\///" | sort -u)  # V6_SEM = builds a IGNORAR, não base
for pre in bobj-a bobj-b bobj-c bobj-d bobj-e bobj-reg pg-reg; do
  ls -dt ${pre}* 2>/dev/null | grep -E "^${pre}[-0-9]" | tail -n +3 | while read d; do
    echo "$usadas" | grep -qx "$d" && continue
    [ -n "$(find "$d" -maxdepth 2 -newermt "-1 hours" -print -quit)" ] && continue
    rm -rf -- "$d" && echo "$(date -Is) apagado build/$d" >> $L
  done
done
# worktrees /root/jp983-* (montagem de regressão/exe por frente; 17/10: 44 x 3,9 GB = disco caiu a 42 GB): mantém as 4 mais novas
# e as mexidas há < 2 h; o diff local (se houver) vai para /root/backups/worktree-diffs antes de remover
mkdir -p /root/backups/worktree-diffs
for d in $(cd /root && ls -dt jp983-* 2>/dev/null | tail -n +5); do
  [ -n "$(find "/root/$d" -maxdepth 2 -newermt '-2 hours' -print -quit)" ] && continue
  P=/root/backups/worktree-diffs/$d.patch
  git -C "/root/$d" diff > "$P" 2>/dev/null; [ -s "$P" ] || rm -f "$P"
  (cd /root/jp983src && flock git.lock git worktree remove --force "/root/$d") && echo "$(date -Is) apagado worktree /root/$d" >> $L
done
(cd /root/jp983src && flock git.lock git worktree prune)
# C531: poupa a entrega de pedido ainda na fila (robô parado 19-22/10 apagou todas) e a com MANTER (aprovada ao dono)
na_fila=$(grep -hoE "^entrega=out/F4/entregas/[^/[:space:]]+" /root/jp983src/out/F4/fila_teste/pedidos/*.txt 2>/dev/null | sed "s|.*/||" | sort -u)
find /root/jp983src/out/F4/entregas -mindepth 1 -maxdepth 1 -type d -mtime +1 | while read d; do
  [ -e "$d/MANTER" ] && continue; echo "$na_fila" | grep -qx "${d##*/}" && continue
  git -C /root/jp983src ls-files --error-unmatch "$d" >/dev/null 2>&1 && continue  # versionada no git (d465-1, d474-1): apagar suja a árvore
  rm -rf -- "$d" && echo "$(date -Is) apagado entrega ${d##*/}" >> $L
done
depois=$(df --output=avail -BG /root | tail -1 | tr -dc 0-9)
echo "$(date -Is) livre ${antes}G -> ${depois}G" >> $L
[ "$depois" -lt 12 ] && echo "$(date -Is) ATENÇÃO: só ${depois}G livres depois da limpeza" >> $L
exit 0
