#!/usr/bin/env python3
"""Frente C, V5 — o que o rugburn faz no exe JP 983 e o que o exe 983 tem que o rugburn toca.

Só leitura. Entradas: ref/ProjectG_983_dump.exe, map/projectg_funcs.tsv, src/ (para "o fonte tem?") e o
trecho do rugburn público (out/V5/rugburn_jp983_trecho.c; se houver um clone em build/C/v5/rugburn, o trecho
é refeito a partir dele). Saídas em out/V5/:
  patches_983.tsv   cada Patch() do ramo "JP 983": endereço, bytes antes/depois, função, veredito
  ggc_chamadas.tsv  quem chama cada função da cola do GameGuard no exe 983
  ganchos_api.tsv   cada API que o rugburn intercepta: está na tabela de importação do exe? quem chama?
  rede_983.tsv      URLs, IPs e porta do login embutidos no exe 983, quem usa e se o nosso fonte tem igual
  constantes.tsv    constantes de partida (login, PANGYA_ARG, mutex, nome do GameGuard): 983 × nosso fonte
uso: python3 tools/v5/rb.py [pasta_do_clone_do_rugburn]
"""
import os, re, struct, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'v4'))
from lib import PE, Funcs, cs, R

OUT = os.path.join(R, 'out', 'V5')
TRECHO = os.path.join(OUT, 'rugburn_jp983_trecho.c')
CLONE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(R, 'build', 'C', 'v5', 'rugburn')
FIM_JOGO = 0xc3c18f          # fim do código do jogo (fronteiras.tsv); depois vem GameGuard/CRT
GG_LIB = (0xc3d7a0, 0xc62000)  # NPGameLib estática (jp983/NOTES)

pe = PE(); F = Funcs(); md = cs()
_, V0, _, RO0, RS0 = pe.secs[0]
SEC = pe.d[RO0:RO0 + RS0]


def nome(va):
    f = F.at(va)
    if not f:
        return ('', '', '')
    return ('%08x' % f[0], (f[3] or f[4]), f[2].split('/')[-1])


def refs(va, so_codigo=True):
    """endereços onde o valor de 4 bytes `va` aparece (operando absoluto)."""
    pat = struct.pack('<I', va); out = []; i = SEC.find(pat)
    lim = (GG_LIB[1] - V0) if so_codigo else len(SEC)
    while 0 <= i < lim:
        out.append(V0 + i); i = SEC.find(pat, i + 1)
    return out


def chamadas(va):
    out = []
    for m in re.finditer(b'[\xe8\xe9]', SEC[:GG_LIB[1] - V0]):
        i = m.start()
        if (V0 + i + 5 + struct.unpack_from('<i', SEC, i + 1)[0]) & 0xffffffff == va:
            out.append(V0 + i)
    return out


def limites(f0, tam):
    """endereços de início de instrução dentro da função (desmonte linear a partir do começo)."""
    return {i.address: i for i in md.disasm(pe.bytes(f0, tam), f0)}


def escreve(nome_arq, cab, linhas):
    with open(os.path.join(OUT, nome_arq), 'w') as o:
        o.write('\t'.join(cab) + '\n')
        for l in linhas:
            o.write('\t'.join(str(x) for x in l) + '\n')
    print('%-20s %d linhas' % (nome_arq, len(linhas)))


# ---------------------------------------------------------------- 1. patches do ramo JP 983
def trecho_rugburn():
    src = os.path.join(CLONE, 'src', 'hooks', 'comctl32', 'dynamic_patch.c')
    if os.path.exists(src):
        t = open(src, encoding='latin1').read()
        m = re.search(r'static void PatchGG_JP\(\) \{.*?\n\}\n', t, re.S)
        commit = os.popen('git -C %s log -1 --format=%%H 2>/dev/null' % CLONE).read().strip()
        with open(TRECHO, 'w') as o:
            o.write('// Trecho de github.com/pangbox/rugburn, src/hooks/comctl32/dynamic_patch.c, commit %s\n'
                    '// Copiado só para conferência (frente C, V5). Aviso da licença ISC do original:\n'
                    '// Copyright 2018-2024 John Chadwick <john@jchw.io>\n'
                    '// Permission to use, copy, modify, and/or distribute this software for any purpose with or without\n'
                    '// fee is hereby granted, provided that the above copyright notice and this permission notice appear\n'
                    '// in all copies. THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD\n'
                    '// TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL\n'
                    '// THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES\n'
                    '// WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE\n'
                    '// OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.\n' % commit)
            o.write(m.group(0))
    return open(TRECHO, encoding='latin1').read()


