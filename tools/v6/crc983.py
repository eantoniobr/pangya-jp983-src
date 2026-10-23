#!/usr/bin/env python3
"""crc983.py ARQ... — CRC do IntegrityPakCRC do 983 (0098f4c0 -> 00a5dac0 -> 00a5d630).
Tabela 00a5d8f0: T[i] = refl32(f(refl8(i) << 24)), f = 8 vezes x = (x<<1) ^ (0xedb88320 se bit31) — o polinômio REFLETIDO
usado no laço MSB-first (não é o CRC32 do zlib). Atualização 00a5d2b0: c = (c >> 8) ^ T[(c ^ b) & 0xff]; início 0xffffffff,
fim = ~c (00a5d89c). O arquivo é lido inteiro (_open/_read em blocos de 0x19000). Saída: crc hex, como int32 (fcrc), fsize."""
import sys, struct

def refl(v, n):
    r = 0
    for i in range(1, n + 1):
        if v & 1: r |= 1 << (n - i)
        v >>= 1
    return r

T = []
for i in range(256):
    x = refl(i, 8) << 24
    for _ in range(8):
        x = ((x << 1) ^ (0xedb88320 if x & 0x80000000 else 0)) & 0xffffffff
    T.append(refl(x, 32))

def crc983(data):
    c = 0xffffffff
    for b in data:
        c = (c >> 8) ^ T[(c ^ b) & 0xff]
    return c ^ 0xffffffff

def int32(v): return struct.unpack('<i', struct.pack('<I', v))[0]

if __name__ == '__main__':
    for p in sys.argv[1:]:
        d = open(p, 'rb').read(); c = crc983(d)
        print(f'{c:08x} {int32(c)} {len(d)} {p}')
