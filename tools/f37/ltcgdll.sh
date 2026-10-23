#!/bin/bash
# ltcgdll.sh nome unidade... — compila as unidades com /GL (flags do exe com /Ob2 /GF /GL; LTCG_FLAGS troca) em build/B/ltcg/<nome>/ e liga uma dll de
# prova com link /LTCG /OPT:NOREF /OPT:NOICF /FORCE /MAP (para o ltcgcmp.py). Os .obj normais em build/B/obj são refeitos no fim.
cd /root/jp983src; N=$1; shift; D=/root/jp983src/build/B/ltcg/$N; mkdir -p $D; VS=/root/kr839/local/vs2010
F="${LTCG_FLAGS:-/MD /W3 /EHsc /Z7 /O2 /Ob2 /GF /Gr /GS /Oy- /GL}"; O=()
for u in "$@"; do
  python3 tools/f37/jpbuild.py obj --flags "$F" --src src/projectg/jp/$u.cpp | grep -v " 1 de 1"
  mv build/B/obj/$u.obj $D/; O+=($D/$u.obj)
  python3 tools/f37/jpbuild.py obj --src src/projectg/jp/$u.cpp | grep -v " 1 de 1"
done
O+=($LTCG_EXTRA)  # B146: objs extras (âncoras da convenção, ver build/B/s146/ancora)
tools/vs.sh link /NOLOGO /DLL /NOENTRY /LTCG /OPT:NOREF /OPT:NOICF /NODEFAULTLIB /MAP:$D/$N.map /FORCE /MACHINE:X86 /OUT:$D/$N.dll \
  "${O[@]}" $VS/VC10/lib/msvcrt.lib $VS/VC10/lib/msvcprt.lib $VS/VC10/lib/oldnames.lib $VS/sdklib/kernel32.lib > $D/link.log 2>&1
echo "ltcgdll: $D/$N.dll ($(stat -c %s $D/$N.dll 2>/dev/null || echo 0) bytes; $(grep -c 'error LNK2001' $D/link.log) externos não resolvidos)"
