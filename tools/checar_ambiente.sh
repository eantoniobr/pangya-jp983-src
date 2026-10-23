#!/bin/bash
# checar_ambiente.sh [-r] — confere o que o jp983src precisa para compilar, comparar e usar o Ghidra (tarefa D1).
# Imprime uma linha por item: OK / FALTA (impede o trabalho) / AVISO (só uma parte fica sem funcionar).
# Só leitura: não cria nem altera nada. Sai com 1 se houver algum FALTA.
#   -r   pula os testes que rodam o Wine (cl/link), para quando já há build pesado em andamento
# Documentação: docs/TECNICO.md (seção "Ambiente") e docs/RETOMAR.md (seção 3).
R=$(cd "$(dirname "$0")/.." && pwd)
VS=${VS:-/root/kr839/local/vs2010}
REBANG=${REBANG:-/root/rebang}
GHIDRA=/opt/ghidra_12.1.4_PUBLIC
RAPIDO=0; [ "$1" = "-r" ] && RAPIDO=1
nok=0; nfalta=0; naviso=0
ok()    { printf 'OK     %-34s %s\n' "$1" "$2"; nok=$((nok+1)); }
falta() { printf 'FALTA  %-34s %s\n' "$1" "$2"; nfalta=$((nfalta+1)); }
aviso() { printf 'AVISO  %-34s %s\n' "$1" "$2"; naviso=$((naviso+1)); }
# tem <FALTA|AVISO> <rótulo> <caminho> [para que serve]
tem() { if [ -e "$3" ]; then ok "$2" "$3"; elif [ "$1" = FALTA ]; then falta "$2" "$3 não existe${4:+ — $4}"; else aviso "$2" "$3 não existe${4:+ — $4}"; fi; }

echo "# programas"
for p in wine python3 flock make git; do
  if command -v $p >/dev/null; then ok "$p" "$(command -v $p)"; else falta "$p" "não está no PATH"; fi
done
if command -v wine >/dev/null; then ok "versão do wine" "$(wine --version 2>/dev/null)"; fi
if python3 -c 'import capstone' 2>/dev/null; then ok "python: capstone" "$(python3 -c 'import capstone; print(capstone.__version__)')"
else falta "python: capstone" "pip install capstone (o tools/cmpfunc desmonta com ele)"; fi
if command -v node >/dev/null; then ok "node" "$(node --version) (só para tools/p1/teste_dom.js)"; else aviso "node" "sem node não roda o teste do painel (tools/p1/teste_dom.js)"; fi
if command -v java >/dev/null; then
  jv=$(java -version 2>&1 | head -1)
  case "$jv" in *'"21'*|*'"22'*|*'"23'*|*'"24'*|*'"25'*) ok "java (JDK 21+)" "$jv" ;; *) aviso "java (JDK 21+)" "$jv — o Ghidra 12 pede JDK 21" ;; esac
else aviso "java" "não está no PATH — sem ele o Ghidra não roda"; fi

echo "# compilador VS2010 SP1 sob Wine ($VS)"
tem FALTA "cl.exe"            "$VS/VC10/bin/cl.exe"
tem FALTA "link.exe"          "$VS/VC10/bin/link.exe"
tem FALTA "cabeçalhos VC10"   "$VS/VC10/include"
tem FALTA "CRT (msvcrt.lib)"  "$VS/VC10/lib/msvcrt.lib"
tem FALTA "compat"            "$VS/compat"
tem FALTA "kernel32.lib 7.1"  "$VS/sdklib/kernel32.lib"
tem FALTA "prefixo do Wine"   "$VS/wine"
if [ $RAPIDO = 1 ]; then aviso "cl roda" "pulado (-r)"
elif [ -x "$R/tools/vs.sh" ] && [ -e "$VS/VC10/bin/cl.exe" ]; then
  v=$(VS=$VS timeout 120 "$R/tools/vs.sh" cl 2>&1 | head -1 | tr -d '\r')
  case "$v" in *16.00.40219.01*) ok "cl roda" "$v" ;; *) falta "cl roda" "esperado 16.00.40219.01; saiu: ${v:-nada}" ;; esac
  v=$(VS=$VS timeout 120 "$R/tools/vs.sh" link 2>&1 | head -1 | tr -d '\r')
  case "$v" in *10.00.40219.01*) ok "link roda" "$v" ;; *) falta "link roda" "esperado 10.00.40219.01; saiu: ${v:-nada}" ;; esac
fi

echo "# binários de referência ($R/ref, fora do git)"
md5ref() { # arquivo md5
  if [ ! -e "$R/ref/$1" ]; then falta "ref/$1" "não existe (restaurar de /root/backups/jp983src-externos-*.tar)"; return; fi
  m=$(md5sum "$R/ref/$1" | cut -d' ' -f1)
  if [ "$m" = "$2" ]; then ok "ref/$1" "md5 $m"; else falta "ref/$1" "md5 $m, esperado $2"; fi
}
md5ref ProjectG_983_dump.exe 8c76194bf825391f63fc951d3d4b09da
md5ref wangreal_983.dll      8b3e48084718ecc10c9a699063d7cb54

echo "# rebang — decomp do KR 645, encerrada ($REBANG, só leitura)"
if [ -d "$REBANG/.git" ]; then
  h=$(git -C "$REBANG" rev-parse --short=7 HEAD 2>/dev/null)
  if git -C "$REBANG" cat-file -e f0a85b5^{commit} 2>/dev/null; then
    if [ "$h" = f0a85b5 ]; then ok "rebang em f0a85b5" "HEAD = $h"
    else aviso "rebang em f0a85b5" "o commit existe, mas o HEAD é $h (o build lê a árvore de trabalho)"; fi
  else falta "rebang em f0a85b5" "commit f0a85b5 não existe neste clone (HEAD $h)"; fi
  if git -C "$REBANG" rev-parse -q --verify refs/tags/kr645-decomp-2026-10-11 >/dev/null; then ok "tag kr645-decomp-2026-10-11" "existe"
  else aviso "tag kr645-decomp-2026-10-11" "não existe neste clone — vale o commit f0a85b5 (HANDOFF, tarefa D1)"; fi
