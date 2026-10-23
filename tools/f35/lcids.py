#!/usr/bin/env python3
# F3.5 (s53): ids de IsLocalContent — para cada .obj do exe roda o cmpfunc --diff em todas as funções e, em cada chamada
# nossa a IsLocalContent, pega o id carregado em ecx logo antes (mov ecx, N | lea ecx, [reg + N] | xor/inc) e o id da
# instrução pareada do 983. Saída: <out>/lcids.tsv (nosso, 983, vezes, unidades) e lcids_locais.tsv (um por chamada).
# uso: lcids.py <out> [-j N] [filtro de caminho ...]   (objs em $PG_OBJ ou build/pg/obj; só leitura)
import sys, os, re, subprocess, collections, glob, concurrent.futures as cf
R = '/root/jp983src'; OBJ = os.environ.get('PG_OBJ') or R + '/build/pg/obj'
PAT = re.compile(r'^(?:mov ecx, (0x[0-9a-f]+|\d+)|lea ecx, \[e\w\w \+ (0x[0-9a-f]+|\d+)\]|push (0x[0-9a-f]+|\d+))$')
def idof(s):
    m = PAT.match(s.strip())
    if not m: return None
    return int(next(g for g in m.groups() if g), 0)
def um(obj):
    cmd = [R + '/tools/cmpfunc', obj, '--no-build', '--ref', R + '/ref/ProjectG_983_dump.exe', '--map', R + '/map/projectg.tsv',
           '--seed', R + '/map/projectg_seed.tsv', '--funcs', R + '/map/projectg_funcs.tsv', '--diff', '@']
    try: t = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, cwd=R).stdout
    except Exception: return obj, []
    res = []; fn = ''; win = []
    for l in t.splitlines():
        if l.startswith('--- '): fn = l[4:].split('  (')[0]; win = []; continue
        if len(l) < 4 or l[0] != ' ' or l[1] not in ' |~<>': continue
        if l.startswith('   ...'): win = []; continue
        body = l[3:]; a = body[:47].rstrip(); b = body[47:].strip()
        if l[1] == '>': continue
        if 'IsLocalContent@@' in a and a.startswith('call'):
            for tag, x, y in reversed(win[-6:]):
                ia = idof(x)
                if ia is not None and 'ecx' in x:
                    ib = idof(y) if tag != '<' else None
                    res.append((ia, ib if ib is not None else -1, fn)); break
            win = []; continue
        win.append((l[1], a, b))
    return obj, res
def main():
    a = sys.argv[1:]; out = a[0]; j = 8; f = a[1:]
    if '-j' in f: i = f.index('-j'); j = int(f[i + 1]); del f[i:i + 2]
    objs = sorted(o for o in glob.glob(OBJ + '/src/**/*.obj', recursive=True) if not f or any(x in o for x in f))
    os.makedirs(out, exist_ok=True); tot = collections.Counter(); un = collections.defaultdict(set)
    with open(out + '/lcids_locais.tsv', 'w') as fl, cf.ThreadPoolExecutor(j) as ex:
        fl.write('nosso\t983\tunidade\tfuncao\n')
        for obj, res in ex.map(um, objs):
            u = os.path.relpath(obj, OBJ)
            for ia, ib, fn in res:
                fl.write('0x%x\t%s\t%s\t%s\n' % (ia, '0x%x' % ib if ib >= 0 else '-', u, fn)); tot[ia, ib] += 1; un[ia, ib].add(u)
    with open(out + '/lcids.tsv', 'w') as fo:
        fo.write('nosso\t983\tvezes\tunidades\n')
        for (ia, ib), n in sorted(tot.items()):
            fo.write('0x%x\t%s\t%d\t%d\n' % (ia, '0x%x' % ib if ib >= 0 else '-', n, len(un[ia, ib])))
    print('%d objs, %d chamadas' % (len(objs), sum(tot.values())))
if __name__ == '__main__': main()
