#!/bin/bash
# tools/v6/ijl15teste/build.sh — ijl15_teste.dll (C-F4.6): rugburn PÚBLICO (build/C/v5/rugburn, commit 7158511) com o VS2010
# do container, SEM nenhum patch de endereço fixo (dynamic_patch.c trocado por sem_endereco.c; ranking US 852 fora).
# Saída: build/C/f4/ijl15teste/ijl15_teste.dll (+ .map/.log). Uso: tools/v6/ijl15teste/build.sh
# C291: ORIG=1 tools/v6/ijl15teste/build.sh = mesmo rugburn COM o dynamic_patch.c público (patches GG por versão, JP 983) para o
# exe ORIGINAL (pedido exe=original ijl=teste; sem eles o original cai em 1 s, C136). Saída em build/C/f4/ijl15orig/ (mesmo nome de dll).
set -e
R=/root/jp983src
RB=$R/build/C/v5/rugburn
O=$R/build/C/f4/ijl15teste
SE=$R/tools/v6/ijl15teste/sem_endereco.c
[ "$ORIG" = 1 ] && { O=$R/build/C/f4/ijl15orig; SE=$RB/src/hooks/comctl32/dynamic_patch.c; }
V=/root/kr839/local/vs2010
S=/root/rebang/tools/PlatformSDK-Aug2002
VS=$R/tools/vs.sh
[ -d $RB/src ] || { echo "falta $RB (clone do rugburn público, make v5)"; exit 1; }
[ -f $R/build/C/f4/ws2_32.lib ] || { echo "falta build/C/f4/ws2_32.lib (import por nome; make f4-link)"; exit 1; }
rm -rf $O; mkdir -p $O
FONTES="common.c config.c dll/rugburn/main.c hex.c hooks/ole32/web_browser.c ijl15.c hooks/hooks.c hooks/kernel32/inject.c
 hooks/user32/window.c hooks/wininet/netredir.c hooks/ws2_32/redir.c json.c patch.c regex.c ld.c hooks/msvcr100/msvcr100.c"
CF="/nologo /c /TP /O2 /GS- /Zl /W1 /DWIN32 /DNDEBUG /D_NO_CRT_STDIO_INLINE /DSTRSAFE_NO_DEPRECATE /D_CRT_SECURE_NO_WARNINGS
 /DSECURITY_FLAG_IGNORE_WEAK_SIGNATURE=0x00010000
 /I$R/tools/v6/ijl15teste/compat /I$V/VC10/include /I$V/compat /I$S/include /I/root/rebang/tools/DirectX9/include"
OBJS=()
for f in $FONTES; do
  o=$O/$(echo $f | tr / _ | sed 's/\.c$/.obj/')
  $VS cl $CF /Fo$o $RB/src/$f >>$O/cl.log 2>&1 || { tail -20 $O/cl.log; echo "ERRO cl $f"; exit 1; }
  OBJS+=($o)
done
$VS cl $CF /I$RB/src/hooks/comctl32 /Fo$O/sem_endereco.obj $SE >>$O/cl.log 2>&1 \
  || { tail -20 $O/cl.log; echo "ERRO cl sem_endereco.c"; exit 1; }
OBJS+=($O/sem_endereco.obj)
if [ "$ORIG" = 1 ]; then  # o dynamic_patch.c público chama o ranking US 852
  $VS cl $CF /Fo$O/us852_ranking.obj $RB/src/hooks/projectg/us852/ranking.c >>$O/cl.log 2>&1 || { tail -20 $O/cl.log; echo "ERRO cl ranking.c"; exit 1; }
  OBJS+=($O/us852_ranking.obj)
fi
$VS ml /nologo /c /coff /Fo$O/stubs.obj $RB/src/stubs.asm >>$O/cl.log 2>&1 || { tail $O/cl.log; echo "ERRO ml"; exit 1; }
OBJS+=($O/stubs.obj)
$VS link /nologo /DLL /NODEFAULTLIB /ENTRY:DllMain /DEF:$RB/export.def /OUT:$O/ijl15_teste.dll /MAP:$O/ijl15_teste.map \
  /IMPLIB:$O/ijl15_teste.lib /LIBPATH:$S/lib "${OBJS[@]}" $V/sdklib/kernel32.lib $S/lib/user32.lib $S/lib/shlwapi.lib \
  $R/build/C/f4/ws2_32.lib $RB/third_party/msvcrt/msvcrt.lib $RB/third_party/ijl/ijl15l.lib >$O/link.log 2>&1 \
  || { cat $O/link.log; echo "ERRO link"; exit 1; }
cat $O/link.log
md5sum $O/ijl15_teste.dll | tee $O/MD5.txt
ls -l $O/ijl15_teste.dll
