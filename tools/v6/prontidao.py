#!/usr/bin/env python3
"""V6: quadro de prontidão por passo do roteiro de teste do exe (out/V6/ROTEIRO.md).

Para cada passo (abrir, login, lobby, sala, partida, loja, my room) junta o que as outras conferências já mediram:
  - código do passo no exe 983 e quanto dele já tem função nossa IGUAL/QUASE/DIFERENTE (comparador; mesma conta do painel);
  - pacotes recebidos pelo despachante do passo: 983 × fonte (out/V4/rx_cmp.tsv);
  - funções nossas que montam/leem pacote nas unidades do passo (out/V4/pk_cmp.tsv);
  - classes das unidades do passo cujo sizeof/offsetof não bate com o 983 (out/V*/layoutcheck.tsv mais novo).
Só leitura. A divisão das unidades por passo é por nome de arquivo (lista PASSOS abaixo): é uma aproximação.
Saída: out/V6/prontidao.tsv, prontidao_unidades.tsv, PRONTIDAO.md, resumo.txt.
"""
import csv, glob, os, re, sys, datetime

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, f"{R}/tools")
import painel                                               # noqa: E402  (Exe, cmp_dirs, tsv)

OUT = f"{R}/out/V6"

# passo -> (título, despachantes da V4, padrões de nome de unidade do 645, sistemas novos do JP)
PASSOS = [
    ("1", "Abrir o jogo", [],
     r"winmain|projectg|splash|logo$|mainframe|clientsetting|ggc_|hackingmanager|integritycheck|registry|inifile|"
     r"pakedresource|threadload|threadpool|threadowner|exception|dxdiaginfo|netresourcemanager|codetinker|scenemanager|"
     r"taskmain|taskmanager|initdelegate|parallelwork|monitor|mousecursor|inputmanager|soundmanager|uwin|wtimer",
     []),
    ("2", "Login e escolha de servidor", ["CTask::OnPacketCommon"],
     r"logindlg|loginunit|logininfo|loginrsdlg|serverdlg|createnickdlg|parannickdlg|networksystem|networkunit|"
     r"networkstate|networkmonitor|clientsocket|socket|packet|packetversion|secondarypassword|securitykeymanager|"
     r"passworddlg|gameunit|classicserver|blowfish|rc4|md5|jrencrypt|tea_helper|ccrc32|crcdef|shareddoc|user_info|"
     r"logoutdlg|quitwindow|chttp|generichttpclient|browser",
     ["rede_web"]),
    ("3", "Lobby", ["CLobbyTask::OnPacket", "CFamilyTask::OnPacket"],
     r"lobby|userlistdlg|chatmsg|messenger|buddymanager|msnunit|msnusersnapshot|frienddlg|friendinfodlg|addfrienddlg|"
     r"guild|addguildmemberdlg|mailboxdlg|notice|topicon|webicons|rankingdlg|rankunit|playerinfodlg|optiondlg|helpdlg|"
     r"memodlg|notedlg|post_|onelineboard|onelinereqdlg|rssmanager|newsreader|family|quest|awarddlg|titles_client|"
     r"emoticondlg|reportdlg|schooldlg|kbdmanualdlg|frquickmovedlg|gateway|pangfbi|ingameguild",
     ["salas_lobby", "lobby_atores", "guilda_social", "quests_presenca", "ui_base", "rf_dialogos"]),
    ("4", "Sala de espera", ["ntAvatarChatTask::OnPacket"],
     r"makeroomdlg|changeroominfodlg|detailedroominfodlg|mapselectdlg|invitedlg|playerdlg|gamepartydlg|avatar|"
     r"balloontext|talkbox|headicon|dlgquickstartsetting|frreadytoall|trainingdlg|trainingoptiondlg|opentournament|"
     r"ladderevent|matchactor|exhibition|bubble",
     ["grandprix", "campeonato"]),
    ("5", "Partida", ["CGolfTask::OnPacket", "CTutorialTask::OnPacket", "CGhostTask::OnPacket"],
     r"golf|ball|camera|club|wind|weather|sky|sea|river|grass|powergauge|scoreboard|scoredlg|resultdlg|finalrankdlg|"
     r"shot|trajectory|guideline|spin|mascot|effect|fx|ground|grid|quadtree|polysoup|particle|rain|snow|icesnow|petal|"
     r"lensflare|shadow|background|beach|obmarker|autotarget|approach|rival|ghost|tutorial|replay|treasure|caddiebonus|"
     r"shufflebonus|bonusticket|newrecorddlg|winnernotice|fallingspot|galleryreaction|cutinsystem|letter_effect|"
     r"standinginline|taileffect|ambientsound|aztecmgr|magiccarpet|paper|pool|igameoverlay|gameoverlaymanager|"
     r"overlay|itembuffactor|netsyncactor|eventactor|actor|npc|g_starmode|miles|ppl|clock|period|3dfont|fadingtext|"
     r"voiceitem|gdvoiceitem|helpmsg|randomhouse|hatmanager|pwc2010|demon",
     ["controladores", "regra_subregra", "holeinone", "clima", "fx", "dados_de_jogo_GD"]),
    ("6", "Loja", ["CShopTask::OnPacket"],
     r"shop|checkoutdlg|giftdlg|giftalarmdlg|panggiftdlg|returngiftdlg|search|cardboxdlg|specialbox|scratchdlg|"
     r"frrandomboxprogress|tikimagicboxdlg|tikireportopener|frticketexchangedlg|rentalextensiondlg|repaydlg|supplypack|"
     r"trade|privatetrade|offlinetradedlg|timelimititem|transferableitem|deleteitem|recycle|levelupitemdlg",
     ["lojas_pontos"]),
    ("7", "My Room e equipamento", ["CRealMyRoomTask::OnPacket"],
     r"realmyroom|equipdlg|itemwindow|iteminfodlg|itemstorage|furniture_ability|setitemdlg|ucc|carddlg|cardsystem|"
     r"ccardbook|cardremove|caddieinfodlg|caddiewarningdlg|upgradecaddiedlg|mascotinfodlg|enchantdlg|downgradedlg|"
     r"compounddlg|detaildlg|partsinfo|parttidlist|petbody|anotherhand|jukeboxdlg|guidebook|selfdesign|contentsdoc|"
     r"icontentsdoc|gamedatadb",
     ["clubset_workshop", "cartas_alquimia", "selfdesign"]),
]
RESTO = ("8", "Comum a todos os passos (engine, Fresh, shared, eventos e o que não entrou acima)")


