#!/usr/bin/env python3
"""vadiff.py VA983 VA_NOSSO N983 N_NOSSO [dll_nossa] — desmonta as duas faixas (983 × nossa dll ligada) e mostra o
diff das instruções (endereços absolutos e alvos de call/jmp trocados por nomes dos mapas quando houver)."""
import sys, os, struct, difflib, re, capstone
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def load(p):
    d = open(p, 'rb').read()
    pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
    oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
    secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
    def blob(va, n):
        rva = va - base
        for vs, v, rs, ro in secs:
            if v <= rva < v + max(vs, rs): return d[ro + rva - v: ro + rva - v + n]
    return blob
n983 = {}
for l in open(os.path.join(R, 'map/wangreal.tsv')):
    p = l.rstrip('\n').split('\t')
    if len(p) > 1 and not l.startswith('#'):
        try: n983.setdefault(int(p[1], 16), p[0])
        except ValueError: pass
nn = {}
DLL = sys.argv[5] if len(sys.argv) > 5 else os.path.join(R, 'build/wangreal-full/wangreal.dll')
for l in open(os.path.join(os.path.dirname(os.path.abspath(DLL)), 'wangreal.map')):
    p = l.split()
    if len(p) >= 3 and ':' in p[0] and p[0].startswith('000'):
        try: nn.setdefault(int(p[2], 16), p[1])
        except ValueError: pass
IMG = 0
for _p in (os.path.join(R, 'ref/wangreal_983.dll'), DLL):
    _d = open(_p, 'rb').read(); _pe = struct.unpack_from('<I', _d, 0x3c)[0]
    IMG = max(IMG, struct.unpack_from('<I', _d, _pe + 24 + 56)[0])
# pares 983 × nossa (funções e dados) do `make image` (VADIFF_IMG=dir; padrão out/W4/image): endereço da nossa dll
# vira o endereço do 983 correspondente (D<va983>); sem par = N<va nosso>. Pega acesso a variável/campo trocado.
PAIRS = []
_img = os.environ.get('VADIFF_IMG', os.path.join(R, 'out/W4/image'))
for _f, _c in (('funcoes.tsv', (2, 3, 4)), ('dados.tsv', (0, 4, 1))):
    _p = os.path.join(_img, _f)
    if not os.path.exists(_p): continue
    for _l in open(_p):
        _x = _l.rstrip('\n').split('\t')
        try: PAIRS.append((int(_x[_c[2]], 16), int(_x[_c[0]], 16), int(_x[_c[1]])))
        except (ValueError, IndexError): pass
PAIRS.sort()
import bisect
_keys = [p[0] for p in PAIRS]
def imports(path):
    # IAT: endereço da entrada -> 'imp:dll!nome' (ordem das entradas difere entre as dlls)
    d = open(path, 'rb').read(); r = {}
    pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
    oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
    secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
    def off(rva):
        for vs, v, rs, ro in secs:
            if v <= rva < v + max(vs, rs): return ro + rva - v
    def cstr(o): return d[o:d.index(b'\0', o)].decode('latin1')
    irva = struct.unpack_from('<I', d, oh + 96 + 8)[0]; o = off(irva)
    while o is not None:
        oft, _, _, nm, ft = struct.unpack_from('<IIIII', d, o)
        if not nm: break
        dll = cstr(off(nm)).lower(); k = 0
        while True:
            t = struct.unpack_from('<I', d, off(oft or ft) + 4 * k)[0]
            if not t: break
            r[base + ft + 4 * k] = 'imp:%s!%s' % (dll, ('#%d' % (t & 0xffff)) if t & 0x80000000 else cstr(off(t) + 2))
            k += 1
        o += 20
    return r
ours = load(DLL)
ref = load(os.path.join(R, 'ref/wangreal_983.dll'))
IMP983 = imports(os.path.join(R, 'ref/wangreal_983.dll')); IMPN = imports(DLL)
def textend(path):
    d = open(path, 'rb').read(); pe = struct.unpack_from('<I', d, 0x3c)[0]; oh = pe + 24
    st = oh + struct.unpack_from('<H', d, pe + 20)[0]; vs, v = struct.unpack_from('<II', d, st + 8)
    return struct.unpack_from('<I', d, oh + 28)[0] + v + vs
TEXTEND = {}
def cstrat(blob, v):
    if not TEXTEND: TEXTEND[ours] = textend(DLL); TEXTEND[ref] = textend(os.path.join(R, 'ref/wangreal_983.dll'))
    if v < TEXTEND[blob]: return None  # endereço no código não é string
    b = blob(v, 80) or b''
    z = b.find(b'\0')
    if z >= 2 and all(c >= 32 and c != 127 for c in b[:z]): return "str:" + b[:z].hex()
P983 = sorted((p[1], p[2]) for p in PAIRS); _k983 = [p[0] for p in P983]
def tr_983(v):
    i = bisect.bisect_right(_k983, v) - 1
    if i >= 0 and P983[i][0] <= v < P983[i][0] + max(P983[i][1], 1): return 'D%x' % v  # item pareado: antes da string
    return IMP983.get(v) or cstrat(ref, v) or 'D%x' % v
def tr_ours(v):
    if v in IMPN: return IMPN[v]
    i = bisect.bisect_right(_keys, v) - 1
    if i >= 0 and PAIRS[i][0] <= v < PAIRS[i][0] + max(PAIRS[i][2], 1): return 'D%x' % (PAIRS[i][1] + v - PAIRS[i][0])
    t = cstrat(ours, v)
    if t: return t
    if i >= 0 and v - PAIRS[i][0] < 0x40: return 'D%x' % (PAIRS[i][1] + v - PAIRS[i][0])  # depois do último item citado (campo de estrutura)
    return 'N%x' % v
def dis(blob, va, n, names, addrs=None):
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    out = []
    for x in md.disasm(blob(va, n), va):
        if addrs is not None: addrs.append(x.address)
        s = '%s %s' % (x.mnemonic, x.op_str)
        def sub(m):
            v = int(m.group(0), 16)
            if va <= v < va + n: return 'L%x' % (v - va)
            if not (0x10000000 < v < 0x10000000 + IMG): return m.group(0)
            if PAIRS: return tr_983(v) if names is n983 else tr_ours(v)
            if v in names: return names[v][:60]
            return 'A'
        out.append(re.sub(r'0x[0-9a-f]{6,}', sub, s))
    return out
if __name__ == '__main__':
    a, b, na, nb = int(sys.argv[1], 16), int(sys.argv[2], 16), int(sys.argv[3]), int(sys.argv[4])
    A = dis(ref, a, na, n983); B = dis(ours, b, nb, nn)
    for l in difflib.unified_diff(A, B, '983', 'nossa', n=2, lineterm=''): print(l)
