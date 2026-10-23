#!/usr/bin/env python3
"""pkt/subsw.py INICIO FIM arquivo.cpp 'case 0xNN' [n] — confere um sub-switch de TEXTOS de um caso de pacote (frente C).
O rx.py do `make v4` compara só as leituras; um sub-código renumerado ou com texto trocado passa como `igual`. Aqui:
no 983, entre INICIO e FIM (VA), acha o n-ésimo (padrão 1º) `cmp eax, N` + `movzx eax, byte [eax+B]`(opcional) + `jmp [eax*4+D]`,
lê as tabelas e, para cada sub-código, o 1º texto (`mov ecx, 0xd.....` antes do K2L_Compatibility) e os números de
mensagem gravados em [ebp-0x2c]/[ebp-0x19c]... ; no fonte, o 1º `switch` depois do rótulo `case 0xNN:` (do despachante),
cada `case X:` → 1º literal. Saída: sub-código, ok/DIFERE/SO_983/SO_FONTE, endereço do texto e leitura cp949.
Rótulo 'Classe::Funcao/case 0xNN' ancora na última definição da função (a cópia que compila).
`subsw.py --varre [Classe::Funcao] > out/PKT/sN/subsw.tsv`: todos os casos dos despachantes (out/V4/pacotes_recebe_983.tsv) que têm sub-switch com textos."""
import sys, os, re, struct, subprocess
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ex = open(R + '/ref/ProjectG_983_dump.exe', 'rb').read()
pe = struct.unpack_from('<I', ex, 0x3c)[0]; ns = struct.unpack_from('<H', ex, pe + 6)[0]
oh = pe + 24; base = struct.unpack_from('<I', ex, oh + 28)[0]; st = oh + struct.unpack_from('<H', ex, pe + 20)[0]
secs = [struct.unpack_from('<IIII', ex, st + 40 * i + 8) for i in range(ns)]
def off(va):
    rva = va - base
    for vs, v, rs, ro in secs:
        if v <= rva < v + max(vs, rs): return ro + rva - v
def cstr(va):
    o = off(va); s = ex[o:ex.index(b'\0', o)]
    lit = ''; hx = False
    for c in s:
        if c > 126 or c < 32: lit += {10: '\\n', 13: '\\r', 9: '\\t'}.get(c, '\\x%02x' % c); hx = c > 126
        else:
            ch = chr(c); ch = '\\' + ch if ch in '"\\' else ch
            lit += ('" "' if hx and ch in '0123456789abcdefABCDEF' else '') + ch; hx = False
    return '"%s"' % lit, s.decode('cp949', 'replace').replace('\n', '\\n').replace('\r', '')
def eh_texto(va):
    o = off(va)
    if o is None or o >= len(ex): return False
    try: e = ex.index(b'\0', o)
    except ValueError: return False
    b = ex[o:e]
    if len(b) < 2 or len(b) > 400: return False
    try: b.decode('cp949')
    except UnicodeDecodeError: return False
    if re.match(rb'^[A-Za-z0-9_]+$', b): return False  # nome de ator/janela ("Lobby", "AvatarChat"...), não aviso
    return all(c >= 32 or c in (9, 10, 13) for c in b)
def desmonta(ini, fim):
    dz = subprocess.run(['python3', R + '/tools/f37/dz.py', ini, fim], capture_output=True, text=True).stdout.split('\n')
    return [(int(l[:8], 16), re.sub(r"\s*;.*$", "", l[10:]).rstrip()) for l in dz if re.match(r'^[0-9a-f]{8}  ', l)]
