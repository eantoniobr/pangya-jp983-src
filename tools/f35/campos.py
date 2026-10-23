#!/usr/bin/env python3
"""campos.py Classe cabeçalho [DEFINE...] — deslocamento de todos os campos (m_*, unk*) da classe como o stdafx do exe a vê, sem pch e com
private/protected abertos; cada campo vai dentro de __if_exists, então serve para classes com membros sob #ifdef (ex.: CGolfRule com
REBANG_GOLFRULE_PCH), onde o tools/f34/offs.py falha. ~20 s. Saída: off_hex nome (sizeof no fim)."""
import sys,types,re,os
sys.path.insert(0,'/root/jp983src/tools/f34'); sys.path.insert(0,'/root/jp983src/tools/f32')
import offs as O, pgbuild as pb
cls,hdr=sys.argv[1:3]; defs=sys.argv[3:]
s=open(hdr,encoding='latin-1').read()
i=re.search(r'\nclass (?:__declspec\((?:[^()]|\([^()]*\))*\) )?%s\b[^;{]*\{'%cls,s).end(); j=s.index('\n};',i); names=[]; depth=0
for l in s[i:j].split('\n'):
    l=l.split('//')[0]; d0=depth; depth+=l.count('{')-l.count('}')
    if d0 or '(' in l or 'static ' in l: continue
    m=re.search(r'\b((?:m_|unk|rb_)\w+)(\[[^;]*\])?(\s*:\s*\d+)?;',l)
    if m and not m.group(3) and m.group(1) not in names: names.append(m.group(1))
a=types.SimpleNamespace(flags=None,B=O.ROOT+'/build/pg'); src='/root/jp983src/build/f34/campos.cpp'
body='#include <stddef.h>\n#pragma warning(disable:4003)\n'
for n in names:
    body+='__if_exists(%s::%s){\nextern const unsigned int rb_o_%s[] = {0x5eed0001, offsetof(%s,%s)};\n}\n'%(cls,n,n,cls,n)
body+='extern const unsigned int rb_o_sizeof[] = {0x5eed0001, sizeof(%s)};\n'%cls
open(src,'w').write(body)
rc=pb.cl(pb.base_args(a)+['/D'+d for d in defs]+['/FIstdafx.h','/Dprivate=public','/Dprotected=public','/FI'+os.path.abspath(hdr),'/FA','/Fa'+src[:-4]+'.asm','/Fo'+src[:-4]+'.obj',src],src[:-4]+'.log')
if rc: sys.exit(open(src[:-4]+'.log',errors='replace').read()[-3000:])
t=open(src[:-4]+'.asm',errors='replace').read()
r=[]
for m in re.finditer(r'\?rb_o_(\w+)@@3QBIB DD 05eed0001H[^\n]*\n\s+DD\s+([0-9a-fA-F]+?)H?\r?\n',t): r.append((int(m.group(2),16),m.group(1)))
for v,n in sorted(r,key=lambda x:(x[1]=='sizeof',x[0])): print('0x%04x %s'%(v,n))
