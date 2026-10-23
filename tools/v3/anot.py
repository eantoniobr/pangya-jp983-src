#!/usr/bin/env python3
"""V3: colhe dos cabeçalhos do exe as anotações de layout que a frente A deixou nos comentários.

  anot.py [OUT_DIR=out/V3]   -> OUT_DIR/anot.tsv (tipo, classe, membro, valor, unidade, evidencia), lido pelo gen.py
  OFF   membro com `// 0xNN` / `// +0xNN` / `// 983: 0xNN` logo depois do `;` (deslocamento anotado do membro)
  SIZE  comentário com `983` e `sizeof 0xNN` dentro da classe
  SIZE  (V7, cabeçalhos da frente B em include/jp) comentário `// JP 983: … 0xNN bytes` logo acima da classe
Em include/jp todo deslocamento anotado é do 983 (as classes são novas, medidas no exe; não há herança do 645).
São asserts de coerência cabeçalho × anotação: pegam membro que saiu do lugar. A anotação é do 983 quando o comentário
diz 983 ou quando o sizeof da classe já confere com o 983 (coluna `origem`: 983 | anot)."""
import sys, os, re, glob
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out = sys.argv[1] if len(sys.argv) > 1 else R + '/out/V3'
MEM = re.compile(r'^\s*(?!static\b|typedef\b|friend\b|virtual\b|return\b|//)[^;()=]*?\b(\w+)\s*(?:\[[^\]]*\]\s*)*;\s*//\s*(983:\s*)?\+?(0x[0-9a-fA-F]+)\b(.*)$')
CLS = re.compile(r'^\s*(?:typedef\s+)?(class|struct|union)\b\s*(?:\w+\s+)*?(\w+)?\s*(?:final\s*)?(?::[^;{]*)?(\{)?\s*(?://.*)?$')
NS = re.compile(r'^\s*namespace\s+(\w+)\s*\{?\s*$')
BY = re.compile(r'\b(0x[0-9a-fA-F]+) bytes\b')
SZ = re.compile(r'sizeof (?:do 983 )?(?:== ?)?(0x[0-9a-fA-F]+)')
rows = []
for f in sorted(glob.glob(R + '/src/**/*.h', recursive=True) + glob.glob(R + '/include/**/*.h', recursive=True)):
    rel = os.path.relpath(f, R)
    if '/asserts/' in f or rel.startswith('src/wangreal/') or ('/lib/' in f and '/refresh/lib/' not in f) or '/third_party/' in f: continue   # C96: lib da RF anotada (B)
    L = open(f, encoding='latin1').read().split('\n'); st = []; depth = 0; pend = None; tmpl = False; ns = []; pns = None
    jp = rel.startswith('include/jp/')
    for i, l in enumerate(L):
        code = re.sub(r'//.*', '', l); m = CLS.match(l)
        n = NS.match(code)                                   # C10: namespace com nome entra no nome da classe (IFF983::sAbility)
        if n: pns = n.group(1)
        if pns and '{' in code: ns.append((pns, depth)); pns = None
        elif pns and not n and code.strip(): pns = None
        q = ''.join(x + '::' for x, _ in ns)
        if jp and m and m.group(2) and depth == 0 and not code.rstrip().endswith(';'):
            j = i - 1; blk = []
            while j >= 0 and L[j].lstrip().startswith('//'): blk.insert(0, L[j]); j -= 1
            b = BY.search(' '.join(blk))
            if b and '983' in ' '.join(blk): rows.append(('SIZE', q + m.group(2), '-', b.group(1).lower(), '983', '%s:%d' % (rel, i - len(blk) + 1)))
        if code.strip().startswith('template'): tmpl = True
        if m and not code.rstrip().endswith(';'):
            pend = (m.group(2) if not tmpl else None)
            if m.group(3): st.append((pend, depth)); pend = None; tmpl = False; depth += 1; continue
        elif pend is not None or (m is None and code.strip() == '{' and pend is None and False): pass
        if code.strip().startswith('{') and (pend is not None or (i and CLS.match(L[i - 1]) and not re.sub(r'//.*', '', L[i - 1]).rstrip().endswith(';'))):
            st.append((pend, depth)); pend = None; tmpl = False
        elif code.strip() and not code.strip().startswith('template') and not m: tmpl = False
        inside = st and depth == st[-1][1] + 1 and all(n for n, _ in st)
        if inside and ':' not in code.split(';')[0].replace('::', ''):
            mm = MEM.match(l)
            if mm:
                v = mm.group(3).lower(); rest = mm.group(4); org = '983' if jp else 'anot'; ok = True
                m2 = re.match(r'\s*;\s*983:\s*\+?(0x[0-9a-fA-F]+)\b', rest)
                if not mm.group(2) and m2: v = m2.group(1).lower(); org = '983'          # `// 0x5b4; 983: 0x638`
                elif mm.group(2):                                                          # `// 983: 0xNN …`: só se for mesmo deslocamento
                    ok = bool(re.match(r'\s*($|[:,;]|\([^)]*\b00[0-9a-f]{6}\b)', rest)) or mm.group(1).lower().endswith('_' + v[2:]); org = '983'
                elif '983' in rest: ok = False                                             # ambíguo: não vira assert
                if ok: rows.append(('OFF', q + '::'.join(n for n, _ in st), mm.group(1), v, org, '%s:%d' % (rel, i + 1)))
        if inside and '983' in l and '//' in l and 'o nosso dava' not in l:
            s = SZ.search(l[l.index('//'):])
            if s and '->' not in l and 'era membro' not in l:
                rows.append(('SIZE', q + '::'.join(n for n, _ in st), '-', s.group(1).lower(), '983', '%s:%d' % (rel, i + 1)))
        depth += code.count('{') - code.count('}')
        while st and depth <= st[-1][1]: st.pop()
        while ns and depth <= ns[-1][1]: ns.pop()
# C96: lib da RF x visoes velhas nao convivem numa unidade (C2011); classe com visao velha fora da lib (include/jp, src/projectg/jp)
# fica so com as anotacoes da visao velha; as da lib valem para as classes que so a lib declara (RFAnimButton, RFThumbButton...)
velha = set()
for f in glob.glob(R + '/include/jp/**/*.h', recursive=True) + glob.glob(R + '/src/projectg/jp/*.h'):
    if '/lib/' in f: continue
    for m in re.finditer(r'^[ \t]*(?:class|struct)\s+(?:\w+\s+)?(\w+)\s*(?::[^;{]*)?\{', open(f, encoding='latin1').read(), re.M): velha.add(m.group(1))
rows = [r for r in rows if not ('/refresh/lib/' in r[5] and r[1].split('::')[0] in velha)]
with open(out + '/anot.tsv', 'w') as o:
    o.write('tipo\tclasse\tmembro\tvalor\tunidade\tevidencia\n')
    for t, c, m, v, org, ev in rows: o.write('%s\t%s\t%s\t%s\t-\t%s: anotação do cabeçalho %s\n' % (t, c, m, v, org, ev))
print('anotações: %d OFF (%d dizem 983), %d SIZE, em %d classes' % (sum(1 for r in rows if r[0] == 'OFF'), sum(1 for r in rows if r[0] == 'OFF' and r[4] == '983'),
      sum(1 for r in rows if r[0] == 'SIZE'), len({r[1] for r in rows})))
