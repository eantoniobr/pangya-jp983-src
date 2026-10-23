#!/usr/bin/env python3
"""msgaplica.py DIR_tabela SAIDA [--aplica] — renumeração das mensagens entre atores 645 → 983 no fonte da frente A.
Cada número de mensagem escrito no fonte (número do 645) passa a `M983(0x<n>)`, e src/projectg/msg983.h (gerado aqui) dá o valor:
  - `firme`: âncora de msg_pares.tsv com peso >= 2, ou com âncora vizinha (até 0x10 de distância) de mesmo deslocamento; e os
    números entre duas âncoras firmes de mesmo deslocamento (interpolado) → número do 983;
  - o resto → valor PROVISÓRIO 0x40000000 + n: quem envia e quem recebe continuam combinando entre si e o valor não colide com
    nenhum número de verdade do 983 (um `case` do 645 não passa a atender outra mensagem). O comparador mostra esses imediatos.
Locais trocados: MsgObject(x, N, …), SendMsg/PostMsg/AfxPostMsg(x, alvo, N, …), `case N:` dos `switch (msg.message)` e
`msg.message ==/!= N`. Ficam de fora: src/projectg/jp (frente B, já nos números do 983), 0 e >= 0x2710 (Gateway, iguais), e os
casos do OnPacketCommon escritos pelo desmonte do 983 (s64–s66), que já usam números do 983.
Pares manuais: map/msg_manual.tsv (msg_645, msg_983, motivo) passa na frente dos votos — é o caminho das mensagens do Gateway
do 645 (0x26b–0x276), que no 983 viraram 0x7530 + n e por isso não cabem no modelo crescente do msgtabela.py (s71).
Sem --aplica só conta. Idempotente (não mexe no que já está em M983)."""
import sys, os, re, csv, glob, collections, bisect
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
tab, out = sys.argv[1], sys.argv[2]; aplica = '--aplica' in sys.argv
GW = 0x2710; PROV = 0x40000000
anc = []
for r in csv.DictReader(open(tab + '/msg_pares.tsv'), delimiter='\t'):
    if r['decisao'] == 'ancora': anc.append((int(r['msg_645'], 16), int(r['msg_983'], 16), float(r['peso'])))
anc.sort()
firme = []
for i, (x, y, w) in enumerate(anc):
    viz = [anc[k] for k in (i - 1, i + 1) if 0 <= k < len(anc) and abs(anc[k][0] - x) <= 0x10 and anc[k][1] - anc[k][0] == y - x]
    if w >= 2 or viz: firme.append((x, y))
firme = [(0, 0)] + firme      # 0 fica 0; com a ordem crescente, uma âncora n -> n firme obriga 1..n-1 a ficarem iguais
FX = [a[0] for a in firme]; FD = dict(firme)
MAN = {}
if os.path.exists(R + '/map/msg_manual.tsv'):
    for r in csv.DictReader((l for l in open(R + '/map/msg_manual.tsv', encoding='utf-8') if not l.startswith('#')), delimiter='\t'):
        MAN[int(r['msg_645'], 16)] = int(r['msg_983'], 16)
def valor(x):
    """(valor do 983 ou None, estado)"""
    if x in MAN: return MAN[x], 'manual'
    if x in FD: return FD[x], 'voto'
    i = bisect.bisect_left(FX, x)
    if 0 < i < len(FX) and firme[i - 1][1] - firme[i - 1][0] == firme[i][1] - firme[i][0]:
        return x + firme[i][1] - firme[i][0], 'interpolado'
    return None, 'aberto'
NUM = r'(0x[0-9a-fA-F]+|\d+)'
PATS = [('MsgObject', re.compile(r'(\bMsgObject\(\s*[^,()]+,\s*)' + NUM + r'(\s*,)')),
        ('SendPost', re.compile(r'(\b(?:Afx)?(?:Send|Post)Msg\(\s*[^,()]+,\s*[^,;]+,\s*)' + NUM + r'(\s*,)')),
        ('compara', re.compile(r'(\b(?:msg|m)\.message\s*[!=]=\s*)' + NUM + r'(\b(?!/\*983))'))]   # /*983*/ = número do 983 escrito direto (msgorigem.py)
CASE = re.compile(r'^(\s*case\s+)' + NUM + r'(\s*:)')
SW = re.compile(r'switch\s*\(\s*msg\.message\s*\)')
FAIXA = re.compile(r'\b(?:msg|m)\.message\s*[<>]=?\s*' + NUM)
usados = collections.defaultdict(collections.Counter); porarq = collections.Counter(); faixas = []
def troca(m, tipo, fn):
    n = int(m.group(2), 0)
    if n == 0 or n >= GW: return m.group(0)
    usados[n][tipo] += 1; porarq[fn] += 1
    return '%sM983(0x%x)%s' % (m.group(1), n, m.group(3))
