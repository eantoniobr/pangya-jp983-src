# C145: gera a tabela de animações por personagem do 983 (00e2dd40) emulando o inicializador estático 00ce6bf0 -> /tmp/c145/emo.inc
import struct,capstone,sys
d=open('/root/jp983src/ref/ProjectG_983_dump.exe','rb').read()
B=0x400000
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); md.detail=False
lo=0xe2dd40; n=15*19*8
tab=list(struct.unpack_from('<%dI'%n,d,lo-B))
tab=[('raw',v) if v else None for v in tab]
R={};S=[]
def val(op):
  op=op.strip()
  if op.startswith('0x') or op.isdigit(): v=int(op,0); return ('raw',v) if v else None
  return R[op]
pc=0xce6bf0
for ins in md.disasm(d[pc-B:pc-B+0x3000],pc):
  m,o=ins.mnemonic,ins.op_str
  if m=='push':
    S.append(R.get(o) if not o.startswith('0x') and not o.isdigit() else int(o,0)); continue
  if m in('pop','int3'): continue
  if m=='add' and o=='esp, 0xc': del S[-3:]; continue
  if m=='call' and o=='0xc3c3cc':
    dst,v,sz=S[-1],S[-2],S[-3]; assert v is None or v==0,v
    for k in range(dst,dst+sz,4): tab[(k-lo)//4]=None
    continue
  if m=='ret': break
  if m=='xor': a,b=o.split(', '); assert a==b; R[a]=None; continue
  if m=='call':
    assert o=='0xb4ec60',(hex(ins.address),o); R['eax']=('k2l',R['ecx'][1]); continue
  if m=='mov':
    a,b=o.split(', ',1)
    if a.startswith('dword ptr ['):
      ad=int(a[11:-1],0); i=(ad-lo)//4; assert 0<=i<n and ad%4==0,(hex(ins.address),o); tab[i]=val(b)
    else: R[a]=val(b)
    continue
  raise SystemExit('?? %x %s %s'%(ins.address,m,o))
print('fim',hex(ins.address),file=sys.stderr)
def cstr(v):
  s=d[v-B:v-B+200].split(b'\0')[0]
  r='';esc=False
  for c in s:
    if 32<=c<127 and c not in b'"\\?':
      if esc and chr(c) in '0123456789abcdefABCDEF': r+='" "'
      r+=chr(c);esc=False
    else: r+='\\x%02x'%c;esc=True
  return '"'+r+'"'
# saída: tabela por personagem; última entrada não nula de cada linha
import collections
st=collections.Counter(t[0] for t in tab if t); print(st,file=sys.stderr)
out=[]
for g in range(15):
  rows=[]
  for i in range(19):
    e=tab[(g*19+i)*8:(g*19+i)*8+8]
    while e and e[-1] is None: e=e[:-1]
    if not e: break
    rows.append('{ '+', '.join('NULL' if x is None else (cstr(x[1]) if x[0]=='raw' else 'K2L_Compatibility(%s)'%cstr(x[1])) for x in e)+' }')
  out.append(rows)
for g,rows in enumerate(out): print('// %d: %d'%(g,len(rows)),file=sys.stderr)
lines=['static const char* s_emoTable983[15][19][8] = {']
for g,rows in enumerate(out): lines.append('\t{ // %d'%g); lines+=['\t\t'+r+',' for r in rows]; lines.append('\t},')
lines.append('};'); open('/tmp/c145/emo.inc','w').write('\n'.join(lines)+'\n')
import json; json.dump(out,open('/tmp/c145/emo.json','w'))