else falta "rebang" "$REBANG não é um repositório git"; fi
tem FALTA "build-projectg.json"   "$REBANG/build-projectg.json" "lista de unidades do exe (tools/f32/pgbuild.py)"
tem FALTA "Platform SDK 2002"     "$REBANG/tools/PlatformSDK-Aug2002/include"
tem FALTA "DirectX 9 SDK"         "$REBANG/tools/DirectX9/include"
tem FALTA "WTL 7.5"               "$REBANG/tools/WTL75/include"
tem FALTA "ATL 7.1 (origem)"      "$REBANG/tools/VC7.1/atlmfc/include" "o make pg-atl gera build/atl71 a partir dele"
tem FALTA "rc.exe (VC7.1)"        "$REBANG/tools/VC7.1/bin/rc.exe" "recursos da wangreal.dll"
tem AVISO "exe do 645"            "$REBANG/tools/original/ProjectG_ReleaseQA.exe" "só tools/f34/seqoffs.py"
tem AVISO ".map do build do 645"  "$REBANG/build/projectg/ProjectG_ReleaseQA.map" "só tools/f32/seed.py (make pg-import)"

echo "# Ghidra e análises anteriores (só leitura; Ghidra sempre sob flock /root/jp983/ghidra.lock)"
tem AVISO "Ghidra"                "$GHIDRA/support/analyzeHeadless" "sem ele não há pseudo-C (tools/f37/dec.sh, tools/decomp983.sh)"
tem AVISO "projeto do exe 983"    "/root/jp983/proj/jp983.gpr"
tem AVISO "projeto do exe 839"    "/root/jp983/proj839"
tem AVISO "scripts do Ghidra"     "/root/jp983/scripts/J4Decomp.java"
tem AVISO "projeto da dll 983"    "$R/proj/wr983.gpr" "fora do git; refazer com tools/f04_export.sh"
tem AVISO "análise J1–J10"        "/root/jp983/out" "pares 983×839; make units"
tem AVISO "ponte 645×839"         "/root/kr839/out/f645.jsonl" "make units, tools/f34/seqoffs.py"

echo "# repositório ($R)"
for t in jp983-F0 jp983-F1 jp983-F2 jp983-F3.4; do
  if git -C "$R" rev-parse -q --verify refs/tags/$t >/dev/null; then ok "tag $t" "$(git -C "$R" rev-parse --short $t^{commit})"; else aviso "tag $t" "não existe"; fi
done
for f in Makefile Makefile.B Makefile.C HANDOFF.md status.json map/projectg.tsv map/projectg_funcs.tsv map/projectg_units.tsv map/wangreal.tsv; do
  tem FALTA "$f" "$R/$f"
done
tem AVISO "build/atl71 (gerado)"  "$R/build/atl71" "rodar make pg-atl (o make pg-obj faz sozinho)"
if ls "$R"/build/pg/pch/*.pch >/dev/null 2>&1; then ok "pch do exe (gerado)" "$(ls "$R"/build/pg/pch/*.pch | wc -l) em build/pg/pch"
else aviso "pch do exe (gerado)" "build/pg/pch vazio — rodar make pg-obj (ou tools/f32/pgbuild.py pch)"; fi
n=$(find "$R/out" -path '*/cmp/src_*/funcs.tsv' 2>/dev/null | head -500 | wc -l)
if [ "$n" -gt 0 ]; then ok "resultados do comparador" "há funcs.tsv em out/**/cmp (o painel lê daqui)"
else aviso "resultados do comparador" "nenhum out/**/cmp/src_*/funcs.tsv — o painel mostra o exe zerado até um make pg-base"; fi
for s in STOP DONE DONE-B DONE-C NEEDS_HUMAN.md NEEDS_HUMAN-B.md NEEDS_HUMAN-C.md; do
  [ -e "$R/$s" ] && aviso "marca $s" "existe — a(s) frente(s) correspondente(s) não inicia(m) sessão nova"
done

echo "# apoio"
tem AVISO "backups"               "/root/backups" "bundle do git + externos (docs/RETOMAR.md, seção 10)"
if command -v systemctl >/dev/null && systemctl is-active --quiet jp983-painel 2>/dev/null; then ok "serviço jp983-painel" "ativo"
else aviso "serviço jp983-painel" "inativo — o painel web não atualiza (make painel continua funcionando)"; fi
mem=$(awk '/MemTotal/{printf "%d", $2/1048576}' /proc/meminfo 2>/dev/null)
[ -n "$mem" ] && { if [ "$mem" -ge 30 ]; then ok "memória" "${mem} GB"; else aviso "memória" "${mem} GB — com menos de 32 GB, um build ou Ghidra por vez"; fi; }
disp=$(df -BG --output=avail "$R" 2>/dev/null | tail -1 | tr -dc 0-9)
[ -n "$disp" ] && { if [ "$disp" -ge 10 ]; then ok "disco livre" "${disp} GB"; else aviso "disco livre" "${disp} GB — build/ ocupa ~3 GB por cópia"; fi; }

echo
echo "resumo: $nok OK, $naviso AVISO, $nfalta FALTA"
[ $nfalta = 0 ]
