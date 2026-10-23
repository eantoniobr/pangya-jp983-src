#!/usr/bin/env python3
"""asmrect645.py — blocos asm do 645 (#ifndef REBANG_SEMANTIC_ONLY ... naked) que chamam FrWnd::SetRect e leem
[reg+2Xh]: o retangulo do FrWnd e +0x20 no 645 e +0x34 no 983 (A169). Lista por arquivo de src/projectg e src/fresh."""
import re,sys,glob
tot=0
for p in sorted(glob.glob('src/projectg/*.cpp')+glob.glob('src/fresh/source/*.cpp')):
    s=open(p,'rb').read().decode('latin-1'); L=s.split('\n'); i=0; n=[]
    while i<len(L):
        if L[i].startswith('#ifndef REBANG_SEMANTIC_ONLY'):
            d=0;j=i;els=None
            while j+1<len(L):
                j+=1;t=L[j]
                if t.startswith('#if'): d+=1
                elif t.startswith('#endif'):
                    if d==0: break
                    d-=1
                elif t.startswith('#else') and d==0: els=j
            b='\n'.join(L[i:els or j])
            if 'FrWnd_SetRect' in b and re.search(r'\+2[0-9A-F]h\]',b):
                m=re.search(r'naked\)?\s+[\w:<>\*& ]*?(\w+::\w+)\(',b); n.append(m.group(1) if m else '?')
            i=j
        i+=1
    if n: print(len(n),p,' '.join(n[:6])); tot+=len(n)
print('total',tot)
