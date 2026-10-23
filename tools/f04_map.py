#!/usr/bin/env python3
"""F0.4: mapa função da wangreal.dll 983 -> par no 839 -> função do 645 -> arquivo .cpp do rebang.

Uso: f04_map.py [dir_exports=build/f04] [saida_mapa=map/wangreal_funcs.tsv] [saida_out=out/F0.4]
Entradas (geradas por tools/f04_export.sh e pelos passos descritos no NOTES, sessão 4):
  f983w/f839w/f645w.jsonl      funções (J3Export) das três dlls
  m983_839/pairs.tsv           casamento 983<->839 (j3_match.py, mesmo compilador)
  /root/kr839/out/wr/m3/pairs.tsv  casamento 645<->839 da A1 (715 pares)
  pdb/{pub,sc,mod}.txt         cvdump do PDB do 645: nome decorado, contribuição de seção (função -> .obj)
  out/F0.3/dev645/funcs.tsv    cmpfunc da device do 645 compilada com VS2010 x dll 983 (nome decorado -> VA 983)
Três caminhos independentes dão o nome/arquivo de uma função do 983:
  cadeia  983 -> 839 (j3) -> 645 (m3)                      [endereço do 645 -> PDB -> .obj]
  nome    983 -> 839 (j3) -> nome IMPORTED no Ghidra do 839 (A1+A3) -> função do 645 de nome único
  cmp     .obj do 645 recompilado, achado no 983 pelo cmpfunc (bytes/vizinhança)
O arquivo das funções sem nome vem da ORDEM DE ENDEREÇO: a dll não tem LTCG e mantém as funções de cada .obj juntas,
na ordem do fonte; as âncoras (funções próprias de arquivo conhecido) delimitam as faixas de cada .obj.
"""
import collections, json, os, re, sys

D = sys.argv[1] if len(sys.argv) > 1 else "build/f04"
MAPA = sys.argv[2] if len(sys.argv) > 2 else "map/wangreal_funcs.tsv"
OUT = sys.argv[3] if len(sys.argv) > 3 else "out/F0.4"
M3 = "/root/kr839/out/wr/m3/pairs.tsv"
CMP = (os.environ.get("F04_CMP") or "out/F0.4/cmp645/funcs.tsv" if os.path.exists("out/F0.4/cmp645/funcs.tsv") else "out/F0.3/dev645/funcs.tsv,out/F0.3/bitmap/funcs.tsv").split(",")
SRC = {  # .obj do 645 -> fonte no rebang (source/client/...)
    "device": "device/device.cpp", "wime": "device/wime/wime.cpp", "dimouse": "device/wdinput/dimouse.cpp",
    "dikeyboard": "device/wdinput/dikeyboard.cpp", "directinput": "device/wdinput/directinput.cpp",
    "wd3d8": "device/wd3d8.cpp", "wd3d": "device/wd3d.cpp", "bitmap": "Wangreal/source/bitmap.cpp",
    "wdxtc": "Wangreal/source/wdxtc.cpp",
}
# trechos sem .obj do 645 (unidades novas do 839/983 e runtime); rótulos provisórios, pelo conteúdo (strings/RTTI/imports)
NOVOS = [("10001000", "10008dc0", "novo:stl_inicio"),      # modelos std:: (bitset/map/string) do 1º .obj; sem código próprio visível
         ("10008dc0", "10012440", "novo:shparam_839"),     # NUM_MAX_BONES_PER_BATCH, D3DXGetShaderInputSemantics (novo no 839)
         ("10048060", "10048122", "device"),
         ("10048122", "100481d0", "thunks_import"),
         ("100481d0", "10058480", "novo:wxshadermtl_839"), # vtable WxShaderMtl, WVDSHBASICUSERPARAMSEMANTIC_* (novo no 839)
         ("10059990", "1005bf60", "novo:lang_983"),        # korea.dat/japan.dat, std::list/vector (SÓ no 983)
         ("1005bf60", "1005f9c8", "runtime:crt_math"),     # CRT (DllMain CRT, onexit, cookie), _CIsqrt..., stubs dobrados pelo ICF
         ("1005f9c8", "10061b50", "funclets_eh")]
