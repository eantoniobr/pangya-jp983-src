#!/bin/bash
for p in $(ps -eo pid,args | awk "\$2==\"/bin/bash\" && \$3==\"/root/jp983src/run-frente.sh\" {print \$1}"); do kill $p; done
sleep 1
for X in A B C D E; do setsid -f /root/jp983src/run-frente.sh $X >/dev/null 2>&1 </dev/null; sleep 3; done
sleep 8; ps -eo args | grep "run-frente" | grep -v grep