def tabelas(L):
    """todas as tabelas de salto do trecho: (i, D, B, N, desvio)"""
    res = []
    for i, (a, t) in enumerate(L):
        m = re.match(r'jmp\s+dword ptr \[(e[a-z]x)\*4 \+ 0x([0-9a-f]+)\]', t)
        if not m: continue
        rg = m.group(1); D = int(m.group(2), 16); B = None; N = None
        for a2, t2 in reversed(L[max(0, i - 4):i]):
            mb = re.match(r'movzx\s+e[a-z]x, byte ptr \[e[a-z]x \+ 0x([0-9a-f]+)\]', t2)
            if mb: B = int(mb.group(1), 16)
            mc = re.match(r'cmp\s+e[a-z]x, (0x[0-9a-f]+|\d+)$', t2)
            if mc and N is None: N = int(mc.group(1), 0)
        if N is None: continue
        desvio = 0; rc = None
        for a2, t2 in reversed(L[max(0, i - 4):i]):
            mc = re.match(r'cmp\s+(e[a-z]{2}), ', t2)
            if mc: rc = mc.group(1); break
        for a2, t2 in reversed(L[max(0, i - 8):i]):
            # C20: só conta add/sub/lea/dec no MESMO registrador do `cmp` (o `add ecx, 0x10c24` de um `this` não é desvio);
            # outra escrita nesse registrador (mov/movzx) encerra a busca
            if re.match(r'movzx\s+e[a-z]{2}, byte ptr \[e[a-z]{2} \+ 0x', t2): continue  # a tabela de bytes do próprio switch
            md = re.match(r'(\w+)\s+(e[a-z]{2})\b', t2)
            if rc and md and md.group(2) == rc and md.group(1) not in ('cmp', 'test', 'add', 'sub', 'lea', 'dec', 'push'): break
            if rc and md and md.group(2) != rc: continue
            if re.match(r'dec\s+e[a-z]x$', t2): desvio = 1; break
            ms = re.match(r'(add|sub)\s+e[a-z]x, (-?0x[0-9a-f]+|-?\d+)$', t2) or re.match(r'lea\s+e[a-z]x, \[e[a-z]{2} - (0x[0-9a-f]+|\d+)\]', t2)  # base esi/edi também (C20)
            if ms:
                k = int(ms.groups()[-1], 0)
                if k > 0x7fffffff: k -= 1 << 32  # `add eax, 0xfffffefb` = sub 0x105 (C20)
                desvio = (-k if ms.group(0).startswith('add') else k); break
        res.append((i, D, B, N, desvio))
    return res
def lado983(L, tab):
    i, D, B, N, desvio = tab
    idx = list(ex[off(B):off(B) + N + 1]) if B is not None else list(range(N + 1))
    nd = max(idx) + 1
    alvo = [struct.unpack_from('<I', ex, off(D) + 4 * k)[0] for k in range(nd)]
    ends = set(alvo); addrs = [a for a, _ in L]; ref = {}
    for code in range(N + 1):
        v = alvo[idx[code]]
        if B is not None and idx[code] == nd - 1 and idx.count(nd - 1) > 1: continue  # entrada "fora" da tabela de bytes
        if v not in addrs: ref[code + desvio] = (v, None, []); continue
        k = addrs.index(v); txt = None; txtp = None; msgs = []
        for a2, t2 in L[k:k + 60]:  # para no início do sub-código seguinte (o `jmp` curto do GetActor não é fim)
            if a2 != v and a2 in ends: break
            m = re.match(r'mov\s+ecx, 0x([cd][0-9a-f]{5})$', t2)
            if m and txt is None: txt = int(m.group(1), 16)
            m = re.match(r'push\s+0x([cd][0-9a-f]{5})$', t2)  # texto passado por `push` (C20): só se parecer texto
            if m and txt is None and txtp is None and eh_texto(int(m.group(1), 16)): txtp = int(m.group(1), 16)
            m = re.match(r'mov\s+dword ptr \[ebp - 0x[0-9a-f]+\], (0x[0-9a-f]+)$', t2)
            if m and int(m.group(1), 16) not in (0x23,) and len(msgs) < 4: msgs.append(m.group(1))
        ref[code + desvio] = (v, txt if txt is not None else txtp, msgs)
    return ref
