#!/bin/bash
# F2.13 (frente W): teste diferencial do upload de textura (tools/w/difftex.cpp) — nossa dll × wangreal_983.dll.
# uso: tools/w/difftex.sh [dll_nossa] [dir_saida]   (padrão: build/W/wangreal-full/wangreal.dll, out/F2.13/difftex)
R=$(cd "$(dirname "$0")/../.." && pwd); D=${1:-$R/build/W/wangreal-full/wangreal.dll}; O=${2:-$R/out/F2.13/difftex}
V=${VS:-/root/kr839/local/vs2010}; M=${D%.dll}.map
mkdir -p "$O/ours" "$O/ref"; O=$(readlink -f "$O"); D=$(readlink -f "$D"); M=${D%.dll}.map
make -s -C "$R" obj F=tools/w/difftex.cpp || exit 1
"$R/tools/vs.sh" link /NOLOGO /MACHINE:X86 /SUBSYSTEM:CONSOLE /NODEFAULTLIB /OUT:$O/difftex.exe \
  $R/build/obj/tools/w/difftex.obj $V/sdklib/kernel32.lib $V/VC10/lib/msvcrt.lib || exit 1
cp "$D" "$O/ours/wangreal.dll"; cp "$R/ref/wangreal_983.dll" "$O/ref/wangreal.dll"
S='?FindPixInfoByFormat@WDirect3D8@@KIPAUpix_info@1@W4_D3DFORMAT@@@Z ??0Bitmap@@QAE@HHH@Z ?UpdateTextureSurface@WDirect3D8@@IAEXPAXHHHPAUpix_info@1@PAUtagBITMAPINFO@@0H@Z ?FixTexturePart@WDirect3D8@@UAEXHABUtagRECT@@PAUtagBITMAPINFO@@PAXH@Z ?UpdateTextureSurface@WDirect3D8@@UAEXHPAUtagBITMAPINFO@@PAXH@Z ?CreateTextureSurface@WDirect3D8@@UAEXKKHHHHHH@Z'
ours=""; ref=""; for s in $S; do
  a=$(awk -v s="$s" '$2==s{print $3; exit}' "$M"); [ -n "$a" ] || { echo "sem $s no .map"; exit 1; }
  b=$(awk -F'\t' -v s="$s" '$1==s{print $2; exit}' "$R/map/wangreal.tsv"); [ -n "$b" ] || { echo "sem $s no tsv"; exit 1; }
  ours="$ours $(printf %x $((0x$a - 0x10000000)))"; ref="$ref $(printf %x $((0x$b - 0x10000000)))"
done
echo "RVA nossa:$ours | 983:$ref"
cd "$O"
timeout 900 "$R/tools/vs.sh" run difftex.exe "Z:${O//\//\\}\\ours\\wangreal.dll" $ours 2>&1 | tr -d '\r' > ours.txt
timeout 900 "$R/tools/vs.sh" run difftex.exe "Z:${O//\//\\}\\ref\\wangreal.dll" $ref 2>&1 | tr -d '\r' > ref.txt
grep -E "casos" ours.txt
echo "linhas: nossa $(wc -l < ours.txt), 983 $(wc -l < ref.txt); linhas diferentes: $(diff ours.txt ref.txt | grep -c '^<')"
grep -q "^casos executados" ours.txt && grep -q "^casos executados" ref.txt || { echo "FALHA: teste não rodou até o fim"; exit 1; }
diff ours.txt ref.txt > diff.txt && echo SAIDAS_IGUAIS