def patches():
    t = trecho_rugburn()
    blocos = re.split(r'(?=compare_virtual_memory)', t)
    alvo = [b for b in blocos if '(JP 983)' in b]
    assert len(alvo) == 1, 'ramo JP 983 não achado'
    b = alvo[0]
    ca, cv = re.match(r'compare_virtual_memory\((0x[0-9A-Fa-f]+), (0x[0-9A-Fa-f]+)\)', b).groups()
    ca, cv = int(ca, 16), int(cv, 16)
    out = [('checagem', '%08x' % ca, 4, '%08x' % pe.u32(ca), '%08x' % cv, *nome(ca), 0, 'sim',
            'bate' if pe.u32(ca) == cv else 'NAO BATE', 'rugburn reconhece o exe 983 pelos 4 primeiros bytes de _GGC_Init')]
    # onde as funções da cola estão de verdade (mapa)
    cola = {f[0]: (f[3] or f[4]) for f in F.l if f[2].endswith('ggc_wrapper.cpp')}
    for a, s, n in re.findall(r'Patch\(\(LPVOID\)(0x[0-9A-Fa-f]+), "((?:\\x[0-9A-Fa-f]{2})+)", (\d+)\)', b):
        a = int(a, 16); novo = bytes(int(x, 16) for x in re.findall(r'\\x(..)', s)); n = int(n)
        velho = pe.bytes(a, n)
        f = F.at(a)
        if f:
            lim = limites(f[0], f[1]); ini = 'sim' if a in lim else 'NAO'
            desl = a - f[0]
        else:
            ini = '-'; desl = ''
        if a in cola and ini == 'sim':
            ver = 'certo'
            ef = 'entrada de %s vira `ret`' % cola[a] if novo[:1] == b'\xc3' else 'entrada de %s vira nop' % cola[a]
        elif f:
            ver = 'ENDERECO ERRADO'
            ef = 'cai no meio de %s (+0x%x, %s início de instrução): estraga o código se for executado' % (
                (f[3] or f[4])[:40], desl, 'é' if ini == 'sim' else 'não é')
        else:
            ver = 'ENDERECO ERRADO'
            ef = 'cai fora de função (dados): ver tabela de switch de GGC_Helper::StackError'
        out.append(('patch', '%08x' % a, n, velho.hex(), novo.hex(), *nome(a), desl, ini, ver, ef))
    escreve('patches_983.tsv', ['tipo', 'va983', 'n', 'bytes_983', 'bytes_rugburn', 'funcao_va', 'funcao', 'unidade',
                                'desl', 'inicio_de_instrucao', 'veredito', 'efeito'], out)
    return out, cola


def tabela_stackerror(pat):
    """para os patches que caem em dados: que índice da tabela de bytes do switch de StackError é."""
    # movzx edx, byte [edx + T]; jmp [edx*4 + J]   com edx = erro - 0x6e
    f = [x for x in F.l if 'StackError@GGC_Helper' in x[3]]
    if not f:
        return []
    f = f[0]; out = []
    ins = list(md.disasm(pe.bytes(f[0], f[1] + 4), f[0]))
    for k, i in enumerate(ins):
        m = re.match(r'edx, byte ptr \[edx \+ 0x([0-9a-f]+)\]', i.op_str)
        if i.mnemonic == 'movzx' and m:
            T = int(m.group(1), 16)
            base = None
            for j in ins[max(0, k - 4):k]:
                mm = re.match(r'edx, \[eax - 0x([0-9a-f]+)\]', j.op_str)
                if j.mnemonic == 'lea' and mm:
                    base = int(mm.group(1), 16)
            for p in pat:
                a = int(p[1], 16)
                if p[0] == 'patch' and not F.at(a) and T <= a < T + 0x100 and base is not None:
                    out.append((p[1], '%08x' % T, a - T, base + a - T, pe.bytes(a, 1).hex(), p[4]))
    return out


