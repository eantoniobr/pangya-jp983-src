#!/usr/bin/env python3
"""acessos.py LO HI off... — instruções com operando [reg+off] (reg != esp/ebp) nas funções do 983 com início em [LO, HI) (hex);
saída: va_função va_instrução instrução. Serve para achar quem usa um campo novo de uma classe."""
import sys,struct,capstone,re
sys.path.insert(0,'/root/jp983src/tools/f34'); import pgdis as P
lo,hi=int(sys.argv[1],16),int(sys.argv[2],16); offs=set(int(x,16) for x in sys.argv[3:])
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); md.detail=True
for l in open('/root/jp983src/map/projectg_funcs.tsv'):
    c=l.split('\t')
    try: va=int(c[0],16); n=int(c[1])
    except: continue
    if not(lo<=va<hi): continue
    o=P.off(va)
    for i in md.disasm(P.d[o:o+n],va):
        for op in i.operands:
            if op.type==3 and op.mem.disp in offs and i.reg_name(op.mem.base) not in('esp','ebp'):
                print('%08x %08x %s %s'%(va,i.address,i.mnemonic,i.op_str))
