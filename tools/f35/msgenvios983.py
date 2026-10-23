#!/usr/bin/env python3
"""msgenvios983.py SAIDA.tsv — todos os envios de mensagem do exe 983, lidos direto do código (sem depender de par no fonte).
Duas formas:
  C = `call 0046e780` (MsgObject::MsgObject(IActor*, int msg, int p1, ...)): 2º push = msg, 3º push = p1;
  L = MsgObject montado em linha: gravações vizinhas (janela de 10 instruções) em [B+D] (remetente), [B+D+4] (msg, imediato) e
      [B+D+8] (p1), B = esp/ebp. Pode dar falso positivo (qualquer struct com 3 campos seguidos); o uso é por assinatura.
Mensagens com sub-código em p1 (guilda, gateway, sala) têm um conjunto de p1 que não muda entre versões.
Saída: va, funcao (início pelo mapa), forma, msg, p1 ('?' = não é imediato)."""
import sys, os, bisect, struct, re, importlib.machinery, importlib.util
import capstone
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ld = importlib.machinery.SourceFileLoader('cmpfunc', R + '/tools/cmpfunc')
sp = importlib.util.spec_from_loader('cmpfunc', ld); cm = importlib.util.module_from_spec(sp); ld.exec_module(cm)
CTOR = 0x46e780
pe = cm.PE(R + '/ref/ProjectG_983_dump.exe')
t = pe.text; lo = pe.tlo; hi = lo + len(t)
starts = sorted(s for s in cm.load_starts(R + '/map/projectg_funcs.tsv') if lo <= s < hi)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
STO = re.compile(r'dword ptr \[(esp|ebp)(?: ([+-]) (0x[0-9a-f]+|\d+))?\], (.+)$')
def num(s):
    try: return int(s, 0)
    except ValueError: return None
out = open(sys.argv[1], 'w'); out.write('va\tfuncao\tforma\tmsg\tp1\n')
nc = nl = 0
for fi, f in enumerate(starts):
    end = starts[fi + 1] if fi + 1 < len(starts) else hi
    if end - f > 0x40000: end = f + 0x40000
    ins = [(x.address, x.mnemonic, x.op_str) for x in md.disasm(t[f - lo:end - lo], f)]
    st = []     # (k, base, disp, valor|None) das gravações em pilha
    for k, (a, m, o) in enumerate(ins):
        if m == 'call':
            v = num(o)
            if v == CTOR:
                ps = []
                for j in range(k - 1, max(k - 40, -1), -1):
                    mj = ins[j][1]
                    if mj == 'call' or mj.startswith('j') or mj.startswith('ret'): break
                    if mj == 'push':
                        ps.append(num(ins[j][2]))
                        if len(ps) == 3: break
                g = lambda q: '?' if len(ps) <= q or ps[q] is None else hex(ps[q])
                out.write('%08x\t%08x\tC\t%s\t%s\n' % (a, f, g(1), g(2))); nc += 1
        elif m == 'mov':
            q = STO.match(o)
            if q:
                d = int(q.group(3), 0) if q.group(3) else 0
                if q.group(2) == '-': d = -d
                st.append((k, q.group(1), d, num(q.group(4))))
    for i, (k, b, d, v) in enumerate(st):
        if v is None or not (1 <= v < 0x400 or 0x2710 <= v < 0x2740 or 0x7530 <= v < 0x7600): continue
        viz = [s for s in st[max(0, i - 8):i + 9] if s[1] == b and abs(s[0] - k) <= 10]
        if not any(s[2] == d - 4 for s in viz): continue
        p1 = [s for s in viz if s[2] == d + 4]
        if not p1: continue
        p1 = min(p1, key=lambda s: abs(s[0] - k))
        out.write('%08x\t%08x\tL\t%s\t%s\n' % (ins[k][0], f, hex(v), '?' if p1[3] is None else hex(p1[3]))); nl += 1
print(nc, 'pelo construtor;', nl, 'em linha')
