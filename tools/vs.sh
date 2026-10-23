#!/bin/bash
# vs.sh <cl|link|lib|dumpbin|undname|run> args...
# Roda uma ferramenta do VS2010 SP1 (cl 16.00.40219.01) sob Wine. Todo caminho absoluto /root/... nos
# argumentos vira Z:\root\... (funciona também colado em opções: /Fo/root/x.obj, /I/root/inc, /OUT:/root/a.dll).
# "run" executa um .exe qualquer no mesmo prefixo (para testar o que foi gerado).
VS=${VS:-/root/kr839/local/vs2010}
export WINEPREFIX=$VS/wine WINEDEBUG=-all WINEDLLOVERRIDES="mscoree,mshtml="
tool=$1; shift
args=()
for a in "$@"; do
  if [[ $a == */root/* ]]; then
    pre=${a%%/root/*}; p=/root/${a#*/root/}
    a="${pre}Z:${p//\//\\}"
  fi
  args+=("$a")
done
case $tool in
  run) exe=$1; shift; exec wine "$exe" "${args[@]:1}" ;;
  *)   exec wine "$VS/VC10/bin/$tool.exe" "${args[@]}" ;;
esac
