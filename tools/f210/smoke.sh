#!/bin/bash
# F2.10: teste de carga sob Wine — compila tools/f210/smoke.cpp, carrega a nossa wangreal.dll e a do 983 e compara a saída.
# uso: tools/f210/smoke.sh [dir_saida]   (depois de make wangreal-full)
R=$(cd "$(dirname "$0")/../.." && pwd); O=${1:-$R/build/f210/smoke}; V=${VS:-/root/kr839/local/vs2010}
mkdir -p "$O/ours" "$O/ref"
make -s -C "$R" obj F=tools/f210/smoke.cpp || exit 1
"$R/tools/vs.sh" link /NOLOGO /MACHINE:X86 /SUBSYSTEM:CONSOLE /NODEFAULTLIB /OUT:$O/smoke.exe \
  $R/build/obj/tools/f210/smoke.obj $V/sdklib/kernel32.lib $V/VC10/lib/msvcrt.lib || exit 1
cp "$R/build/wangreal-full/wangreal.dll" "$O/ours/wangreal.dll"; cp "$R/ref/wangreal_983.dll" "$O/ref/wangreal.dll"
cd "$O"
for d in ours ref; do
  echo "== $d"; timeout 60 "$R/tools/vs.sh" run smoke.exe "Z:${O//\//\\}\\$d\\wangreal.dll" 2>&1 | tr -d '\r' | tee $d.txt
done
diff ours.txt ref.txt && echo SAIDAS_IGUAIS
