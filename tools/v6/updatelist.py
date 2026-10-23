#!/usr/bin/env python3
# Pedido C85 (frente C, C-F4.8): updatelist de teste para o web local do PC.
# Cifra = DecodeTEA_NBYTE do 983 (00bc6560; src/shared/tea.cpp): XTEA 16 rodadas, blocos de 8 B little-endian,
# chave g_updateListKey do 983 (00d3d60c). Uso:
#   updatelist.py dec <cifrada> <saida.xml>
#   updatelist.py troca <cifrada_original> <exe> <saida_cifrada> [relatorio.txt]
#     troca fcrc/fsize da linha fname="ProjectG.exe", recifra e confere decifrando de volta.
import sys, struct, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crc983 import crc983
KEY = (0x020a5fd4, 0x01eebdff, 0x02b3c6a0, 0x04f6a3e1)
D = 0x9e3779b9; M = 0xffffffff

def dec_blk(v0, v1, k=KEY):
    s = (D * 16) & M
    for _ in range(16):
        v1 = (v1 - ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ (s + k[(s >> 11) & 3]))) & M
        s = (s - D) & M
        v0 = (v0 - ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ (s + k[s & 3]))) & M
    return v0, v1

def enc_blk(v0, v1, k=KEY):
    s = 0
    for _ in range(16):
        v0 = (v0 + ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ (s + k[s & 3]))) & M
        s = (s + D) & M
        v1 = (v1 + ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ (s + k[(s >> 11) & 3]))) & M
    return v0, v1

def _run(data, f):
    if len(data) % 8: data += b'\0' * (8 - len(data) % 8)
    out = bytearray()
    for i in range(0, len(data), 8):
        out += struct.pack('<2I', *f(*struct.unpack_from('<2I', data, i)))
    return bytes(out)

def decrypt(data): return _run(data, dec_blk)
def encrypt(data):
    # o cliente decifra size arredondado a 8 e faz text += xml: precisa de ao menos um \0 depois do texto
    return _run(data + b'\0', enc_blk)

def s32(x): return x - (1 << 32) if x & 0x80000000 else x

def crc_exe(path):
    # C86: CRC_32::CalcCRC (ccrc32.cpp = 983 00a5d630) NAO e o zlib.crc32: a tabela usa 0xEDB88320 no laco MSB-first
    # + reflexao (tools/v6/crc983.py; confere 0xfb08f75e = fcrc da lista p/ o dump). IntegrityPakCRC compara com
    # atoi(fcrc): a lista guarda int32 com sinal (atoi do msvcr100 satura acima de 2^31-1)
    return s32(crc983(open(path, 'rb').read()))

def troca(orig, exe, saida, rel=None):
    cif = open(orig, 'rb').read()
    xml = decrypt(cif)
    corpo = xml.rstrip(b'\0')
    pad = len(xml) - len(corpo)
    m = re.search(rb'<fileinfo\b[^>]*fname="ProjectG\.exe"[^>]*/?>', corpo, re.I)
    if not m: sys.exit('updatelist.py: linha fname="ProjectG.exe" nao achada')
    antes = m.group(0)
    crc, tam = crc_exe(exe), os.path.getsize(exe)
    depois = re.sub(rb'fcrc="[^"]*"', b'fcrc="%d"' % crc, antes)
    depois = re.sub(rb'fsize="[^"]*"', b'fsize="%d"' % tam, depois)
    novo = corpo[:m.start()] + depois + corpo[m.end():]
    out = encrypt(novo)
    os.makedirs(os.path.dirname(saida) or '.', exist_ok=True)
    open(saida, 'wb').write(out)
    # conferencia: decifrar de volta e comparar com o texto pretendido; tamanho/linhas fora da troca iguais
    volta = decrypt(open(saida, 'rb').read()).rstrip(b'\0')
    ok = volta == novo
    outras = corpo.replace(antes, b'') == volta.replace(depois, b'')
    lin = ['original: %s (%d B, xml %d B, pad %d)' % (orig, len(cif), len(corpo), pad),
           'exe: %s fsize=%d fcrc=%d (0x%08x)' % (exe, tam, crc, crc & M),
           'antes : ' + antes.decode('latin-1'),
           'depois: ' + depois.decode('latin-1'),
           'saida: %s (%d B)' % (saida, len(out)),
           'decifra de volta == texto pretendido: %s' % ('OK' if ok else 'FALHOU'),
           'resto da lista inalterado: %s' % ('OK' if outras else 'FALHOU')]
    t = '\n'.join(lin) + '\n'
    sys.stdout.write(t)
    if rel: open(rel, 'w').write(t)
    if not (ok and outras): sys.exit(1)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['dec']: open(a[2], 'wb').write(decrypt(open(a[1], 'rb').read()).rstrip(b'\0'))
    elif a[:1] == ['troca']: troca(*a[1:5])
    else: sys.exit(__doc__ or 'uso: dec|troca')
