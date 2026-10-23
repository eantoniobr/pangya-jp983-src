#!/usr/bin/env python3
"""parfeat.py OBJ NOMES VAS [--map M] — pareia funções do .obj com funções do 983 pelo CONTEÚDO, não pela ordem: constantes
de ponto flutuante (valor de __real@… × valor lido no 983), textos (??_C@ × string no 983) e alvos de chamada com endereço no
mapa. Serve onde o layout mudou e o 983 tem LTCG (notas do cmpfunc baixas para todo mundo, ordem do .obj não é a do 983).
NOMES = arquivo com um nome decorado por linha (ou 'SEM_PAR:funcs.tsv' = as SEM_PAR próprias de um funcs.tsv do cmpfunc);
VAS = arquivo com um VA por linha (1ª coluna) ou lista 'va,va,…'. Saída: para cada nome, as 3 melhores candidatas
(pontos = feições em comum, multiconjunto) e a tabela gulosa nome → VA (sem repetir VA). Sessão 98 (camerawork)."""
import sys, os, struct, collections, importlib.machinery, importlib.util
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ld = importlib.machinery.SourceFileLoader('cmpfunc', R + '/tools/cmpfunc')
cf = importlib.util.module_from_spec(importlib.util.spec_from_loader('cmpfunc', ld)); ld.exec_module(cf)

a = [x for x in sys.argv[1:] if not x.startswith('--')]
mp = R + '/map/projectg.tsv'
if '--map' in sys.argv: mp = sys.argv[sys.argv.index('--map') + 1]; a.remove(mp)
objp, nomesp, vasp = a[:3]
name2va = {}
for l in open(mp, errors='replace'):
    p = l.rstrip('\n').split('\t')
    if len(p) >= 2:
        try: name2va[p[0]] = int(p[1], 16)
        except ValueError: pass
if nomesp.startswith('SEM_PAR:'):
    nomes = [l.split('\t')[1] for l in open(nomesp[8:]) if l.split('\t')[2:4] == ['1', 'SEM_PAR']]
else:
    nomes = [l.split()[0] for l in open(nomesp) if l.strip()]
vas = [int(x, 16) for x in vasp.split(',')] if ',' in vasp or not os.path.exists(vasp) else \
      [int(l.split()[0], 16) for l in open(vasp) if l.strip() and not l.startswith('#')]

ob = cf.Obj(objp); pe = cf.PE(R + '/ref/ProjectG_983_dump.exe')
def fval(v): return 'F%.5g' % v if v == v and abs(v) < 1e30 else None

def feats_obj(nm):
    for (n, sec, s, e, own) in ob.funcs():
        if n == nm: break
    else: return None
    t = cf.obj_tokens(ob, sec, s, e)
    c = collections.Counter()
    for refs in t.refs:
        for r in refs:
            n2 = r[1]
            if not isinstance(n2, str): continue
            if n2.startswith('__real@'):
                h = n2[7:]
                v = struct.unpack('<f', bytes.fromhex(h)[::-1])[0] if len(h) == 8 else struct.unpack('<d', bytes.fromhex(h)[::-1])[0]
                f = fval(v)
                if f: c[f] += 1
            elif n2.startswith('??_C@') and r[3] is not None:
                d = ob.symdata(r[3])
                if d: c['S' + d.split(b'\0')[0].decode('latin1')] += 1
            elif n2 in name2va:
                c['C%08x' % name2va[n2]] += 1
    return c

def feats_pe(va):
    nxt = min([v for v in vas if v > va] or [va + 0x4000])
    t, size = cf.pe_tokens(pe, va, nxt)
    c = collections.Counter()
    if not t: return c
    for txt, refs in zip(t.txt, t.refs):
        for r in refs:
            v = r[2]
            if not pe.inimg(v): continue
            o = pe.off(v)
            if o is None: continue
            if txt.startswith(('call', 'jmp')) or txt.startswith('push') and False:
                c['C%08x' % v] += 1; continue
            if 'qword ptr' in txt:
                f = fval(struct.unpack_from('<d', pe.d, o)[0])
            elif 'dword ptr' in txt and txt.startswith('f'):
                f = fval(struct.unpack_from('<f', pe.d, o)[0])
            else:
                f = None
            if f: c[f] += 1; continue
            if txt.startswith('push') or txt.startswith('mov'):
                s = pe.d[o:o + 80].split(b'\0')[0]
                if len(s) >= 3 and all(32 <= ch < 127 for ch in s): c['S' + s.decode('latin1')] += 1
            c['C%08x' % v] += 1     # dado/função por endereço (só conta se o .obj tiver o mesmo nome no mapa)
    return c

FO = {n: feats_obj(n) for n in nomes}
FP = {v: feats_pe(v) for v in vas}
def score(a, b): return sum((a & b).values())
pares = []
for n in nomes:
    if FO[n] is None: print('?? sem função no .obj:', n); continue
    sc = sorted(((score(FO[n], FP[v]), v) for v in vas), reverse=True)
    tot = sum(FO[n].values())
    print('%-60s feições=%3d  ' % (n[:60], tot) + '  '.join('%08x:%d' % (v, s) for s, v in sc[:3]))
    for s, v in sc: pares.append((s, n, v))
print('\n# gulosa (pontos, nome, va)')
usado_n, usado_v = set(), set()
for s, n, v in sorted(pares, reverse=True):
    if s == 0 or n in usado_n or v in usado_v: continue
    usado_n.add(n); usado_v.add(v)
    print('%d\t%s\t%08x' % (s, n, v))