def ladofonte(arq, rot, todos=False):
    """rot = 'Classe::Funcao/case 0xNN' (âncora na ÚLTIMA definição da função: cópia viva) ou só 'case 0xNN'.
    todos=True: lista com TODOS os switch do caso (aninhados inclusive), para escolher o que casa com cada tabela do 983 (C20)"""
    src = open(R + '/' + arq, encoding='latin1').read().split('\n')
    k0 = 0
    if '/' in rot:
        fn, rot = rot.split('/', 1)
        k0 = [j for j, l in enumerate(src) if re.match(r'^\w[^;]*\b' + re.escape(fn) + r'\s*\(', l)][-1]
    ks = [j for j in range(k0, len(src)) if re.match(r'\s*' + re.escape(rot) + r':', src[j])]
    if not ks: raise StopIteration
    if k0:  # C20: o rótulo do DESPACHANTE é o menos recuado (o 1º `case 0x110:` depois da definição pode ser um sub-caso)
        fimf = next((j for j in range(k0 + 1, len(src)) if src[j].startswith('}')), len(src))
        ks = [j for j in ks if j < fimf] or ks
        mi = min(len(src[j]) - len(src[j].lstrip()) for j in ks); ks = [j for j in ks if len(src[j]) - len(src[j].lstrip()) == mi]
    k = ks[0]
    ind = len(src[k]) - len(src[k].lstrip())
    sws = []
    for j in range(k + 1, len(src)):
        l = src[j]
        if re.match(r'\s*(case [^:]+|default):', l) and len(l) - len(l.lstrip()) <= ind: break
        if re.search(r'\bswitch\s*\(', l): sws.append(j)
    if not sws: return None
    if todos: return [umswitch(src, sw) for sw in sws]
    return umswitch(src, sws[0])
def umswitch(src, sw):
    prof = 0; cur = []; out = {}; comeco = True; ant = ''
    for l in src[sw:]:
        cego = re.sub(r'"(?:[^"\\]|\\.)*"', lambda m: '"' + 'x' * (len(m.group(0)) - 2) + '"', l)
        if '//' in cego: l = l[:cego.index('//')]  # comentário fora de literal
        sem = re.sub(r'"(?:[^"\\]|\\.)*"', '""', l)
        m = re.match(r'\s*case (0x[0-9a-f]+|\d+):', l)
        if m and prof == 1: cur.append(int(m.group(1), 0))
        lit = re.search(r'"((?:[^"\\]|\\.)*)"(\s*"((?:[^"\\]|\\.)*)")*', re.sub(r'GetActor\("\w*"\)|"[A-Za-z0-9_]*"', '', l))  # nomes de ator/janela não são aviso
        if lit and cur and prof >= 1:
            for c in cur: out[c] = lit.group(0)
            cur = []
        if re.match(r'\s*break;', l) and prof == 1 and not re.match(r'\s*(if|else)\b', ant): cur = []
        if l.strip(): ant = l
        prof += sem.count('{') - sem.count('}')
        if not comeco and prof <= 0: break
        if prof > 0: comeco = False
    return out
def norm(s):
    """literal C (um ou vários colados) -> bytes; aceita \\xNN, octal, \\n etc."""
    if not s: return s
    out = bytearray()
    for parte in re.findall(r'"((?:[^"\\]|\\.)*)"', s):
        j = 0; b = parte.encode('latin1')
        while j < len(b):
            c = b[j]
            if c != 0x5c: out.append(c); j += 1; continue
            n = chr(b[j + 1])
            if n == 'x':
                m = re.match(rb'[0-9a-fA-F]+', b[j + 2:]); out.append(int(m.group(0), 16) & 0xff); j += 2 + len(m.group(0))
            elif n in '01234567':
                m = re.match(rb'[0-7]{1,3}', b[j + 1:]); out.append(int(m.group(0), 8) & 0xff); j += 1 + len(m.group(0))
            else:
                out.append({'n': 10, 'r': 13, 't': 9, '0': 0}.get(n, ord(n))); j += 2
    return bytes(out)
def melhor(ref, outs):
    """switch do fonte que mais casa (textos iguais) com a tabela do 983; None se nenhum casa"""
    best, bn = None, 0
    for out in outs or []:
        n = sum(1 for e in compara(ref, out) if e[1] == 'ok')
        if n > bn: best, bn = out, n
    return best
