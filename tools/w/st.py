# uso: flock status.lock python3 tools/w/st.py <id> <estado|-> "<evento>" ["<nota>"]
import json, sys, datetime
tid, estado, ev = sys.argv[1], sys.argv[2], sys.argv[3]
nota = sys.argv[4] if len(sys.argv) > 4 else None
now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
d = json.load(open('status.json'))
for t in d['tarefas'] if 'tarefas' in d else []:
    if t['id'] == tid:
        if estado != '-': t['estado'] = estado
        if nota is not None: t['nota'] = nota
        t['atualizado'] = now
d['eventos'].append({'quando': now, 'texto': ev})
json.dump(d, open('status.json', 'w'), ensure_ascii=False, indent=1)
