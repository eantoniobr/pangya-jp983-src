#!/usr/bin/env python3
# F3.3 — unidades do 645 sem lugar no mapa do 983: ainda existem no JP 983?
# Para cada unidade sem trecho e com código (>= 200 B de .text no 645): classes do PDB do 645 cujos métodos estão no
# módulo (>= 80% deles) -> procura o nome RTTI (.?AV<classe>@@ / .?AU) no dump do 983; strings que só as funções do módulo usam (export do
# Ghidra do 645) -> procura no dump. Nenhuma classe nem string achada = indício forte de que a unidade saiu do JP.
# uso: semlugar.py [--out out/F3.3]
import argparse, collections, csv, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'f31'))
from load import *  # noqa
from map import classe_de

ap = argparse.ArgumentParser()
ap.add_argument('--out', default='out/F3.3')
a = ap.parse_args()
dump = open('ref/ProjectG_983_dump.exe', 'rb').read()
mods = modules645()
mo = ModOf(contribs645())
porm = collections.defaultdict(list)
clsm = collections.defaultdict(collections.Counter)    # classe -> módulos dos métodos
strm = collections.defaultdict(set)                    # string -> módulos que a usam
for f in funcs645():
    m = mo(int(f['a'], 16))
    porm[m].append(f)
    clsm[classe_de(f['n'])][m] += 1
    for x in f.get('s', []):
        strm[x].add(m)
TODAS = [r for r in csv.DictReader(open('map/projectg_units.tsv'), delimiter='\t') if r['grupo'] != 'lib']
U = [r for r in TODAS if r['classe_mapa'] in ('sem_ancora', 'so_ancoras_soltas')]
CTRL = [r for r in TODAS if r['classe_mapa'] == 'forte']
ctrl = collections.Counter()
peq = [r for r in U if int(r['bytes645']) < 200]
def prova(r):
    fs = porm[int(r['modulo645'])]
    cls = collections.Counter(classe_de(f['n']) for f in fs)
    mm = int(r['modulo645'])
    # só classes cujos métodos estão (>= 80%) neste módulo e strings que só este módulo usa no 645
    cls = [c for c, n in cls.items() if c and n >= 2 and '<' not in c and not c.startswith(('std', 'ATL'))
           and n >= 0.8 * sum(clsm[c].values())]
    ach = []
    for c in cls:
        dec = '@'.join(reversed(c.split('::'))) + '@@'
        if any((p + dec).encode() in dump for p in ('.?AV', '.?AU')):
            ach.append(c)
    ss = {s for f in fs for s in f.get('s', []) if len(s) >= 8 and strm[s] == {mm}}
    sa = [s for s in sorted(ss) if s.encode('latin-1', 'replace') + b'\0' in dump]
    v = ('existe no 983' if ach or len(sa) >= 2 else 'sem indicio no 983 (saiu do JP?)' if cls or ss else
         'sem classe nem string para testar')
    return cls, ach, ss, sa, v


for r in CTRL:
    if int(r['bytes645']) >= 200:
        ctrl[prova(r)[4]] += 1
with open(f'{a.out}/sem_lugar.tsv', 'w') as o:
    o.write('unidade\testado\tbytes645\tfuncs645\tclasses_645\tclasses_no_983\tstrings_645\tstrings_no_983\tveredito\t'
            'classes achadas\tstrings achadas (até 5)\n')
    for r in sorted(U, key=lambda r: -int(r['bytes645'])):
        if int(r['bytes645']) < 200:
            continue
        cls, ach, ss, sa, v = prova(r)
        o.write('\t'.join([r['unidade'], r['estado_rebang'], r['bytes645'], r['funcs645'], str(len(cls)), str(len(ach)),
                           str(len(ss)), str(len(sa)), v, ', '.join(ach), ' | '.join(sa[:5])]) + '\n')
    o.write('# controle (mesma prova nas unidades com trecho firme, >= 200 B): ' +
            ', '.join(f'{k}={v}' for k, v in sorted(ctrl.items())) + '\n')
    o.write(f'# + {len(peq)} unidades com menos de 200 B de .text no 645 (só cabeçalhos/inline; sem função para '
            f'colocar): ' + ', '.join(os.path.basename(r['unidade']) for r in peq) + '\n')
print(open(f'{a.out}/sem_lugar.tsv').read())
