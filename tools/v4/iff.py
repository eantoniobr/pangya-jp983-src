#!/usr/bin/env python3
"""Frente C, V4 — tabelas .iff: quem carrega cada arquivo no exe 983 (CItemManager::Load) e o tamanho do registro.

  iff.py            -> out/V4/iff_983.tsv (arquivo .iff, função do 983 que carrega, tamanhos candidatos)
Método: no Load do 983, cada `push "X.iff"` + stricmp é seguido da chamada ao carregador; no carregador, o tamanho do
registro é o imediato que aparece como cópia (`mov ecx,N/4; rep movsd` ou memcpy com `push N`) E como passo do ponteiro
(`add reg,N`). Só leitura."""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import R, PE, Funcs, cs

LOAD983 = 0x00a3de50


def tamanhos(code, va):
    """candidatos a tamanho de registro numa função: (cópias, passos)."""
    md = cs()
    cop, pas = collections.Counter(), collections.Counter()
    ecx = None
    pushes = []
    for a, size, mn, ops in md.disasm_lite(code, va):
        if mn == 'mov' and ops.startswith('ecx, 0x'):
            ecx = int(ops[5:], 16)
        elif mn.startswith('rep movsd') or (mn == 'rep' and 'movsd' in ops):
            if ecx:
                cop[ecx * 4] += 1
                ecx_last = ecx
            ecx = None
        elif mn == 'push':
            try:
                pushes.append(int(ops, 16))
            except ValueError:
                pushes.append(None)
        elif mn == 'call':
            if len(pushes) >= 3 and pushes[-3] and pushes[-3] > 8:      # memcpy(dst, src, n)
                cop[pushes[-3]] += 1
            pushes = []
        elif mn == 'add':
            m = re.match(r'(e[a-ds][xip]|e[sd]i), (0x[0-9a-f]+|\d+)$', ops)
            if m and m.group(1) not in ('esp',):
                v = int(m.group(2), 0)
                if 8 < v < 0x10000:
                    pas[v] += 1
        elif mn == 'lea':
            m = re.match(r'(e\w\w), \[(e\w\w) \+ (0x[0-9a-f]+)\]$', ops)
            if m and m.group(1) == m.group(2) and m.group(1) != 'esp':
                v = int(m.group(3), 16)
                if 8 < v < 0x10000:
                    pas[v] += 1
    return cop, pas


def escolhe(ambos, cop, pas):
    """tamanho do registro: imediato que é cópia e passo (alta); senão a única cópia (media); senão o único passo (media)."""
    a = [int(x, 16) for x in ambos.split(',') if x]
    c = [int(x, 16) for x in cop.split(',') if x]
    p = [int(x, 16) for x in pas.split(',') if x]
    for pp in p:                    # cópia com resto (movsw/movsb): passo = cópia + 1..3
        for cc in c:
            if 0 < pp - cc < 4:
                return pp, 'alta'
    if len(a) == 1:
        return a[0], 'alta'
    if len(a) > 1:
        return max(a), 'baixa'
    if len(c) == 1 and len(p) <= 1:
        return c[0], 'media'
    if not c and len(p) == 1:
        return p[0], 'media'
    return None, ''


def arquivos839(pasta='/root/kr839/local/assets/iff'):
    out = {}
    for fn in os.listdir(pasta):
        d = open(os.path.join(pasta, fn), 'rb').read()
        n = struct.unpack_from('<H', d, 0)[0]
        if n and (len(d) - 8) % n == 0:
            out[fn.lower()] = (len(d) - 8) // n
    return out


