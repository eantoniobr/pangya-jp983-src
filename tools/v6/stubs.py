#!/usr/bin/env python3
"""F4 (frente C, C-F4.3): stubs para os símbolos que ainda não têm corpo no fonte (out/F4/link/nao_resolvidos.tsv).

Gera build/C/f4/stubs/stubs983.cpp (+ .obj com o cl do VS2010) com UM stub por símbolo, ligado ao nome decorado por
`/alternatename` (pragma do linker). O /alternatename só vale enquanto o símbolo real NÃO existe: quando A/B escreverem o
corpo, o real ganha sozinho — o stub nunca dá LNK2005 e não precisa ser apagado à mão.

Função: o stub chama jp983_falta(nome, va983, fatal): grava a linha em jp983_stubs.log (pasta do exe) e
  - padrão: MessageBox com o nome decorado e a VA do 983 e ExitProcess(983) — o testador vê QUAL função falta;
  - JP983_STUB=continuar no ambiente: volta e o stub devolve 0 (construtor devolve this; float/double: fldz) e limpa a
    pilha certa (ret N pela convenção e pelos parâmetros do undname). "fatal" = não dá para voltar com segurança
    (devolve classe por valor ou referência, ou parâmetro por valor de tamanho desconhecido em convenção em que o chamado limpa a pilha):
    esses param sempre.
Dado: armazenamento próprio (alinhado a 16) com o valor inicial do 983 (o dump é de antes do main: .data/.rdata de
  carga) quando há VA (coluna va983, sufixo _xxxxxx do nome, ou o comentário `// 00xxxxxx` do extern no fonte).
  Símbolos com a MESMA VA no 983 partilham o armazenamento (ex.: 3 nomes para 00f02340). std::wstring const: construída
  com o texto achado no inicializador do 983 (push L"..." / mov ecx, global). Ponteiros: nulos (endereço do 983 não vale);
  const char* do 983: a cadeia apontada.
Saída: build/C/f4/stubs/stubs983.{cpp,obj,log}, out/F4/stubs.tsv (um por símbolo) e out/F4/stubs_resumo.txt.
Uso: make f4-stubs  (= python3 tools/v6/stubs.py; ~15 s; lê out/F4/link/nao_resolvidos.tsv do último make f4-link)
"""
import os, sys, re, struct, subprocess, collections
R = '/root/jp983src'
VS = os.environ.get('VS', '/root/kr839/local/vs2010')
sys.path.insert(0, R + '/tools/v6')
import f4cfg
B = f4cfg.B4 + '/stubs'      # C94 (C-ROBO): build/C/f4 ou F4_BUILD
OUT = f4cfg.O4
from pe import PE

CONV = ('__thiscall', '__cdecl', '__stdcall', '__fastcall')
ESC4 = {'bool', 'char', 'signed char', 'unsigned char', 'short', 'unsigned short', 'int', 'unsigned int', 'long',
        'unsigned long', 'float', 'wchar_t', '__int8', 'unsigned __int8', '__int16', 'unsigned __int16', 'unsigned'}
ESC8 = {'double', '__int64', 'unsigned __int64', 'long double'}
# classes passadas por valor (sizeof no VC10 /MD release; conferidos nos asserts da C / cabeçalhos)
VALOR = {'class WVector': 0xc, 'class WMatrix': 0x40, 'class WRect': 0x10, 'struct _WRECT': 0x10, 'struct RFVector2': 8,
         'struct RFRect': 0x10, 'class WPoint': 8, 'struct _WPOINT': 8,
         'class std::basic_string<char,struct std::char_traits<char>,class std::allocator<char> >': 0x1c,
         'class std::basic_string<wchar_t,struct std::char_traits<wchar_t>,class std::allocator<wchar_t> >': 0x1c}
# tamanho dos dados por código de tipo no nome decorado (depois de @@3 / @@2): o que não está aqui fica com 0x40
TAM = {'_N': 4, 'H': 4, 'I': 4, 'K': 4, 'J': 4, 'M': 4, 'N': 8, 'VWMatrix@@': 0x40, 'VWVector@@': 0xc, 'VWRect@@': 0x10,
       'U_WRECT@@': 0x10, 'URFRect@@': 0x10, 'URFVector2@@': 8, 'UsLobbyRect983@@': 0x10, 'USize@CUiFrameSetManager@@': 8}


def vs(*a, cwd=None):
    p = subprocess.run([R + '/tools/vs.sh'] + list(a), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd,
                       env=dict(os.environ, VS=VS))
    return p.returncode, p.stdout.decode('latin1').replace('\r', '')