CONF = {"alta": 3, "media": 2, "gemea": 1, "baixa": 0}


def load(p):
    return collections.OrderedDict((d["a"], d) for d in map(json.loads, open(p, encoding="utf-8")))


def is_tpl(name):
    """Nome de modelo/STL/CRT: COMDAT que o linker põe no primeiro .obj que o usa (não serve de âncora de arquivo)."""
    return bool(re.search(r"<|^std::|^_|`|^operator|^FUN_|^thunk_|^Catch|^Unwind|::WList|^mem|^str", name))


A, B, C = load(f"{D}/f983w.jsonl"), load(f"{D}/f839w.jsonl"), load(f"{D}/f645w.jsonl")

# ---- 645: endereço -> nome decorado e .obj (PDB)
pub = collections.defaultdict(list)
for l in open(f"{D}/pdb/pub.txt"):
    m = re.match(r"S_PUB32: \[0001:([0-9A-F]{8})\], Flags: \w+, (\S+)", l)
    if m: pub["%08x" % (0x10001000 + int(m.group(1), 16))].append(m.group(2))
mods = {}
for l in open(f"{D}/pdb/mod.txt"):
    m = re.match(r"([0-9A-F]{4}) (.*)", l.strip())
    if m:
        o = re.findall(r'"([^"]*)"', m.group(2))
        if o: mods[m.group(1)] = (re.split(r"[\\/]", o[-1])[-1].lower().replace(".obj", ""), len(o) > 1 and "wangreal" not in o[0].lower())
sc = []
for l in open(f"{D}/pdb/sc.txt"):
    m = re.match(r"\s+([0-9A-F]{4})\s+0001:([0-9A-F]{8})\s+([0-9A-F]{8})", l)
    if m: sc.append((0x10001000 + int(m.group(2), 16), int(m.group(3), 16), m.group(1)))
sc.sort()


def obj645(a):
    """(.obj, é_lib_externa) da função do 645 no endereço a."""
    v = int(a, 16)
    lo, hi = 0, len(sc)
    while lo < hi:
        mid = (lo + hi) // 2
        if sc[mid][0] <= v: lo = mid + 1
        else: hi = mid
    if lo and v < sc[lo - 1][0] + sc[lo - 1][1]: return mods.get(sc[lo - 1][2], ("?", True))
    return ("?", True)


n645 = collections.defaultdict(list)
for c, d in C.items(): n645[d["n"]].append(c)

# ---- pares
p98 = {}   # a983 -> (b839, conf, fontes, igual)
for l in open(f"{D}/m983_839/pairs.tsv"):
    p = l.rstrip("\n").split("\t")
    p98[p[0]] = (p[1], p[2], p[3], p[4])
m3 = {}    # b839 -> (c645, conf, origem)
for l in open(M3):
    p = l.rstrip("\n").split("\t")
    m3[p[1]] = (p[0], p[4], p[3])

# ---- cmpfunc (device do 645 recompilada com VS2010 x dll 983); vários símbolos por VA por causa do /OPT:ICF
cmpva = collections.defaultdict(list)   # va983 -> [(decorado, obj, propria, classe, pct, origem)]
for f in CMP:
    if not os.path.exists(f): continue
    for r in [l.rstrip("\n").split("\t") for l in open(f)][1:]:
        if len(r) < 7 or not re.fullmatch(r"[0-9a-f]{8}", r[5]): continue
        obj = os.path.basename(r[0]).rsplit(".", 1)[0]
        cmpva[r[5]].append((r[1], obj, r[2] == "1", r[3], float(r[4]), r[6]))

