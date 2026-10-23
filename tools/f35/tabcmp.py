# tabcmp.py arquivo.cpp "nome[N]" VA N — compara a tabela de int (literal no fonte) com N dwords do exe 983 em VA
import re,struct,sys
src=open(sys.argv[1],encoding='latin1').read()
name,va,n=sys.argv[2],int(sys.argv[3],16),int(sys.argv[4])
i=src.index(name); b=src.index('{',i); e=src.index('};',b)
ours=[int(x,0) for x in re.findall(r'-?0x[0-9a-fA-F]+|-?\d+',src[b+1:e])]
d=open('/root/jp983src/ref/ProjectG_983_dump.exe','rb').read()
pe=struct.unpack_from('<I',d,0x3c)[0]; ns=struct.unpack_from('<H',d,pe+6)[0]; oh=pe+24
base=struct.unpack_from('<I',d,oh+28)[0]; st=oh+struct.unpack_from('<H',d,pe+20)[0]
for k in range(ns):
    vs,v,rs,ro=struct.unpack_from('<IIII',d,st+40*k+8)
    if v<=va-base<v+max(vs,rs): off=ro+va-base-v
theirs=list(struct.unpack_from('<%di'%n,d,off))
diff=[k for k in range(min(len(ours),n)) if ours[k]!=theirs[k]]
print('nossa %d, 983 %d; diferem %d %s'%(len(ours),n,len(diff),diff[:20]))
