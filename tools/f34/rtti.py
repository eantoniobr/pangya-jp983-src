#!/usr/bin/env python3
"""rtti.py Classe... — acha no dump do 983 a(s) vtable(s) da classe pelo RTTI (.?AVClasse@@) e quem as grava
(mov [reg(+d)], imm32 = construtores/destrutores). Complementa o vt.py (que parte da vtable)."""
import sys, os, struct, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pgdis as P
def find(cls):
    out = []
    for pre in (b'.?AV', b'.?AU'):
        i = P.d.find(pre + cls.encode() + b'@@\0')
        if i < 0: continue
        td = None
        # o dump é imagem em memória ou arquivo: usa a inversa de P.off por busca do ponteiro
        for m in re.finditer(re.escape(struct.pack('<I', 0)), b''): pass
        out.append(i - 8)
    return out
def va_of(o, lo=0x400000, hi=0x2000000):
    # inversa de P.off por bisseção em passos de página
    for va in range(lo, hi, 0x1000):
        b = P.off(va)
        if b is not None and b <= o < b + 0x1000: return va + (o - b)
if __name__ == '__main__':
    for cls in sys.argv[1:]:
        for o in find(cls):
            td = va_of(o); pat = struct.pack('<I', td)
            cols = [m.start() - 12 for m in re.finditer(re.escape(pat), P.d) if P.d[m.start() - 12:m.start() - 8] == b'\0\0\0\0']
            for c in cols:
                cva = va_of(c)
                if cva is None: continue
                for m in re.finditer(re.escape(struct.pack('<I', cva)), P.d):
                    vt = va_of(m.start() + 4); sub = struct.unpack_from('<I', P.d, c + 4)[0]
                    ws = [va_of(w.start()) for w in re.finditer(re.escape(struct.pack('<I', vt)), P.d)]
                    ws = [w for w in ws if w and 0x401000 <= w < 0xc3d000]
                    print('%s typedesc %08x vtable %08x (subobjeto +0x%x) gravada em: %s' % (cls, td, vt, sub, ' '.join('%08x' % w for w in ws[:12])))