# ---------------------------------------------------------------- 2. quem chama a cola do GameGuard
def ggc(cola):
    out = []
    extras = {f[0]: (f[3] or f[4]) for f in F.l
              if f[2].endswith('ggc_helper.cpp') and ('GGC_GetHelper' in f[3] or f[3].endswith('GGC_Helper::GGC_Helper')
                                                     or 'StackError@GGC_Helper' in f[3])}
    for a, n in sorted({**cola, **extras}.items()):
        cs_ = chamadas(a)
        for c in cs_:
            out.append(('%08x' % a, n, '%08x' % c, *nome(c)))
        if not cs_:
            out.append(('%08x' % a, n, '', '', '(sem chamada direta)', ''))
    escreve('ggc_chamadas.tsv', ['va983', 'funcao', 'chamada_em', 'quem_va', 'quem', 'unidade'], out)
    return out


# ---------------------------------------------------------------- 3. APIs que o rugburn intercepta
GANCHOS = [  # (dll, função, arquivo do rugburn, para quê)
    ('kernel32.dll', 'CreateProcessA', 'kernel32/inject.c', 'finge que GameGuard.des abriu (devolve um mutex como processo)'),
    ('kernel32.dll', 'GetExitCodeProcess', 'kernel32/inject.c', 'devolve 0x755 (NPGAMEMON_SUCCESS) para o processo falso'),
    ('kernel32.dll', 'GetStartupInfoA', 'comctl32/dynamic_patch.c', 'gatilho: 1ª chamada vinda do exe aplica o patch do GG + PatchAddress'),
    ('kernel32.dll', 'GetStartupInfoW', 'comctl32/dynamic_patch.c', 'idem'),
    ('comctl32.dll', 'InitCommonControlsEx', 'comctl32/dynamic_patch.c', 'idem (2º gatilho)'),
    ('user32.dll', 'CreateWindowExA', 'user32/window.c', 'tira WS_EX_TOPMOST de toda janela'),
    ('ws2_32.dll', 'connect', 'ws2_32/redir.c', 'PortRewrites: troca destino pela porta (FromPort -> ToAddr:ToPort)'),
    ('wininet.dll', 'InternetOpenUrlA', 'wininet/netredir.c', 'UrlRewrites (regex) na URL'),
    ('wininet.dll', 'InternetConnectA', 'wininet/netredir.c', 'UrlRewrites (guarda host/porta para o pedido)'),
    ('wininet.dll', 'HttpOpenRequestA', 'wininet/netredir.c', 'UrlRewrites (monta a URL e reabre a conexão se mudar)'),
    ('wininet.dll', 'HttpSendRequestA', 'wininet/netredir.c', 'acompanha o pedido reescrito'),
    ('wininet.dll', 'HttpSendRequestExA', 'wininet/netredir.c', 'idem'),
    ('wininet.dll', 'HttpEndRequestA', 'wininet/netredir.c', 'idem'),
    ('wininet.dll', 'HttpAddRequestHeadersA', 'wininet/netredir.c', 'idem'),
    ('wininet.dll', 'HttpQueryInfoA', 'wininet/netredir.c', 'idem'),
    ('wininet.dll', 'InternetQueryDataAvailable', 'wininet/netredir.c', 'idem'),
    ('wininet.dll', 'InternetReadFile', 'wininet/netredir.c', 'idem'),
    ('wininet.dll', 'InternetWriteFile', 'wininet/netredir.c', 'idem'),
    ('wininet.dll', 'InternetCloseHandle', 'wininet/netredir.c', 'idem'),
    ('ole32.dll', 'CoCreateInstance', 'ole32/web_browser.c', 'UrlRewrites no IWebBrowser2::Navigate (páginas dentro do jogo)'),
    ('ole32.dll', 'CoGetClassObject', 'ole32/web_browser.c', 'UrlRewrites no IDispatch::Invoke do WebBrowser'),
    ('msvcr100.dll', '_stricmp', 'msvcr100/msvcr100.c', 'só sob Wine com defeito no _stricmp (locale japonês); no Windows não instala'),
]


