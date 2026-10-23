#!/bin/bash
# W4 (frente W): teste diferencial do WDirect3D::ModifyVertices (tools/w/diffmv.cpp) — nossa dll × wangreal_983.dll.
# uso: tools/w/diffmv.sh [dll_nossa] [dir_saida]   (padrão: build/W/wangreal-full/wangreal.dll, out/W4/diffmv; .map ao lado da dll)
R=$(cd "$(dirname "$0")/../.." && pwd); D=${1:-$R/build/W/wangreal-full/wangreal.dll}; O=${2:-$R/out/W4/diffmv}
V=${VS:-/root/kr839/local/vs2010}
mkdir -p "$O/ours" "$O/ref"; O=$(readlink -f "$O"); D=$(readlink -f "$D"); M=${D%.dll}.map
make -s -C "$R" obj F=tools/w/diffmv.cpp || exit 1
"$R/tools/vs.sh" link /NOLOGO /MACHINE:X86 /SUBSYSTEM:CONSOLE /NODEFAULTLIB /OUT:$O/diffmv.exe \
  $R/build/obj/tools/w/diffmv.obj $V/sdklib/kernel32.lib $V/VC10/lib/msvcrt.lib || exit 1
cp "$D" "$O/ours/wangreal.dll"; cp "$R/ref/wangreal_983.dll" "$O/ref/wangreal.dll"
S='?ModifyVertices@WDirect3D@@IAEPAXABVWTVertexList@@IK_N@Z ?VertexSize@WDirect3D@@MAEKK@Z'
ours=""; ref=""; for s in $S; do
  a=$(awk -v s="$s" '$2==s{print $3; exit}' "$M"); [ -n "$a" ] || { echo "sem $s no .map"; exit 1; }
  b=$(awk -F'\t' -v s="$s" '$1==s{print $2; exit}' "$R/map/wangreal.tsv"); [ -n "$b" ] || { echo "sem $s no tsv"; exit 1; }
  ours="$ours $(printf %x $((0x$a - 0x10000000)))"; ref="$ref $(printf %x $((0x$b - 0x10000000)))"
done
echo "RVA nossa:$ours | 983:$ref"
cd "$O"
timeout 900 "$R/tools/vs.sh" run diffmv.exe "Z:${O//\//\\}\\ours\\wangreal.dll" $ours 2>&1 | tr -d '\r' > ours.txt
timeout 900 "$R/tools/vs.sh" run diffmv.exe "Z:${O//\//\\}\\ref\\wangreal.dll" $ref 2>&1 | tr -d '\r' > ref.txt
grep -E "^resumo|^casos" ours.txt ref.txt
echo "linhas: nossa $(wc -l < ours.txt), 983 $(wc -l < ref.txt); linhas diferentes: $(diff ours.txt ref.txt | grep -c '^<')"
grep -q "^casos executados" ours.txt && grep -q "^casos executados" ref.txt || { echo "FALHA: teste não rodou até o fim"; exit 1; }
diff ours.txt ref.txt > diff.txt && echo SAIDAS_IGUAIS
