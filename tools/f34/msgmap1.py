#!/usr/bin/env python3
"""msgmap1.py VA|Classe — mapa de mensagens Fresh de uma classe do 983 a partir do GetMessageMap (VA da função, VA do
sFRESH_MSGMAP, ou nome da classe em map/projectg.tsv): segue map->entries (32 B: pmf de 16 B gravado por inicializador
estático, nome, cmd, tipo, 0) e acha o handler de cada entrada procurando no código `mov eax, handler; mov [entrada], eax`
(ou `mov dword [entrada], handler`). Vale também para herança simples (msgmap.py precisa do VA do inicializador).
Saída: handler  cmd  nome_do_controle  [deslocamentos que o handler grava em this]"""
import sys, os, re, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pgdis as P, msgmap as M
def u32(va): return struct.unpack_from('<I', P.d, P.off(va))[0]
TEXT = None
def handler(slot):
    global TEXT
    if TEXT is None: TEXT = P.d[P.off(0x401000):P.off(0xd00000 - 1)]
    s = struct.pack('<I', slot)
    i = TEXT.find(b'\xc7\x05' + s)
    if i >= 0: return struct.unpack_from('<I', TEXT, i + 6)[0]
    for r in range(8):   # mov [entrada], reg com o `mov reg, handler` logo antes (ou um pouco antes)
        i = TEXT.find((b'\xa3' if r == 0 else bytes([0x89, 0x05 | r << 3])) + s)
        for j in range(i - 5, max(i - 0x180, 0), -1) if i >= 0 else ():
            h = struct.unpack_from('<I', TEXT, j + 1)[0]
            if TEXT[j] == 0xb8 + r and 0x401000 <= h < 0xc3d000: return h
    return 0
def table(a):
    """lista (handler, cmd, nome) do mapa em a (VA do GetMessageMap, do sFRESH_MSGMAP, ou nome de classe)."""
    if not re.fullmatch(r'[0-9a-fA-F]{6,8}', a):
        a = '%x' % [va for va, n in P.names.items() if n.startswith('?GetMessageMap@%s@@' % a)][0]
    va = int(a, 16)
    if P.d[P.off(va)] == 0xb8 and P.d[P.off(va) + 5] == 0xc3: va = u32(va + 1)
    ent = u32(va + 4); out = []
    while True:
        name, cmd, typ = struct.unpack_from('<III', P.d, P.off(ent) + 16)
        if not name and not typ: break
        out.append((handler(ent), cmd, P.cstr(name) if name else '', ent)); ent += 32
    return out
if __name__ == '__main__':
    for h, cmd, nm, ent in table(sys.argv[1]):
        print('%08x cmd=%-6x %-36s %s' % (h, cmd, nm, ' '.join(M.stores(h)) if h else '?'))
