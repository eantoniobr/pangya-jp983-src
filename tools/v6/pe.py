"""Leitor mínimo de PE (F4, frente C): seções, VA<->arquivo, imports por nome -> VA do IAT."""
import struct


class PE:
    def __init__(s, path):
        d = s.d = open(path, 'rb').read()
        o = struct.unpack_from('<I', d, 0x3c)[0]
        nsec, opt = struct.unpack_from('<H', d, o + 6)[0], struct.unpack_from('<H', d, o + 20)[0]
        s.base = struct.unpack_from('<I', d, o + 24 + 28)[0]
        s.dirs = [struct.unpack_from('<II', d, o + 24 + 96 + 8 * i) for i in range(16)]
        s.secs = []
        for i in range(nsec):
            nm, vs, va, rs, ro = struct.unpack_from('<8sIIII', d, o + 24 + opt + 40 * i)
            s.secs.append((nm.rstrip(b'\0').decode('latin1'), va, vs, ro, rs))

    def off(s, rva):
        for _, va, vs, ro, rs in s.secs:
            if va <= rva < va + max(vs, rs): return ro + rva - va
        return None

    def u32(s, va): return struct.unpack_from('<I', s.d, s.off(va - s.base))[0]

    def cstr(s, rva):
        o = s.off(rva); return s.d[o:s.d.index(b'\0', o)].decode('latin1')

    def imports(s):
        """{(dll minúsculo, nome): VA do slot no IAT}"""
        r, rva = {}, s.dirs[1][0]
        while True:
            o = s.off(rva)
            ilt, _, _, name, iat = struct.unpack_from('<IIIII', s.d, o)
            if not name: break
            dll = s.cstr(name).lower()
            t, i = ilt or iat, 0
            while True:
                e = struct.unpack_from('<I', s.d, s.off(t + 4 * i))[0]
                if not e: break
                nm = ('#%d' % (e & 0xffff)) if e & 0x80000000 else s.cstr(e + 2)
                r[(dll, nm)] = s.base + iat + 4 * i
                i += 1
            rva += 20
        return r

    def exports(s):
        """nomes exportados (como estão na tabela de nomes da dll; mss32 exporta decorado: _AIL_startup@0)"""
        rva, _ = s.dirs[0]
        if not rva: return set()
        o = s.off(rva)
        n, nomes = struct.unpack_from('<I', s.d, o + 24)[0], struct.unpack_from('<I', s.d, o + 32)[0]
        return {s.cstr(struct.unpack_from('<I', s.d, s.off(nomes + 4 * i))[0]) for i in range(n)}


def recursos(pe):
    """[(tipo, id, língua, tamanho)] do diretório de recursos (nível 3)"""
    rva = pe.dirs[2][0]
    if not rva: return []
    base = pe.off(rva); d = pe.d; r = []

    def nome(x):
        if x & 0x80000000:
            o = base + (x & 0x7fffffff); n = struct.unpack_from('<H', d, o)[0]
            return d[o + 2:o + 2 + 2 * n].decode('utf-16le')
        return x

    def ents(o):
        nn, ni = struct.unpack_from('<HH', d, o + 12)
        return [struct.unpack_from('<II', d, o + 16 + 8 * i) for i in range(nn + ni)]
    for t, ot in ents(base):
        for i, oi in ents(base + (ot & 0x7fffffff)):
            for l, ol in ents(base + (oi & 0x7fffffff)):
                drva, sz = struct.unpack_from('<II', d, base + ol)
                r.append((nome(t), nome(i), l, sz))
    return r
