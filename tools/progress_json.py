#!/usr/bin/env python3
"""Resumo compacto do progresso (para o painel). Só leitura."""
import json, os, re, datetime, glob
R = "/root/jp983src"
s = json.load(open(f"{R}/status.json"))
def fase(i): return i.split(".")[0]
tarefas = [{"id": t["id"], "titulo": t.get("titulo", ""), "estado": t["estado"], "nota": (t.get("nota") or "")[:280]} for t in s["tarefas"]]
fases = {}
for t in tarefas:
    f = fases.setdefault(fase(t["id"]), {"total": 0, "feitas": 0})
    f["total"] += 1; f["feitas"] += t["estado"] == "feito"
log = open(f"{R}/runs/runner.log").read().splitlines()
ses = [l for l in log if "inicio sessao" in l]
ultimo = log[-1] if log else ""
estado = "parado" if any(os.path.exists(f"{R}/{x}") for x in ("DONE", "STOP", "NEEDS_HUMAN.md")) else ("rodando" if "inicio sessao" in ultimo else "entre sessões")
nh = open(f"{R}/NEEDS_HUMAN.md").read()[:600] if os.path.exists(f"{R}/NEEDS_HUMAN.md") else ""
iguais = None
for t in s["tarefas"][::-1]:
    m = re.search(r"make base[^0-9]*(?:\d+ → )?(\d+) IGUAL", t.get("nota") or "") or re.search(r"make base (\d+) IGUAL", " ".join(e["texto"] for e in s.get("eventos", [])[::-1]))
    if m: iguais = int(m.group(1)); break
print(json.dumps({
    "gerado": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "status_atualizado": s.get("updated"), "executor": estado, "sessoes": len(ses), "ultimo_log": ultimo[:160],
    "fases": fases, "tarefas": tarefas, "eventos": s.get("eventos", [])[-12:], "pergunta": nh,
    "funcoes_iguais_dll": iguais}, ensure_ascii=False))