def importacoes(path=None):
    p = PE(path) if path else pe
    d = p.d; o = struct.unpack_from('<I', d, 0x3c)[0] + 24
    irva = struct.unpack_from('<I', d, o + 96 + 8)[0]
    out = {}; va = p.base + irva
    while True:
        b = p.bytes(va, 20)
        if len(b) < 20:
            break
        oft, _, _, nm, ft = struct.unpack('<IIIII', b)
        if not nm and not ft:
            break
        dll = p.cstr(p.base + nm).decode().lower(); k = 0
        while True:
            v = p.u32(p.base + (oft or ft) + 4 * k)
            if not v:
                break
            n = ('#%d' % (v & 0xffff)) if v & 0x80000000 else p.cstr(p.base + v + 2).decode()
            out[(dll, n)] = p.base + ft + 4 * k; k += 1
        va += 20
    return out


def ganchos():
    im = importacoes(); out = []
    for dll, fn, arq, pq in GANCHOS:
        s = im.get((dll, fn))
        if s is None:
            out.append((dll, fn, arq, 'nao importa', '', 0, 0, '', pq)); continue
        rs = refs(s)
        jogo = [r for r in rs if r < FIM_JOGO]; lib = [r for r in rs if r >= FIM_JOGO]
        quem = []
        for r in jogo:
            n = nome(r); q = (n[1][:40] + ' [' + n[2] + ']') if n[0] else '%08x' % r
            if q not in quem:
                quem.append(q)
        out.append((dll, fn, arq, 'importa', '%08x' % s, len(jogo), len(lib), '; '.join(quem[:6]), pq))
    escreve('ganchos_api.tsv', ['dll', 'api', 'arquivo_rugburn', 'exe_983', 'iat', 'usos_jogo', 'usos_gg_crt',
                                'quem_usa_no_jogo', 'para_que'], out)
    ij = sorted(n for (d, n) in im if d == 'ijl15.dll')
    wr = importacoes(os.path.join(R, 'ref', 'wangreal_983.dll'))
    return out, ij, sorted(n for (d, n) in wr if d == 'ijl15.dll')


# ---------------------------------------------------------------- 4. rede e constantes embutidas
def fonte():
    b = []
    for base in ('src', 'include'):
        for dp, dn, fn in os.walk(os.path.join(R, base)):
            for f in fn:
                if f.endswith(('.cpp', '.h', '.inl', '.c')):
                    b.append((os.path.relpath(os.path.join(dp, f), R), open(os.path.join(dp, f), 'rb').read()))
    return b


def no_fonte(SRC, s):
    return [p for p, t in SRC if s in t]


def va_de(off):
    for n, v, sz, ro, rs in pe.secs:
        if ro <= off < ro + rs:
            return v + off - ro
    return None


