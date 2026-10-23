#!/bin/bash
# tools/f35/ijl15limpo.sh — ijl15.dll LIMPO (A193, docs/RUGBURN.md): só a Intel JPEG Library 1.5 (third_party/ijl/ijl15l.lib
# do rugburn público) com as 6 exportações do ijl15 verdadeiro; sem DllMain, sem ganchos, sem rugburn.json.
# Saída: build/A/ijl15limpo/ijl15.dll (+ MD5.txt). Uso: tools/f35/ijl15limpo.sh
set -e
R=/root/jp983src; RB=$R/build/C/v5/rugburn; O=$R/build/A/ijl15limpo
V=/root/kr839/local/vs2010; S=/root/rebang/tools/PlatformSDK-Aug2002; VS=$R/tools/vs.sh
rm -rf $O; mkdir -p $O
$VS cl /nologo /c /TP /O2 /GS- /Zl /W1 /DWIN32 /DNDEBUG /I$R/tools/v6/ijl15teste/compat /I$V/VC10/include /I$V/compat /I$S/include /Fo$O/ijl15.obj $RB/src/ijl15.c >$O/cl.log 2>&1 \
  || { cat $O/cl.log; exit 1; }
$VS ml /nologo /c /coff /Fo$O/stubs.obj $RB/src/stubs.asm >>$O/cl.log 2>&1 || { cat $O/cl.log; exit 1; }  # __except_list, __fltused, __aullshr
$VS link /nologo /DLL /NOENTRY /NODEFAULTLIB /DEF:$RB/export.def /OUT:$O/ijl15.dll /MAP:$O/ijl15.map /IMPLIB:$O/ijl15.lib \
  $O/ijl15.obj $O/stubs.obj $RB/third_party/ijl/ijl15l.lib $RB/third_party/msvcrt/msvcrt.lib $V/sdklib/kernel32.lib >$O/link.log 2>&1 \
  || { cat $O/link.log; exit 1; }
md5sum $O/ijl15.dll | tee $O/MD5.txt
