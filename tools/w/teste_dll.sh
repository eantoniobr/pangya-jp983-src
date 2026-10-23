#!/bin/bash
# W: carga (smoke da F2.10) + teste diferencial (difftest da F2.11) de uma wangreal.dll qualquer (ex.: híbrida da F2.12)
# contra a do 983. uso: tools/w/teste_dll.sh DLL DIR_SAIDA   (os .exe de teste vêm de build/f210 e build/f211; se
# faltarem, rode antes make smoke / make difftest)
R=$(cd "$(dirname "$0")/../.." && pwd); DLL=$(readlink -f "$1"); O=$(mkdir -p "$2" && readlink -f "$2")
M=${DLL%.dll}.map; [ -f "$M" ] || M=$R/build/wangreal-full/wangreal.map  # W4: RVA pelo .map da PRÓPRIA dll (antes: sempre o de build/wangreal-full)
SM=$R/build/f210/smoke/smoke.exe; DT=$R/build/f211/difftest/difftest.exe
[ -f "$SM" ] && [ -f "$DT" ] || { echo "falta $SM ou $DT"; exit 1; }
mkdir -p "$O/t/ours" "$O/t/ref"; cp "$SM" "$DT" "$O/t/"
cp "$DLL" "$O/t/ours/wangreal.dll"; cp "$R/ref/wangreal_983.dll" "$O/t/ref/wangreal.dll"
cd "$O/t"
W=$(echo "$O/t" | sed 's#/#\\#g')
for d in ours ref; do
  timeout 60 "$R/tools/vs.sh" run smoke.exe "Z:$W\\$d\\wangreal.dll" 2>&1 | tr -d '\r' > "$O/smoke_$d.txt"
done
diff "$O/smoke_ours.txt" "$O/smoke_ref.txt" > /dev/null && echo "smoke: SAIDAS_IGUAIS" || echo "smoke: DIFERENTE"
S='?FillVertex@WDirect3D8@@CIXPAEPBEHHHPBUD3DXMATRIX@@@Z ?SetFromAxisAngle@WQuat@@AAEXABVWVector@@M@Z ?WIsInTriangle@@YI_NABVWVector@@000H@Z ?WCollisionTest@@YIMABVWaabb@@ABVWVector@@0PAVWPlane@@@Z'
ours=""; for s in $S; do
  a=$(awk -v s="$s" '$2==s{print $3; exit}' "$M"); ours="$ours $(printf %x $((0x$a - 0x10000000)))"
done
timeout 300 "$R/tools/vs.sh" run difftest.exe "Z:$W\\ours\\wangreal.dll" $ours 2>&1 | tr -d '\r' > "$O/dt_ours.txt"
timeout 300 "$R/tools/vs.sh" run difftest.exe "Z:$W\\ref\\wangreal.dll" 18fb0 5ce10 5db10 5de90 2>&1 | tr -d '\r' > "$O/dt_ref.txt"
echo "difftest: linhas nossa $(wc -l < "$O/dt_ours.txt"), 983 $(wc -l < "$O/dt_ref.txt"), diferentes $(diff "$O/dt_ours.txt" "$O/dt_ref.txt" | grep -c '^<')"
rm -rf "$O/t"
