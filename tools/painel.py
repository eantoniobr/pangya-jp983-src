#!/usr/bin/env python3
"""Painel de progresso do jp983src (tarefas P1 e P2) -> out/painel/index.html + 1 linha em out/painel/historico.jsonl.

Só lê o repositório (mapas, saídas do comparador em out/, status.json, runs/runner*.log, out/PEDIDOS.md, out/V3, git log).
Dona: frente C (P2). Tarefa/fila nova aparece sozinha: o painel lê status.json; a frente de cada tarefa vem do campo
`frente` (se houver) ou de FRENTE_REGRAS; a fase vem do campo `fase`, do prefixo F<n> ou de FASE_APOIO.
Uso:  python3 tools/painel.py                 gera o painel e acrescenta 1 ponto ao histórico
      python3 tools/painel.py --sem-historico gera o painel sem mexer no histórico
      python3 tools/painel.py --reconstruir   refaz os pontos antigos do histórico (saídas guardadas em out/F*)

Métrica: % dos BYTES de código próprio do 983 cobertos por funções do nosso fonte que o comparador dá IGUAL
(e, à parte, IGUAL+QUASE). Conta por endereço do 983: cada endereço vale uma vez, função sem lugar único não conta.
  wangreal.dll  = comparação da dll ligada (make image -> codigo_resumo/funcoes.tsv), sem as libs (crt, thunks);
                  nos pontos antigos, as funções de `make base` (funcs.tsv) por endereço.
  ProjectG.exe  = funções de out/**/cmp/<unidade>/funcs.tsv (a mais nova de cada unidade) sobre map/projectg_funcs.tsv;
                  código próprio = tudo abaixo de 00c3d000 que não é unidade de biblioteca.
"""
import bisect, csv, datetime, glob, json, os, re, subprocess, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{R}/out/painel"
HIST = f"{OUT}/historico.jsonl"
EXE_FIM = 0xC3D000                      # depois disto: GameGuard/CRT (F3.1)
# resultados de experimento (A/B) que não valem como estado atual
CMP_FORA = ("/antes/", "/tmp/", "/ab/")
try:                                    # A127.1 (C63): unidades do 645 que saíram do build do 983 (pgbuild.FORA_983)
    sys.path.insert(0, f"{R}/tools/f32")
    from pgbuild import FORA_983 as _F983
except Exception:
    _F983 = set()
UNI_FORA = {re.sub(r"\.cpp$", "", u).replace("/", "_") for u in _F983}          # chave de pasta de cmp: src_projectg_x
UNI_FORA_K = {(u.split("/")[1], os.path.splitext(u.split("/")[-1])[0]) for u in _F983}  # ('projectg', 'x')
REGIOES = [(0x46D8D0, "UI nova RF"), (0x491CA0, "bloco de funções em linha"), (0x525CF0, "região B"),
           (0xB50000, "jogo"), (EXE_FIM, "engine/Fresh")]
GRUPOS = [  # chave, nome no painel, cor
    ("dll", "wangreal.dll", "--s2"),
    ("ProjectG", "ProjectG.exe · jogo", "--s1"),
    ("Wangreal", "ProjectG.exe · engine Wangreal", "--s4"),
    ("Fresh", "ProjectG.exe · Fresh (janelas)", "--s3"),
    ("shared", "ProjectG.exe · shared", "--s7"),
    ("novo", "ProjectG.exe · sistemas novos do JP", "--s1"),
    ("vao", "ProjectG.exe · entre unidades (a definir)", "--s1"),
]
FASES = [("F0", "Preparação: repositório, build, comparador, piloto"),
         ("F1", "wangreal.dll: cabeçalhos e tipos do 983"),
         ("F2", "wangreal.dll: código completo, link e teste"),
         ("F3", "ProjectG.exe: mapa, base, tipos e unidades em ondas"),
         ("F4", "Link do exe completo e teste no servidor"),
         ("F5", "Acabamento e entrega")]
FASE_APOIO = "F3"                       # tarefas sem prefixo F<n> (V*, P*, D*…) e sem campo `fase`
# frente de uma tarefa sem campo `frente`: primeira regra que casa; senão A
FRENTE_REGRAS = [(r"E-|F3\.6E", "E"), (r"D-|F3\.6", "D"), (r"F3\.7", "B"), (r"V[3-9]|V\d\d|D\d|P[2-9]|C-", "C"), (r"F2\.1[2-9]|W\d", "W")]  # W: F2.12 em diante (12/10)
FRENTE_NOME = {"A": "caminho do jogo e estrutura (layout, UI do 983, RF ligada) · Opus", "B": "sistemas novos do JP (biblioteca RF) · Sonnet",
               "C": "testes do exe pelo robô, prioridades e painel · Opus", "D": "unidades alteradas no 983: jogo (F3.6) · Sonnet",
               "E": "unidades alteradas no 983: interface (F3.6E) · Sonnet",
               "W": "wangreal.dll (regressões do teste no PC)"}
