#!/usr/bin/env python3
# richhdr.py <pe>... : decodifica o Rich header (ferramentas usadas no build): prodid, build, contagem.
import sys, struct
# prodids do VS2010 (linker 10.0); os demais saem só como número
PROD = {0x00: 'Unmarked', 0x01: 'Import0', 0x9a: 'Cvtres1000', 0x9b: 'Export1000', 0x9c: 'Implib1000',
        0x9d: 'Linker1000', 0x9e: 'Masm1000', 0xaa: 'Utc1600_C', 0xab: 'Utc1600_CPP', 0xac: 'Utc1600_CVTCIL_C',
        0xad: 'Utc1600_CVTCIL_CPP', 0xae: 'Utc1600_LTCG_C', 0xaf: 'Utc1600_LTCG_CPP', 0xb0: 'Utc1600_LTCG_MSIL',
        0xb1: 'Utc1600_POGO_I_C', 0xb2: 'Utc1600_POGO_I_CPP', 0xb3: 'Utc1600_POGO_O_C', 0xb4: 'Utc1600_POGO_O_CPP',
        0x93: 'Implib900', 0x83: 'Utc1500_C', 0x84: 'Utc1500_CPP', 0x95: 'Masm900', 0x7b: 'Implib800',
        0x5d: 'Implib710', 0x5f: 'Utc1310_C', 0x60: 'Utc1310_CPP', 0x0f: 'Masm710', 0x19: 'Implib700',
        0x0a: 'Utc12_C', 0x0b: 'Utc12_CPP', 0x04: 'Linker600', 0x06: 'Cvtres500', 0x0e: 'Masm613'}
def rich(path):
    d = open(path, 'rb').read(0x1000)
    e = d.find(b'Rich')
    if e < 0: return None
    key = struct.unpack_from('<I', d, e + 4)[0]
    s = None
    for o in range(e - 4, 0x3c, -4):
        if struct.unpack_from('<I', d, o)[0] ^ key == 0x536e6144: s = o; break
    if s is None: return None
    out = []
    for o in range(s + 16, e, 8):
        v, c = struct.unpack_from('<II', d, o)
        v ^= key; c ^= key
        out.append((v >> 16, v & 0xffff, c))
    return out
for p in sys.argv[1:]:
    print('==', p)
    r = rich(p)
    if not r: print('  sem Rich header'); continue
    for prod, build, cnt in r:
        print('  prod=0x%02x %-20s build=%5d n=%d' % (prod, PROD.get(prod, '?'), build, cnt))
