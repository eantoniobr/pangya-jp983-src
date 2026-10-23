#!/usr/bin/env python3
"""Frente C, C-PKT lote 9 — funções com duas cópias (ramo morto × ramo que compila com REBANG_SEMANTIC_ONLY):
ids de pacote ENVIADO (`WSendPacket x(N)`, `new WSendPacket(N)`, `InitPacket(N)`) de cada cópia, função a função.

  copias.py [OUT]   -> OUT/copias_envio.tsv (toda função com envio em algum ramo) e resumo na saída
Estado:  igual        = as duas cópias mandam os mesmos ids, na mesma ordem
         difere       = as duas têm envio e a lista de ids não é a mesma
         so_morta     = a cópia que compila não tem envio com id constante (pode usar nome de enum: coluna `viva_txt`)
         so_viva      = só a cópia que compila tem envio
Só leitura do fonte; a verdade do que compila é o .obj (tools/v4/pk.py)."""
import sys, os, re, collections
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = re.compile(r'(?:(?:WSendPacket|RbSendPacketExtern)\s*&?\s*\w+\s*(?:=\s*\*\s*new\s+WSendPacket\s*)?\(|new\s+WSendPacket\s*\(|\bInitPacket\s*\()\s*'
                  r'((?:\(\s*enumClientPacket\s*\)\s*)?)([^;{]*?)\)\s*[;,)]')
DEF = re.compile(r'^[A-Za-z_][^;=]*?\b((?:\w+::)+~?\w+)\s*\([^;]*$')
COND = re.compile(r'^\s*#\s*(if|ifdef|ifndef|elif|else|endif)\b(.*)')


def ramo_de(tipo, resto):
    """'morto' / 'vivo' / None para a 1ª metade de um bloco condicional."""
    if 'REBANG_SEMANTIC_ONLY' not in resto:
        return None
    if tipo == 'ifndef' or (tipo == 'if' and re.search(r'!\s*defined\s*\(\s*REBANG_SEMANTIC_ONLY', resto)):
        return 'morto'
    if tipo == 'ifdef' or (tipo == 'if' and re.search(r'defined\s*\(\s*REBANG_SEMANTIC_ONLY', resto)):
        return 'vivo'
    return None


def num(t):
    t = t.strip()
    try:
        return '0x%x' % int(t, 0)
    except ValueError:
        return None


def varre(p):
    """-> {funcao: {'morto': [(linha, id|None, texto)], 'vivo': [...], 'comum': [...]}}"""
    pilha = []          # cada item: ramo atual do bloco ('morto'/'vivo'/None)
    func = {'morto': None, 'vivo': None, 'comum': None}
    out = collections.defaultdict(lambda: collections.defaultdict(list))
    for n, l in enumerate(open(p, encoding='latin-1'), 1):
        m = COND.match(l)
        if m:
            t, resto = m.group(1), m.group(2)
            if t in ('if', 'ifdef', 'ifndef'):
                pilha.append(ramo_de(t, resto))
            elif t in ('else', 'elif') and pilha:
                pilha[-1] = {'morto': 'vivo', 'vivo': 'morto'}.get(pilha[-1])
            elif t == 'endif' and pilha:
                pilha.pop()
            continue
        r = 'comum'
        if 'morto' in pilha:
            r = 'morto'
        elif 'vivo' in pilha:
            r = 'vivo'
        d = DEF.match(l)
        if d and not l.startswith(('return', 'else', 'case', 'if', 'while', 'for', 'switch', 'delete', 'new')):
            func[r] = d.group(1)
            if r == 'comum':
                func['morto'] = func['vivo'] = d.group(1)
        for s in SITE.finditer(l.split('//')[0]):
            f = func[r] or func['comum']
            if f:
                out[f][r].append((n, num(s.group(2)), s.group(2).strip()))
    return out


def main():
    od = sys.argv[1] if len(sys.argv) > 1 else os.path.join(R, 'out', 'PKT', 's9')
    os.makedirs(od, exist_ok=True)
    rows = []
    for base in ('src/projectg', 'src/shared'):
        for d, _, fs in os.walk(os.path.join(R, base)):
            if '/jp' in d[len(R):]:
                continue
            for f in sorted(fs):
                if not f.endswith(('.cpp', '.inl', '.h')):
                    continue
                p = os.path.join(d, f)
                for fn, rr in sorted(varre(p).items()):
                    mo, vi = rr.get('morto', []), rr.get('vivo', [])
                    if not mo and not vi:
                        continue        # função de cópia única
                    im = [x[1] or x[2] for x in mo]
                    iv = [x[1] or x[2] for x in vi]
                    if mo and vi:
                        est = 'igual' if im == iv else ('igual_conjunto' if sorted(set(im)) == sorted(set(iv)) else 'difere')
                    elif mo:
                        est = 'so_morta'
                    else:
                        est = 'so_viva'
                    rows.append((est, os.path.relpath(p, R), fn, ' '.join(im), ' '.join(iv),
                                 ','.join(str(x[0]) for x in mo), ','.join(str(x[0]) for x in vi)))
    with open(os.path.join(od, 'copias_envio.tsv'), 'w') as f:
        f.write('estado\tarquivo\tfuncao\tids_morta\tids_viva\tlinhas_morta\tlinhas_viva\n')
        for r in sorted(rows):
            f.write('\t'.join(r) + '\n')
    c = collections.Counter(r[0] for r in rows)
    print('funções com envio dentro de ramo condicional de REBANG_SEMANTIC_ONLY: %d em %d arquivos' % (len(rows), len({r[1] for r in rows})))
    for k in ('igual', 'igual_conjunto', 'difere', 'so_morta', 'so_viva'):
        print('  %-15s %d' % (k, c[k]))


if __name__ == '__main__':
    main()