JP_INI = 0x46D8D0                       # abaixo disto: biblioteca Refresh (RF), F3.7.13
# sistema de out/F3.7/**/sistemas.tsv -> (nome no painel, tarefa da fila da frente B)
SISTEMAS = {
    "controladores": ("Controladores de item/efeito", "F3.7.2"),
    "dados_de_jogo_GD": ("Dados de jogo (GD)", "F3.7.3"), "regra_subregra": ("Regras novas de jogo", "F3.7.3"),
    "clima": ("Clima", "F3.7.3"), "holeinone": ("Hole-in-one", "F3.7.3"),
    "lobby_atores": ("Atores do lobby e bonecos", "F3.7.4"), "salas_lobby": ("Salas e lobby", "F3.7.5"),
    "ui_base": ("Base nova de telas", "F3.7.6"), "fx": ("Efeitos (FxInterpreter)", "F3.7.7"),
    "grandprix": ("Grand Prix", "F3.7.8"), "clubset_workshop": ("Oficina de tacos", "F3.7.9"),
    "cartas_alquimia": ("Cartas e alquimia", "F3.7.10"), "quests_presenca": ("Missões, conquistas e presença", "F3.7.10"),
    "lojas_pontos": ("Lojas e pontos", "F3.7.11"), "guilda_social": ("Guilda e social", "F3.7.11"),
    "campeonato": ("Campeonato", "F3.7.11"), "rede_web": ("Rede e web", "F3.7.11"), "outros": ("Outros", "F3.7.11"),
    "selfdesign": ("Self Design", "F3.7.12"), "arin2014_eventos": ("Eventos (Arin 2014, oficina 2013)", "F3.7.12"),
    "rf_dialogos": ("Telas novas (diálogos RF)", "F3.7.12"), "rf_biblioteca": ("Biblioteca de telas Refresh (RF)", "F3.7.13"),
    "sem_classe": ("Trechos ainda sem dono", "F3.7.14"),
}