def carrega_nosso():
    """arquivo .iff (minúsculas) -> (função nossa que carrega, tamanho do registro medido no nosso .obj)."""
    import glob
    from pk import cmpfunc_mod
    cm = cmpfunc_mod()
    c = sorted(glob.glob(os.path.join(R, 'out', '**', 'cmp', 'src_shared_itemmanager', 'funcs.tsv'), recursive=True),
               key=os.path.getmtime)
    objp = None
    for l in open(c[-1]):
        x = l.split('\t')
        if x[0] != 'arquivo':
            objp = os.path.join(R, x[0])
            break
    ob = cm.Obj(objp)
    fs = {nm: (sec, a, b) for nm, sec, a, b, pr in ob.funcs()}
    sec, a, b = fs['?Load@CItemManager@@QAE_NXZ']
    data, rel, ch = ob.secs[sec - 1]
    cur = None
    res = {}
    for ro in sorted(rel):
        if not a <= ro < b:
            continue
        typ, si = rel[ro]
        nm = ob.syms[si][0]
        if typ == 6:
            sd = ob.symdata(si)
            if sd:
                t = sd.split(b'\0')[0]
                if t.lower().endswith((b'.iff', b'.sff')) and len(t) > 4:
                    cur = t.decode('latin1').lower()
        elif typ == 0x14 and cur and cur not in res and 'IsLocalContent' not in nm and nm in fs:
            s2, a2, b2 = fs[nm]
            cop, pas = tamanhos(ob.secs[s2 - 1][0][a2:b2], 0)
            h = lambda z: ','.join('0x%x' % v for v in sorted(z))
            r, conf = escolhe(h(set(cop) & set(pas)), h(cop), h(pas))
            res[cur] = (nm, r, h(cop) + ' / ' + h(pas))
    return res


def main():
    pe = PE()
    F = Funcs()
    md = cs()
    i = F.vas.index(LOAD983)
    fim = F.vas[i + 1]
    # o Load pode continuar em pedaços (funclets à parte): anda até o ret
    code = pe.bytes(LOAD983, 0x4000)
    cur = None
    ordem = []
    calls = collections.defaultdict(list)
    for a, size, mn, ops in md.disasm_lite(code, LOAD983):
        if mn == 'push' and ops.startswith('0x'):
            s = pe.cstr(int(ops, 16), 64)
            if s.lower().endswith((b'.iff', b'.sff')) and len(s) > 4:
                cur = s.decode('latin1')
                ordem.append(cur)
        elif mn == 'call' and ops.startswith('0x') and cur:
            calls[cur].append(int(ops, 16))
        elif mn == 'ret' and a > fim - 0x40:
            break
    rows = []
    for nm in ordem:
        cs_ = calls[nm]          # o stricmp é chamada indireta (call edi)
        # carregador = 1ª chamada que não é biblioteca comum a todos
        rows.append((nm, cs_))
    comuns = collections.Counter(c for nm, cs_ in rows for c in set(cs_))
    out = []
    for nm, cs_ in rows:
        prop = [c for c in cs_ if comuns[c] < 3 and c != 0xa7a8d0]      # 00a7a8d0 = IsLocalContent
        ld = prop[0] if prop else None
        if ld is None:
            out.append((nm, '', '', '', '', ''))
            continue
        k = F.vas.index(ld) if ld in F.vas else None
        f2 = F.vas[k + 1] if k is not None else ld + 0x400
        cop, pas = tamanhos(pe.bytes(ld, f2 - ld), ld)
        ambos = sorted(set(cop) & set(pas))
        out.append((nm, '%08x' % ld, F.nome(ld), ','.join('0x%x' % v for v in ambos),
                    ','.join('0x%x' % v for v in sorted(cop)), ','.join('0x%x' % v for v in sorted(pas))))
    nosso = carrega_nosso()
    f839 = arquivos839()
    os.makedirs(os.path.join(R, 'out', 'V4'), exist_ok=True)
    cont = collections.Counter()
    with open(os.path.join(R, 'out', 'V4', 'iff_983.tsv'), 'w') as f:
        f.write('iff\tcarregador983\tnome983\treg983\tconf\treg839_arquivo\tdif_839\tnosso_carregador\treg_nosso\testado\tcopias983\tpassos983\tnosso_copias_passos\n')
        for nm, ld, nome, ambos, cop, pas in out:
            r983, conf = escolhe(ambos, cop, pas)
            r839 = f839.get(nm.lower())
            nf, nreg, ncand = nosso.get(nm.lower(), ('', None, ''))
            if not nf:
                est = 'sem_fonte'
            elif r983 is None or nreg is None:
                est = 'nao_medido'
            else:
                est = 'ok' if r983 == nreg else 'DIFERE'
            cont[est] += 1
            hx = lambda v: '' if v is None else '0x%x' % v
            d = '' if r983 is None or r839 is None else '%+d' % (r983 - r839)
            f.write('\t'.join((nm, ld, nome, hx(r983), conf, hx(r839), d, nf, hx(nreg), est, cop, pas, ncand)) + '\n')
    print('tabelas no Load do 983: %d; %s' % (len(out), ', '.join('%s %d' % kv for kv in sorted(cont.items()))))


if __name__ == '__main__':
    main()
