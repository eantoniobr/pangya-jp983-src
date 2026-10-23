#!/usr/bin/env python3
# f27_var.py — testa variantes do corpo de uma função em shparam.cpp; imprime % de cada e restaura a melhor se pedido
import re,subprocess,sys,itertools
P='/root/jp983src/src/wangreal/shparam.cpp'
def run(body, start, end, key):
    s=open(P).read(); i=s.index(start); j=s.index(end,i)
    new=s[:i]+body+s[j:]; open(P,'w').write(new)
    try:
        subprocess.run(['tools/cmpfunc',P,'--inline'],cwd='/root/jp983src',stdout=open('/root/jp983src/build/f27/v.log','w'),stderr=subprocess.STDOUT)
        t=open('/root/jp983src/build/f27/v.log').read()
        m=[l for l in t.split('\n') if key in l and not l.startswith('---')]
        return (m[0][:40] if m else ('ERRO '+' '.join(re.findall(r'error.*',t)[:2])[:150]))
    finally:
        open(P,'w').write(s)