def compara(ref, out):
    res = []
    for c in sorted(set(ref) | set(out)):
        v, txt, msgs = ref.get(c, (None, None, []))
        s = out.get(c)
        if c not in ref: e = 'SO_FONTE'
        elif txt is None: e = 'sem_texto' + ('' if s is None else ' (fonte tem texto)')
        elif s is None: e = 'SO_983'
        else: e = 'ok' if norm(cstr(txt)[0]) == norm(s) else 'DIFERE'
        res.append((c, e, v, txt, (cstr(txt)[1] if txt else ' '.join(msgs))))
    return res
if sys.argv[1] == '--varre':
    # --varre: todos os casos de out/V4/pacotes_recebe_983.tsv com sub-switch de textos; fonte pela tabela de despachantes do rx.py
    desp = {'009c20a0': ('src/projectg/taskmanager.cpp', 'CTask::OnPacketCommon'), '00ac03a0': ('src/projectg/lobbytask.cpp', 'CLobbyTask::OnPacket'),
            '0069eef0': ('src/projectg/golftask.cpp', 'CGolfTask::OnPacket'), '005a8360': ('src/projectg/realmyroomtask.cpp', 'CRealMyRoomTask::OnPacket'),
            '007b5a20': ('src/projectg/avatar_task.cpp', 'ntAvatarChatTask::OnPacket'), '005e0ff0': ('src/projectg/shoptask.cpp', 'CShopTask::OnPacket'),
            '006b2ee0': ('src/projectg/tutorialtask.cpp', 'CTutorialTask::OnPacket'), '0082c830': ('src/projectg/ghosttask.cpp', 'CGhostTask::OnPacket'),
            '00b1c5d0': ('src/projectg/familytask.cpp', 'CFamilyTask::OnPacket')}
    casos = {}
    for l in list(open(R + '/out/V4/pacotes_recebe_983.tsv'))[1:]:
        c = l.rstrip('\n').split('\t'); casos.setdefault(c[0], []).append((c[3], c[2]))
    print('despachante\tid\tva_caso\ttabela\tsub\testado\tva_sub\ttexto983\tleitura')
    for d, lst in sorted(casos.items()):
        if d not in desp or (len(sys.argv) > 2 and desp[d][1] != sys.argv[2]): continue
        arq, fn = desp[d]; lst = sorted(set(lst))
        for j, (va, cid) in enumerate(lst):
            fim = lst[j + 1][0] if j + 1 < len(lst) else '%08x' % (int(va, 16) + 0x2000)
            L = desmonta(va, fim)
            for n, tab in enumerate(tabelas(L)):
                ref = lado983(L, tab)
                if not any(t for _, t, _ in ref.values()): continue  # sem texto: não é sub-switch de avisos
                try: outs = ladofonte(arq, fn + '/case ' + cid, todos=True)
                except (StopIteration, IndexError): outs = None
                out = melhor(ref, outs)  # C20: switch do fonte escolhido pelos textos (antes: só o 1º, só na 1ª tabela)
                if out is None: out = (outs[0] if outs and n == 0 else None)
                lido = out is not None
                if out is None: out = {}
                for c, e, v, txt, s in compara(ref, out):
                    print('%s\t%s\t%s\t%x\t%s\t%s\t%s\t%s\t%s' % (fn, cid, va, tab[1], hex(c), e if lido else e + '(tabela %d: fonte não lido)' % (n + 1),
                          '%08x' % v if v else '-', ('%x' % txt) if txt else '-', s))
    sys.exit()
ini, fim, arq, rot = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
nth = int(sys.argv[5]) if len(sys.argv) > 5 else 1
L = desmonta(ini, fim); tabs = tabelas(L)
if len(tabs) < nth: sys.exit('sub-switch %d não achado em %s-%s' % (nth, ini, fim))
tab = tabs[nth - 1]; ref = lado983(L, tab); out = melhor(ref, ladofonte(arq, rot, todos=True)) or ladofonte(arq, rot) or {}
print('983: tabela %x (bytes %s), %d sub-códigos, desvio %d; fonte: %s, %s' % (tab[1], '%x' % tab[2] if tab[2] else '-', tab[3] + 1, tab[4], arq, rot))
for c, e, v, txt, s in compara(ref, out):
    print('%-6s %-28s %s %s %s' % (hex(c), e, '%08x' % v if v else '-', ('%x' % txt) if txt else '-', s))
