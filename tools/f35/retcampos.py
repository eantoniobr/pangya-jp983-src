#!/usr/bin/env python3
"""retcampos.py VA [min_off] — campos lidos do ponteiro devolvido pela função VA (ex.: um Find* do CItemManager) em todos os
chamadores do exe 983: segue eax e as cópias (mov reg, eax / mov [ebp-x], eax) até o fim da função chamadora.
Saída: deslocamento, tamanho do acesso, nº de usos e até 4 lugares (função!instrução). É aproximado (varredura linear)."""
import sys,struct,capstone,bisect,collections
from capstone import x86 as X
d=open('/root/jp983src/ref/ProjectG_983_dump.exe','rb').read()
pe=struct.unpack_from('<I',d,0x3c)[0]; ns=struct.unpack_from('<H',d,pe+6)[0]; oh=pe+24
base=struct.unpack_from('<I',d,oh+28)[0]; st=oh+struct.unpack_from('<H',d,pe+20)[0]
secs=[struct.unpack_from('<IIII',d,st+40*i+8) for i in range(ns)]
vs,v,rs,ro=secs[0]; tlo,thi=base+v,base+v+vs
F=[]
for l in open('/root/jp983src/map/projectg_funcs.tsv').read().split('\n')[1:]:
    p=l.split('\t')
    try: F.append((int(p[0],16),int(p[1])))
    except: pass
F.sort(); ks=[f[0] for f in F]
tgt=int(sys.argv[1],16); mn=int(sys.argv[2],16) if len(sys.argv)>2 else 0
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); md.detail=True
text=d[ro:ro+vs]; res=collections.defaultdict(list); ncall=0
i=0
while True:
    i=text.find(b'\xe8',i)
    if i<0: break
    va=tlo+i
    if va+5+struct.unpack_from('<i',text,i+1)[0]!=tgt: i+=1; continue
    k=bisect.bisect_right(ks,va)-1
    if k<0 or not(F[k][0]<=va<F[k][0]+F[k][1]): i+=1; continue
    ncall+=1; f0,fn=F[k]; regs={X.X86_REG_EAX}; slots=set()
    for ins in md.disasm(text[i+5:f0+fn-tlo],va+5):
        ops=ins.operands
        for o in ops:
            if o.type==X.X86_OP_MEM and o.mem.base in regs and o.mem.index==0 and o.mem.disp>=mn:
                res[o.mem.disp].append((o.size,f0,ins.address,ins.mnemonic+' '+ins.op_str))
        if ins.mnemonic=='call':
            regs-={X.X86_REG_EAX,X.X86_REG_ECX,X.X86_REG_EDX}
        elif ins.mnemonic in('ret','int3'): break
        elif len(ops)==2 and ops[0].type==X.X86_OP_REG:
            r=ops[0].reg
            if ins.mnemonic=='mov' and ops[1].type==X.X86_OP_REG and ops[1].reg in regs: regs.add(r)
            elif ins.mnemonic=='mov' and ops[1].type==X.X86_OP_MEM and ops[1].mem.base in(X.X86_REG_EBP,X.X86_REG_ESP) and (ops[1].mem.base,ops[1].mem.disp) in slots: regs.add(r)
            elif ins.mnemonic not in('cmp','test'): regs.discard(r)
        elif len(ops)==2 and ins.mnemonic=='mov' and ops[0].type==X.X86_OP_MEM and ops[0].mem.base in(X.X86_REG_EBP,X.X86_REG_ESP):
            key=(ops[0].mem.base,ops[0].mem.disp)
            if ops[1].type==X.X86_OP_REG and ops[1].reg in regs: slots.add(key)
            else: slots.discard(key)
        elif len(ops)==1 and ops[0].type==X.X86_OP_REG and ins.mnemonic in('pop','lea'): regs.discard(ops[0].reg)
        if not regs and not slots: break
    i+=1
print('# alvo %08x: %d chamadas'%(tgt,ncall))
for o in sorted(res):
    u=res[o]; print('+0x%03x sz=%s n=%d  %s'%(o,','.join(str(s) for s in sorted(set(x[0] for x in u))),len(u),' | '.join('%08x!%08x %s'%(x[1],x[2],x[3]) for x in u[:4])))