def tsv(path):
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def agora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def git(*a):
    try:
        return subprocess.run(["git", "-C", R, *a], capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return ""


# ---------------------------------------------------------------- wangreal.dll
def dll_image(d):
    """Comparação da dll ligada: bytes do 983 por classe, sem as libs. Devolve (total, igual, quase, por_obj)."""
    tot = ig = qu = 0
    por = {}
    for r in tsv(f"{d}/funcoes.tsv"):
        obj, uni = r["obj_nosso"], r["unidade983"]
        b = int(r["bytes983"]) if r["bytes983"].isdigit() else 0
        if obj.startswith("lib:") or uni in ("crt", "thunks_import"):
            continue
        nome = obj[:-4] if obj.endswith(".obj") else (uni if obj == "-" else obj)
        if nome.startswith("(funclets"):
            nome = "(tratadores de exceção)"
        p = por.setdefault(nome, [0, 0, 0])
        p[0] += b; tot += b
        if r["classe"] == "IGUAL":
            p[1] += b; ig += b
        elif r["classe"] == "QUASE":
            p[2] += b; qu += b
    return tot, ig, qu, por


def dll_base(path):
    """`make base`: bytes do 983 cobertos por função IGUAL / QUASE, por endereço."""
    best = {}
    for r in tsv(path):
        va, c = r["va983"], r["classe"]
        if va in ("-", "") or c not in ("IGUAL", "QUASE"):
            continue
        b = int(r["bytes_983"] or 0)
        o = best.get(va)
        if o is None or (c == "IGUAL" and o[0] != "IGUAL"):
            best[va] = (c, b)
    ig = sum(b for c, b in best.values() if c == "IGUAL")
    return ig, ig + sum(b for c, b in best.values() if c == "QUASE")


def achar_image():
    c = [d for d in glob.glob(f"{R}/out/**/image", recursive=True) if os.path.exists(f"{d}/funcoes.tsv")]
    return max(c, key=lambda d: os.path.getmtime(f"{d}/funcoes.tsv")) if c else None


# ---------------------------------------------------------------- ProjectG.exe
def unidade_do_obj(arquivo):
    """build/pg/obj/src/projectg/x.obj ou src/projectg/x.cpp -> ('projectg', 'x')"""
    a = arquivo.replace("\\", "/")
    m = re.search(r"build/B/obj/(.+)\.obj$", a)          # unidades novas do JP (frente B)
    if m:
        return ("jp", m.group(1).lower())
    m = re.search(r"src/([^/]+)/(.+)\.(?:obj|cpp|c)$", a)
    return (m.group(1).lower(), m.group(2).lower()) if m else None


def chave_rebang(u):
    """source/client/ProjectG/x.cpp -> ('projectg', 'x'); source/shared/x.cpp -> ('shared', 'x')"""
    p = u.replace("\\", "/").lower().split("/")
    base = os.path.splitext(p[-1])[0]
    pasta = p[-2] if len(p) > 1 else ""
    return ({"wangreal": "engine"}.get(pasta, pasta), base)


def cmp_dirs(so=None):
    """unidade (pasta de cmp) -> funcs.tsv mais novo. `so` = raiz única (para reconstruir pontos antigos)."""
    r = {}
    pads = [f"{so}/cmp/*/funcs.tsv"] if so else [f"{R}/out/**/cmp/*/funcs.tsv"]
    for pad in pads:
        for p in glob.glob(pad, recursive=True):
            if not so and any(x in p for x in CMP_FORA):
                continue
            k = os.path.basename(os.path.dirname(p))
            if "/out/F3.7/" in p:       # frente B: cmp/<unidade>/ sem o prefixo src_
                k = "jp:" + k
            elif not k.startswith("src_") or (not so and k in UNI_FORA):
                continue
            if k not in r or os.path.getmtime(p) > os.path.getmtime(r[k]):
                r[k] = p
    return r


class Exe:
    def __init__(self):
        self.units = tsv(f"{R}/map/projectg_units.tsv")
        self.grupo = {u["unidade"]: u["grupo"] for u in self.units}
        self.F = []                     # (va, tam, grupo, unidade)
        for f in tsv(f"{R}/map/projectg_funcs.tsv"):
            va = int(f["f983"], 16)
            if va >= EXE_FIM:
                continue
            onde, uni = f["onde"], f["unidade"]
            g = self.grupo.get(uni) if onde == "nucleo" else ("novo" if onde == "vao_novo" else "vao")
            if g is None or g == "lib":
                continue
            self.F.append((va, int(f["tam"]), g, uni if onde == "nucleo" else ""))
        self.F.sort()
        self.vas = [f[0] for f in self.F]
        self.total = {}
        for _, t, g, _u in self.F:
            self.total[g] = self.total.get(g, 0) + t

    def cobertura(self, dirs):
        """Devolve (por grupo {g: [igual, quase]}, por unidade do nosso fonte {chave: contagem própria})."""
        best = {}                       # va -> (classe, bytes)
        dif = {}                        # va -> bytes do 983 de função escrita que o comparador dá DIFERENTE
        proprias = {}                   # ('projectg','x') -> [n, B, B_igual, B_quase, n_igual]
        for k, p in dirs.items():
            key = None
            for r in tsv(p):
                if key is None:
                    key = unidade_do_obj(r["arquivo"])
                c = r["classe"]
                b = int(r["bytes_983"] or 0) if c in ("IGUAL", "QUASE") else 0
                if r["propria"] == "1":
                    q = proprias.setdefault(key, [0, 0, 0, 0, 0])
                    bo = int(r["bytes_obj"] or 0)
                    q[0] += 1; q[1] += bo
                    if c == "IGUAL":
                        q[2] += bo; q[4] += 1
                    elif c == "QUASE":
                        q[3] += bo
                va = r["va983"]
                if c == "DIFERENTE" and va not in ("-", ""):
                    dif[va] = max(dif.get(va, 0), int(r["bytes_983"] or 0))
                if b and va not in ("-", ""):
                    o = best.get(va)
                    if o is None or (c == "IGUAL" and o[0] != "IGUAL"):
                        best[va] = (c, b)
            if key is not None:
                proprias.setdefault(key, [0, 0, 0, 0, 0])
        g = {k: [0, 0] for k in self.total}
        por_uni = {}                    # unidade do mapa -> [igual, quase] em bytes do 983 dentro da faixa dela
        vs = sorted((int(v, 16), c, b) for v, (c, b) in best.items())
        self.porva = []                 # (va, classe, bytes) dentro do código próprio; classe I, Q ou D
        self.escritas = set()           # começos de função do mapa que têm função nossa (qualquer classe com par)
        for v, b in dif.items():
            if v in best:
                continue
            va = int(v, 16)
            j = bisect.bisect_right(self.vas, va) - 1
            if j >= 0 and va < self.F[j][0] + self.F[j][1]:
                self.porva.append((va, "D", min(b, self.F[j][0] + self.F[j][1] - va)))
                if va == self.F[j][0]:
                    self.escritas.add(va)
        for i, (va, c, b) in enumerate(vs):
            j = bisect.bisect_right(self.vas, va) - 1
            if j < 0:
                continue
            fva, ft, fg, fu = self.F[j]
            if va >= fva + ft:          # fora do código próprio (lib, enchimento, GameGuard)
                continue
            if i + 1 < len(vs):
                b = min(b, vs[i + 1][0] - va)
            k = 0 if c == "IGUAL" else 1
            g[fg][k] += b
            self.porva.append((va, "IQ"[k], b))
            if va == fva:
                self.escritas.add(va)
            if fu:
                por_uni.setdefault(fu, [0, 0])[k] += b
        self.porva.sort()
        return g, proprias, por_uni

    def faixa(self, ini, fim):
        """Bytes [igual, quase, diferente] das nossas funções em [ini, fim) do 983 (depois de cobertura())."""
        r = {"I": 0, "Q": 0, "D": 0}
        i = bisect.bisect_left(self.porva, (ini,))
        while i < len(self.porva) and self.porva[i][0] < fim:
            r[self.porva[i][1]] += self.porva[i][2]; i += 1
        return [r["I"], r["Q"], r["D"]]


# ---------------------------------------------------------------- histórico
def ponto(quando, dll_tot, dll_ig, dll_iq, exe_tot, exe_ig, exe_iq, **extra):
    return dict(date=quando, dll_total=dll_tot, dll_igual=dll_ig, dll_iq=dll_iq,
                exe_total=exe_tot, exe_igual=exe_ig, exe_iq=exe_iq, **extra)


def data_commit(path):
    return git("log", "-1", "--format=%cI", "--", path).strip()


def reconstruir(exe, dll_tot):
    """Pontos antigos a partir das saídas guardadas: `make base` de cada tarefa da dll e as duas bases do exe."""
    pts = []
    exe_tot = sum(exe.total.values())
    for p in sorted(glob.glob(f"{R}/out/F[0-2]*/**/base/funcs.tsv", recursive=True)):
        quando = data_commit(os.path.relpath(p, R))
        if not quando:
            continue
        ig, iq = dll_base(p)
        img = os.path.dirname(os.path.dirname(p)) + "/image"
        if os.path.exists(f"{img}/funcoes.tsv"):      # já havia dll ligada: vale a comparação da dll inteira
            _, ig, qu, _ = dll_image(img)
            iq = ig + qu
        pts.append(ponto(quando, dll_tot, ig, iq, exe_tot, 0, 0, origem=os.path.relpath(os.path.dirname(p), R), reconstruido=True))
    pts.sort(key=lambda r: datetime.datetime.fromisoformat(r["date"]))
    ult = pts[-1] if pts else None
    for raiz in ("out/F3.2", "out/F3.4/depois"):
        d = cmp_dirs(f"{R}/{raiz}")
        quando = data_commit(f"{raiz}/base.tsv")
        if not d or not quando:
            continue
        g, _, _ = exe.cobertura(d)
        ig = sum(v[0] for v in g.values()); iq = ig + sum(v[1] for v in g.values())
        pts.append(ponto(quando, dll_tot, ult["dll_igual"] if ult else 0, ult["dll_iq"] if ult else 0, exe_tot, ig, iq,
                         origem=raiz, reconstruido=True))
    return pts


def ler_hist():
    if not os.path.exists(HIST):
        return []
    return [json.loads(l) for l in open(HIST, encoding="utf-8") if l.strip()]


# ---------------------------------------------------------------- estado geral
def nat(i):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", i)]


def frente_de(t):
    if t.get("frente"):
        return t["frente"]
    for pad, f in FRENTE_REGRAS:
        if re.match(pad, t["id"]):
            return f
    return "A"


def fase_de(t):
    if t.get("fase"):
        return t["fase"]
    m = re.match(r"F(\d)", t["id"])
    return "F" + m.group(1) if m else FASE_APOIO


def hospedagem(suf=""):
    """Estado de uma frente pelo runs/runner<suf>.log e pelos arquivos STOP, DONE<suf>, NEEDS_HUMAN<suf>.md."""
    log = []
    if os.path.exists(f"{R}/runs/runner{suf}.log"):
        log = open(f"{R}/runs/runner{suf}.log", encoding="utf-8", errors="replace").read().splitlines()
    ult = log[-1] if log else ""
    ses = [int(m.group(1)) for l in log for m in [re.search(r"inicio sessao (\d+)", l)] if m]
    n = ses[-1] if ses else 0
    idade = None
    try:
        idade = (datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(ult[:25])).total_seconds() / 3600
    except ValueError:
        pass
    nhp = f"{R}/NEEDS_HUMAN{suf}.md"
    if os.path.exists(f"{R}/DONE{suf}"):
        est, txt = "parado", "concluída"
    elif os.path.exists(nhp):
        est, txt = "parado", "parada: esperando você responder"
    elif os.path.exists(f"{R}/STOP"):
        est, txt = "parado", "parada a pedido"
    elif not log:
        est, txt = "parado", "ainda não começou"
    elif "inicio sessao" in ult and idade is not None and idade > 3.2:      # a sessão tem teto de 3 h
        est, txt = "pausa", f"sem sinal há {idade:.0f} h (sessão {n})"
    elif "inicio sessao" in ult:
        est, txt = "rodando", f"rodando (sessão {n})"
    elif "limite atingido" in ult:
        est, txt = "pausa", "em pausa: limite de uso"
    else:
        est, txt = "pausa", f"entre sessões (última: {n})"
    nh = open(nhp, encoding="utf-8", errors="replace").read()[:700] if os.path.exists(nhp) else ""
    return dict(estado=est, texto=txt, sessao=n, ultimo=ult[:25], pergunta=nh)


def frentes(st):
    """Uma entrada por frente: as dos runs/runner*.log mais as que tiverem tarefa no status.json."""
    ids = ({"A"} | {frente_de(t) for t in st["tarefas"]}) - {"W"}   # W concluída (DONE-W) sai do painel
    for p in glob.glob(f"{R}/runs/runner-*.log"):
        ids.add(os.path.basename(p)[7:-4])
    ids -= {f for f in ids if os.path.exists(f"{R}/DONE-{f}")}   # frente concluída (DONE-X) sai do painel
    r = []
    for f in sorted(ids):
        h = hospedagem("" if f == "A" else "-" + f)
        ts = [t for t in st["tarefas"] if frente_de(t) == f]
        and_ = sorted((t for t in ts if t["estado"] == "em_andamento" and not any(
            o["id"].startswith(t["id"] + ".") for o in ts)), key=lambda t: t.get("atualizado", ""))
        pend = sorted((t for t in ts if t["estado"] == "pendente"), key=lambda t: nat(t["id"]))
        if f == "C":                    # a fila da C não é a ordem dos ids: P2, D1, depois V4…
            pend.sort(key=lambda t: (t["id"][0] != "P", t["id"][0] != "D", nat(t["id"])))
        cur = and_[-1] if and_ else pend[0] if pend else None
        h.update(id=f, nome=FRENTE_NOME.get(f, ""), feitas=sum(t["estado"] == "feito" for t in ts), total=len(ts),
                 tarefa=dict(id=cur["id"], titulo=cur.get("titulo", ""), agora=bool(and_)) if cur else None)
        r.append(h)
    return r


def fases(st):
    r = []
    for fid, nome in FASES:
        ts = [dict(id=t["id"], titulo=t.get("titulo", ""), estado=t["estado"], nota=(t.get("nota") or "")[:400],
                   frente=frente_de(t))
              for t in st["tarefas"] if fase_de(t) == fid]
        ts.sort(key=lambda t: nat(t["id"]))
        r.append(dict(id=fid, nome=nome, tarefas=ts))
    return r


def pedidos():
    """out/PEDIDOS.md: um pedido por título `## X → Y (data…) — texto`. Atendido = título com [ATENDIDO…]/[FEITO…]/~~."""
    p = f"{R}/out/PEDIDOS.md"
    r = []
    if not os.path.exists(p):
        return r
    for l in open(p, encoding="utf-8", errors="replace"):
        m = re.match(r"##\s+(.*?)(\w+)\s*(?:→|->)\s*(\w+)\s*(?:\(([^)]*)\))?\s*[—–-]*\s*(.*)", l)
        if not m:
            continue
        fechado = bool(re.search(r"ATENDID|FEIT[OA]\b|RESOLVID|FECHAD|~~|✔|✅", l, re.I))
        txt = re.sub(r"\[[^\]]*\]|~~", "", m.group(5)).strip()
        r.append(dict(de=m.group(2), para=m.group(3), quando=(m.group(4) or "").split(",")[0].strip(),
                      texto=txt[:170] + ("…" if len(txt) > 170 else ""), aberto=not fechado))
    return r


def asserts_v3():
    """Última rodada de `make layoutcheck` (out/V*/layoutcheck.tsv mais novo)."""
    c = glob.glob(f"{R}/out/V*/layoutcheck.tsv")
    if not c:
        return None
    p = max(c, key=os.path.getmtime)
    ok = falha = outros = 0
    falhas = []
    for r in tsv(p):
        if r["resultado"] == "ok":
            ok += 1
        elif r["resultado"] == "FALHA":
            falha += 1
            falhas.append(r["classe"])
        else:
            outros += 1
    quando = datetime.datetime.fromtimestamp(os.path.getmtime(p), datetime.timezone.utc).isoformat(timespec="seconds")
    return dict(ok=ok, falha=falha, outros=outros, total=ok + falha + outros, quando=quando, falhas=falhas[:60])


def sistemas_jp(exe, proprias):
    """Sistemas novos do JP (fila F3.7.x): bytes do 983 por sistema e quanto já tem função nossa.
    Devolve (lista de sistemas, quadrados do mapa de unidades, nº de unidades propostas)."""
    c = glob.glob(f"{R}/out/F3.7/**/unidades_novas.tsv", recursive=True)
    if not c:
        return [], [], 0
    rows = tsv(max(c, key=os.path.getmtime))
    S, quad, faixas = {}, [], []
    for r in rows:
        ini, fim = int(r["ini"], 16), int(r["fim"], 16)
        faixas.append((ini, fim))
        i, q, d = exe.faixa(ini, fim)
        b = int(r["bytes"] or 0)
        s = S.setdefault(r["sistema"] or "outros", [0, 0, 0, 0, 0, 0])
        s[0] += 1; s[1] += b; s[2] += i; s[3] += q; s[4] += d; s[5] += bool(i + q + d)
        nome = os.path.splitext(os.path.basename(r["arquivo"]))[0]
        pr = proprias.get(("jp", nome.lower()))
        u = dict(name=nome, group="novo", size=b, state="novo", obs=r["principal"] or r["sistema"])
        if pr and pr[1]:
            u.update(pi=round(100 * pr[2] / pr[1], 1), pq=round(100 * (pr[2] + pr[3]) / pr[1], 1), n=pr[0], n_igual=pr[4])
            u["state"] = "igual" if pr[4] == pr[0] else "quase" if u["pq"] >= 90 else "andamento"
        quad.append(u)
    # biblioteca Refresh: funções novas abaixo de JP_INI (fora das unidades propostas)
    rf = sum(t for va, t, g, _u in exe.F if g == "novo" and va < JP_INI)
    if rf:
        i, q, d = exe.faixa(0, JP_INI)
        S["rf_biblioteca"] = [0, rf, i, q, d, 0]
    out = []
    for k, (n, b, i, q, d, nf) in S.items():
        nome, tarefa = SISTEMAS.get(k, (k, ""))
        out.append(dict(key=k, nome=nome, tarefa=tarefa, unidades=n, com_codigo=nf, total=b, igual=i, quase=q, dif=d))
    out.sort(key=lambda x: (nat(x["tarefa"]) if x["tarefa"] else [99], -x["total"]))
    return out, quad, len(rows), faixas


# ---------------------------------------------------------------- principal
def main():
    args = sys.argv[1:]
    os.makedirs(OUT, exist_ok=True)
    st = json.load(open(f"{R}/status.json", encoding="utf-8"))
    exe = Exe()
    units = []

    # dll
    img = achar_image()
    dll_tot, dll_ig, dll_qu, por = dll_image(img) if img else (0, 0, 0, {})
    for nome, (b, ig, qu) in sorted(por.items(), key=lambda kv: -kv[1][0]):
        pi, pq = (100 * ig / b, 100 * (ig + qu) / b) if b else (0, 0)
        units.append(dict(name=nome, group="dll", size=b, pi=round(pi, 1), pq=round(pq, 1),
                          state="igual" if pi >= 99.5 else "quase" if pq >= 90 else "andamento"))

    # exe
    dirs = cmp_dirs()
    g, proprias, por_uni = exe.cobertura(dirs)
    comp = {}
    for d in sorted(glob.glob(f"{R}/out/**/base.tsv", recursive=True), key=os.path.getmtime):
        if any(x in d for x in CMP_FORA):
            continue
        for r in tsv(d):
            k = unidade_do_obj(r["unidade"])
            if k and k not in UNI_FORA_K:
                comp[k] = r["estado"]
    cont = {}
    for u in exe.units:
        if u["grupo"] == "lib":
            continue
        k = chave_rebang(u["unidade"])
        if k in UNI_FORA_K:                     # não existe no 983 (fora do build)
            continue
        firme = u["classe_mapa"] == "forte"     # nas outras o bytes983 é a faixa candidata (um vão inteiro)
        size = int((u["bytes983"] if firme else u["bytes645"]) or 0)
        pr = proprias.get(k)
        d = dict(name=u["unidade"].split("/")[-1], group=u["grupo"], size=size)
        if not firme:
            d["est"] = 1                        # tamanho estimado pelo 645 (sem faixa firme no 983)
        if u["estado_rebang"] == "obj" and pr is None:
            d["state"] = "semfonte"
        elif pr is None or pr[1] == 0:
            d["state"] = "importado"
            d["obs"] = "não compila ainda" if comp.get(k) == "nao_compila" else "sem função própria comparada"
        else:
            pi, pq = 100 * pr[2] / pr[1], 100 * (pr[2] + pr[3]) / pr[1]
            d.update(pi=round(pi, 1), pq=round(pq, 1), n=pr[0], n_igual=pr[4])
            d["state"] = "igual" if pr[4] == pr[0] else "quase" if pq >= 90 else "andamento" if pr[2] else "importado"
            if d["state"] == "importado":
                d["obs"] = "comparada: nenhuma função igual ainda"
        units.append(d)
        c = cont.setdefault(u["grupo"], [0, 0])
        c[0] += 1; c[1] += d["state"] == "igual"
    # sistemas novos do JP: cada unidade proposta pela frente B é um quadrado; onde ainda não há proposta, o vão inteiro
    sist, quad, jp_unidades, faixas = sistemas_jp(exe, proprias)
    units += quad
    fr = f"{R}/out/F3.3/fronteiras.tsv"
    if os.path.exists(fr):
        for r in tsv(fr):
            ini, fim = int(r["ini983"], 16), int(r["fim983"], 16)
            if r["classe_vao"] != "vao_novo" or fim > EXE_FIM or any(a < fim and ini < b for a, b in faixas):
                continue
            cls = [re.sub(r"\(\d+\)$", "", c.strip().lstrip("*")) for c in (r.get("classes_983 (*=classe que o 645 não tem)") or "").split(", ")]
            cls = [c for c in cls if c and len(c) < 40][:3]
            units.append(dict(name=f"{r['ini983']}–{r['fim983']}", group="novo", size=int(r["bytes_funcs"] or 0),
                              state="novo", obs=", ".join(cls)))
    c = cont.setdefault("novo", [0, 0])
    c[0] = sum(1 for u in units if u["group"] == "novo"); c[1] = sum(1 for u in units if u["group"] == "novo" and u["state"] == "igual")

    # métricas do critério FUNCIONAL
    # estado de compilação: o base.tsv mais novo de cada unidade (inclui o cabeçalho pré-compilado)
    compila = sum(1 for v in comp.values() if v == "ok")
    ncomp = sorted(f"{k[1]}.cpp" for k, v in comp.items() if v != "ok")
    jp_lista = [l.strip() for l in open(f"{R}/src/projectg/jp/units.txt", encoding="utf-8") if l.strip() and not l.startswith("#")] \
        if os.path.exists(f"{R}/src/projectg/jp/units.txt") else []
    jp_ok = sum(1 for l in jp_lista if ("jp", os.path.splitext(l)[0].lower()) in proprias)
    esc_b = sum(b for _va, _c, b in exe.porva)
    func = dict(unidades=len(comp), compilam=compila, nao_compilam=ncomp[:20],
                jp_propostas=jp_unidades, jp_escritas=len(jp_lista), jp_comparadas=jp_ok,
                funcoes_total=len(exe.F), funcoes_escritas=len(exe.escritas), bytes_escritos=esc_b,
                asserts=asserts_v3())

    grupos = [dict(key="dll", label="wangreal.dll", color="--s2", total=dll_tot, igual=dll_ig, quase=dll_qu,
                   units=len(por), units_igual=sum(1 for u in units if u["group"] == "dll" and u["state"] == "igual"))]
    for key, label, cor in GRUPOS[1:]:
        c = cont.get(key, [0, 0])
        grupos.append(dict(key=key, label=label, color=cor, total=exe.total.get(key, 0), igual=g.get(key, [0, 0])[0],
                           quase=g.get(key, [0, 0])[1], units=c[0], units_igual=c[1]))
    exe_tot = sum(exe.total.values())
    exe_ig = sum(v[0] for v in g.values()); exe_qu = sum(v[1] for v in g.values())

    # histórico
    if "--reconstruir" in args:
        velhos = [h for h in ler_hist() if not h.get("reconstruido")]
        pts = reconstruir(exe, dll_tot) + velhos
        pts.sort(key=lambda r: datetime.datetime.fromisoformat(r["date"]))
        with open(HIST + ".tmp", "w", encoding="utf-8") as f:
            for p in pts:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
        os.replace(HIST + ".tmp", HIST)
    gerado = agora()
    atual = ponto(gerado, dll_tot, dll_ig, dll_ig + dll_qu, exe_tot, exe_ig, exe_ig + exe_qu,
                  commit=git("rev-parse", "--short", "HEAD").strip(), sessao=hospedagem()["sessao"])
    NUM = ("dll_total", "dll_igual", "dll_iq", "exe_total", "exe_igual", "exe_iq")
    igual_a = lambda a, b: all(a.get(k) == b.get(k) for k in NUM)
    velho = ler_hist()
    # o servidor do painel regera a cada 2 min: só entra ponto novo quando algum número (ou o commit) muda
    if "--sem-historico" not in args and not (velho and igual_a(velho[-1], atual) and velho[-1].get("commit") == atual["commit"]):
        with open(HIST, "a", encoding="utf-8") as f:
            f.write(json.dumps(atual, ensure_ascii=False) + "\n")
    hist = ler_hist()
    hist = [h for i, h in enumerate(hist) if i == 0 or not igual_a(hist[i - 1], h)]     # degraus só onde algo mudou
    if not hist or not igual_a(hist[-1], atual):
        hist.append(atual)

    feitas = sum(1 for t in st["tarefas"] if t["estado"] == "feito")
    D = dict(
        generated=gerado, host=hospedagem(), frentes=frentes(st), pedidos=pedidos(), sistemas=sist, func=func, commit=git("log", "-1", "--format=%h %s").strip()[:140],
        dll=dict(total=dll_tot, igual=dll_ig, quase=dll_qu, fonte=os.path.relpath(img, R) if img else ""),
        exe=dict(total=exe_tot, igual=exe_ig, quase=exe_qu, comparadas=len(dirs),
                 funcoes=sum(v[0] for v in proprias.values()), funcoes_igual=sum(v[4] for v in proprias.values())),
        groups=grupos, history=hist, units=units, fases=fases(st), fase=st.get("fase", ""),
        tarefas=dict(total=len(st["tarefas"]), feitas=feitas),
        eventos=st.get("eventos", [])[-14:],
    )
    modelo = open(f"{R}/tools/painel_modelo.html", encoding="utf-8").read()
    dados = json.dumps(D, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = modelo.replace("/*__DADOS__*/", "window.PROGRESS = " + dados + ";")
    with open(f"{OUT}/index.html.tmp", "w", encoding="utf-8") as f:
        f.write(html)
    os.replace(f"{OUT}/index.html.tmp", f"{OUT}/index.html")

    tot = dll_tot + exe_tot
    p = lambda a, b: f"{100 * a / b:.2f}%" if b else "–"
    print(f"painel: {OUT}/index.html ({len(html)} B), histórico {len(hist)} pontos")
    print(f"  wangreal.dll  IGUAL {dll_ig} de {dll_tot} B = {p(dll_ig, dll_tot)}; +QUASE {p(dll_ig + dll_qu, dll_tot)}  [{D['dll']['fonte']}]")
    print(f"  ProjectG.exe  IGUAL {exe_ig} de {exe_tot} B = {p(exe_ig, exe_tot)}; +QUASE {p(exe_ig + exe_qu, exe_tot)}  [{len(dirs)} unidades comparadas]")
    print(f"  total         IGUAL {dll_ig + exe_ig} de {tot} B = {p(dll_ig + exe_ig, tot)}; +QUASE {p(dll_ig + exe_ig + dll_qu + exe_qu, tot)}")
    for x in grupos:
        print(f"    {x['label']:44s} {x['igual']:8d} + {x['quase']:8d} de {x['total']:8d} B  {p(x['igual'], x['total'])}")
    for f in D["frentes"]:
        print(f"  frente {f['id']}: {f['texto']}; {f['feitas']}/{f['total']} tarefas; " + (f"{'agora' if f['tarefa']['agora'] else 'próxima'}: {f['tarefa']['id']}" if f["tarefa"] else "sem tarefa"))
    a = func["asserts"] or {}
    print(f"  compilam {func['compilam']}/{func['unidades']} unidades + {func['jp_comparadas']} novas do JP (de {func['jp_propostas']} propostas); "
          f"funções escritas {func['funcoes_escritas']}/{func['funcoes_total']}; asserts ok {a.get('ok')} falha {a.get('falha')}; "
          f"pedidos abertos {sum(p['aberto'] for p in D['pedidos'])}/{len(D['pedidos'])}; sistemas JP {len(sist)}")
    cs = {}
    for u in units:
        cs[u["state"]] = cs.get(u["state"], 0) + 1
    print("  unidades:", ", ".join(f"{k} {v}" for k, v in sorted(cs.items())))


if __name__ == "__main__":
    main()