# ---- linha por função do 983
rows = []
st = collections.Counter()
val = collections.Counter()
div = []
for a, d in A.items():
    r = dict(va=a, sz=d["sz"], ni=d["ni"], n983=d["n"], src983=d["src"], va839="-", conf839="-", igual839="-",
             va645="-", nome="-", decorado="-", conf="-", via="-", obj="-", obj_via="-", cls="")
    b = p98.get(a)
    cadeia = nome_c = None
    if b:
        r.update(va839=b[0], conf839=b[1], igual839=b[3])
        ok98 = CONF[b[1]] >= 2 or (b[1] == "gemea")      # gemea: corpo idêntico, mas qual das vizinhas é incerto
        db = B[b[0]]
        if b[0] in m3 and m3[b[0]][0] in C:
            c, cf, org = m3[b[0]]
            cadeia = (c, min(CONF[cf], CONF[b[1]] if b[1] != "gemea" else 1))
        if db["src"] == "IMPORTED" and len(n645.get(db["n"], ())) == 1:
            nome_c = (n645[db["n"]][0], min(2, CONF[b[1]] if b[1] != "gemea" else 1) if not cadeia else 2)
        if db["src"] == "IMPORTED": r["nome"] = db["n"]
    c645 = None
    if cadeia and nome_c:
        val["cadeia x nome: " + ("concordam" if cadeia[0] == nome_c[0] else "DIVERGEM")] += 1
        if cadeia[0] != nome_c[0]: div.append((a, cadeia[0], C[cadeia[0]]["n"], "cadeia", "-", C[nome_c[0]]["n"], "nome839", "-"))
    if nome_c: c645, cf, via = nome_c[0], nome_c[1], "nome839"
    if cadeia and (not nome_c or cadeia[1] >= 2): c645, cf, via = cadeia[0], cadeia[1], "cadeia" + ("+nome" if nome_c and nome_c[0] == cadeia[0] else "")
    ks = cmpva.get(a)
    if ks:
        last = C[c645]["n"].split("::")[-1] if c645 else ""
        # estáticas não têm público no PDB: aí vale o nome simples no início do decorado
        good = [k for k in ks if c645 and (k[0] in pub.get(c645, ()) or (not pub.get(c645) and k[0].startswith(("?" + last + "@", "_" + last + "@"))) or k[0] == "_" + last)]
        k = max(good or ks, key=lambda k: (k[3] == "IGUAL", k[2], k[4]))
        dec = k[0]
        if c645:
            val["cmp x cadeia/nome: " + ("concordam" if good else "divergem")] += 1
            if not good:
                r["cls"] += "conflito_cmp;"
                div.append((a, c645, C[c645]["n"], via, ("baixa", "gemea", "media", "alta")[cf], dec, k[3], k[5]))
        if good or not c645 or (k[3] == "IGUAL" and k[5].startswith("bytes") and "*" not in k[5] and (cf < 2 or is_tpl(C[c645]["n"]))):
            r["decorado"] = dec
            if good:
                via = "cmp+" + via
                if k[3] == "IGUAL": cf = 3
            else:
                via = "cmp"
                cf = 3 if k[3] == "IGUAL" and k[5] == "bytes" else 2 if k[3] in ("IGUAL", "QUASE") else 0
                c645 = next((x for x, ds in pub.items() if dec in ds), None)
            r["cmp"] = f"{k[3]}:{k[4]*100:.0f}"
            if k[2]: r["obj"], r["obj_via"] = k[1], "cmp"
    if c645:
        r["va645"] = c645
        r["conf"] = ("baixa", "gemea", "media", "alta")[cf]
        r["via"] = via
        if r["nome"] == "-" or via.startswith("cadeia") or via.startswith("cmp"): r["nome"] = C[c645]["n"]
        if r["decorado"] == "-" and len(pub.get(c645, ())) == 1: r["decorado"] = pub[c645][0]
        o, ext = obj645(c645)
        r["o645"], r["ext645"] = o, ext
    rows.append(r)

# ---- faixas de .obj por ordem de endereço
# âncora = função com par 645 de confiança >= media, não-modelo, de .obj próprio (device/engine), ou própria no cmpfunc
anc = []
for i, r in enumerate(rows):
    o = None
    if r["obj_via"] == "cmp" and r.get("cmp", "").startswith(("IGUAL", "QUASE")): o = r["obj"]
    elif r["va645"] != "-" and r["conf"] in ("alta", "media") and not r.get("ext645") and r.get("o645") in SRC \
            and not is_tpl(r["nome"]):
        o = r["o645"]
    if o: anc.append((i, o))
