#!/usr/bin/env python3
"""f37/gemeo.py <stem> <CtrlClass> <ObjClass> <fctrl> <fobj> <habilidade hex> <ini da unidade ctrl> <fim da unidade obj>
Gera um par controlador/objeto gêmeo do CPangyaCorrection{Controller,Object} (mesmo código no 983, conferido antes por
diff do desmonte normalizado: só mudam vtable, nome e eSpecialAbility): include/jp/<f>.h, src/projectg/jp/<f>.cpp, linhas
em jp.tsv (símbolo → VA pela ordem das funções) e em units.txt. <stem> = nome sem C e sem sufixo (ex.: PlusYardItem)."""
import sys, os, re, subprocess
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
stem, cc, oc, fc, fo, ab, ini, fim = sys.argv[1:]
def starts(a, b):
    o = subprocess.run([sys.executable, R + '/tools/f37/dz.py', a, b], stdout=subprocess.PIPE, text=True).stdout
    open('/tmp/gemeo.txt', 'w').write(o)
    return subprocess.run([sys.executable, R + '/tools/f37/ini.py', '/tmp/gemeo.txt'], stdout=subprocess.PIPE, text=True).stdout.split()[2:]
ref = starts('005ac150', '005ac4e0'); new = starts(ini, fim)
assert len(ref) == len(new) == 19, (len(ref), len(new))
amap = dict(zip(ref, new))
def tr(s):
    s = s.replace('CPangyaCorrectionController', '\x01').replace('CPangyaCorrectionObject', '\x02')
    s = s.replace('pangyacorrectioncontroller', '\x03').replace('pangyacorrectionobject', '\x04')
    s = s.replace('PangyaCorrection', stem)
    s = s.replace('\x01', cc).replace('\x02', oc).replace('\x03', fc).replace('\x04', fo)
    s = re.sub(r'\b00[0-9a-f]{6}\b', lambda m: amap.get(m.group(0), m.group(0)), s)
    return s.replace('habilidade 0x0a', 'habilidade 0x%02x' % int(ab, 16))
for d, a, b, e in (('include/jp', 'pangyacorrectioncontroller', fc, '.h'), ('include/jp', 'pangyacorrectionobject', fo, '.h'),
                   ('src/projectg/jp', 'pangyacorrectioncontroller', fc, '.cpp'), ('src/projectg/jp', 'pangyacorrectionobject', fo, '.cpp')):
    s = tr(open('%s/%s/%s%s' % (R, d, a, e)).read())
    if e == '.cpp':
        s = re.sub(r'^// JP 983: unidade.*\n', '// JP 983: unidade %s–%s (%s; gêmea do CPangyaCorrection, gerada por tools/f37/gemeo.py e conferida no 983).\n'
                   % ((new[0], new[10], cc) if b == fc else (new[10], fim, oc)), s, count=1)
    open('%s/%s/%s%s' % (R, d, b, e), 'w').write(s)
t = R + '/src/projectg/jp/jp.tsv'; L = open(t).read().splitlines(); have = set(l.split('\t')[0] for l in L)
for l in list(L):
    p = l.split('\t')
    if len(p) > 1 and p[1] in amap and '005ac150' <= p[1] < '005ac4e0':
        n = tr(p[0])
        if n not in have: L.append(n + '\t' + amap[p[1]])
open(t, 'w').write('\n'.join(L) + '\n')
u = R + '/src/projectg/jp/units.txt'; s = open(u).read()
for f in (fc, fo):
    if f + '.cpp\n' not in s: s += f + '.cpp\n'
open(u, 'w').write(s)
print(cc, oc, new[0], fim)
