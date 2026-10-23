#!/usr/bin/env python3
"""F3.4: votos de deslocamento de campo .obj do exe (build/pg/obj) -> ProjectG 983, por classe da função.
uso: votes.py unit SRC.cpp SAIDA.tsv     (uma unidade; mesma comparação do cmpfunc, com mapa e semente)
     votes.py all DIR [-j N] [filtro...] (todas as unidades que compilam -> DIR/<unidade>.tsv)
     votes.py sum DIR SAIDA.tsv          (soma por classe: off_obj -> off_983 mais votado, nº de funções que votam)
Como o tools/f12_votes.py: alinha as instruções pela ficha sem imediato/deslocamento e conta cada par
(deslocamento no .obj, deslocamento no 983) de operando [reg+N] com reg != esp/ebp, e cada par de imediato
diferente (linhas 'imm'). A classe é a do nome decorado da função (quem vota é o `this` na maioria das vezes)."""
import sys, os, re, collections, difflib, importlib.machinery, importlib.util, subprocess, glob
import concurrent.futures as cfu
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OBJ = os.environ.get('PG_OBJ') or os.path.join(ROOT, 'build', 'pg', 'obj')   # PG_OBJ: cópia congelada dos .obj (dá para recompilar enquanto os votos rodam)
MEM = re.compile(r'^(\w+:)?\[(\w*)\+(\w*)\*(\d+)\+([0-9a-f]+)\]$')

def cls_of(nm):
    if nm.startswith('??') and not nm.startswith('??$'):       # operador/construtor: ??0Classe@escopo@@
        m = re.match(r'^\?\?(?:_.|.)((?:[^@?]+@)+)@', nm)
    else:
        m = re.match(r'^\?\??[^@]*@((?:[^@]+@)+)@', nm)
    if not m:
        return '-'
    return '::'.join(reversed(m.group(1).rstrip('@').split('@')))

def unit(src, out):
    ld = importlib.machinery.SourceFileLoader('cmpfunc', os.path.join(ROOT, 'tools', 'cmpfunc'))
    sp = importlib.util.spec_from_loader('cmpfunc', ld); cf = importlib.util.module_from_spec(sp); ld.exec_module(cf)
    obj = os.path.join(OBJ, os.path.splitext(src)[0] + '.obj')
    pe = cf.PE(os.path.join(ROOT, 'ref', 'ProjectG_983_dump.exe'))
    c = cf.Cmp(pe, cf.load_map(os.path.join(ROOT, 'map', 'projectg.tsv')),
               cf.load_starts(os.path.join(ROOT, 'map', 'projectg_funcs.tsv')),
               cf.load_map(os.path.join(ROOT, 'map', 'projectg_seed.tsv')))
    c.run_obj(obj, src, False)
    votes = collections.Counter(); ex = {}
    for x in c.rows:
        if not x['va'] or x['pct'] < 0.5 or x['cls'] == 'IGUAL' and x['bytes_eq']:
            continue
        to, tr = c.details.get(x['nm'], (None, None))
        if not to or not tr:
            continue
        k = cls_of(x['nm'])
        sm = difflib.SequenceMatcher(None, to.r, tr.r, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != 'equal':
                continue
            for q in range(i2 - i1):
                a, b = to.s[i1 + q], tr.s[j1 + q]
                pa, pb = a.split(' ', 1), b.split(' ', 1)
                if len(pa) < 2 or len(pb) < 2:
                    continue
                oa, ob = pa[1].split(','), pb[1].split(',')
                if len(oa) != len(ob):
                    continue
                for u, v in zip(oa, ob):
                    mu, mv = MEM.match(u), MEM.match(v)
                    if mu and mv:
                        if mu.group(2) in ('esp', 'ebp', '') or mu.group(1):
                            continue
                        key = (k, 'mem', int(mu.group(5), 16), int(mv.group(5), 16), x['nm'], x['own'] and 1 or 0)
                    elif not mu and not mv and u != v and re.match(r'^[0-9a-f]+$', u) and re.match(r'^[0-9a-f]+$', v):
                        key = (k, 'imm', int(u, 16), int(v, 16), x['nm'], x['own'] and 1 or 0)
                    else:
                        continue
                    votes[key] += 1
                    ex.setdefault(key, '%08x: %s' % (x['va'], tr.txt[j1 + q]))
    with open(out, 'w') as f:
        for key in sorted(votes):
            f.write('%s\t%s\t0x%x\t0x%x\t%s\t%d\t%d\t%s\t%s\n' % (key[0], key[1], key[2], key[3], key[4], key[5], votes[key], src, ex[key]))

def run_all(d, j, filt):
    os.makedirs(d, exist_ok=True)
    us = [l.split('\t')[0] for l in subprocess.run([sys.executable, ROOT + '/tools/f32/pgbuild.py', 'list'], capture_output=True, text=True).stdout.split('\n') if l]
    us = [u for u in us if os.path.exists(os.path.join(OBJ, u[:-4] + '.obj')) and (not filt or any(f in u for f in filt))]
    def one(u):
        o = os.path.join(d, u[:-4].replace('/', '_') + '.tsv')
        p = subprocess.run([sys.executable, os.path.abspath(__file__), 'unit', u, o], capture_output=True, text=True)
        return u, p.returncode, p.stderr[-300:]
    bad = 0
    with cfu.ThreadPoolExecutor(j) as ex:
        for u, rc, err in ex.map(one, us):
            if rc: bad += 1; print('FALHOU', u, err)
    print('%d unidades, %d falharam' % (len(us), bad))

def summ(d, out):
    v = collections.defaultdict(collections.Counter); fn = collections.defaultdict(set); ex = {}
    for p in sorted(glob.glob(d + '/*.tsv')):
        for l in open(p):
            c = l.rstrip('\n').split('\t')
            key = (c[0], c[1], int(c[2], 16))
            # um voto por função (não por instrução): função grande não domina
            v[key][int(c[3], 16)] += 1; fn[key, int(c[3], 16)].add(c[4]); ex.setdefault((key, int(c[3], 16)), c[4][:40] + ' ' + c[8])
    with open(out, 'w') as f:
        f.write('classe\ttipo\toff_obj\toff_983\tdelta\tfuncoes\toutros\texemplo\n')
        for key in sorted(v):
            cn = v[key]
            (b, n), rest = cn.most_common(1)[0], cn.most_common()[1:]
            f.write('%s\t%s\t0x%x\t0x%x\t%+d\t%d\t%s\t%s\n' % (key[0], key[1], key[2], b, b - key[2] if abs(b - key[2]) < 1 << 31 else 0, n,
                    ' '.join('0x%x:%d' % kv for kv in rest), ex[(key, b)]))
    print('%d chaves em %s' % (len(v), out))

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'unit': unit(a[1], a[2])
    elif a[0] == 'sum': summ(a[1], a[2])
    elif a[0] == 'all':
        j = 8; r = a[2:]
        if '-j' in r: i = r.index('-j'); j = int(r[i + 1]); del r[i:i + 2]
        run_all(a[1], j, r)
