#!/usr/bin/env python3
"""f37/rsum.py <diff.txt> [ini fim] — resume o lado 983 (coluna da direita do dfull.sh) como lista de envios de mensagem
(ator, id, args), calls por endereco, comparacoes e saltos. Para ler o OnPacket case a case sem ler o asm todo."""
import sys, re, struct
d = open('/root/jp983src/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe+6)[0]; oh = pe+24
base = struct.unpack_from('<I', d, oh+28)[0]; st = oh+struct.unpack_from('<H', d, pe+20)[0]
secs = [struct.unpack_from('<IIII', d, st+40*i+8) for i in range(ns)]
def cstr(va):
    r = va-base
    for vs, v, rs, ro in secs:
        if v <= r < v+max(vs, rs):
            return d[ro+r-v:ro+r-v+60].split(b'\0')[0].decode('latin-1')
f = sys.argv[1]; a = int(sys.argv[2]) if len(sys.argv) > 2 else 0; b = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
R = []
for i, l in enumerate(open(f)):
    if a <= i <= b:
        t = l[104:].strip()
        if t: R.append((i, t))
name = None; fields = {}; out = []; pushes = []; zero = set()
def val(v):
    return '0' if v in zero else v
for i, t in R:
    m = re.match(r'xor (e..), (e..)$', t)
    if m and m.group(1) == m.group(2): zero.add(m.group(1))
    else:
        m = re.match(r'(?:mov|movzx|lea|pop|add|sub|imul|shr|sar) (e..),', t)
        if m: zero.discard(m.group(1))
        if t.startswith('call'): zero -= {'eax', 'ecx', 'edx'}
        if re.match(r'(j|L)', t) : pass
    m = re.match(r'push 0x([0-9a-f]{6,8})\s+<', t)
    if m and cstr(int(m.group(1), 16)) is not None and int(m.group(1), 16) > 0xc00000:
        name = cstr(int(m.group(1), 16)); continue
    m = re.match(r'mov dword ptr \[ebp - 0x([0-9a-f]+)\], (.*)', t)
    if m:
        fields[int(m.group(1), 16)] = val(m.group(2)); continue
    m = re.match(r'push (\S+)', t)
    if m: pushes.append(val(re.sub(r'\s.*', '', m.group(1)))); continue
    m = re.match(r'call <([0-9a-f]{8})>', t)
    if m and m.group(1) == '0046e780':
        v = pushes[::-1][:7]
        out.append('%5d MSG id=%s a=[%s]' % (i, v[1] if len(v) > 1 else '?', ','.join(v[2:])))
        pushes = []; continue
    if m:
        pushes = []
        if m.group(1) == '009bac50' and fields:
            cand = [k for k in fields if (k+4) in fields and (k-4) in fields and fields[k].startswith(('0x', '1', '2', '3', '4', '5', '6', '7', '8', '9'))]
            k = max(cand) if cand else None
            if k is None:
                out.append('%5d SEND "%s" ?' % (i, name))
            else:
                vals = [fields.get(k+4-4*j, '-') for j in range(8)]
                out.append('%5d SEND "%s" id=%s a=[%s]' % (i, name, vals[1], ','.join(vals[2:7])))
            name = None; fields = {}
        else:
            out.append('%5d call %s' % (i, m.group(1)))
        continue
    if re.match(r'(cmp|test|j[a-z]+|jmp|ret|rep )', t) or 'switch' in t or t.startswith('mov eax, 1'):
        out.append('%5d   %s' % (i, t[:60]))
print('\n'.join(out))
