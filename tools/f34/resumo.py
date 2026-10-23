#!/usr/bin/env python3
"""resumo.py DIR_VOTOS SAIDA_DIR SUFIXO — de uma pasta de votos brutos (tools/f34/votes.py all):
 ranking_classes_<SUFIXO>.tsv  classes por nº de funções-voto com deslocamento diferente (e os deltas mais comuns)
 degraus_<SUFIXO>.tsv          deslocamentos >= 0x400 somados entre todas as classes: onde o delta muda (objetos grandes
                               acessados por ponteiro de qualquer classe: CSharedDoc, CGolfDoc…)"""
import sys, glob, collections
d, out, suf = sys.argv[1:4]
cls = collections.defaultdict(collections.Counter); big = collections.defaultdict(collections.Counter); exb = {}
seen = set()
for p in sorted(glob.glob(d + '/*.tsv')):
    for l in open(p):
        c = l.rstrip('\n').split('\t')
        if c[1] != 'mem': continue
        a, b = int(c[2], 16), int(c[3], 16)
        if (c[0], a, b, c[4]) not in seen:
            seen.add((c[0], a, b, c[4])); cls[c[0]][b - a if abs(b - a) < 1 << 24 else 0x7fffffff] += 1
        if 0x400 <= a < 0x80000 and b < 0x80000:
            big[a][b] += 1; exb.setdefault((a, b), c[4][:44] + ' ' + c[8])
with open('%s/ranking_classes_%s.tsv' % (out, suf), 'w') as f:
    f.write('classe\tvotos_delta_nao_zero\tvotos_delta_zero\tdeltas_mais_comuns\n')
    for k, h in sorted(cls.items(), key=lambda kv: -sum(v for q, v in kv[1].items() if q)):
        nz = sum(v for q, v in h.items() if q)
        if nz: f.write('%s\t%d\t%d\t%s\n' % (k, nz, h[0], ' '.join('%+d:%d' % kv for kv in h.most_common(8) if kv[0] and kv[0] != 0x7fffffff)))
tn = sum(v for h in cls.values() for q, v in h.items() if q); tz = sum(h[0] for h in cls.values())
with open('%s/degraus_%s.tsv' % (out, suf), 'w') as f:
    f.write('off_obj\toff_983\tdelta\tvotos\tmuda\texemplo\n'); last = None
    for a in sorted(big):
        (b, n), tot = big[a].most_common(1)[0], sum(big[a].values())
        if n < 3 or n < 0.6 * tot: continue
        f.write('0x%x\t0x%x\t%+d\t%d\t%s\t%s\n' % (a, b, b - a, n, '*' if b - a != last else '', exb[(a, b)])); last = b - a
print('%s: %d classes; votos (classe, off_obj, off_983, função) com delta != 0: %d, == 0: %d' % (suf, len(cls), tn, tz))