def undname(nomes):
    """nome decorado -> undname (cache em build/C/f4/stubs/undname.tsv; o undname do Wine leva ~30 s para 500)"""
    cache, r = B + '/undname.tsv', {}
    if not os.path.exists(cache) and os.path.exists(f4cfg.C4 + '/stubs/undname.tsv'):  # C94: rodada nova parte do cache da C
        os.makedirs(B, exist_ok=True); open(cache, 'wb').write(open(f4cfg.C4 + '/stubs/undname.tsv', 'rb').read())
    if os.path.exists(cache):
        for l in open(cache, encoding='latin1'):
            a, _, b = l.rstrip('\n').partition('\t'); r[a] = b
    # namespace anônimo (?A0x...): o undname do VS2010 não decora; troca pelo nome `anon` só para ler a assinatura
    anon = lambda x: re.sub(r'\?A0x[0-9a-f]+@', 'anon@', x)
    pede = sorted({anon(x) for x in nomes} - set(r))
    for i in range(0, len(pede), 60):
        _, o = vs('undname', *pede[i:i + 60])
        for a, b in re.findall(r'Undecoration of :- "([^"]*)"\nis :- "([^"]*)"', o): r[a] = b
    with open(cache, 'w', encoding='latin1') as g:
        for a in sorted(r): g.write('%s\t%s\n' % (a, r[a]))
    return {x: r.get(anon(x), x) for x in nomes}


def topo(s, ch):
    """posições de `ch` fora de <> e ()"""
    d, r = 0, []
    for i, c in enumerate(s):
        if d == 0 and s.startswith(ch, i): r.append(i)
        if c in '<(': d += 1
        elif c in '>)': d -= 1
    return r


def tam_param(t):
    t = re.sub(r'\b(const|volatile)\b', '', t).strip()
    t = re.sub(r'\s+', ' ', t)
    if t.endswith('*') or t.endswith('&') or '(__' in t or t.endswith('* const'): return 4
    if t in ESC4 or t.startswith('enum '): return 4
    if t in ESC8: return 8
    return VALOR.get(t)


def assinatura(u):
    """(convenção, bytes que o chamado tira da pilha ou None, retorno: 'void'|'int'|'fpu'|'i64'|'struct'|'this', varargs)"""
    cv = [(i, c) for c in CONV for i in topo(u, ' ' + c + ' ')]
    if not cv: return None
    i, c = min(cv)
    antes, depois = u[:i], u[i + len(c) + 2:]
    ab = topo(depois, '(')
    if not ab: return None
    nome, pars = depois[:ab[0]], depois[ab[0] + 1:]
    pars = pars[:topo(pars, ')')[0]] if topo(pars, ')') else pars
    antes = re.sub(r'^\s*(public|protected|private):', '', antes).strip()
    antes = re.sub(r'^(static|virtual)\b', '', antes).strip()
    simples = nome.split('::')[-1]
    classe = nome.split('::')[-2] if '::' in nome else ''
    if not antes:  # construtor/destrutor
        ret = 'this' if simples.split('<')[0] == classe.split('<')[0] else 'void'
    else:
        a = re.sub(r'\b(const|volatile)\b', '', antes).strip()
        if a == 'void': ret = 'void'
        elif a.endswith('&'): ret = 'ref'  # referência nula = crash sem aviso: fatal
        elif a.endswith('*') or a in ESC4 - {'float'} or a.startswith('enum '): ret = 'int'
        elif a in ('float', 'double', 'long double'): ret = 'fpu'
        elif a in ('__int64', 'unsigned __int64'): ret = 'i64'
        else: ret = 'struct'
    lp = [x.strip() for x in re.split(r'\x00', ''.join('\x00' if j in topo(pars, ',') else ch for j, ch in enumerate(pars)))]
    va = '...' in lp
    lp = [x for x in lp if x not in ('void', '...', '')]
    tams = [tam_param(x) for x in lp]
    pilha = 0
    if c == '__cdecl': pilha = 0
    else:
        regs = 2 if c == '__fastcall' else 0
        for t, x in zip(tams, lp):
            if t is None: pilha = None; break
            # fastcall: os 2 primeiros inteiros/ponteiros de até 4 bytes vão em ecx/edx; float e classe por valor, na pilha
            reg = t == 4 and (x.rstrip().endswith(('*', '&', '* const')) or not x.startswith(('class ', 'struct ', 'union ')))
            if regs and reg and re.sub(r'\b(const|volatile)\b', '', x).strip() != 'float': regs -= 1; continue
            pilha += t
        if pilha is not None and ret == 'struct': pilha += 4  # ponteiro escondido do retorno
    return c, pilha, ret, va