# segmenta: sequência de âncoras -> blocos; âncora isolada que quebra um bloco longo é tratada como fora de ordem
blocks = []
for i, o in anc:
    if blocks and blocks[-1][0] == o: blocks[-1][2] = i; blocks[-1][3] += 1
    else: blocks.append([o, i, i, 1])
changed = True
while changed:                       # absorve bloco de 1-2 âncoras cercado pelo mesmo .obj
    changed = False
    for j in range(1, len(blocks) - 1):
        if blocks[j][3] <= 2 and blocks[j - 1][0] == blocks[j + 1][0] and blocks[j - 1][3] + blocks[j + 1][3] >= 6:
            st["ancoras_fora_de_ordem"] += blocks[j][3]
            blocks[j - 1][2] = blocks[j + 1][2]; blocks[j - 1][3] += blocks[j + 1][3]
            del blocks[j:j + 2]; changed = True; break
for o, i0, i1, n in blocks:
    for i in range(i0, i1 + 1):
        if rows[i]["obj"] == "-": rows[i]["obj"], rows[i]["obj_via"] = o, "faixa"
# entre blocos: unidade nova do 839/983 ou fronteira indefinida
gaps = []
prev_end, prev_o = -1, "inicio"
for o, i0, i1, n in blocks + [["fim", len(rows), len(rows), 0]]:
    if i0 - prev_end > 1: gaps.append((prev_end + 1, i0 - 1, prev_o, o))
    prev_end, prev_o = i1, o

for r in rows:
    if r["obj"] == "-":
        for lo, hi, lab in NOVOS:
            if lo <= r["va"] < hi: r["obj"], r["obj_via"] = lab, "trecho"; break

# ---- classe de cada função
IMP = re.compile(r"^[A-Za-z0-9_]+\.(DLL|dll)::")
for r in rows:
    n = r["n983"]
    c = r["cls"]
    if IMP.match(n) or A[r["va"]]["th"]: kind = "thunk_import"
    elif n.startswith(("Unwind@", "Catch")): kind = "funclet_eh"
    elif r["src983"] == "ANALYSIS" and not n.startswith("FUN_"): kind = "crt"
    elif r.get("cmp", "").startswith("IGUAL"): kind = "igual_645"
    elif r.get("cmp", "").startswith("QUASE"): kind = "quase_645"
    elif r["va645"] != "-" and r["conf"] in ("alta", "media"): kind = "alterada_645"
    elif r["va645"] != "-": kind = "par645_incerto"
    else: kind = "sem_par_645"
    r["kind"] = kind
    r["d839"] = {"hx": "igual", "hr": "so_imediatos", "hm": "mnemonicos", "dif": "difere", "-": "sem_par"}[r["igual839"]]
    r["cls"] = c.rstrip(";")

os.makedirs(OUT, exist_ok=True)
cols = ["va", "sz", "ni", "kind", "d839", "va839", "conf839", "va645", "conf", "via", "obj", "obj_via", "cmp", "nome", "decorado", "cls"]
with open(MAPA, "w", encoding="utf-8") as o:
    o.write("# wangreal.dll 983: função -> par 839 -> função 645 -> .obj/fonte. Gerado por tools/f04_map.py (não editar à mão)\n")
    o.write("\t".join(cols) + "\n")
    for r in rows: o.write("\t".join(str(r.get(c, "-") or "-") for c in cols) + "\n")

with open(f"{OUT}/divergencias.tsv", "w", encoding="utf-8") as o:
    o.write("va983\tva645\tnome_cadeia\tvia\tconf\toutro_caminho\tclasse_cmp\torigem_cmp\n")
    for x in div: o.write("\t".join(map(str, x)) + "\n")
# mapa candidato nome decorado -> VA (para o cmpfunc conferir no endereço certo): só alta/media, sem ambiguidade
cand = collections.defaultdict(set)
for r in rows:
    if r["va645"] != "-" and r["conf"] in ("alta", "media") and not is_tpl(r["nome"]):
        for dname in pub.get(r["va645"], ()): cand[dname].add(r["va"])
    if r["decorado"] != "-" and r["conf"] in ("alta", "media"): cand[r["decorado"]].add(r["va"])
