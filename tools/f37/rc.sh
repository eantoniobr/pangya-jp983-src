#!/bin/bash
# f37/rc.sh <JPOUT> <unidade sem .cpp>... — recompila e compara só as unidades dadas (jpbuild obj + cmp) e mostra o resumo (res.sh)
cd /root/jp983src
o=$1; shift
S=""; for u in "$@"; do S="$S src/projectg/jp/$u.cpp"; done
python3 tools/f37/jpbuild.py obj --src $S 2>&1 | tail -1
for u in "$@"; do grep -h ' error ' build/B/obj/$u.log | cut -c1-220; done
python3 tools/f37/jpbuild.py cmp --out $o --src $S 2>&1 | tail -1
tools/f37/res.sh $o "$@"