def va_do_fonte():
    """extern ... NOME; // 00xxxxxx  (em include/ e src/)"""
    r = {}
    rx = re.compile(r'^\s*(?:extern\s+|static\s+)[^;/]*?\b(\w+)\s*;\s*//\s*(00[0-9a-f]{6})\b')
    for raiz in ('include', 'src'):
        for d, _, fs in os.walk(R + '/' + raiz):
            for f in fs:
                if not f.endswith(('.h', '.cpp')): continue
                try:
                    for l in open(os.path.join(d, f), encoding='utf-8', errors='replace'):
                        m = rx.match(l)
                        if m: r.setdefault(m.group(1), int(m.group(2), 16))
                except OSError: pass
    return r


def alternates_existentes(nomes):
    """/alternatename:<s>=<T> que JÁ estão nos .obj do link (ex.: os `__pg_c_*` e as visões da A): o linker usa o primeiro
    que vê, então o stub tem de responder também por <T> (encadeado: /alternatename:<T>=stub)"""
    r = {}
    alvo = set(nomes)
    for l in open(f4cfg.V6 + '/objs.tsv'):
        c = l.rstrip('\n').split('\t')
        if len(c) < 2 or not c[1].endswith('.obj'): continue
        o = c[1] if c[1].startswith('/') else R + '/' + c[1]
        try: d = open(o, 'rb').read()
        except OSError: continue
        for m in re.finditer(rb'/alternatename:([^= "\0]+)=([^ "\0]+)', d):
            a = m.group(1).decode('latin1')
            if a in alvo: r.setdefault(a, (m.group(2).decode('latin1'), os.path.basename(o), o))
    # C98: alvo já DEFINIDO num .obj do link (ex.: CMouseCursor::InArea na pg-a170) não ganha stub no stubs983a (LNK2005)
    defs = {}
    for a, (t, _, o) in r.items():
        defs.setdefault(t, set()).add(o)
    definidos = set()
    for l in open(f4cfg.V6 + '/objs.tsv'):
        c = l.rstrip('\n').split('\t')
        if len(c) < 2 or not c[1].endswith('.obj'): continue
        o = c[1] if c[1].startswith('/') else R + '/' + c[1]
        try: d = open(o, 'rb').read()
        except OSError: continue
        ts = [t for t in defs if t not in definidos and t.encode('latin1') in d]
        if not ts: continue
        nm = subprocess.run(['nm', o], capture_output=True, text=True, errors='replace').stdout
        for t in ts:
            if re.search(r' [TDBR] ' + re.escape(t) + r'$', nm, re.M): definidos.add(t)
    return {a: v[:2] for a, v in r.items() if v[0] not in definidos}


def wstring_983(pe, va):
    """texto do push L"..." logo antes do `mov ecx, va` do inicializador do 983"""
    d, pat = pe.d, b'\xb9' + struct.pack('<I', va)
    i = d.find(pat)
    while i >= 0:
        w = d[i - 12:i]
        for k in range(len(w) - 4):
            if w[k] == 0x68:
                o = pe.off(struct.unpack_from('<I', w, k + 1)[0] - pe.base)
                if o:
                    e = o
                    while d[e:e + 2] != b'\0\0' and e - o < 200: e += 2
                    try:
                        s = d[o:e].decode('utf-16le')
                        if s and s.isprintable(): return s
                    except UnicodeDecodeError: pass
        i = d.find(pat, i + 1)
    return None


def ret_983(pe, va):
    """bytes que a função do 983 tira da pilha: o primeiro `ret`/`ret N` (capstone) nos primeiros 4 kB"""
    from capstone import Cs, CS_ARCH_X86, CS_MODE_32
    o = pe.off(va - pe.base)
    for i in Cs(CS_ARCH_X86, CS_MODE_32).disasm(pe.d[o:o + 0x1000], va):
        if i.mnemonic == 'ret': return int(i.op_str, 16) if i.op_str else 0
        if i.mnemonic == 'int3': return None
    return None


def cstr(s):
    return '"' + ''.join(c if 32 <= ord(c) < 127 and c not in '"\\' else '\\x%02x""' % ord(c) for c in s) + '"'


