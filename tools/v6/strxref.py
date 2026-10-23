#!/usr/bin/env python3
"""strxref.py EXE 'texto'[enc] ... — VA das strings (cp949/ascii) e instruções que as referenciam (imm32 no .text) + função
(início pelo map/j2_funcs ou pelo 'push ebp/sub esp' anterior). Uso: frente C, F4 (teste 3)."""
import sys, struct, re
f = sys.argv[1]; d = open(f, 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [(d[st+40*i:st+40*i+8].rstrip(b'\0').decode(),) + struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def va(o):
    for n, vs, v, rs, ro in secs:
        if ro <= o < ro + rs: return base + v + o - ro
text = ([s for s in secs if s[0] == '.text'] or [secs[0]])[0]  # dump do 983: 1ª seção sem nome
tb = d[text[4]:text[4] + text[3]]; tva = base + text[2]
for s in sys.argv[2:]:
    for m in re.finditer(re.escape(s.encode('cp949')), d):
        # início da string (volta até o \0)
        o = m.start()
        while o > 0 and d[o - 1] != 0: o -= 1
        v = va(o)
        if v is None: continue
        refs = [tva + r.start() for r in re.finditer(re.escape(struct.pack('<I', v)), tb)]
        print(f'{s!r} str@{v:08x} ' + d[o:d.find(b"\0", o)].decode('cp949', 'replace') + ' refs: ' + ' '.join(f'{r:08x}' for r in refs))