def zonas(lines, fn):
    """linhas (índices) que já estão nos números do 983"""
    z = set()
    if not fn.endswith('/taskmanager.cpp'): return z
    a = [i for i, l in enumerate(lines) if '// S65: casos do 983 sem par' in l]
    b = [i for i, l in enumerate(lines) if '// 645 0x162/0x163' in l]
    if a and b: z |= set(range(a[0], b[0]))
    for i, l in enumerate(lines):
        if '// S65: corpo do 983 (009c8bd6)' in l:
            k = i
            while k < len(lines) and not re.match(r'\tcase ', lines[k]): z.add(k); k += 1
    return z
arquivos = sorted(glob.glob(R + '/src/projectg/**/*.cpp', recursive=True) + glob.glob(R + '/src/projectg/**/*.h', recursive=True))
mudados = 0
for fn in arquivos:
    if '/jp/' in fn or fn.endswith('/msg983.h'): continue
    raw = open(fn, 'rb').read(); txt = raw.decode('latin1'); rel = os.path.relpath(fn, R)
    lines = txt.split('\n'); z = zonas(lines, fn)
    # 1) case dos switch (msg.message): por linha, com profundidade de chaves
    em = False; prof = 0
    for i, l in enumerate(lines):
        if SW.search(l) or (fn.endswith('/eventactor.cpp') and re.search(r'switch\s*\(\s*message\s*\)', l)): em = True; prof = l.count('{') - l.count('}'); continue
        if not em: continue
        if prof <= 1 and i not in z:
            m = CASE.match(l)
            if m: lines[i] = troca(m, 'case', rel) + l[m.end():]
        prof += l.count('{') - l.count('}')
        if prof <= 0 and '}' in l: em = False
    # 2) envios e comparações: no texto inteiro (chamadas ocupam mais de uma linha); zonas protegidas por marcador
    for i in z: lines[i] = lines[i].replace('MsgObject(', 'MsgObject\x00(').replace('Msg(', 'Msg\x00(')
    new = '\n'.join(lines)
    for tipo, p in PATS: new = p.sub(lambda m: troca(m, tipo, rel), new)
    new = new.replace('\x00', '')
    for m in FAIXA.finditer(new): faixas.append((rel, new.count('\n', 0, m.start()) + 1, m.group(0)))
    if new != txt:
        mudados += 1
        if aplica: open(fn, 'wb').write(new.encode('latin1'))
# números que já estão em M983 no fonte (rodada anterior) também entram no cabeçalho
for fn in arquivos:
    if '/jp/' in fn: continue
    for m in re.finditer(r'\bM983\((0x[0-9a-f]+)\)', open(fn, encoding='latin1').read()):
        usados[int(m.group(1), 16)]['ja'] += 0
os.makedirs(out, exist_ok=True)
est = collections.Counter(); loc = collections.Counter(); H = []
with open(out + '/aplica_numeros.tsv', 'w') as f:
    f.write('msg_645\testado\tvalor\tMsgObject\tSendPost\tcase\tcompara\n')
    for x in sorted(usados):
        v, e = valor(x); c = usados[x]; n = sum(c.values())
        if v == x: e += '_igual'
        est[e] += 1; loc[e] += n
        f.write('0x%x\t%s\t%s\t%d\t%d\t%d\t%d\n' % (x, e, '0x%x' % v if v is not None else 'provisorio', c['MsgObject'], c['SendPost'], c['case'], c['compara']))
        H.append('#define MSG645_0x%x 0x%x%s' % (x, v if v is not None else PROV + x, '' if v is not None and e.startswith('voto') else
                 '\t// manual (map/msg_manual.tsv)' if e.startswith('manual') else '\t// interpolado' if v is not None else '\t// ABERTO: sem voto; valor provisório'))
with open(out + '/aplica_arquivos.tsv', 'w') as f:
    f.write('arquivo\tlocais\n')
    for k, n in sorted(porarq.items()): f.write('%s\t%d\n' % (k, n))
with open(out + '/aplica_faixas.txt', 'w') as f:
    for x in faixas: f.write('%s:%d: %s\n' % x)
if aplica:
    hdr = ['// msg983.h - números das mensagens entre atores: 645 -> 983. GERADO por tools/f35/msgaplica.py; não editar à mão.',
           '// O fonte veio do KR 645 e escreve M983(0x<número do 645>); aqui fica o número que o JP 983 usa.',
           '// Tabela e votos: out/F3.5/s68/msg/ (msg_pares.tsv) + map/msg_manual.tsv. "ABERTO" = ainda sem voto: valor provisório 0x40000000 + n, que',
           '// mantém quem envia e quem recebe combinando e não colide com número de verdade do 983.',
           '// 0 e os números >= 0x2710 são iguais nas duas versões e ficam escritos direto. Gateway: 645 0x26b+ -> 983 0x7530+ (manual).',
           '#pragma once', '#define M983(n) MSG645_##n', ''] + H + ['']
    open(R + '/src/projectg/msg983.h', 'wb').write('\r\n'.join(hdr).encode('latin1'))
print('%s: arquivos %d | números %d: %s | locais %d: %s | comparações de faixa (não trocadas) %d' % (
    'APLICADO' if aplica else 'contagem', mudados, len(usados), dict(est), sum(loc.values()), dict(loc), len(faixas)))
print('âncoras %d, firmes %d' % (len(anc), len(firme)))
