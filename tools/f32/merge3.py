#!/usr/bin/env python3
# F3.5 (s43): o import.py não atualiza arquivo que já existe aqui; o rebang segue mexendo nos cabeçalhos (acessores, classes
# novas, pch) e as unidades novas param de compilar. Este passo traz essas mudanças por mescla de 3 vias:
#   base   = arquivo do rebang no commit em que foi importado (importados.tsv de cada import; depois, map/rebang_base.txt)
#   deles  = arquivo do rebang no HEAD          nosso = arquivo daqui (com ajustes e edições do 983)
# nosso == base -> copia o deles; senão `git merge-file`; conflito -> o nosso fica como está e vai para conflitos.tsv.
# Arquivos adotados (map/adotados.txt) não são tocados: os que mudaram no rebang vão para adotados_mudaram.tsv (rever à mão).
# uso: merge3.py <out> [--dry]     (somente leitura no rebang)
import os, re, sys, glob, subprocess, tempfile
RB = '/root/rebang'; ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
out = sys.argv[1]; DRY = '--dry' in sys.argv
MAP = [('source/client/ProjectG/', 'src/projectg/'), ('source/client/Fresh/', 'src/fresh/'),
       ('source/client/Wangreal/source/', 'src/engine/'), ('source/client/Wangreal/include/', 'include/engine/'),
       ('source/shared/', 'src/shared/')]
SKIP = re.compile(r'(^|/)(lib|third_party)/|\.(obj|lib|tar\.gz|zip|patch|pdb|res|aps)$')
TEXT = ('.cpp', '.c', '.h', '.inl', '.hpp', '.rc', '.def', '.rc2')
inc = re.compile(rb'^(\s*#\s*include\s*")([^"]*\.\./[^"]*)(")', re.M)
def newpath(rel):
    for a, b in MAP:
        if rel.startswith(a): return b + rel[len(a):]
def git(*a): return subprocess.run(['git', '-C', RB] + list(a), capture_output=True)
def show(commit, rel):
    r = git('show', '%s:%s' % (commit, rel)); return r.stdout if r.returncode == 0 else None
def tree(commit): return set(git('ls-tree', '-r', '--name-only', commit, 'source').stdout.decode().split('\n'))
TREES = {}
def conv(commit, rel, data):
    # a mesma reescrita de `#include "../..."` do import.py, com a árvore do commit
    if not rel.endswith(TEXT): return data
    t = TREES.setdefault(commit, tree(commit)); np = newpath(rel)
    def fix(m):
        tgt = os.path.normpath(os.path.join(os.path.dirname(rel), m.group(2).decode())).replace(os.sep, '/')
        nt = newpath(tgt)
        if nt is None: return m.group(0)
        if tgt not in t and not os.path.exists(os.path.join(ROOT, nt)): return m.group(0)
        return m.group(1) + os.path.relpath(nt, os.path.dirname(np)).replace(os.sep, '/').encode() + m.group(3)
    return inc.sub(fix, data)
head = git('rev-parse', 'HEAD').stdout.decode().strip()
# base de cada arquivo: o último import que o copiou; map/rebang_base.txt (mescla anterior) vale para todos se existir
BASE = {}
imps = []
for f in glob.glob(os.path.join(ROOT, 'out/**/rebang_commit.txt'), recursive=True):
    tsv = os.path.join(os.path.dirname(f), 'importados.tsv')
    if os.path.exists(tsv): imps.append((os.path.getmtime(tsv), open(f).read().strip(), tsv))
for _, c, tsv in sorted(imps):
    for l in open(tsv).read().split('\n')[1:]:
        if l: BASE[l.split('\t')[1]] = c
bf = os.path.join(ROOT, 'map/rebang_base.txt')
ALL = open(bf).read().split()[0] if os.path.exists(bf) else None
ad = os.path.join(ROOT, 'map/adotados.txt')
ADOT = set(l.split('\t')[0].strip() for l in open(ad) if l.strip() and not l.startswith('#')) if os.path.exists(ad) else set()
rep = []; conf = []; adm = []
os.makedirs(out, exist_ok=True)
for rel in sorted(tree(head)):
    if not rel or SKIP.search(rel): continue
    np = newpath(rel)
    if not np: continue
    dst = os.path.join(ROOT, np)
    if not os.path.exists(dst): continue
    bc = ALL or BASE.get(np)
    if not bc or bc == head: continue
    if git('diff', '--quiet', bc, head, '--', rel).returncode == 0: continue
    b = show(bc, rel); t = show(head, rel)
    if b is None or t is None: rep.append((np, 'sem base em %s' % bc[:10])); continue
    b = conv(bc, rel, b); t = conv(head, rel, t); o = open(dst, 'rb').read()
    if np in ADOT: adm.append((np, bc[:10])); continue
    if o == t: continue
    if o == b:
        if not DRY: open(dst, 'wb').write(t)
        rep.append((np, 'copiado (aqui era igual à base)')); continue
    with tempfile.TemporaryDirectory() as td:
        P = [os.path.join(td, n) for n in ('nosso', 'base', 'deles')]
        for p, d in zip(P, (o, b, t)): open(p, 'wb').write(d)
        r = subprocess.run(['git', 'merge-file', '-p', P[0], P[1], P[2]], capture_output=True)
    if r.returncode == 0:
        if r.stdout != o:
            if not DRY: open(dst, 'wb').write(r.stdout)
            rep.append((np, 'mesclado'))
    else:
        conf.append((np, bc[:10], r.returncode))
        open(os.path.join(out, 'conflito_' + np.replace('/', '_')), 'wb').write(r.stdout)
open(os.path.join(out, 'mescla.tsv'), 'w').write('arquivo\tresultado\n' + ''.join('%s\t%s\n' % x for x in rep))
open(os.path.join(out, 'conflitos.tsv'), 'w').write('arquivo\tbase\tblocos\n' + ''.join('%s\t%s\t%s\n' % x for x in conf))
open(os.path.join(out, 'adotados_mudaram.tsv'), 'w').write('arquivo\tbase\n' + ''.join('%s\t%s\n' % x for x in adm))
if not DRY and not conf: open(bf, 'w').write(head + '\n')
print('mescla: rebang %s; %d arquivos atualizados (%d copiados), %d conflitos, %d adotados mudaram no rebang%s' % (
    head[:10], len(rep), sum(1 for x in rep if x[1].startswith('copiado')), len(conf), len(adm), ' [--dry]' if DRY else ''))
