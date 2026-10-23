"""Frente C, V4 — base comum: lê o exe 983 (PE), desmonta, nomes do mapa."""
import os, struct, bisect, capstone
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXE = os.path.join(R, 'ref', 'ProjectG_983_dump.exe')


class PE:
    def __init__(self, path=EXE):
        d = self.d = open(path, 'rb').read()
        pe = struct.unpack_from('<I', d, 0x3c)[0]
        ns = struct.unpack_from('<H', d, pe + 6)[0]
        oh = pe + 24
        self.base = struct.unpack_from('<I', d, oh + 28)[0]
        st = oh + struct.unpack_from('<H', d, pe + 20)[0]
        self.secs = []
        for i in range(ns):
            name = d[st + 40 * i:st + 40 * i + 8].rstrip(b'\0').decode('latin1')
            vs, v, rs, ro = struct.unpack_from('<IIII', d, st + 40 * i + 8)
            self.secs.append((name, self.base + v, max(vs, rs), ro, rs))

    def off(self, va):
        for n, v, sz, ro, rs in self.secs:
            if v <= va < v + sz:
                o = ro + va - v
                return o if va - v < rs else None
        return None

    def bytes(self, va, n):
        o = self.off(va)
        return self.d[o:o + n] if o is not None else b''

    def u32(self, va):
        b = self.bytes(va, 4)
        return struct.unpack('<I', b)[0] if len(b) == 4 else None

    def cstr(self, va, mx=200):
        b = self.bytes(va, mx)
        return b.split(b'\0')[0]


def funcs():
    """map/projectg_funcs.tsv -> lista ordenada (va, tam, unidade, nome645, nome983)."""
    out = []
    for l in open(os.path.join(R, 'map', 'projectg_funcs.tsv')):
        p = l.rstrip('\n').split('\t')
        if p[0] == 'f983' or len(p) < 11:
            continue
        out.append((int(p[0], 16), int(p[1]), p[3], p[6], p[10]))
    out.sort()
    return out


class Funcs:
    def __init__(self):
        self.l = funcs()
        self.vas = [f[0] for f in self.l]

    def at(self, va):
        i = bisect.bisect_right(self.vas, va) - 1
        if i >= 0 and self.l[i][0] <= va < self.l[i][0] + max(self.l[i][1], 1):
            return self.l[i]
        return None

    def nome(self, va):
        f = self.at(va)
        if not f:
            return ''
        return f[3] or f[4]


def cs(detail=False):
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = detail
    return md
