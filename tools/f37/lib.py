"""f37/lib — apoio da F3.7.1: funções do mapa do exe, referências código → dados (build/B/refs.tsv) e o teste da
escada (mesma ideia do tools/f13_stairs.py, agora no ProjectG): cada COMDAT de .rdata (string, vtable, constante) fica
no 1º .obj que o define, então o menor endereço de função que usa cada dado sobe em degraus ao longo da .rdata."""
import os, csv, bisect, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RD_LO, RD_HI = 0x00cfc424, 0x00d70000      # .rdata útil (depois da IAT; antes das tabelas de exceção/RTTI)
CODE_HI = 0x00b50000                        # fim da região C (jogo); depois vêm bibliotecas, Lua, CRT


def funcs():
    out = []
    for r in csv.DictReader(open(os.path.join(ROOT, 'map', 'projectg_funcs.tsv')), delimiter='\t'):
        r['va'] = int(r['f983'], 16); r['sz'] = int(r['tam'])
        out.append(r)
    out.sort(key=lambda r: r['va'])
    return out


def minref(code_lo=0x401000, code_hi=0x00c3c18f):
    """dado da .rdata -> menor endereço de função que o referencia"""
    mn = {}
    for l in open(os.path.join(ROOT, 'build', 'B', 'refs.tsv')):
        f, _, t, _ = l.split('\t')
        f = int(f, 16); t = int(t, 16)
        if RD_LO <= t < RD_HI and code_lo <= f < code_hi:
            if t not in mn or f < mn[t]:
                mn[t] = f
    return mn


class Escada:
    def __init__(self, mn=None):
        self.mn = mn or minref()
        self.D = sorted(self.mn)
        self.M = [self.mn[d] for d in self.D]
        self.porM = sorted((m, i) for i, m in enumerate(self.M))
        self._k = [m for m, _ in self.porM]

    def janela(self, lo, hi):
        """primeiros usos (em ordem de endereço do dado) dos dados cujo 1º uso cai em [lo, hi)"""
        a = bisect.bisect_left(self._k, lo); b = bisect.bisect_left(self._k, hi)
        return [self.M[i] for i in sorted(i for _, i in self.porM[a:b])]

    def V(self, c, janela=0x60000, m=None):
        """nº mínimo de dados do lado errado para o corte de código c, olhando só os dados cujo 1º uso cai a menos
        de `janela` bytes de c. Devolve (V, nº de dados antes de c na janela, nº depois)."""
        if m is None:
            m = self.janela(c - janela, c + janela)
        n1 = sum(1 for v in m if v < c)
        # divisão k: dados [0,k) devem ser "antes", [k,n) "depois"; custo = depois em [0,k) + antes em [k,n)
        z = 0; o = n1; best = o
        for v in m:
            if v < c: o -= 1
            else: z += 1
            if z + o < best: best = z + o
        return best, n1, len(m) - n1
