#!/usr/bin/env python3
"""msgvotos.py SAIDA — votos para a renumeração das mensagens entre atores (645 → 983): para cada caso do despachante comum que
existe no fonte (ramo em C do CTask::OnPacketCommon, números de mensagem do 645) e no exe 983 (009c20a0), compara a sequência de
números de mensagem dos MsgObject(NULL, N, ...) com a sequência dos `push N` que antecedem o construtor 0046e780 no 983. Só vota
quando as duas sequências têm o mesmo tamanho (par posição a posição). Casos escritos pelo desmonte (s64–s66) ficam de fora."""
import sys, re, csv, struct, capstone, collections, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out = sys.argv[1]
d = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]; ns = struct.unpack_from('<H', d, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', d, oh + 28)[0]; st = oh + struct.unpack_from('<H', d, pe + 20)[0]
secs = [struct.unpack_from('<IIII', d, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
CTOR = 0x46e780
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
def tail_kind(va):
    """0 = alvo começa por `call ctor` (pushes completos); 1 = `push 0; call ctor` (falta o ator); None = outro"""
    b = d[off(va):off(va) + 8]
    if b[0] == 0xe8 and va + 5 + struct.unpack_from('<i', b, 1)[0] == CTOR: return 0
    if b[:2] == b'\x6a\x00' and b[2] == 0xe8 and va + 7 + struct.unpack_from('<i', b, 3)[0] == CTOR: return 1
rows = [r for r in csv.DictReader(open(R + '/out/V4/pacotes_recebe_983.tsv'), delimiter='\t') if r['despachante983'] == '009c20a0']
vas = sorted(set(int(r['va_caso'], 16) for r in rows))
def seq983(va):
    nx = [v for v in vas if v > va]; end = min(nx[0] if nx else va + 0x1000, va + 0x1000)
    pushes = []; seq = []
    for i in md.disasm(d[off(va):off(end)], va):
        if i.mnemonic == 'push':
            o = i.op_str
            pushes.append(int(o, 0) if re.fullmatch(r'(0x)?[0-9a-f]+', o) else None)
        elif i.mnemonic == 'call' and i.op_str.startswith('0x') and int(i.op_str, 16) == CTOR:
            seq.append(pushes[-2] if len(pushes) > 1 else None); pushes = []
        elif i.mnemonic == 'jmp' and i.op_str.startswith('0x') and not (va <= int(i.op_str, 16) < end):
            k = tail_kind(int(i.op_str, 16))
            if k == 0 and len(pushes) > 1: seq.append(pushes[-2])
            elif k == 1 and pushes: seq.append(pushes[-1])
            pushes = []
        elif i.mnemonic == 'call': pushes = []
    return seq
s = open(R + '/src/projectg/taskmanager.cpp', encoding='latin1').read()
a = s.rindex('\nint CTask::OnPacketCommon(WReceivedPacket& packet)'); b = s.index('\n}\n', a) if '\n}\n' in s[a:] else len(s)
body = s[a:b].replace('\r', '')
fora = set()
for l in open(R + '/out/F3.5/s65/casos_novos_983.tsv').read().split('\n')[1:]:
    if l: fora.add(int(l.split('\t')[0], 16))
fora |= {0x1dd, 0x1de, 0x1df, 0x1e0, 0x11f}
src = {}; cur = []; pend = []
for l in body.split('\n'):
    m = re.match(r'\tcase (0x[0-9a-f]+|\d+):', l)
    if m or re.match(r'\tcase PKT645|\tdefault:', l):
        if cur and pend == []: cur = []
        if m:
            if pend == [] or not fresh: cur = [int(m.group(1), 0)]; 
            else: cur.append(int(m.group(1), 0))
            for c in cur: src.setdefault(c, [])
        else: cur = []
        fresh = True; pend = [1]; continue
    if l.strip(): fresh = False
    for n in re.findall(r'MsgObject\((?:NULL|0|this), ([^,]+),', l):
        for c in cur:
            try: src[c].append(int(n, 0))
            except ValueError: src[c].append(None)
votes = collections.defaultdict(lambda: collections.defaultdict(list)); rep = []
for r in rows:
    i0 = int(r['id'], 16)
    if i0 in fora or i0 not in src: continue
    S = src[i0]; Rq = seq983(int(r['va_caso'], 16))
    ok = len(S) == len(Rq) and len(S) > 0
    rep.append((i0, r['va_caso'], ' '.join('%x' % x if x is not None else '?' for x in S), ' '.join('%x' % x if x is not None else '?' for x in Rq), 'vota' if ok else ('vazio' if not S and not Rq else 'tamanho')))
    if ok:
        for x, y in zip(S, Rq):
            if x is not None and y is not None: votes[x][y].append(i0)
os.makedirs(out, exist_ok=True)
with open(out + '/msg_casos.tsv', 'w') as f:
    f.write('id_983\tva_caso\tmsgs_fonte_645\tmsgs_983\testado\n')
    for x in sorted(rep): f.write('0x%x\t%s\t%s\t%s\t%s\n' % x)
with open(out + '/msg_votos.tsv', 'w') as f:
    f.write('msg_645\tmsg_983\tvotos\tvotos_contra\tids\n')
    for x in sorted(votes):
        tot = sum(len(v) for v in votes[x].values())
        for y, ids in sorted(votes[x].items(), key=lambda kv: -len(kv[1])):
            f.write('0x%x\t0x%x\t%d\t%d\t%s\n' % (x, y, len(ids), tot - len(ids), ' '.join('%x' % i for i in ids[:12])))
c = collections.Counter(x[4] for x in rep)
ig = sum(1 for x in votes if max(votes[x], key=lambda y: len(votes[x][y])) == x); 
print('casos', dict(c), '| mensagens do 645 com voto', len(votes), '| maioria igual', ig, '| maioria diferente', len(votes) - ig,
      '| disputadas', sum(1 for x in votes if len(votes[x]) > 1))