def passo_da(nome, sistema=None):
    if sistema:
        for p, _t, _d, _re, sis in PASSOS:
            if sistema in sis:
                return p
        return RESTO[0]
    for p, _t, _d, pad, _s in PASSOS:
        if re.match(rf"(?:{pad})", nome) or re.search(rf"(?:{pad})", nome) and p != "1":
            return p
    return RESTO[0]


def base(u):
    return re.sub(r"\.(cpp|c|obj)$", "", os.path.basename(u.replace("\\", "/")).lower().replace(".obj", ""))


def mais_novo(pad):
    c = sorted(glob.glob(pad, recursive=True), key=os.path.getmtime)
    return c[-1] if c else None


def main():
    os.makedirs(OUT, exist_ok=True)
    exe = painel.Exe()
    exe.cobertura(painel.cmp_dirs())

    # --- unidades: do mapa (645) e novas do JP ---
    # Conta por FUNÇÃO do mapa (as faixas ini983..fim983 das unidades se sobrepõem aos vãos: 509 kB contados 2 vezes).
    import bisect
    novas = []                                              # (ini, fim, arquivo, sistema) das unidades novas do JP
    un = mais_novo(f"{R}/out/F3.7/**/unidades_novas.tsv")
    for u in painel.tsv(un) if un else []:
        novas.append((int(u["ini"], 16), int(u["fim"], 16), base(u["arquivo"]), u["sistema"]))
    novas.sort()
    nini = [x[0] for x in novas]
    grupo = {base(u["unidade"]): u["grupo"] for u in exe.units}
    D = {}                                                  # (origem, unidade) -> dict
    dono = []                                               # por função de exe.F: chave em D

    def ent(origem, nome, passo):
        k = (origem, nome)
        if k not in D:
            D[k] = dict(passo=passo, origem=origem, unidade=nome, bytes=0, I=0, Q=0, D=0)
        return k
    for va, tam, g, uni in exe.F:
        if uni:                                             # núcleo de unidade do 645
            nome = base(uni)
            k = ent(grupo.get(nome, g), nome, passo_da(nome) if g == "ProjectG" else RESTO[0])
        else:
            j = bisect.bisect_right(nini, va) - 1
            if g == "novo" and j >= 0 and va < novas[j][1]:
                k = ent("JP:" + novas[j][3], novas[j][2], passo_da("", novas[j][3]))
            else:
                k = ent("vao" if g == "vao" else "novo_sem_unidade", "(funções de vão sem unidade)", RESTO[0])
        D[k]["bytes"] += tam
        dono.append(k)
    for va, c, b in exe.porva:
        j = bisect.bisect_right(exe.vas, va) - 1
        if j >= 0 and va < exe.F[j][0] + exe.F[j][1]:
            D[dono[j]][c] += b
    U = list(D.values())

    def sem_mapa(n):                                        # unidade sem função "nucleo" no mapa (só aparece na V3/V4)
        g = grupo.get(n, "?")
        return dict(passo=passo_da(n) if g in ("ProjectG", "?") else RESTO[0], origem=g + " (sem função no mapa)",
                    unidade=n, bytes=0, I=0, Q=0, D=0, pk={}, lay=[])
    for u in U:
        u["pk"] = {}
        u["lay"] = []
    idx = {}
    for u in U:
        idx.setdefault(u["unidade"], u)

    # --- pacotes montados/lidos por função nossa (V4) ---
    for r in painel.tsv(f"{R}/out/V4/pk_cmp.tsv"):
        n = re.sub(r"^src_[a-z0-9]+_", "", r["unidade"])
        n = n.split("_")[-1] if n not in idx and n.split("_")[-1] in idx else n
        u = idx.get(n)
        if u is None:
            u = sem_mapa(n)
            idx[n] = u; U.append(u)
        u["pk"][r["estado"]] = u["pk"].get(r["estado"], 0) + 1

    # --- layout (V3) ---
    lc = mais_novo(f"{R}/out/V*/layoutcheck.tsv")
    lay_tot = {"ok": 0, "FALHA": 0, "outro": 0}
    for r in painel.tsv(lc) if lc else []:
        if r["tipo"] == "ANOT":
            continue
        res = r["resultado"]
        lay_tot[res if res in lay_tot else "outro"] += 1
        if res == "ok":
            continue
        n = base(r["unidade"])
        u = idx.get(n)
        if u is None:
            u = sem_mapa(n)
            idx[n] = u; U.append(u)
        u["lay"].append(f"{r['classe']} {r['valor_983']} (nosso {r['valor_nosso'] or res})")

    # --- recebidos por despachante (V4) ---
    rx = {}
    for r in painel.tsv(f"{R}/out/V4/rx_cmp.tsv"):
        rx.setdefault(r["despachante"], {}).setdefault(r["estado"], []).append(r["id"])

    # --- ids que o cliente 983 manda, por passo (para conferir no log do servidor) ---
    env = {}                                                # (passo, destino) -> {id: unidades}
    with open(f"{OUT}/pacotes_por_passo.tsv", "w") as f:
        f.write("passo\tsentido\tdestino_ou_despachante\tid_983\tcampos_ou_leituras\tfuncao_983\tunidade\n")
        for r in painel.tsv(f"{R}/out/V4/pacotes_envio_983.tsv"):
            n = base(r["unidade"].split("|")[-1].strip()) if r["unidade"] else ""
            ps = passo_da(n) if n and grupo.get(n, "ProjectG") == "ProjectG" else RESTO[0]
            if n in idx:
                ps = idx[n]["passo"]
            env.setdefault((ps, r["destino"] or "?"), {}).setdefault(r["id"], set()).add(n or "?")
            f.write(f"{ps}\tcliente->servidor\t{r['destino'] or '?'}\t{r['id']}\t{r['campos']}\t{r['funcao']}\t{n}\n")
        dp = {dd: p for p, _t, desp, _r, _s in PASSOS for dd in desp}
        for r in painel.tsv(f"{R}/out/V4/rx_cmp.tsv"):
            if r["estado"] == "so_fonte":
                continue
            f.write(f"{dp.get(r['despachante'], RESTO[0])}\tservidor->cliente\t{r['despachante']}\t{r['id']}\t"
                    f"{r['leituras_983']}\t\t{r['estado']}\n")

    # --- saída ---
    PK = ["igual", "igual_curinga", "difere_id", "difere_bloco", "difere_id_bloco", "difere_campos", "so_nosso", "sem_par"]
    with open(f"{OUT}/prontidao_unidades.tsv", "w") as f:
        f.write("passo\torigem\tunidade\tbytes_983\tigual\tquase\tdiferente\tnao_escrito\t" + "\t".join("pk_" + k for k in PK)
                + "\tlayout_falha\n")
        for u in sorted(U, key=lambda u: (u["passo"], -u["bytes"])):
            ne = max(u["bytes"] - u["I"] - u["Q"] - u["D"], 0)
            f.write(f"{u['passo']}\t{u['origem']}\t{u['unidade']}\t{u['bytes']}\t{u['I']}\t{u['Q']}\t{u['D']}\t{ne}\t"
                    + "\t".join(str(u["pk"].get(k, 0)) for k in PK) + "\t" + "; ".join(u["lay"]) + "\n")

    linhas = []
    for p, tit, desp, _pad, _sis in PASSOS + [(RESTO[0], RESTO[1], [], "", [])]:
        us = [u for u in U if u["passo"] == p]
        b = sum(u["bytes"] for u in us)
        i, q, d = (sum(u[k] for u in us) for k in "IQD")
        jp = sum(u["bytes"] for u in us if u["origem"].startswith("JP:"))
        pk = {k: sum(u["pk"].get(k, 0) for u in us) for k in PK}
        lay = [x for u in us for x in u["lay"]]
        r_ = {k: sum(len(rx.get(dd, {}).get(k, [])) for dd in desp) for k in ("igual", "difere", "so_983", "so_fonte")}
        linhas.append(dict(passo=p, titulo=tit, unidades=len(us), bytes=b, jp=jp, I=i, Q=q, D=d, pk=pk, lay=lay, rx=r_,
                           desp=desp))
    with open(f"{OUT}/prontidao.tsv", "w") as f:
        f.write("passo\ttitulo\tunidades\tbytes_983\tbytes_sistemas_novos_jp\tigual\tquase\tdiferente\tnao_escrito\t"
                "pct_escrito\tpct_igual_quase\trx_despachantes\trx_casos_983\trx_igual\trx_difere\trx_so_983\trx_so_fonte\t"
                "pk_funcoes\tpk_igual\tpk_difere_id\tpk_difere_bloco_campos\tpk_sem_comparar\tlayout_falhas\n")
        for L in linhas:
            esc = L["I"] + L["Q"] + L["D"]
            pk = L["pk"]
            f.write("\t".join(str(x) for x in [
                L["passo"], L["titulo"], L["unidades"], L["bytes"], L["jp"], L["I"], L["Q"], L["D"], max(L["bytes"] - esc, 0),
                f"{100 * esc / L['bytes']:.1f}" if L["bytes"] else "-",
                f"{100 * (L['I'] + L['Q']) / L['bytes']:.1f}" if L["bytes"] else "-",
                ", ".join(L["desp"]) or "-",
                L["rx"]["igual"] + L["rx"]["difere"] + L["rx"]["so_983"], L["rx"]["igual"], L["rx"]["difere"],
                L["rx"]["so_983"], L["rx"]["so_fonte"], sum(pk.values()), pk["igual"] + pk["igual_curinga"],
                pk["difere_id"] + pk["difere_id_bloco"], pk["difere_bloco"] + pk["difere_campos"],
                pk["so_nosso"] + pk["sem_par"], len(L["lay"])]) + "\n")

    def kb(n):
        return f"{n / 1024:,.0f}".replace(",", ".")
    quando = datetime.datetime.now(datetime.timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
    md = [f"# V6 — prontidão do exe compilado, por passo do roteiro ({quando})", "",
          "Gerado por `make v6` (tools/v6/prontidao.py). **Não edite à mão**; o roteiro para o dono é o `ROTEIRO.md`.",
          "Junta o comparador (mesma conta do painel), a V3 (layout) e a V4 (pacotes). A divisão das unidades por passo é",
          "pelo nome do arquivo (aproximação; lista em `prontidao_unidades.tsv`).", "",
          "## Código de cada passo: quanto já tem função nossa", "",
          "| # | Passo | Unidades | kB no 983 | dos quais sistemas novos do JP | Escrito | Igual ou quase |",
          "|---|---|---:|---:|---:|---:|---:|"]
    for L in linhas:
        esc = L["I"] + L["Q"] + L["D"]
        md.append(f"| {L['passo']} | {L['titulo']} | {L['unidades']} | {kb(L['bytes'])} | {kb(L['jp'])} | "
                  f"{100 * esc / max(L['bytes'], 1):.0f}% | {100 * (L['I'] + L['Q']) / max(L['bytes'], 1):.0f}% |")
    tb = sum(L["bytes"] for L in linhas); te = sum(L["I"] + L["Q"] + L["D"] for L in linhas)
    tiq = sum(L["I"] + L["Q"] for L in linhas)
    md += [f"| | **Total** | {sum(L['unidades'] for L in linhas)} | {kb(tb)} | {kb(sum(L['jp'] for L in linhas))} | "
           f"{100 * te / tb:.0f}% | {100 * tiq / tb:.0f}% |", "",
           "\"Escrito\" = bytes do 983 cobertos por função nossa que o comparador pareou (igual, quase ou diferente).", "",
           "## Pacotes que o servidor manda em cada passo (despachante do 983 × nosso fonte)", "",
           "| # | Passo | Despachante | Casos no 983 | Mesmo id e mesmas leituras | Mesmo id, leituras diferentes | Só no 983 | Só no fonte |",
           "|---|---|---|---:|---:|---:|---:|---:|"]
    for L in linhas:
        for dd in L["desp"]:
            e = rx.get(dd, {})
            n = {k: len(e.get(k, [])) for k in ("igual", "difere", "so_983", "so_fonte")}
            md.append(f"| {L['passo']} | {L['titulo']} | `{dd}` | {n['igual'] + n['difere'] + n['so_983']} | {n['igual']} | "
                      f"{n['difere']} | {n['so_983']} | {n['so_fonte']} |")
    md += ["", "`CTask::OnPacketCommon` vale para todas as telas (está no passo 2 porque é o primeiro a rodar depois do login).",
           "\"Só no 983\" + \"Só no fonte\" altos = numeração de pacotes do KR 645 ainda no fonte (achado da V4) e casos novos do JP.",
           "", "## Pacotes montados ou lidos por função nossa, por passo", "",
           "| # | Passo | Funções | Iguais ao 983 | Só o id difere | Bloco ou campos diferem | Sem comparar |",
           "|---|---|---:|---:|---:|---:|---:|"]
    for L in linhas:
        pk = L["pk"]
        md.append(f"| {L['passo']} | {L['titulo']} | {sum(pk.values())} | {pk['igual'] + pk['igual_curinga']} | "
                  f"{pk['difere_id'] + pk['difere_id_bloco']} | {pk['difere_bloco'] + pk['difere_campos']} | "
                  f"{pk['so_nosso'] + pk['sem_par']} |")
    md += ["", "## Ids que o cliente 983 manda em cada passo (para conferir no registro do servidor)", "",
           "Lista completa, com campos e função, em `pacotes_por_passo.tsv` (numeração do **983**).", ""]
    hx = lambda v: sorted((x for x in v if x.startswith("0x")), key=lambda x: int(x, 16))
    for L in linhas:
        for (ps, dest), ids in sorted(env.items()):
            if ps == L["passo"] and dest != "?":
                md.append(f"- **{L['passo']} {L['titulo'].split(' (')[0]}** → {dest} ({len(ids)} ids): " + " ".join(hx(ids)))
    md += ["", f"## Classes com tamanho diferente do 983, por passo (`{os.path.relpath(lc, R) if lc else '-'}`: "
           f"{lay_tot['ok']} ok, {lay_tot['FALHA']} FALHA, {lay_tot['outro']} outro, sem contar anotações)", ""]
    for L in linhas:
        if L["lay"]:
            md.append(f"- **{L['passo']} {L['titulo']}** ({len(L['lay'])}): " + "; ".join(sorted(L["lay"])))
    lk = f"{R}/out/V6/link/resumo.txt"  # make v6-link (tools/v6/simbolos.py): portão A1 do roteiro (o exe liga)
    if os.path.exists(lk):
        md += ["", "## O exe liga? Símbolos sem corpo (`make v6-link`; lista em `out/V6/link/falta.tsv`)", "",
               "```"] + open(lk).read().rstrip("\n").split("\n") + ["```"]
    md += ["", "## As 12 maiores unidades ainda sem nenhuma função nossa, por passo", ""]
    for L in linhas:
        v = sorted((u for u in U if u["passo"] == L["passo"] and u["bytes"] and u["I"] + u["Q"] + u["D"] == 0),
                   key=lambda u: -u["bytes"])
        if v:
            md.append(f"- **{L['passo']} {L['titulo']}** ({len(v)} unidades, {kb(sum(u['bytes'] for u in v))} kB): "
                      + ", ".join(f"{u['unidade']} {kb(u['bytes'])}" for u in v[:12]))
    open(f"{OUT}/PRONTIDAO.md", "w").write("\n".join(md) + "\n")

    res = [f"V6 prontidao ({quando})",
           f"unidades {len(U)}; bytes 983 {tb}; escrito {100 * te / tb:.1f}%; igual+quase {100 * tiq / tb:.1f}%",
           f"layout (sem anotacoes): {lay_tot}  [{os.path.relpath(lc, R) if lc else '-'}]"]
    for L in linhas:
        esc = L["I"] + L["Q"] + L["D"]
        res.append(f"passo {L['passo']} {L['titulo'][:28]:28s} unid {L['unidades']:4d}  kB {L['bytes'] / 1024:8.0f}  escrito "
                   f"{100 * esc / max(L['bytes'], 1):5.1f}%  rx983 {L['rx']['igual'] + L['rx']['difere'] + L['rx']['so_983']:4d} "
                   f"(igual {L['rx']['igual']})  pk {sum(L['pk'].values()):4d}  layout_falha {len(L['lay'])}")
    open(f"{OUT}/resumo.txt", "w").write("\n".join(res) + "\n")
    print("\n".join(res))


if __name__ == "__main__":
    main()
