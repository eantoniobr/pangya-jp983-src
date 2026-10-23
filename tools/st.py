import json,sys,datetime,os
# uso: st.py task <id> <estado> <nota> | ev <texto> | fase <x> | add <id> <titulo>
# rodar sob: flock /root/jp983src/status.lock python3 tools/st.py ...
p='/root/jp983src/status.json'
now=datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
T=[('F0.1','Estrutura do repositório e README'),
   ('F0.2','Build com o VS2010 do Wine (olá + 1 .cpp real)'),
   ('F0.3','Comparador tools/cmpfunc (função do .obj × função do 983)'),
   ('F0.4','wangreal.dll 983 no Ghidra + casamento com 839 e 645'),
   ('F0.5','Piloto: 5 funções da wangreal ponta a ponta')]
if os.path.exists(p): d=json.load(open(p))
else: d={'updated':now,'fase':'F0','tarefas':[{'id':i,'titulo':t,'estado':'pendente','nota':'','atualizado':now} for i,t in T],'eventos':[]}
a=sys.argv[1:]; i=0
while i<len(a):
    if a[i]=='ev': d['eventos'].append({'quando':now,'texto':a[i+1]}); i+=2
    elif a[i]=='fase': d['fase']=a[i+1]; i+=2
    elif a[i]=='add':
        if not any(t['id']==a[i+1] for t in d['tarefas']):
            d['tarefas'].append({'id':a[i+1],'titulo':a[i+2],'estado':'pendente','nota':'','atualizado':now})
        i+=3
    elif a[i]=='task':
        for t in d['tarefas']:
            if t['id']==a[i+1]:
                t['estado']=a[i+2]; t['atualizado']=now
                if a[i+3]: t['nota']=a[i+3]
        i+=4
    else: sys.exit('st.py: argumento desconhecido %r (uso: task|ev|fase|add)'%a[i])
d['eventos']=d['eventos'][-30:]; d['updated']=now
json.dump(d,open(p+'.tmp','w'),ensure_ascii=False,indent=1); os.replace(p+'.tmp',p)
