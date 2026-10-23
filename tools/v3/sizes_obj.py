#!/usr/bin/env python3
"""V3: sizeof de cada classe como os NOSSOS .obj a veem — `push N; call ??2@YAPAXI@Z` e o construtor (`??0…`) ou a
vtable (`??_7…@@6B@`) que vem logo depois, pelas relocações. Também acha a unidade "casa" de cada classe (a que define o
construtor) para o `make layoutcheck` saber em qual unidade a classe é completa.

  sizes_obj.py OUT_DIR [--objs build/pg-s58b/obj] [--jp build/B/obj]
Saída: OUT_DIR/news_obj.tsv (um new por linha) e OUT_DIR/sizes_obj.tsv (classe, sizeof nosso, unidade casa, unidades que dão new)."""
import sys, os, struct, glob, re, collections, importlib.machinery, importlib.util
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ld = importlib.machinery.SourceFileLoader('cmpfunc', R + '/tools/cmpfunc')
sp = importlib.util.spec_from_loader('cmpfunc', ld); cm = importlib.util.module_from_spec(sp); ld.exec_module(cm)
out = sys.argv[1]; objs = sys.argv[sys.argv.index('--objs') + 1] if '--objs' in sys.argv else R + '/build/pg-s58b/obj'
def cls_of(s):
    m = re.match(r'\?\?0([\w@]+?)@@', s) or re.match(r'\?\?_7([\w@]+?)@@6B@$', s)
    return m.group(1) if m else None
rows = []; home = collections.defaultdict(set)
jp = sys.argv[sys.argv.index('--jp') + 1] if '--jp' in sys.argv else R + '/build/B/obj'   # unidades novas do JP (frente B)
for p in sorted(glob.glob(objs + '/**/*.obj', recursive=True)) + sorted(glob.glob(jp + '/*.obj')):
    try: ob = cm.Obj(p)
    except (SystemExit, struct.error): continue      # .obj vazio = compilação em curso ou falha
    u = 'src/projectg/jp/' + os.path.basename(p)[:-4] + '.cpp' if p.startswith(jp + '/') else os.path.relpath(p, objs)[:-4] + '.cpp'
    for nm, sec, a, b, own in ob.funcs():
        if own and nm.startswith('??0'):
            c = cls_of(nm)
            if c: home[c].add(u)
        data, rel, ch = ob.secs[sec - 1]; rl = sorted((o, ob.syms[si][0]) for o, (typ, si) in rel.items() if a <= o < b)
        for k, (o, s) in enumerate(rl):
            if s != '??2@YAPAXI@Z' or o < a + 3 or data[o - 1] != 0xe8: continue
            if o >= a + 6 and data[o - 6] == 0x68: n = struct.unpack_from('<I', data, o - 5)[0]
            elif data[o - 3] == 0x6a and data[o - 2] < 0x80: n = data[o - 2]      # push curto (V7)
            else: continue
            c = None; how = ''
            for o2, s2 in rl[k + 1:k + 4]:          # só o que vem logo depois (até 0x60 bytes)
                if o2 - o > 0x60: break
                if s2 == '??2@YAPAXI@Z': break
                c = cls_of(s2)
                if c: how = 'ctor' if s2.startswith('??0') else 'vtable'; break
                if not s2.startswith(('__', '??_')): break   # outra chamada qualquer: não é o construtor
            rows.append((u, nm, n, c or '-', how or '-'))
os.makedirs(out, exist_ok=True)
with open(out + '/news_obj.tsv', 'w') as f:
    f.write('unidade\tfuncao\tN\tclasse\tvia\n')
    for r in rows: f.write('%s\t%s\t0x%x\t%s\t%s\n' % r)
by = collections.defaultdict(collections.Counter); un = collections.defaultdict(collections.Counter)
for u, nm, n, c, how in rows:
    if c != '-': by[c][n] += 1; un[c][u] += 1
with open(out + '/sizes_obj.tsv', 'w') as f:
    f.write('classe_decorada\tsizeof_nosso\tnews\tconflito\tunidade_casa\tunidades_new\n')
    for c in sorted(by):
        (n, k) = by[c].most_common(1)[0]
        f.write('%s\t0x%x\t%d\t%s\t%s\t%s\n' % (c, n, sum(by[c].values()), '' if len(by[c]) == 1 else ' '.join('0x%x×%d' % x for x in by[c].most_common()),
                ','.join(sorted(home.get(c, []))) or '-', ','.join(x for x, _ in un[c].most_common())))
print('nosso: %d `new` com tamanho imediato, %d com classe; %d classes (%d com conflito)' % (
    len(rows), sum(1 for r in rows if r[3] != '-'), len(by), sum(1 for c in by if len(by[c]) > 1)))
