#!/usr/bin/env python3
"""msgmap.py VA_INI [n_bytes] — mapa de mensagens Fresh de classe com herança múltipla no 983: os ponteiros de método são
gravados por um inicializador estático (`mov eax, handler; mov [entrada+k], eax`). Desmonta a partir de VA_INI, e para cada
handler gravado lê na entrada estática (32 B: pmf de 16 B, nome, cmd, tipo, 0) o nome do controle e o cmd.
Saída: handler  cmd  nome_do_controle  [deslocamentos que o handler grava em this, 0x1c..0x400]"""
import sys, os, re, struct, capstone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pgdis as P
def entries(va, n=0x4000, back=0x3000):
    """(slot, handler) de cada `mov eax, imm32; mov [slot], eax` (b8 .. a3 ..) em [va-back, va+n), por padrão de bytes
    (o inicializador de uma classe pode começar antes de va e não há fronteira de função confiável)."""
    o = P.off(va - back); blob = P.d[o:o + back + n]; out = []
    for m in re.finditer(rb'\xb8(.{3}\x00)\xa3(.{3}\x00)', blob, re.S):
        h, slot = struct.unpack('<I', m.group(1))[0], struct.unpack('<I', m.group(2))[0]
        if 0x401000 <= h < 0xc3d000 and P.off(slot) is not None: out.append((slot, h))
    return out
def stores(h, lo=0x1c, hi=0x4000):
    """deslocamentos gravados em `this` pelo handler (thiscall: ecx, ou o registrador que recebeu ecx no começo)."""
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); w = []; th = {'ecx'}
    for i in md.disasm(P.d[P.off(h):P.off(h) + 600], h):
        m = re.match(r'(?:dword|byte|word) ptr \[(e\w\w) \+ (0x[0-9a-f]+)\], ', i.op_str)
        if i.mnemonic == 'mov' and m and m.group(1) in th and lo <= int(m.group(2), 16) < hi and m.group(2) not in w: w.append(m.group(2))
        m = re.match(r'(e\w\w), (e\w\w)$', i.op_str)
        if i.mnemonic == 'mov' and m:
            if m.group(2) == 'ecx' and 'ecx' in th: th.add(m.group(1))
            else: th.discard(m.group(1))
        elif i.mnemonic in ('mov', 'lea', 'pop', 'xor', 'movzx') and i.op_str.split(',')[0] in th: th.discard(i.op_str.split(',')[0])
        if i.mnemonic == 'call': th -= {'ecx', 'eax', 'edx'}
        if i.mnemonic in ('ret', 'int3'): break
    return w
if __name__ == '__main__':
    va = int(sys.argv[1], 16); n = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x4000
    for slot, h in entries(va, n, 0):
        o = P.off(slot); nm = None
        name, cmd = struct.unpack_from('<II', P.d, o + 16)   # entrada do 983 = pmf (16 B) + nome + cmd + tipo + 0
        nm = P.cstr(name) if name else None
        print('%08x cmd=%-6x %-36s %s' % (h, cmd if nm else 0, nm or '?', ' '.join(stores(h))))
