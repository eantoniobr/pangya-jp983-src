#!/usr/bin/env python3
"""hybrid.py SAIDA.dll NOME [NOME...] — dll de TESTE (F2.12): a nossa wangreal.dll ligada (build/wangreal-full) com as
funções pedidas trocadas pelo código EXATO da wangreal 983 (ref/wangreal_983.dll), relocado para a nossa imagem.

Como: cada função do 983 (do início até o início da próxima no map/wangreal_funcs.tsv, inclui tabelas de salto) é
copiada para uma seção nova `.w983`; a entrada da nossa função vira `jmp` para a cópia. Na cópia:
  - endereço absoluto (fixup da .reloc do 983) dentro da própria função -> posição na cópia; início de outra função ->
    a nossa função par (out/F2.11/image/funcoes.tsv); item de dados -> o item par (out/F2.11/image/dados.tsv, com
    deslocamento); slot de import -> o nosso slot do mesmo nome; constante de .rdata sem par -> mesma sequência de
    bytes única na nossa .rdata;
  - call/jmp/jcc rel32 para fora -> a nossa função par (se ela também for trocada, passa pelo jmp da entrada).
Funções com tratamento de exceção (fs:[0]) não são trocadas (o funcinfo do 983 descreveria a cópia errada).
Relocações: seção nova `.wrel` = .reloc antiga (com as entradas dos 5 bytes do jmp anuladas) + blocos da cópia.
NOME = nome decorado (map/wangreal.tsv) ou VA 983 em hex. Só para teste: o conserto vai para o fonte."""
import sys, os, struct, bisect, capstone
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OURS = os.environ.get('OURS', os.path.join(R, 'build/wangreal-full/wangreal.dll'))
REF = os.path.join(R, 'ref/wangreal_983.dll')
IMG = os.environ.get('IMG', os.path.join(R, 'out/F2.11/image'))