def rede(SRC):
    out = []; visto = set()
    for tipo, pat in (('url', rb'https?://[\x21-\x7e]{3,120}'), ('ip', rb'(?<![\d.])\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?![\d.])')):
        for m in re.finditer(pat, pe.d):
            va = va_de(m.start())
            if va is None or not (FIM_JOGO <= va < 0xf32000) or va in visto:
                continue
            if tipo == 'ip' and (pe.bytes(va - 1, 1) != b'\0' or pe.bytes(va + len(m.group()), 1) != b'\0'):
                continue      # só ip que é a string inteira
            visto.add(va)
            rs = refs(va, so_codigo=False)
            cod = [r for r in rs if r < FIM_JOGO]; dad = [r for r in rs if r >= GG_LIB[1]]
            quem = []
            for r in cod:
                n = nome(r); q = (n[1][:45] + ' [' + n[2] + ']') if n[0] else '%08x' % r
                if q not in quem:
                    quem.append(q)
            for r in dad:
                quem.append('dado %08x' % r)
            onde = no_fonte(SRC, m.group())
            # regra de exemplo do rugburn.json (casamento inteiro): http://[a-zA-Z0-9:.]+/(.*)
            casa = '-' if tipo == 'ip' else ('sim' if re.fullmatch(rb'http://[a-zA-Z0-9:.]+/(.*)', m.group()) else 'NAO')
            out.append((tipo, '%08x' % va, m.group().decode('latin1'), len(cod), len(dad), '; '.join(quem[:4]),
                        'sim' if onde else 'NAO', ';'.join(onde[:3]), casa))
    escreve('rede_983.tsv', ['tipo', 'va983', 'texto', 'refs_codigo', 'refs_dado', 'quem_usa', 'nosso_fonte_tem', 'onde',
                             'regra_exemplo_casa'], out)
    return out


