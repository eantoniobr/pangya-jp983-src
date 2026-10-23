#!/usr/bin/env python3
# F3.3 — onde estão os objs LTCG do ProjectG 983 (o Rich header conta 54 objs Utc1600_LTCG_CPP).
# Indício: só com /GL (LTCG) o cl 16 troca a convenção de chamada de funções internas — o argumento chega em
# EAX/ESI/EDI/EBX. Com /Gr comum (o resto do exe) os argumentos vêm em ECX/EDX/pilha e EAX/ESI/EDI/EBX nunca são
# lidos antes de escritos (fora `push reg` de salvar). Para cada função do 983 (lista do Ghidra, map/projectg_funcs.tsv)
# percorre o 1º bloco básico e marca "entrada em registrador fora da convenção". Depois soma por unidade/vão do mapa.
# uso: ltcg.py [--out out/F3.3] [--ref ref/ProjectG_983_dump.exe] [--funcs map/projectg_funcs.tsv]
import argparse, collections, csv, struct, sys
import capstone
from capstone import x86_const as X

ap = argparse.ArgumentParser()
ap.add_argument('--out', default='out/F3.3')
ap.add_argument('--ref', default='ref/ProjectG_983_dump.exe')
ap.add_argument('--funcs', default='map/projectg_funcs.tsv')
a = ap.parse_args()

d = open(a.ref, 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]
nsec = struct.unpack_from('<H', d, pe + 6)[0]
opt = pe + 24
base = struct.unpack_from('<I', d, opt + 28)[0]
sec0 = opt + struct.unpack_from('<H', d, pe + 20)[0]
secs = []
for i in range(nsec):
    vs, va, rs, ro = struct.unpack_from('<IIII', d, sec0 + 40 * i + 8)
    secs.append((base + va, max(vs, rs), ro, rs))


def off(va):
    for s, n, ro, rs in secs:
        if s <= va < s + n:
            o = va - s
            return ro + o if o < rs else None
    return None


FAM = {}
for fam, rs in (('eax', 'EAX AX AH AL'), ('ebx', 'EBX BX BH BL'), ('esi', 'ESI SI SIL'), ('edi', 'EDI DI DIL'),
                ('ecx', 'ECX CX CH CL'), ('edx', 'EDX DX DH DL')):
    for r in rs.split():
        FAM[getattr(X, 'X86_REG_' + r)] = fam
ALVO = ('eax', 'ebx', 'esi', 'edi')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = True
FIM = {X.X86_GRP_JUMP, X.X86_GRP_CALL, X.X86_GRP_RET, X.X86_GRP_INT, X.X86_GRP_IRET}


def entrada(va, sz):
    """registradores de ALVO lidos antes de escritos no 1º bloco (até 40 instruções)"""
    o = off(va)
    if o is None:
        return None
    escritos, lidos = set(), set()
    n = 0
    for ins in md.disasm(d[o:o + min(max(sz, 1), 400)], va):
        n += 1
        if n > 40:
            break
        try:
            rd, wr = ins.regs_access()
        except capstone.CsError:
            break
        idiom = False
        if ins.id in (X.X86_INS_XOR, X.X86_INS_SUB, X.X86_INS_SBB, X.X86_INS_PXOR) and len(ins.operands) == 2:
            p, q = ins.operands
            idiom = p.type == X.X86_OP_REG and q.type == X.X86_OP_REG and p.reg == q.reg
        if ins.id != X.X86_INS_PUSH and not idiom:        # push reg = salvar; xor r,r = zerar
            for r in rd:
                f = FAM.get(r)
                if f in ALVO and f not in escritos:
                    lidos.add(f)
        elif ins.id == X.X86_INS_PUSH and ins.operands[0].type == X.X86_OP_MEM:
            for r in rd:
                f = FAM.get(r)
                if f in ALVO and f not in escritos:
                    lidos.add(f)
        for r in wr:
            f = FAM.get(r)
            if f:
                escritos.add(f)
        if FIM & set(ins.groups):
            break
    return lidos


linhas = list(csv.DictReader(open(a.funcs), delimiter='\t'))
porU = collections.defaultdict(lambda: [0, 0, 0, 0, None, None])   # funções, marcadas, bytes, bytes marcados, ini, fim
with open(f'{a.out}/ltcg_funcs.tsv', 'w') as o:
    o.write('f983\ttam\tentrada_em\tonde\tunidade\tnome983\n')
    for r in linhas:
        va, sz = int(r['f983'], 16), int(r['tam'])
        if va >= 0xc3d000 or sz < 8:      # região E (GameGuard/CRT/funclets) e funções mínimas: fora
            continue
        e = entrada(va, sz)
        if e is None:
            continue
        k = (r['onde'], r['unidade'], r['trecho'])
        u = porU[k]
        u[0] += 1
        u[2] += sz
        u[4] = va if u[4] is None else min(u[4], va)
        u[5] = max(u[5] or 0, va + sz)
        if e:
            u[1] += 1
            u[3] += sz
            o.write('\t'.join([r['f983'], r['tam'], ','.join(sorted(e)), r['onde'], r['unidade'], r['nome983']]) + '\n')
tf = sum(u[0] for u in porU.values())
tm = sum(u[1] for u in porU.values())
R = [f'funcoes examinadas (>= 8 B, antes de 00c3d000): {tf}; com entrada em EAX/EBX/ESI/EDI: {tm} ({100 * tm / tf:.2f}%)']
with open(f'{a.out}/ltcg_unidades.tsv', 'w') as o:
    o.write('ini983\tfim983\tonde\tunidade\tfuncs\tmarcadas\tpct\tbytes\tbytes_marcados\n')
    for k, u in sorted(porU.items(), key=lambda x: x[1][4]):
        o.write('\t'.join([f'{u[4]:08x}', f'{u[5]:08x}', k[0], k[1], str(u[0]), str(u[1]),
                           f'{100 * u[1] / u[0]:.1f}', str(u[2]), str(u[3])]) + '\n')
# histograma por janela de 64 kB
jan = collections.defaultdict(lambda: [0, 0])
for l in open(f'{a.out}/ltcg_funcs.tsv').read().splitlines()[1:]:
    jan[int(l.split('\t')[0], 16) >> 16][1] += 1
for r in linhas:
    va = int(r['f983'], 16)
    if va < 0xc3d000 and int(r['tam']) >= 8:
        jan[va >> 16][0] += 1
R.append('janela de 64 kB: funcoes, marcadas, %')
for j in sorted(jan):
    n, m = jan[j]
    R.append(f'  {j << 16:08x} {n:5d} {m:4d} {100 * m / max(n, 1):5.1f}% ' + '#' * int(40 * m / max(n, 1)))
open(f'{a.out}/ltcg_resumo.txt', 'w').write('\n'.join(R) + '\n')
print('\n'.join(R))