def main():
    os.makedirs(B, exist_ok=True)
    linhas = [l.rstrip('\n').split('\t') for l in open(OUT + '/link/nao_resolvidos.tsv', encoding='utf-8')][1:]
    # o literal "" só aparece no link SEM /FORCE (a NPGameLib.lib entra por outro membro): sempre com stub
    if not any(c[0] == '??_C@_00A@?$AA@' for c in linhas):
        linhas.append(['??_C@_00A@?$AA@', 'NAO', 'lib', '-', 'NPGameLib.lib(0558_NPGameLib.obj)'])
    pe = PE(R + '/ref/ProjectG_983_dump.exe')
    und = undname([c[0] for c in linhas if c[0].startswith('?')])
    vfonte = va_do_fonte()
    funcs, dados, fora, literais = [], [], [], []
    for c in linhas:
        s, frentes, va, quem = c[0], c[2], c[3], c[4]
        if not s.startswith('?'): fora.append(c); continue
        if s == '??_C@_00A@?$AA@':  # literal "" (a NPGameLib.lib do VC7.1 conta com o COMDAT; nós compilamos com /GF-)
            literais.append(c); continue
        u = und.get(s, s)
        sig = assinatura(u) if '(' in u and not re.match(r'^[^(]*\(__\w+ ?\*', u) else None
        if sig and sig[1] is None and sig[2] not in ('struct', 'ref') and va not in ('-', ''):
            # (C-F4.4) parâmetro de tamanho desconhecido (classe por valor, ex. std::tr1::function): a pilha pelo `ret N` do
            # 983. O stub não chama o destrutor do parâmetro (só vaza; o RegisterCreator983 sobe pelo .CRT$XCU antes do WinMain)
            n = ret_983(pe, int(va, 16))
            if n is not None: sig = (sig[0], n, sig[2], sig[3])
        if sig: funcs.append((s, u, sig, va, frentes, quem))
        else: dados.append((s, u, va, frentes, quem))
    # ---- dados: VA, tamanho, valor inicial, grupos por VA
    grupos = collections.OrderedDict()
    info = {}
    for s, u, va, fr, q in dados:
        m = re.match(r'\?(\w+)@', s)
        if not m: print('dado sem nome simples:', s, u); continue
        nm = m.group(1)
        v = int(va, 16) if va != '-' else None
        if v is None:
            m = re.search(r'_([0-9a-f]{6})$', nm)
            if m: v = int(m.group(1), 16)
        if v is None and nm in vfonte: v = vfonte[nm]
        tipo = re.search(r'@@[0-9]([^@]*@@|_N|[A-Z])', s)
        cod = tipo.group(1) if tipo else '?'
        ws = 'basic_string<wchar_t' in u
        ptr = s[s.index('@@') + 3:].startswith(('PA', 'PB', 'QA', 'QB')) if '@@' in s else False
        cptr = 'char const *' in u and u.startswith(('char const *', 'public: static char const *'))
        n = TAM.get(cod, 4 if ptr else 0x40)
        info[s] = dict(nm=nm, va=v, ws=ws, ptr=ptr, cptr=cptr, n=n, fr=fr, q=q, u=u)
        chave = ('va', v) if v is not None else ('nome', s)
        grupos.setdefault(chave, []).append(s)
    alt = alternates_existentes([c[0] for c in linhas])
    corpo_d, tab = [], []
    for i, c in enumerate(literais):
        corpo_d.append('extern "C" const char jp983_lit%d[1] = {0};' % i)
        corpo_d.append('#pragma comment(linker, "/alternatename:%s=_jp983_lit%d")' % (c[0], i))
        tab.append((c[0], 'dado', '-', '-', '-', '-', 'jp983_lit%d; literal "" (COMDAT do VC7.1 que a NPGameLib.lib cita)' % i, c[2], c[4]))

    asm = collections.OrderedDict()  # alvo do alternatename alheio -> stub (o link.exe NÃO encadeia alternatename)

    def liga(s, nome_c, dst):
        dst.append('#pragma comment(linker, "/alternatename:%s=_%s")' % (s, nome_c))
        if s in alt:
            asm.setdefault(alt[s][0], nome_c)
            return '; o %s já liga o nome a %s (alternatename): o alvo é definido no stubs983a.asm (jmp %s)' % (
                alt[s][1], alt[s][0], asm[alt[s][0]])
        return ''
    for gi, (chave, ss) in enumerate(grupos.items()):
        ii = [info[s] for s in ss]
        v = chave[1] if chave[0] == 'va' else None
        nome_c = 'jp983_d%d' % gi
        n = max(x['n'] for x in ii)
        off = pe.off(v - pe.base) if v else None
        val, nota = None, ''
        if any(x['ws'] for x in ii):
            txt = wstring_983(pe, v) if v else None
            val = ('ws', txt or '')
            nota = 'wstring L"%s" (inicializador do 983)' % txt if txt else 'wstring VAZIA (texto não achado)'
        elif any(x['cptr'] for x in ii) and off is not None:
            p = struct.unpack_from('<I', pe.d, off)[0]
            o2 = pe.off(p - pe.base) if p else None
            t = pe.cstr(p - pe.base) if o2 else None
            val = ('cs', t)
            nota = 'const char* -> "%s" (983 %08x)' % (t, p) if t is not None else 'const char* nulo'
        elif any(x['ptr'] for x in ii):
            p = struct.unpack_from('<I', pe.d, off)[0] if off is not None else 0
            val = ('b', b'\0' * n)
            nota = 'ponteiro nulo' + (' (no 983 começa = %08x, objeto estático do 983: o nosso fica nulo)' % p if p else '')
        else:
            bs = pe.d[off:off + n] if off is not None else b''
            if 'Identity' in ii[0]['nm'] and not bs.strip(b'\0'):
                bs = struct.pack('<16f', *[1.0 if i % 5 == 0 else 0.0 for i in range(16)]); nota = 'matriz identidade (no dump: zero, feita em tempo de execução)'
            elif ii[0]['nm'] == 'g_fullUV983':
                bs = struct.pack('<4f', 0, 0, 1, 1); nota = 'UV inteira (0,0,1,1) — sem VA no fonte; igual ao g_rectUnit983_e4296c'
            elif off is not None: nota = 'valor do 983 (%d bytes)%s' % (n, ' = zero' if not bs.strip(b'\0') else '')
            else: nota = 'zero (sem VA)'
            val = ('b', bs.ljust(n, b'\0'))
        if val[0] == 'ws':
            corpo_d.append('extern "C" const std::wstring %s = L%s;' % (nome_c, cstr(val[1])))
        elif val[0] == 'cs':
            corpo_d.append('extern "C" const char* %s = %s;' % (nome_c, cstr(val[1]) if val[1] is not None else '0'))
        else:
            corpo_d.append('extern "C" __declspec(align(16)) unsigned char %s[%d] = {%s};' % (
                nome_c, len(val[1]), ','.join('0x%02x' % b for b in val[1])))
        for s in ss:
            ex = liga(s, nome_c, corpo_d)
            x = info[s]
            tab.append((s, 'dado', '-', '-', '-', '%08x' % v if v else '-', nome_c + (' (partilhado por %d)' % len(ss) if len(ss) > 1 else '')
                        + '; ' + nota + ex, x['fr'], x['q']))
    # ---- funções
    corpo_f = []
    for i, (s, u, (cv, pilha, ret, var), va, fr, q) in enumerate(funcs):
        fatal = ret in ('struct', 'ref') or pilha is None
        v = int(va, 16) if va != '-' else 0
        f = 'jp983_f%d' % i
        fim = []
        if ret == 'this': fim.append('mov eax, ecx')
        else: fim.append('xor eax, eax')
        if ret == 'i64': fim.append('xor edx, edx')
        if ret == 'fpu': fim.append('fldz')
        fim.append('ret %d' % pilha if pilha else 'ret')
        corpo_f.append('static const char %s_n[] = "%s";' % (f, s))
        corpo_f.append('extern "C" __declspec(naked) void __cdecl %s(void) { __asm {\n'
                       '\tpush ecx\n\tpush edx\n\tpush %d\n\tpush 0x%08x\n\tlea eax, %s_n\n\tpush eax\n\tcall jp983_falta\n'
                       '\tadd esp, 12\n\tpop edx\n\tpop ecx\n\t%s\n} }' % (f, 1 if fatal else 0, v, f, '\n\t'.join(fim)))
        ex = liga(s, f, corpo_f)
        tab.append((s, 'função', cv, '?' if pilha is None else str(pilha), 'fatal' if fatal else 'continua',
                    va, f + '; ret ' + ret + ('; varargs' if var else '') + '; ' + u + ex, fr, q))
    rt = open(R + '/tools/v6/f4stub/falta983.cpp', encoding='utf-8').read()
    src = ('// GERADO por tools/v6/stubs.py (make f4-stubs) a partir de out/F4/link/nao_resolvidos.tsv — não editar.\n'
           '// %d funções + %d dados (%d armazenamentos). O /alternatename só vale enquanto o símbolo real não existe.\n'
           % (len(funcs), len(dados), len(grupos)) + rt + '\n// ---- dados\n' + '\n'.join(corpo_d) + '\n\n// ---- funções\n' + '\n'.join(corpo_f) + '\n')
    open(B + '/stubs983.cpp', 'w', encoding='utf-8').write(src)
    # alvos dos alternatename alheios: rótulo público com o nome exato (MASM aceita ? @ $) que salta para o stub
    a = ['; GERADO por tools/v6/stubs.py — alvos de /alternatename que já estão nos .obj de A/B e não existem', '.386',
         '.model flat', 'option casemap:none']
    a += ['EXTERN _%s:PROC' % n for n in sorted(set(asm.values()))]
    a += ['_TEXT SEGMENT'] + ['PUBLIC %s\n%s:\n\tjmp _%s' % (t, t, n) for t, n in asm.items()] + ['_TEXT ENDS', 'END']
    open(B + '/stubs983a.asm', 'w').write('\n'.join(a) + '\n')
    aobj = B + '/stubs983a.obj'
    if os.path.exists(aobj): os.remove(aobj)
    rca, loga = vs('ml', '/nologo', '/c', '/coff', '/Fo' + aobj, B + '/stubs983a.asm')
    open(B + '/stubs983a.log', 'w').write(loga)
    obj = B + '/stubs983.obj'
    if os.path.exists(obj): os.remove(obj)
    rc, log = vs('cl', '/nologo', '/c', '/MD', '/O2', '/Gr', '/EHsc', '/W3', '/DWIN32', '/DNDEBUG', '/D_CRT_SECURE_NO_WARNINGS', '/I' + VS + '/VC10/include',
                 '/I' + VS + '/compat', '/I/root/rebang/tools/PlatformSDK-Aug2002/include', '/Fo' + obj, B + '/stubs983.cpp')
    open(B + '/stubs983.log', 'w').write(log)
    with open(OUT + '/stubs.tsv', 'w', encoding='utf-8') as g:
        g.write('simbolo\ttipo\tconvencao\tpilha\tmodo\tva983\tstub_nota\tfrentes\tquem_cita\n')
        for t in sorted(tab): g.write('\t'.join(t) + '\n')
    cf = collections.Counter(t[2] for t in tab if t[1] == 'função')
    mf = collections.Counter(t[4] for t in tab if t[1] == 'função')
    fr = collections.Counter(t[7] for t in tab)
    res = ['stubs do 1º exe (make f4-stubs): %d símbolos de out/F4/link/nao_resolvidos.tsv' % len(linhas),
           '  funções: %d (%s); modo com JP983_STUB=continuar: %s' % (len(funcs), ', '.join('%s %d' % kv for kv in cf.most_common()),
                                                                   ', '.join('%s %d' % kv for kv in mf.most_common())),
           '  dados:   %d em %d armazenamentos (mesma VA do 983 = mesmo armazenamento) + %d literal ""' % (len(dados), len(grupos), len(literais)),
           '  já com /alternatename noutro .obj (stub responde também pelo alvo): %d — %s' % (len(alt), ', '.join(
               sorted('%s(%d)' % kv for kv in collections.Counter(v[1] for v in alt.values()).items()))),
           '  por frente (do v6-link): %s' % ', '.join('%s %d' % kv for kv in fr.most_common()),
           '  fora dos stubs: %s' % (', '.join(c[0] for c in fora) or 'nenhum') + (' (resolvido pela libpng/zlib VC10: make f4-terc)' if [c for c in fora if c[0] == '__iob'] else ''),
           'compilação: %s (build/C/f4/stubs/stubs983.obj, %s bytes)' % ('ok' if rc == 0 and os.path.exists(obj) else 'ERRO (ver build/C/f4/stubs/stubs983.log)',
                                                                       os.path.getsize(obj) if os.path.exists(obj) else 0)]
    open(OUT + '/stubs_resumo.txt', 'w', encoding='utf-8').write('\n'.join(res) + '\n')
    print('\n'.join(res))
    if rca or not os.path.exists(aobj): print('stubs983a.asm: ERRO (ver build/C/f4/stubs/stubs983a.log)')
    sys.exit(0 if rc == 0 and rca == 0 else 1)


if __name__ == '__main__':
    main()