def constantes(SRC):
    out = []

    def lin(o_que, v983, onde983, nosso, onde_nosso):
        out.append((o_que, v983, onde983, nosso, onde_nosso, 'igual' if v983 == nosso else 'DIFERE'))

    def rx(arq, pat):
        t = dict(SRC).get(arq, b'').decode('latin1')
        m = re.search(pat, t)
        return m.group(1) if m else '(não achado)'
    # login: struct { const char* ip; int porta[2]; } lida por LoginUnit::Connect
    g = None
    for f in F.l:
        if f[2].endswith('loginunit.cpp'):
            for i in md.disasm(pe.bytes(f[0], f[1]), f[0]):
                m = re.match(r'ecx, dword ptr \[0x([0-9a-f]+)\]', i.op_str)
                if i.mnemonic == 'mov' and m and pe.u32(int(m.group(1), 16)) and 0xc3c000 < pe.u32(int(m.group(1), 16)) < 0xf32000:
                    s = pe.cstr(pe.u32(int(m.group(1), 16)))
                    if re.fullmatch(rb'[\d.]+', s):
                        g = (int(m.group(1), 16), s.decode(), f)
    if g:
        a, ip, f = g
        lin('login: endereço', ip, 'global %08x, lido em %08x %s' % (a, f[0], (f[3] or f[4])[:30]),
            rx('src/projectg/loginunit.cpp', r'LSIP_ADDRESS\[\]\s*=\s*\{\s*"([^"]+)"'), 'src/projectg/loginunit.cpp LSIP_ADDRESS')
        p1, p2 = pe.u32(a + 4), pe.u32(a + 8)
        lin('login: portas (sorteia 1 de 2)', '%d, %d' % (p1, p2), 'global %08x' % (a + 4),
            rx('src/projectg/loginunit.cpp', r'LOGIN_PORT_LIST\[\]\s*=\s*\{\s*([^}]+?)\s*\}'), 'src/projectg/loginunit.cpp LOGIN_PORT_LIST')
    # nome do jogo no GameGuard
    for f in F.l:
        if '_GGC_Init' in f[3]:
            for i in md.disasm(pe.bytes(f[0], f[1]), f[0]):
                m = re.match(r'0x([0-9a-f]+)$', i.op_str)
                if i.mnemonic == 'push' and m and 0xc3c000 < int(m.group(1), 16) < 0xf32000:
                    lin('GameGuard: nome do jogo', pe.cstr(int(m.group(1), 16)).decode(), '%08x _GGC_Init' % f[0],
                        rx('src/projectg/ggc_wrapper.cpp', r'new CNPGameLib\("([^"]+)"\)'), 'src/projectg/ggc_wrapper.cpp')
    # PANGYA_ARG e mutex
    for o_que, pat, arq in (('PANGYA_ARG: guid esperado (WinMain)', rb'\{E69B65A2-[0-9A-Fa-f-]+\}', 'src/projectg/winmain.cpp'),
                            ('mutex de instância única', rb'\{071784A2-[0-9A-Fa-f-]+\}', 'src/projectg/winmain.cpp')):
        m = re.search(pat, pe.d); va = va_de(m.start())
        rs = [r for r in refs(va) if r < FIM_JOGO]
        onde = no_fonte(SRC, m.group())
        lin(o_que, m.group().decode(), '; '.join('%08x %s' % (r, nome(r)[1][:30]) for r in rs),
            m.group().decode() if onde else '(não achado)', ';'.join(onde[:2]) or arq)
    for s in (b'PANGYA_ARG',):
        onde = no_fonte(SRC, s)
        rs = []
        for m in re.finditer(s + b'\0', pe.d):
            va = va_de(m.start())
            if va:
                rs += [nome(r)[1][:30] + ' [' + nome(r)[2] + ']' for r in refs(va) if r < FIM_JOGO]
        # C79: a função do 983 que lê a variável tem par no map/projectg.tsv e esse nome está num arquivo do fonte que lê?
        vas = sorted(set(nome(r)[0] for m in re.finditer(s + b'\0', pe.d) if va_de(m.start())
                         for r in refs(va_de(m.start())) if r < FIM_JOGO))
        pares = [l.split('\t')[0] for mp in ('projectg.tsv', 'pkt_c.tsv') for l in open(R + '/map/' + mp, encoding='latin1')
                 if '\t' in l and l.split('\t')[1].strip().lower() in vas]
        base = [re.sub(r'^[?_]|@.*$', '', n) for n in pares]
        ok = any(b and re.search(rb'\b' + b.encode() + rb'\b', dict(SRC).get(a, b'')) for b in base for a in onde)
        out.append(('quem lê a variável PANGYA_ARG', '; '.join(sorted(set(rs))), ', '.join(pares),
                    '; '.join(onde) or '(ninguém)', '', 'igual' if ok else 'DIFERE'))
    escreve('constantes.tsv', ['o_que', 'valor_983', 'onde_983', 'nosso_fonte', 'onde_nosso', 'veredito'], out)
    return out


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    pat, cola = patches()
    tb = tabela_stackerror(pat)
    escreve('patches_em_dados.tsv', ['va983', 'tabela', 'indice', 'codigo_de_erro_gg', 'byte_983', 'byte_rugburn'], tb)
    ggc(cola)
    g, ij, ijw = ganchos()
    SRC = fonte()
    r = rede(SRC)
    c = constantes(SRC)
    certos = sum(1 for p in pat if p[0] == 'patch' and p[10] == 'certo')
    with open(os.path.join(OUT, 'resumo.txt'), 'w') as o:
        o.write('patches do ramo JP 983: %d (certos %d, endereço errado %d); checagem %s\n' % (
            len(pat) - 1, certos, len(pat) - 1 - certos, pat[0][10]))
        o.write('ijl15.dll: exe importa %s; wangreal.dll importa %s\n' % (ij, ijw or 'nada'))
        o.write('APIs interceptadas: %d; importadas pelo exe: %d; usadas pelo código do jogo: %d\n' % (
            len(g), sum(1 for x in g if x[3] == 'importa'), sum(1 for x in g if x[5])))
        o.write('rede: %d urls, %d ips; fora do nosso fonte: %d\n' % (
            sum(1 for x in r if x[0] == 'url'), sum(1 for x in r if x[0] == 'ip'), sum(1 for x in r if x[6] == 'NAO')))
        o.write('urls que a regra de exemplo (só http://host/...) NÃO pega: %d (https: %d)\n' % (
            sum(1 for x in r if x[8] == 'NAO'), sum(1 for x in r if x[2].startswith('https'))))
        o.write('constantes: %d; diferem do nosso fonte: %d\n' % (len(c), sum(1 for x in c if x[5] == 'DIFERE')))
    print(open(os.path.join(OUT, 'resumo.txt')).read())
