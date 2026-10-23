#!/usr/bin/env python3
"""msgorigem.py SAIDA [--aplica] — depois do msgaplica.py: acha os locais M983(n) cujo número NÃO veio do 645.
Compara, arquivo por arquivo, a sequência de números de mensagem do fonte (antes do M983: `git show HEAD:arquivo`) com a do
rebang f0a85b5 (KR 645). Local igual ao do rebang = número do 645 (fica em M983). Local trocado ou novo aqui = alguém já escreveu
o número do 983 à mão (sessões anteriores, funções que davam IGUAL): M983(0xN) volta a ser 0xN direto, com a marca /*983*/.
Arquivo que não existe no rebang: todos os locais são daqui (números do 983).
Saída: origem_locais.tsv (arquivo, posição, número aqui, número no rebang, decisão) e origem_arquivos.tsv."""
import sys, os, re, subprocess, difflib, collections
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.argv.insert(1, '/dev/null'); sys.argv.insert(2, '/dev/null')
out = sys.argv[3]; aplica = '--aplica' in sys.argv
NUM = r'(0x[0-9a-fA-F]+|\d+)'
TOK = re.compile(r'\bMsgObject\(\s*[^,()]+,\s*' + NUM + r'\s*,|\b(?:Afx)?(?:Send|Post)Msg\(\s*[^,()]+,\s*[^,;]+,\s*' + NUM + r'\s*,|'
                 r'\b(?:msg|m)\.message\s*[!=]=\s*' + NUM + r'\b|^\s*case\s+' + NUM + r'\s*:', re.M)
WRAP = re.compile(r'M983\((0x[0-9a-f]+)\)')
def seq(txt):
    """números (>0 e < 0x2710) nos formatos de envio/case, na ordem do arquivo; `case` conta em qualquer switch (só para alinhar)"""
    r = []
    for m in TOK.finditer(txt):
        n = int(next(g for g in m.groups() if g), 0)
        if 0 < n < 0x2710: r.append((n, m.group(0).lstrip().startswith('case')))
    return r
def git(repo, spec):
    p = subprocess.run(['git', '-C', repo, 'show', spec], capture_output=True)
    return p.stdout.decode('latin1') if p.returncode == 0 else None
os.makedirs(out, exist_ok=True)
files = subprocess.run(['grep', '-rlE', r'M983\(0x', R + '/src/projectg', '--include=*.cpp', '--include=*.h'], capture_output=True, text=True).stdout.split()
L = []; A = []; tot = collections.Counter()
for fn in sorted(files):
    rel = os.path.relpath(fn, R)
    if '/jp/' in rel or rel.endswith('msg983.h'): continue
    cur = open(fn, encoding='latin1').read()
    antes = git(R, 'HEAD:' + rel)
    rb = git('/root/rebang', 'f0a85b5:source/client/ProjectG/' + rel[len('src/projectg/'):])
    # locais embrulhados, na ordem, com o número
    wr = [(m.start(), int(m.group(1), 16)) for m in WRAP.finditer(cur)]
    dec = {}          # índice do local embrulhado -> (decisão, número no rebang)
    if antes is None: continue
    sa = seq(antes)
    # índice na sequência de `antes` de cada local embrulhado: os embrulhados são subsequência (mesma ordem); casa por valor
    k = 0; pos = []
    sc = seq(WRAP.sub(lambda m: m.group(1), cur))
    wi = 0; curw = seq_w = []
    # reconstrói: percorre o texto atual marcando quais tokens estão embrulhados
    marc = WRAP.sub(lambda m: '\x01' + m.group(1), cur)
    T2 = re.compile(TOK.pattern.replace(NUM, '(\x01?(?:0x[0-9a-fA-F]+|\\d+))'), re.M)
    flags = []
    for m in T2.finditer(marc):
        g = next(g for g in m.groups() if g); n = int(g.lstrip('\x01'), 0)
        if 0 < n < 0x2710: flags.append(g.startswith('\x01'))
    if len(flags) != len(sa): flags = None
    if rb is None:
        for i in range(len(wr)): dec[i] = ('novo_arquivo', None)
    elif flags is None:
        for i in range(len(wr)): dec[i] = ('nao_alinhado', None)
    else:
        sr = seq(rb); sm = difflib.SequenceMatcher(None, [x[0] for x in sr], [x[0] for x in sa], autojunk=False)
        orig = {}
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            for j in range(j1, j2):
                if tag == 'equal': orig[j] = ('645', sr[i1 + j - j1][0])
                elif tag == 'replace' and i2 - i1 == j2 - j1: orig[j] = ('trocado', sr[i1 + j - j1][0])
                else: orig[j] = ('novo', None)
        w = 0
        for j, f in enumerate(flags):
            if f: dec[w] = orig[j]; w += 1
    cnt = collections.Counter(d[0] for d in dec.values()); tot.update(cnt)
    A.append((rel, len(wr), dict(cnt)))
    for i, (p, n) in enumerate(wr):
        d = dec.get(i, ('?', None)); L.append((rel, cur.count('\n', 0, p) + 1, n, d[1], d[0]))
    if aplica:
        i = [0]
        def rep(m):
            d = dec.get(i[0], ('?', None))[0]; i[0] += 1
            return m.group(0) if d in ('645', 'nao_alinhado', '?') else m.group(1) + '/*983*/'
        new = WRAP.sub(rep, cur)
        if new != cur: open(fn, 'wb').write(new.encode('latin1'))
with open(out + '/origem_locais.tsv', 'w') as f:
    f.write('arquivo\tlinha\tnumero\tnumero_rebang\torigem\n')
    for a, l, n, o, d in L: f.write('%s\t%d\t0x%x\t%s\t%s\n' % (a, l, n, '0x%x' % o if o else '', d))
with open(out + '/origem_arquivos.tsv', 'w') as f:
    f.write('arquivo\tlocais\torigens\n')
    for a, n, c in A: f.write('%s\t%d\t%s\n' % (a, n, ' '.join('%s=%d' % kv for kv in sorted(c.items()))))
print('%s: arquivos %d | locais %d: %s' % ('APLICADO' if aplica else 'contagem', len(A), len(L), dict(tot)))
