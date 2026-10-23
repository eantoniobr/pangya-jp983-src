"""f13_lib — apoio da F1.3: PE do 983, funções do mapa e referências código → dados (pelos fixups da .reloc)."""
import os, sys, struct, bisect, json, importlib.machinery, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ld = importlib.machinery.SourceFileLoader('cmpfunc', os.path.join(ROOT, 'tools', 'cmpfunc'))
_sp = importlib.util.spec_from_loader('cmpfunc', _ld); cf = importlib.util.module_from_spec(_sp); _ld.exec_module(cf)
pe = cf.PE(os.path.join(ROOT, 'ref', 'wangreal_983.dll'))


def sections():
    d = pe.d
    o = struct.unpack_from('<I', d, 0x3c)[0]
    n = struct.unpack_from('<H', d, o + 6)[0]
    p = o + 24 + struct.unpack_from('<H', d, o + 20)[0]
    out = []
    for i in range(n):
        nm = d[p:p + 8].rstrip(b'\0').decode()
        vs, va, rs, ro = struct.unpack_from('<IIII', d, p + 8)
        out.append((nm, pe.base + va, vs, rs))
        p += 40
    return out


SECS = sections()


def secof(va):
    for nm, a, vs, rs in SECS:
        if a <= va < a + max(vs, rs):
            return nm
    return None


def funcs():
    """lista de dict do map/wangreal_funcs.tsv (va, sz inteiros), em ordem de endereço"""
    out = []
    hdr = None
    for l in open(os.path.join(ROOT, 'map', 'wangreal_funcs.tsv')):
        if l.startswith('#'):
            continue
        a = l.rstrip('\n').split('\t')
        if hdr is None:
            hdr = a
            continue
        r = dict(zip(hdr, a))
        r['va'] = int(r['va'], 16); r['sz'] = int(r['sz'])
        out.append(r)
    out.sort(key=lambda r: r['va'])
    return out


FUNCS = funcs()
_FA = [r['va'] for r in FUNCS]


def func_at(va):
    """função cujo início é o maior <= va (None antes da primeira)"""
    i = bisect.bisect_right(_FA, va) - 1
    return FUNCS[i] if i >= 0 else None


def refs():
    """[(va do fixup, alvo)] de todos os fixups, ordenado"""
    return sorted((f, pe.u32(f)) for f in pe.fix)
