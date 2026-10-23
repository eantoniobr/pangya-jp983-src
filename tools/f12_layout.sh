#!/bin/bash
# f12_layout.sh <arquivo.cpp> <saida.txt> — layout de todas as classes vistas pelo .cpp (cl /d1reportAllClassLayout)
R=/root/jp983src; VS=${VS:-/root/kr839/local/vs2010}; RB=/root/rebang
mkdir -p $R/build/f12
VS=$VS $R/tools/vs.sh cl /nologo /c /MD /W3 /EHsc /O2 /Ob1 /Gr /GS /Oy- /DNDEBUG /DWIN32 /D_WINDOWS /D_MBCS /DWANGREAL_DEVICE \
  /I$R/include /I$R/include/engine /I$R/src/shared /I$VS/VC10/include /I$VS/compat \
  /I$RB/tools/PlatformSDK-Aug2002/include /I$RB/tools/DirectX9/include \
  /d1reportAllClassLayout /Fo$R/build/f12/layout.obj "$R/$1" | tr -d '\r' > "$2"
