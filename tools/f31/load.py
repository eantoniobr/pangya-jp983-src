# F3.1 — carga dos insumos do mapa unidade do 645 -> ProjectG 983.
# Tudo somente leitura: /root/rebang (docs do PDB do 645 + build-projectg.json), /root/kr839/out (ponte 645<->839),
# /root/jp983/out (pares 983<->839, classes, exports do Ghidra).
import bisect, collections, csv, json, os, re

REBANG = '/root/rebang'
KR = '/root/kr839/out'
JP = '/root/jp983/out'
TEXT645 = 0x401000


def modules645():
    """módulo do PDB -> dict(obj, lib, path, size, estado, grupo)"""
    mods = {}
    for r in csv.DictReader(open(f'{REBANG}/docs/module-list.csv')):
        mods[int(r['module'])] = dict(obj=r['original_object'], lib=r['original_module'], path='', size=0,
                                      estado='fora', grupo='lib')
    for r in csv.DictReader(open(f'{REBANG}/docs/module-sizes.csv')):
        m = mods[int(r['module'])]
        m['path'] = r['path']
        m['size'] = int(r['size'])
    # estado no rebang: o build-projectg.json diz se a unidade entra como .cpp/.c (pronta) ou .obj (ainda delinkada)
    d = json.load(open(f'{REBANG}/build-projectg.json'))
    estado = {}

    def walk(items):
        for i in items:
            if isinstance(i, dict) and 'members' in i:
                walk(i['members'])
                continue
            p = i if isinstance(i, str) else i['path']
            stem, ext = os.path.splitext(p)
            if ext in ('.cpp', '.c', '.obj'):
                estado[stem.lower()] = (ext, p)
    walk(d['inputs'])
    for m in mods.values():
        if not m['path']:
            continue
        stem = os.path.splitext(m['path'])[0].lower()
        e = estado.get(stem)
        if e:
            m['estado'] = 'cpp' if e[0] in ('.cpp', '.c') else 'obj'
            m['path'] = e[1]
        else:
            m['estado'] = '?'
        p = m['path']
        m['grupo'] = ('Fresh' if '/Fresh/' in p else 'Wangreal' if '/Wangreal/' in p else
                      'ProjectG' if '/ProjectG/' in p else 'shared')
    return mods


def contribs645():
    """contribuições da .text do 645: listas paralelas ordenadas (va, fim, módulo)"""
    out = []
    for r in csv.DictReader(open(f'{REBANG}/docs/object-boundaries.csv')):
        if r['section'] == '1':
            va = TEXT645 + int(r['offset'], 16)
            out.append((va, va + int(r['size'], 16), int(r['module'])))
    out.sort()
    return out


def jsonl(path):
    return [json.loads(l) for l in open(path, encoding='utf-8', errors='replace')]


def funcs645():
    return jsonl(f'{KR}/f645.jsonl')


def funcs983():
    return jsonl(f'{JP}/j6_f983.jsonl')


def pairs_645_839():
    """645 -> (839, método, confiança)"""
    d = {}
    for l in open(f'{KR}/match2/pairs.tsv'):
        a, b, how, conf = l.rstrip('\n').split('\t')[:4]
        d[a] = (b, how, conf)
    return d


def pairs_983_839():
    """839 -> lista de (983, confiança, evidência)  (um 839 pode ter gêmeas)"""
    d = collections.defaultdict(list)
    for l in open(f'{JP}/j3/pairs.tsv'):
        c = l.rstrip('\n').split('\t')
        d[c[1]].append((c[0], c[2], c[3]))
    # pares achados depois (J7): IGUAL/ALTERADA com 'b'
    for r in csv.DictReader(open(f'{JP}/J7_exclusivas.tsv'), delimiter='\t'):
        if r['cat'] in ('IGUAL', 'ALTERADA') and r['b']:
            d[r['b']].append((r['a'], 'j7', r['ev']))
    return d


def classes983():
    """função 983 -> classe (vtable da J3 + vizinhança da J7)"""
    d = {}
    for l in open(f'{JP}/j3/classes.tsv'):
        c = l.rstrip('\n').split('\t')
        d[c[0]] = c[2]
    for r in csv.DictReader(open(f'{JP}/J7_exclusivas.tsv'), delimiter='\t'):
        if r['cls'] and r['clsrc'] != 'vizinhança':
            d.setdefault(r['a'], r['cls'])
    return d


class ModOf:
    def __init__(self, contribs):
        self.c = contribs
        self.k = [x[0] for x in contribs]

    def __call__(self, va):
        i = bisect.bisect_right(self.k, va) - 1
        if i >= 0 and va < self.c[i][1]:
            return self.c[i][2]
        return None
