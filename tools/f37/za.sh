#!/bin/bash
# za.sh ini fim — desmontagem compacta (sem prólogo/epílogo/montagem de std::string)
cd /root/jp983src
python3 tools/f37/dz.py $1 $2 | grep -Ev "fs:\[0\]|0xe43bd8|xor +e.x, ebp|^\S+ +pop +e(bx|si|di|bp)$|mov +ebp, esp|ebp - 4\], |ebp - 0x[0-9a-f]+\], (edi|ebx|0xf)$|byte ptr \[e.x\], bl$|ecx \+ 0x1[04]\], e(di|bx)|mov +ecx, esp$|sub +esp, 0x1c|ebp - 0x[0-9a-f]+\], esp$|call +0xc3c190|cmp +dword ptr \[ebp - 0x[0-9a-f]+\], 0x10|security_check|^\S+ +ret|leave|push +-1$|push +0xc6[0-9a-f]{4}|sub +esp, 0x[0-9a-f]+$|mov +esp, ebp|add +esp, " | sed -E 's/  ; f=.*//; s/dword ptr //g; s/byte ptr /b:/g' | cut -c1-120