class PE:
    def __init__(self, path):
        self.d = bytearray(open(path, 'rb').read())
        d = self.d
        self.pe = struct.unpack_from('<I', d, 0x3c)[0]
        self.ns = struct.unpack_from('<H', d, self.pe + 6)[0]
        self.oh = self.pe + 24
        self.base = struct.unpack_from('<I', d, self.oh + 28)[0]
        self.st = self.oh + struct.unpack_from('<H', d, self.pe + 20)[0]
        self.secs = []
        for i in range(self.ns):
            o = self.st + 40 * i
            nm = bytes(d[o:o + 8]).rstrip(b'\0').decode()
            vs, va, rs, ro = struct.unpack_from('<IIII', d, o + 8)
            self.secs.append((nm, vs, va, rs, ro))
        self.dd = self.oh + 96
    def ddir(self, i): return struct.unpack_from('<II', self.d, self.dd + 8 * i)
    def off(self, va):
        rva = va - self.base
        for nm, vs, v, rs, ro in self.secs:
            if v <= rva < v + max(vs, rs): return ro + rva - v
        raise KeyError('%x' % va)
    def sec_of(self, va):
        rva = va - self.base
        for nm, vs, v, rs, ro in self.secs:
            if v <= rva < v + max(vs, rs): return nm
    def u32(self, va): return struct.unpack_from('<I', self.d, self.off(va))[0]
    def read(self, va, n): o = self.off(va); return bytes(self.d[o:o + n])
    def cstr(self, va):
        o = self.off(va); e = self.d.index(b'\0', o); return bytes(self.d[o:e]).decode('latin1')
    def imports(self):
        rva, sz = self.ddir(1); res = {}
        p = self.base + rva
        while True:
            oft, ts, fc, name, ft = struct.unpack_from('<IIIII', self.d, self.off(p))
            if not name: break
            dll = self.cstr(self.base + name).lower()
            i = 0
            while True:
                t = self.u32(self.base + (oft or ft) + 4 * i)
                if not t: break
                key = (dll, ('#%d' % (t & 0xffff)) if t & 0x80000000 else self.cstr(self.base + t + 2))
                res[self.base + ft + 4 * i] = key
                i += 1
            p += 20
        return res
    def relocs(self):
        rva, sz = self.ddir(5); out = []
        p = self.off(self.base + rva); end = p + sz
        while p < end:
            page, bs = struct.unpack_from('<II', self.d, p)
            if bs < 8: break
            for k in range((bs - 8) // 2):
                e = struct.unpack_from('<H', self.d, p + 8 + 2 * k)[0]
                out.append((self.base + page + (e & 0xfff), e >> 12, p + 8 + 2 * k))
            p += bs
        return out

def load_tables():
    f983 = []
    for l in open(os.path.join(R, 'map/wangreal_funcs.tsv')):
        p = l.rstrip('\n').split('\t')
        if l.startswith(('#', 'va\t')) or len(p) < 2: continue
        f983.append(int(p[0], 16))
    f983.sort()
    names = {}
    for l in open(os.path.join(R, 'map/wangreal.tsv')):
        p = l.rstrip('\n').split('\t')
        if len(p) > 1 and not l.startswith('#'):
            try: names.setdefault(p[0], int(p[1], 16))
            except ValueError: pass
    fpair, fsz_our = {}, {}
    for l in open(os.path.join(IMG, 'funcoes.tsv')):
        p = l.rstrip('\n').split('\t')
        if p[0] in ('classe', 'SO_983', 'SO_NOSSO'): continue
        fpair[int(p[2], 16)] = int(p[4], 16); fsz_our[int(p[4], 16)] = int(p[5])
    dpair = []
    for l in open(os.path.join(IMG, 'dados.tsv')):
        p = l.rstrip('\n').split('\t')
        if p[0] == 'va983': continue
        dpair.append((int(p[0], 16), int(p[4]), int(p[1], 16), p[6]))
    dpair.sort()
    return f983, names, fpair, fsz_our, dpair

def main():
    out = sys.argv[1]; want = sys.argv[2:]
    ref, our = PE(REF), PE(OURS)
    f983, names, fpair, fsz_our, dpair = load_tables()
    rimp, oimp = ref.imports(), our.imports()
    oimp_by = {v: k for k, v in oimp.items()}
    rrel = set(va for va, t, _ in ref.relocs() if t == 3)
    ourmap = {}
    for l in open(os.path.join(os.path.dirname(OURS), 'wangreal.map')):
        p = l.split()
        if len(p) >= 3 and ':' in p[0] and p[0].startswith('000'):
            try: ourmap.setdefault(p[1], int(p[2], 16))
            except ValueError: pass
    dk = [x[0] for x in dpair]
    extra = dict((int(x.split(':')[0], 16), int(x.split(':')[1], 16)) for x in os.environ.get('EXTRA', '').split(',') if x)
    # .rdata nossa para busca por conteúdo
    rd = [s for s in our.secs if s[0] == '.rdata'][0]
    rdata = bytes(our.d[rd[4]:rd[4] + rd[3]]); rdbase = our.base + rd[2]
    text = [s for s in our.secs if s[0] == '.text'][0]
    # seção nova
    last = our.secs[-1]
    salign = struct.unpack_from('<I', our.d, our.oh + 32)[0]; falign = struct.unpack_from('<I', our.d, our.oh + 36)[0]
    al = lambda x, a: (x + a - 1) // a * a
    new_rva = al(last[2] + last[1], salign); new_va = our.base + new_rva
    blob = bytearray(); fix = []      # fixups absolutos na blob (deslocamentos)
    patches = []; log = []
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); md.detail = True
    for w in want:
        a = int(w, 16) if all(c in '0123456789abcdefABCDEF' for c in w) and len(w) == 8 else names.get(w)
        if a is None: sys.exit('sem VA para %s' % w)
        i = bisect.bisect_left(f983, a)
        if i >= len(f983) or f983[i] != a: sys.exit('%x não é início de função no funcs.tsv' % a)
        end = f983[i + 1]
        if a not in fpair: log.append('SEM PAR %x %s' % (a, w)); continue
        ours_va = fpair[a]
        code = bytearray(ref.read(a, end - a))
        # tira o enchimento int3/nop do fim? não: mantém (alinhamento interno inofensivo)
        if b'\x64\xa1\x00\x00\x00\x00' in code or b'\x64\x89\x25\x00\x00\x00\x00' in code:
            log.append('PULADA (EH fs:[0]) %x %s' % (a, w)); continue
        while len(blob) % 16: blob.append(0xcc)
        nb = new_va + len(blob); start = len(blob); nfix0 = len(fix)
        def mapabs(v):
            if a <= v < end: return nb + (v - a), 'interno'
            if v in rimp:
                k = rimp[v]
                if k not in oimp_by: raise ValueError('import %s sem par' % (k,))
                return oimp_by[k], 'import %s' % k[1]
            j = bisect.bisect_right(f983, v) - 1
            if j >= 0 and f983[j] == v and v in fpair: return fpair[v], 'função'
            k = bisect.bisect_right(dk, v) - 1
            if k >= 0 and dpair[k][0] <= v < dpair[k][0] + max(dpair[k][1], 1):
                if dpair[k][3] != 'IGUAL' and ref.sec_of(v) == '.data':
                    pass
                return dpair[k][2] + (v - dpair[k][0]), 'dado %s' % dpair[k][3]
            if v in extra: return extra[v], 'manual'
            if ref.sec_of(v) == '.rdata':
                o = ref.off(v); e = ref.d.index(b'\0', o); sv = bytes(ref.d[o:e + 1])
                if len(sv) > 2 and (o == 0 or ref.d[o - 1] == 0 or True):
                    q = rdata.find(b'\0' + sv)
                    if q >= 0: return rdbase + q + 1, 'rdata cadeia'
                for n in (16, 8, 4):
                    pat = ref.read(v, n)
                    if rdata.count(pat) == 1: return rdbase + rdata.index(pat), 'rdata conteúdo %d' % n
            raise ValueError('absoluto %x sem par (seção %s)' % (v, ref.sec_of(v)))
        try:
            # absolutos
            for k in range(len(code) - 3):
                if a + k in rrel:
                    v = struct.unpack_from('<I', code, k)[0]
                    nv, why = mapabs(v)
                    struct.pack_into('<I', code, k, nv); fix.append(start + k)
            # relativos
            for x in md.disasm(bytes(ref.read(a, end - a)), a):
                if x.group(capstone.CS_GRP_JUMP) or x.group(capstone.CS_GRP_CALL):
                    op = x.operands[0] if x.operands else None
                    if op is None or op.type != capstone.x86.X86_OP_IMM: continue
                    t = op.imm
                    if a <= t < end: continue
                    if x.size < 5: raise ValueError('salto curto para fora em %x' % x.address)
                    if t not in fpair: raise ValueError('alvo %x de %x sem par' % (t, x.address))
                    k = x.address - a; dpos = k + x.size - 4
                    newt = fpair[t]
                    struct.pack_into('<i', code, dpos, newt - (nb + k + x.size))
        except ValueError as e:
            log.append('FALHOU %x %s: %s' % (a, w, e)); del fix[nfix0:]; continue
        blob += code
        if fsz_our.get(ours_va, 99) < 5: sys.exit('nossa função %x curta demais' % ours_va)
        patches.append((ours_va, nb))
        log.append('trocada %x -> nossa %x (cópia em %x, %d B) %s' % (a, ours_va, nb, len(code), w))
    if not patches: print('\n'.join(log)); sys.exit('nada trocado')
    # aplica jmp
    oldrel = our.relocs()
    for ova, nb in patches:
        o = our.off(ova)
        our.d[o:o + 5] = b'\xe9' + struct.pack('<i', nb - (ova + 5))
        for va, t, eo in oldrel:
            if ova - 3 <= va < ova + 5 and t == 3:
                struct.pack_into('<H', our.d, eo, 0)  # anula (tipo ABSOLUTE, deslocamento 0)
    # nova .reloc
    rrva, rsz = our.ddir(5)
    relo = bytearray(our.d[our.off(our.base + rrva):our.off(our.base + rrva) + rsz])
    pages = {}
    for k in fix:
        rv = new_rva + k; pages.setdefault(rv & ~0xfff, []).append(rv & 0xfff)
    for pg in sorted(pages):
        ents = [(3 << 12) | x for x in sorted(pages[pg])]
        if len(ents) % 2: ents.append(0)
        relo += struct.pack('<II', pg, 8 + 2 * len(ents)) + b''.join(struct.pack('<H', e) for e in ents)
    # seções novas
    def add_section(name, data, chars):
        nonlocal our
        d = our.d; ns = struct.unpack_from('<H', d, our.pe + 6)[0]
        o = our.st + 40 * ns
        hdr_end = struct.unpack_from('<I', d, our.oh + 60)[0]
        if o + 40 > hdr_end: sys.exit('sem espaço para cabeçalho de seção')
        lastv = max(v + vs for _, vs, v, rs, ro in our.secs)
        va = al(lastv, salign)
        raw = al(len(d), falign); d.extend(b'\0' * (raw - len(d)))
        rs = al(len(data), falign)
        d.extend(data); d.extend(b'\0' * (rs - len(data)))
        struct.pack_into('<8sIIIIIIHHI', d, o, name.encode(), len(data), va, rs, raw, 0, 0, 0, 0, chars)
        struct.pack_into('<H', d, our.pe + 6, ns + 1)
        struct.pack_into('<I', d, our.oh + 56, al(va + len(data), salign))  # SizeOfImage
        our.secs.append((name, len(data), va, rs, raw))
        return va
    v1 = add_section('.w983', bytes(blob), 0x60000020)
    assert v1 == new_rva, (hex(v1), hex(new_rva))
    v2 = add_section('.wrel', bytes(relo), 0x42000040)
    struct.pack_into('<II', our.d, our.dd + 8 * 5, v2, len(relo))
    struct.pack_into('<I', our.d, our.oh + 64, 0)  # checksum
    open(out, 'wb').write(our.d)
    print('\n'.join(log)); print('trocadas %d; fixups novos %d; %s' % (len(patches), len(fix), out))

if __name__ == '__main__':
    main()