with open(f"{D}/map_cadeia.tsv", "w", encoding="utf-8") as o:
    o.write("# candidato: nome decorado -> VA 983 pela cadeia 983->839->645 (tools/f04_map.py)\n")
    for dname, vs in sorted(cand.items()):
        if len(vs) == 1: o.write(f"{dname}\t{next(iter(vs))}\n")
st["mapa_candidato_simbolos"] = sum(1 for v in cand.values() if len(v) == 1)
st["mapa_candidato_ambiguos"] = sum(1 for v in cand.values() if len(v) > 1)

# ---- relatório
rep = []
P = rep.append
tot_b = sum(r["sz"] for r in rows)
P(f"funcoes 983: {len(rows)}  bytes: {tot_b}")
P("\n== por classe (funcoes / bytes)")
kc, kb = collections.Counter(), collections.Counter()
for r in rows: kc[r["kind"]] += 1; kb[r["kind"]] += r["sz"]
for k, n in kc.most_common(): P(f"  {k:16s} {n:5d} {kb[k]:7d}  {kb[k]*100/tot_b:5.1f}%")
P("\n== 983 x 839 (funcoes / bytes)")
kc, kb = collections.Counter(), collections.Counter()
for r in rows: kc[r["d839"]] += 1; kb[r["d839"]] += r["sz"]
for k, n in kc.most_common(): P(f"  {k:16s} {n:5d} {kb[k]:7d}  {kb[k]*100/tot_b:5.1f}%")
P("\n== nome do 645 por confianca / via")
kc = collections.Counter((r["conf"], r["via"]) for r in rows if r["va645"] != "-")
for k, n in sorted(kc.items(), key=lambda x: -x[1]): P(f"  {k[0]:6s} {k[1]:14s} {n}")
P("\n== validacao cruzada entre caminhos")
for k, n in sorted(val.items()): P(f"  {k}: {n}")
for k, n in sorted(st.items()): P(f"  {k}: {n}")
P("\n== faixas de .obj na ordem de endereco (ancoras = funcoes proprias de arquivo conhecido)")
for o, i0, i1, n in blocks:
    b = sum(rows[i]["sz"] for i in range(i0, i1 + 1))
    P(f"  {rows[i0]['va']}..{rows[i1]['va']}  {o:12s} {i1-i0+1:5d} funcoes {b:7d} bytes  {n:4d} ancoras  -> {SRC.get(o, '?')}")
P("\n== trechos fora das faixas (unidade nova ou fronteira; ver nota)")
for i0, i1, po, no in gaps:
    b = sum(rows[i]["sz"] for i in range(i0, i1 + 1))
    kk = collections.Counter(rows[i]["kind"] for i in range(i0, i1 + 1))
    dd = collections.Counter(rows[i]["d839"] for i in range(i0, i1 + 1))
    P(f"  {rows[i0]['va']}..{rows[i1]['va']}  {i1-i0+1:5d} funcoes {b:7d} bytes  entre {po} e {no}  {dict(kk)}  839:{dict(dd)}")
P("\n== por .obj (funcoes com arquivo atribuido): classe -> funcoes/bytes")
per = collections.defaultdict(lambda: collections.Counter())
perb = collections.defaultdict(lambda: collections.Counter())
for r in rows:
    per[r["obj"]][r["kind"]] += 1; perb[r["obj"]][r["kind"]] += r["sz"]
for o in sorted(per, key=lambda x: -sum(perb[x].values())):
    P(f"  {o:12s} " + "  ".join(f"{k}={per[o][k]}/{perb[o][k]}" for k, _ in per[o].most_common()))
# nomes para o Ghidra (ApplyNames.java): endereço, nome, confiança
with open(f"{OUT}/names983w.tsv", "w", encoding="utf-8") as o:
    for r in rows:
        if r["nome"] != "-" and r["conf"] in ("alta", "media") and r["kind"] not in ("thunk_import", "funclet_eh", "crt"):
            o.write(f"{r['va']}\t{r['nome']}\t{r['conf']}\t1/1\t{r['via']}\n")
open(f"{OUT}/mapa_resumo.txt", "w").write("\n".join(rep) + "\n")
print("\n".join(rep))
