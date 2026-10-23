#!/bin/bash
# F2.11: teste diferencial — FillVertex, WQuat::SetFromAxisAngle, WIsInTriangle e WCollisionTest chamadas por RVA na
# nossa wangreal.dll (RVA do .map) e na do 983 (RVA de map/wangreal.tsv), mesmas entradas; compara os resumos.
# uso: tools/f211/difftest.sh [dir_saida]   (depois de make wangreal-full)
R=$(cd "$(dirname "$0")/../.." && pwd); O=${1:-$R/build/f211/difftest}; V=${VS:-/root/kr839/local/vs2010}
mkdir -p "$O/ours" "$O/ref"
make -s -C "$R" obj F=tools/f211/difftest.cpp || exit 1
"$R/tools/vs.sh" link /NOLOGO /MACHINE:X86 /SUBSYSTEM:CONSOLE /NODEFAULTLIB /OUT:$O/difftest.exe \
  $R/build/obj/tools/f211/difftest.obj $V/sdklib/kernel32.lib $V/VC10/lib/msvcrt.lib || exit 1
cp "$R/build/wangreal-full/wangreal.dll" "$O/ours/wangreal.dll"; cp "$R/ref/wangreal_983.dll" "$O/ref/wangreal.dll"
S='?FillVertex@WDirect3D8@@CIXPAEPBEHHHPBUD3DXMATRIX@@@Z ?SetFromAxisAngle@WQuat@@AAEXABVWVector@@M@Z ?WIsInTriangle@@YI_NABVWVector@@000H@Z ?WCollisionTest@@YIMABVWaabb@@ABVWVector@@0PAVWPlane@@@Z'
ours=""; for s in $S; do
  a=$(awk -v s="$s" '$2==s{print $3; exit}' "$R/build/wangreal-full/wangreal.map"); [ -n "$a" ] || { echo "sem $s no .map"; exit 1; }
  ours="$ours $(printf %x $((0x$a - 0x10000000)))"
done
ref="18fb0 5ce10 5db10 5de90"
echo "RVA nossa:$ours | 983: $ref"
cd "$O"
timeout 120 "$R/tools/vs.sh" run difftest.exe "Z:${O//\//\\}\\ours\\wangreal.dll" $ours 2>&1 | tr -d '\r' > ours.txt
timeout 120 "$R/tools/vs.sh" run difftest.exe "Z:${O//\//\\}\\ref\\wangreal.dll" $ref 2>&1 | tr -d '\r' > ref.txt
tail -4 ours.txt
echo "linhas: nossa $(wc -l < ours.txt), 983 $(wc -l < ref.txt); linhas diferentes: $(diff ours.txt ref.txt | grep -c '^<')"
diff ours.txt ref.txt > diff.txt && echo SAIDAS_IGUAIS
