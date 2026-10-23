#!/usr/bin/env python3
# F3.2: copia do rebang (somente leitura) as unidades .cpp do exe e os cabeçalhos para src/ e include/.
#   source/client/ProjectG/**            -> src/projectg/**            (.cpp/.h/.inl/.rc e afins; sem lib/ e sem .obj)
#   source/client/Fresh/**               -> src/fresh/**               (sem lib/ e third_party/)
#   source/client/Wangreal/source/*      -> src/engine/*
#   source/client/Wangreal/include/*     -> include/engine/*
#   source/shared/**                     -> src/shared/**              (Lua 5.1 e minilzo 2.02 extraídos dos .tar.gz; minilzo com o patch do rebang)
# Não sobrescreve arquivo que já existe aqui (os da dll já estão no layout do 983): lista em mantidos.txt.
# Única mudança de texto: `#include "../..."` relativo é reescrito para o caminho relativo no layout novo.
import os, re, sys, json, subprocess, shutil
RB = '/root/rebang'; ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out/F3.2')
MAP = [('source/client/ProjectG/', 'src/projectg/'), ('source/client/Fresh/', 'src/fresh/'),
       ('source/client/Wangreal/source/', 'src/engine/'), ('source/client/Wangreal/include/', 'include/engine/'),
       ('source/shared/', 'src/shared/')]
SKIP = re.compile(r'(^|/)(lib|third_party)/|\.(obj|lib|tar\.gz|zip|patch|pdb|res|aps)$')
TEXT = ('.cpp', '.c', '.h', '.inl', '.hpp', '.rc', '.def', '.rc2')
def newpath(rel):
    for a, b in MAP:
        if rel.startswith(a): return b + rel[len(a):]
    return None
files = subprocess.check_output(['git', '-C', RB, 'ls-files', 'source'], text=True).split('\n')
files = [f for f in files if f]
inc = re.compile(rb'^(\s*#\s*include\s*")([^"]*\.\./[^"]*)(")', re.M)
copied, kept, rewrites, lost = [], [], [], []
def third():
    lua = os.path.join(ROOT, 'src/shared/LuaSystem/Lua'); lzo = os.path.join(ROOT, 'src/shared/minilzo')
    if not os.path.exists(lua + '/src/lua.h'):
        os.makedirs(lua, exist_ok=True)
        subprocess.check_call(['tar', 'xzf', RB + '/source/shared/LuaSystem/lua-5.1.tar.gz', '-C', lua, '--strip-components=1'])
    if not os.path.exists(lzo + '/minilzo.cpp'):
        os.makedirs(lzo, exist_ok=True)
        subprocess.check_call(['tar', 'xzf', RB + '/source/shared/minilzo-2.02.tar.gz', '-C', lzo, '--strip-components=1'])
        subprocess.check_call(['patch', '-s', '-p1', '-d', lzo, '-i', RB + '/source/shared/minilzo-2.02.patch'])
    # freetype 2.2.1 (com o patch), libpng 1.2.8 e zlib 1.2.2: árvores já extraídas pelo build do rebang (fora do git de lá)
    for a, b in (('source/client/Wangreal/lib/freetype-2.2.1', 'src/engine/lib/freetype-2.2.1'),
                 ('source/client/Fresh/third_party/libpng-1.2.8', 'src/fresh/third_party/libpng-1.2.8'),
                 ('source/client/Fresh/third_party/zlib-1.2.2', 'src/fresh/third_party/zlib-1.2.2')):
        if not os.path.isdir(os.path.join(ROOT, b)):
            shutil.copytree(os.path.join(RB, a), os.path.join(ROOT, b), ignore=shutil.ignore_patterns('.unpacked', '*.obj', '*.lib'))
third()
# o que uma importação anterior trouxe pode ser atualizado; o resto que já existe aqui é nosso e fica
prev_tsv = os.path.join(out, 'importados.tsv')
PREV = set(l.split('\t')[1] for l in open(prev_tsv).read().split('\n')[1:] if l) if os.path.exists(prev_tsv) else set()
# F3.5: arquivos adotados (map/adotados.txt) já são fonte do 983 editada à mão: o reimporte não os toca
_ad = os.path.join(ROOT, 'map/adotados.txt')
ADOT = set(l.split('\t')[0].strip() for l in open(_ad) if l.strip() and not l.startswith('#')) if os.path.exists(_ad) else set()
for rel in sorted(set(files)):
    if SKIP.search(rel): continue
    np = newpath(rel)
    if not np: continue
    dst = os.path.join(ROOT, np)
    if os.path.exists(dst) and (np not in PREV or np in ADOT):
        kept.append((rel, np)); continue
    data = open(os.path.join(RB, rel), 'rb').read()
    if rel.endswith(TEXT):
        def fix(m):
            tgt = os.path.normpath(os.path.join(os.path.dirname(rel), m.group(2).decode()))
            nt = newpath(tgt.replace(os.sep, '/'))
            if nt is None or not os.path.exists(os.path.join(RB, tgt)):
                # alvo que o git do rebang não tem (terceiros extraídos de arquivo: Lua, minilzo) ou caminho errado
                if nt is None or not os.path.exists(os.path.join(ROOT, nt)): lost.append((rel, m.group(2).decode()))
                if nt is None: return m.group(0)
            r = os.path.relpath(nt, os.path.dirname(np)).replace(os.sep, '/')
            if r != m.group(2).decode(): rewrites.append((np, m.group(2).decode(), r))
            return m.group(1) + r.encode() + m.group(3)
        data = inc.sub(fix, data)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'wb').write(data); copied.append((rel, np))
os.makedirs(out, exist_ok=True)
head = subprocess.check_output(['git', '-C', RB, 'rev-parse', 'HEAD'], text=True).strip()
open(os.path.join(out, 'importados.tsv'), 'w').write('rebang\taqui\n' + ''.join('%s\t%s\n' % x for x in copied))
open(os.path.join(out, 'mantidos.txt'), 'w').write(''.join('%s\t%s\n' % x for x in kept))
open(os.path.join(out, 'includes_reescritos.tsv'), 'w').write('arquivo\tantes\tdepois\n' + ''.join('%s\t%s\t%s\n' % x for x in rewrites))
open(os.path.join(out, 'includes_sem_alvo.tsv'), 'w').write(''.join('%s\t%s\n' % x for x in lost))
open(os.path.join(out, 'rebang_commit.txt'), 'w').write(head + '\n')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ajustes
ajustes.run(out)
print('rebang', head[:10], 'copiados', len(copied), 'mantidos', len(kept), 'includes reescritos', len(rewrites), 'sem alvo', len(lost))
