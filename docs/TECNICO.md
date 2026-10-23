# Manual técnico do jp983src

Complemento do `docs/RETOMAR.md` (visão geral, caminhos, frentes, backups). Aqui: o ambiente, cada alvo do `make`, cada
pasta de `tools/`, o formato dos arquivos de `map/` e do estado, como usar o comparador e um exemplo completo de adaptar
uma unidade. Última revisão: 11/10/2026 (frente C, sessão C3, tarefa D1).

**Regra de manutenção:** toda frente que criar alvo de `make`, ferramenta ou arquivo de mapa novo acrescenta uma linha
na tabela certa deste arquivo, no mesmo commit.

Convenções do texto: "983" = binários de referência do JP 983 em `ref/`; "nosso" = o que sai do fonte deste repositório;
VA = endereço virtual (exe com base `00400000`, dll com base `10000000`); "unidade" = um `.cpp` que vira um `.obj`.

---

## 1. Ambiente

`tools/checar_ambiente.sh` confere tudo e imprime `OK` / `AVISO` / `FALTA` por item (sai com 1 se houver `FALTA`;
`-r` pula os testes que rodam o Wine). Saída de hoje guardada em `out/D1/checar_ambiente.txt` (56 OK, 1 AVISO, 0 FALTA).

| Item | Onde | Para quê |
|---|---|---|
| VS2010 SP1 (cl 16.00.40219.01, link 10.00.40219.01) | `/root/kr839/local/vs2010` (`VC10/`, `compat/`, `sdklib/`, prefixo `wine/`) | compilar tudo; chamado por `tools/vs.sh` |
| Wine 9.0 | `/usr/bin/wine` | roda o cl/link/rc |
| rebang (decomp do KR 645), commit `f0a85b5` | `/root/rebang` (só leitura) | `build-projectg.json` (lista e configuração das unidades do exe), Platform SDK 2002, DirectX 9, WTL 7.5, ATL 7.1, `rc.exe` |
| Binários de referência | `ref/ProjectG_983_dump.exe`, `ref/wangreal_983.dll` (fora do git; md5 no README) | o que o comparador lê |
| Ghidra 12.1.4 + JDK 21 | `/opt/ghidra_12.1.4_PUBLIC` | pseudo-C de funções do 983 |
| Projeto Ghidra do exe 983 | `/root/jp983/proj` (`jp983`), scripts em `/root/jp983/scripts` | sempre `-readOnly` e sob `flock /root/jp983/ghidra.lock` |
| Projeto Ghidra da dll 983 | `proj/wr983` (neste repo, fora do git) | idem, para a dll |
| Análises anteriores | `/root/jp983/out` (pares 983×839), `/root/kr839/out` (ponte 645×839) | só para refazer os mapas (`make units`) |
| Python 3 + `capstone` 5 | sistema | o comparador e quase todas as ferramentas |
| node | sistema | só `tools/p1/teste_dom.js` (teste do painel) |

Particularidades que custaram tempo:
- **Caminhos:** `tools/vs.sh` troca todo `/root/...` dos argumentos por `Z:\root\...`. Use sempre caminho absoluto.
- **Sem PDB:** o `mspdb100` não funciona sob Wine; compila-se com `/Z7` (símbolos no `.obj`) e liga-se sem `/DEBUG`.
- **ATL:** o VS2010 que temos não traz ATL; `make pg-atl` gera `build/atl71` a partir do ATL 7.1 do rebang, consertado.
- **Memória/CPU:** 32 GB, 40 núcleos, divididos entre três frentes. Antes de build grande: `pgrep -a make; pgrep -af wine`.
  No máximo `-j8` por frente e um Ghidra por vez (o `ghidra.lock` garante).
- **`build/` e `ref/` estão fora do git.** Num clone novo: restaurar `ref/` do backup e rodar `make pg-obj` + `make pg-base`
  (sem isso o painel mostra o exe zerado, porque os resultados do comparador ficam em `out/**/cmp/`, também fora do git).

Flags de compilação (provadas por variantes; `out/F0.2/variants.txt`, `out/F3.2/variantes.txt`, `out/F3.5/s38/ob2_fresh.txt`):
- comum: `/MD /W3 /EHsc /Z7 /O2 /Ob1 /GF- /Gr /GS /Oy- /DNDEBUG /DWIN32 /D_WINDOWS /D_MBCS`
- exe: mais `/Zm200 /DREBANG_SEMANTIC_ONLY` (escolhe a versão em C das funções que o rebang tem em asm);
  a biblioteca Fresh (`src/fresh/`) usa `/Ob2`; o projeto da dll (`src/wangreal/`) define `/DWANGREAL_DEVICE`.
- A UI nova "RF" do exe 983 foi compilada com LTCG (`/GL`): nela não se espera IGUAL (critério funcional).

---

## 2. Alvos do make

Três arquivos: `Makefile` (frente A; dll, exe, mapas, painel), `Makefile.B` (frente B) e `Makefile.C` (frente C), os dois
últimos incluídos pelo primeiro. Tudo roda da raiz do repositório. Tempos aproximados, com as outras frentes trabalhando: os com
`*` foram medidos (sessão C3 ou diário da sessão que criou o alvo); os demais são estimativa; "—" = sem estimativa.

### 2.1 Compilador e wangreal.dll
| Alvo | O que faz | Entrada → saída | Tempo |
|---|---|---|---|
| `make info` | versão do cl/link e flags | — | 1 s* |
| `make hello` | teste do compilador: dll + exe mínimos, e roda o exe | `tools/hello/` → `build/hello/` | ~20 s |
| `make obj F=src/x.cpp` | compila um arquivo da dll/engine | → `build/obj/src/x.obj` (+ `.log`) | ~5 s |
| `make cmp F=src/x.cpp ARGS="..."` | compila e compara com o 983 (seção 5) | → tela; `ARGS="--out DIR"` grava | 3 s* |
| `make pilot` | compara os 4 arquivos do piloto F0.5 | `PILOT_SRC` | ~30 s |
| `make base` | compara os 13 `.cpp` da dll com a dll 983 | `BASE_SRC` → `out/base/` (`OUT=`) | ~1 min |
| `make cmp-selftest` | autoteste do comparador (corpus: device do 645) | `tools/cmpfunc_selftest.sh` → `build/f03/` | ~1 min* |
| `make wangreal` | dll parcial antiga (2 `.cpp`); mantido só por histórico | → `build/wangreal/` | — |
| `make wangreal-full` | **a wangreal.dll completa** (14 `.cpp` + recursos, ordem de link do 983) | `FULL_SRC` → `build/wangreal-full/wangreal.dll` + `.map` | ~1 min |
| `make image` | dll ligada × dll 983: PE/imports, código, alvos e dados | → `out/image/` (`OUT=`): `pe.txt`, `funcoes.tsv`, `codigo_resumo.txt`, `dados_resumo.txt` | ~1 min |
| `make smoke` | carrega a nossa dll e a do 983 no Wine, chama os 4 exports, compara | `tools/f210/smoke.sh` | ~20 s |
| `make difftest` | 4 funções puras chamadas por RVA nas duas dlls, mesmas entradas | `tools/f211/difftest.sh` | ~20 s |
| `make clean` | apaga `build/obj`, `build/hello`, `build/wangreal` (não toca em `build/pg*`) | — | — |

### 2.2 ProjectG.exe (frente A)
A lista de unidades e a configuração de cada uma (qual pch, `/FI`, includes extras) vêm de `/root/rebang/build-projectg.json`;
quem lê é `tools/f32/pgbuild.py` (`pgbuild.py list` mostra as 499 unidades). `U="filtro ..."` restringe pelo caminho.
| Alvo | O que faz | Entrada → saída | Tempo |
|---|---|---|---|
| `make pg-import` | copia do rebang o que ainda não existe aqui, mescla em 3 vias o que o rebang mudou e reaplica os ajustes do 983 (`tools/f32/ajustes*.py`); não toca nos arquivos de `map/adotados.txt` | `/root/rebang` → `src/`, `include/`, `map/projectg_seed.tsv`, relatório em `$(OUT)/mescla` | ~1 min |
| `make pg-atl` | ATL 7.1 consertado para o cl 16 | → `build/atl71` | segundos |
| `make pg-obj [U=…] [OUT=…]` | compila os 17 pch e as unidades | `src/` → `build/pg/pch`, `build/pg/obj/<caminho>.obj` (+ `.log`), `$(OUT)/compila.tsv` | uma unidade 4 s*; pch 1–2 min*; tudo 15–25 min |
| `make pg-base [U=…] [OUT=…]` | comparador em cada `.obj` × exe 983 | → `$(OUT)/cmp/src_<unidade>/{funcs.tsv,resumo.txt,simbolos.tsv}`, `$(OUT)/base.tsv`, `base_resumo.txt` | uma unidade 6 s*; tudo 20–45 min* |
| `make pg-variantes` | prova das flags do exe em 6 unidades | → `$(OUT)/variantes.txt` | ~10 min |
| `make pg-map` | refaz `map/projectg.tsv` (nome decorado → VA) a partir de uma linha de base | `BASE=…funcs_all.tsv.gz` + `map/projectg_manual.tsv` − `map/projectg_fora.tsv` | ~10 s |
| `make units` | refaz `map/projectg_units.tsv` e `map/projectg_funcs.tsv` (unidade do 645 → faixa no 983) | rebang, `/root/kr839/out`, `/root/jp983/out`, `BASE` → `map/`, `out/F3.3/` | ~1 min |
| `make pg-ltcg` | onde estão os objs LTCG do exe 983 | → `out/F3.3/` | — |
| `make pg-votes [U=…] [VOUT=…]` | "votos" de deslocamento de campo por classe (nosso `.obj` × 983): mostra que campo mudou de lugar | `build/pg/obj` → `$(VOUT)/votos.tsv` | ~10 min |

Opções do `pgbuild.py` úteis à mão: `--tag NOME` usa `build/pg-NOME` (cópia de trabalho que não mexe no build da frente A),
`--force` recompila mesmo em dia, `--out DIR`. **Experimento vai para um caminho com `/tmp/`, `/antes/` ou `/ab/`**: o painel
ignora essas pastas; qualquer outro `out/**/cmp/src_*/funcs.tsv` mais novo passa a valer como estado atual.

### 2.3 Sistemas novos do JP (frente B, `Makefile.B`)
| Alvo | O que faz | Entrada → saída | Tempo |
|---|---|---|---|
| `make jp` | compila as unidades novas | `src/projectg/jp/units.txt` (um `.cpp` por linha) → `build/B/obj/<nome>.obj` | ~5 s por unidade |
| `make jp-cmp JPOUT=out/F3.7/<sessão>` | `jp` + comparador × exe 983 | mapa = `map/projectg.tsv` + `src/projectg/jp/jp.tsv` → `$(JPOUT)/cmp/<unidade>/` | ~6 s por unidade |
| `make jp-mapa JPOUT=…` | refaz as fronteiras de unidade nos vãos novos do 983 | → `$(JPOUT)/unidades_novas.tsv`, `classes_novas.tsv`, `sistemas.tsv` | ~2 min |

### 2.4 Verificação e painel (frente C, `Makefile.C` e `Makefile`)
| Alvo | O que faz | Entrada → saída | Tempo |
|---|---|---|---|
| `make layoutcheck [U=…]` | compila (`cl /Zs`, sem pch) cada unidade seguida do seu `include/asserts/<unidade>.h`; falha se algum `static_assert` de valor do 983 falhar | `include/asserts/*.h` → `out/V3/layoutcheck.tsv`, `layoutcheck_resumo.txt`; build em `build/C` | ~3 min* (221 cabeçalhos) |
| `make layout-gen [OBJS=build/pg/obj]` | mede de novo o `sizeof` das classes no exe 983 e nos nossos `.obj` (inclui `build/B/obj`), colhe as anotações dos cabeçalhos (`anot.py`) e regenera os asserts; desde a V7 inclui as unidades de `src/projectg/jp/units.txt` | → `out/V3/sizes_983.tsv`, `sizes_obj.tsv`, `anot.tsv`, `include/asserts/*.h` | ~30 s* |
| `make v4` | V4: assinatura de pacotes (API WSendPacket/WReceivedPacket) do exe 983 × nossos `.obj`, ids dos despachantes, conversão de ids 645→983, tamanho do registro de cada tabela `.iff` | `ref/ProjectG_983_dump.exe`, `funcs.tsv` mais novos, `.obj` → `out/V4/*.tsv` (ver `out/V4/RELATORIO.md`) | 15 s* |
| `make v5` | V5: confere os patches do rugburn público (ramo JP 983) contra o exe 983, lista as APIs interceptadas e quem as usa, URLs/IPs/porta do login e constantes de partida (983 × nosso fonte) | `ref/ProjectG_983_dump.exe`, `map/projectg_funcs.tsv`, `src/`, `out/V5/rugburn_jp983_trecho.c` → `out/V5/*.tsv` (ver `out/V5/RELATORIO.md`) | 15 s* |
| `make v6` | V6: quadro de prontidão do exe por bloco do roteiro de teste (abrir, login, lobby, sala, partida, loja, my room): código escrito, pacotes recebidos/enviados (V4) e classes com layout errado (V3) | `map/projectg_{units,funcs}.tsv`, `out/**/cmp/*/funcs.tsv`, `out/V4/*.tsv`, `out/V*/layoutcheck.tsv`, `out/F3.7/**/unidades_novas.tsv` → `out/V6/{PRONTIDAO.md,prontidao*.tsv,pacotes_por_passo.tsv,resumo.txt}` (o roteiro em si, `out/V6/ROTEIRO.md`, é escrito à mão) | 5 s* |
| `make v6-link` | V6/F4 (frente C): o exe liga? Lê a tabela de símbolos dos .obj (unidades da A: o mais novo sem erro entre `build/pg*/obj`; da B: `build/B/obj`) e das .lib do link (VC10, SDK 2002, atls 7.1, mss32/NPGameLib, `build/wangreal-full/wangreal.lib`; lua/freetype/zlib/libpng/ijl15 do rebang à parte) e lista o que ninguém define, as visões cujo endereço do 983 já está definido sob outro nome e os LNK2005 | `.obj`, `.lib`, `map/projectg.tsv`, `map/pkt_c.tsv`, `src/projectg/jp/jp.tsv` → `out/V6/link/{resumo.txt,falta.tsv,falta_classes.tsv,duplicados.tsv,objs.tsv}` (o `make v6` copia o resumo no PRONTIDAO.md) | 20 s |
| `make f4-link` | F4 (frente C, C-F4.1): link de PROVA do exe com o link.exe do VS2010 e `/FORCE:MULTIPLE,UNRESOLVED` (refaz o `v6-link` antes). Libs: CRT VC10 (msvcr100/msvcp100 como o 983), SDK 2002, atls, mss32/NPGameLib, lua/freetype/zlib/libpng do rebang; ws2_32/oleaut32/ijl15 por NOME (import libs de `tools/v6/f4def/*.def` via dll-stub); recursos = `src/projectg/ProjectG.rc` + manifesto ID 1 do 983 (`tools/v6/f4res/`). O exe NÃO roda (símbolo que falta = chamada a 0) | `out/V6/link/objs.tsv` → `build/C/f4/ProjectG_983_prova.{exe,map,log}`, `out/F4/link/{resumo.txt,avisos.tsv,nao_resolvidos.tsv,imports*.tsv,recursos.tsv,xcu*.tsv}` | 45 s |
| `make f4-portoes` | F4 (frente C, C-F4.2): portões A1–A4 do `out/V6/ROTEIRO.md` (refaz o `v5` antes). A2 compila `src/projectg/ggc_wrapper.cpp` com `CL=/DJP983_SEM_GAMEGUARD` (pch da tag c, tag provisória `pg-f4gg` apagada no fim) e confere `_GGC_Init` = 2 instruções e sem `CNPGameLib`; sem a chave tem de seguir IGUAL | `out/F4/link/*`, `out/V5/constantes.tsv` → `out/F4/portoes.{tsv,txt}`, `build/C/f4/gg/ggc_wrapper.obj` (fora de `build/pg*`: o `v6-link` não pega) | 30 s |
| `make f4-terc` | F4 (frente C, C-F4.3): zlib 1.2.2 e libpng 1.2.8 (fontes do rebang, mesmos membros das .lib dele) recompiladas com o cl do VS2010 `/MD /O2 /Gr` — as .lib do rebang são VC7.1 e a libpng cita `__iob` (o msvcr100 só tem `__iob_func`) | `/root/rebang/source/client/Fresh/third_party/` → `build/C/f4/terc/{zlib,libpng}.lib` | 5 s |
| `make f4-stubs` | F4 (frente C, C-F4.3): refaz `f4-link` e `f4-terc`; gera um stub por símbolo não resolvido (`tools/v6/stubs.py`: assinatura pelo undname → `ret N` certo; dados com o valor inicial do 983 e armazenamento partilhado por VA; wstring dos eventos RF com o texto do inicializador do 983), ligado por `/alternatename` (o símbolo real ganha sozinho quando A/B escreverem o corpo). Stub de função: `jp983_stubs.log` + MessageBox com o nome e fecha; `JP983_STUB=continuar` devolve 0 (menos os `fatal`). Depois liga SEM `/FORCE` (`linkprova.py --stubs`) | `out/F4/link/nao_resolvidos.tsv` → `build/C/f4/stubs/stubs983.{cpp,obj}`, `out/F4/stubs.tsv`, `out/F4/stubs_resumo.txt`, `build/C/f4/ProjectG_983_stubs.exe`, `out/F4/link_stubs/` | 1,5 min |
| `make exe` | F4 (frente C, C-F4.4): `f4-stubs` + `portoes.py --so-a2` (recompila `build/C/f4/gg/ggc_wrapper.obj` com `JP983_SEM_GAMEGUARD`) + `linkprova.py --exe` (o link do `--stubs` com esse `ggc_wrapper.obj` no lugar do da lista, SEM `/FORCE`) + `falta_exe.py` (stubs alcançados pelo `.CRT$XCU` e pelo WinMain por chamada direta; por frente × passo do roteiro) + `f4-ijl15` + `portoes.py` (A1–A7; A5 = imports de mss32/ijl15/msvcr100/msvcp100 × exports reais em `tools/v6/f4dll/`; A6 = ijl15 de teste; A7 (C87) = chave dos .pak/updatelist do 983 no exe e nada do 645 QA) + `entrega.py` (copia exe, `ijl15_teste.dll` e os .bat de `out/V6/bat` para `out/F4/entrega/` só com 7/7 ok; senão o make falha). O link inclui `build/C/f4/mss32x.lib` (C-F4.6: `_AIL_file_*_info` do Miles novo que a mss32.lib do rebang não tem; gerada pelo linkprova.py). Esperar o `pgbuild` da A terminar (LNK1104 em .obj sendo regravado) | `out/V6/link/objs.tsv`, `out/F4/stubs.tsv` → `build/C/f4/ProjectG_983.exe` (+ `.map`/`.log`), `out/F4/exe/`, `out/F4/FALTA.md`, `out/F4/falta_exe.tsv`, `out/F4/portoes.*` | 2–4 min |
| `make f4-updatelist` | F4 (frente C, C-F4.8, pedido C85): `tools/v6/updatelist.py troca` — decifra `out/F4/updatelist_web_local_original` (XTEA 16 rodadas = `DecodeTEA_NBYTE` do 983, chave 00d3d60c), troca `fsize`/`fcrc` (int32 com sinal; `atoi` no cliente) da linha `ProjectG.exe` pelos do exe entregue, recifra (com ≥1 `\0` final) e confere decifrando de volta. O `entrega.py` (fim do `make exe`) faz o mesmo e põe o md5 no MD5.txt. `updatelist.py dec <cifrada> <xml>` decifra; `tools/v6/updatelist_teacheck.cpp` confere com o `tea.cpp` do cliente (g++) | `out/F4/updatelist_web_local_original`, `out/F4/entrega/ProjectG_nosso.exe` → `out/F4/entrega/www_teste/patch/updatelist`, `out/F4/updatelist_resumo.txt` | <1 s |
| `make painel [PARGS=…]` | gera o painel; soma um ponto ao histórico se algo mudou | repositório inteiro (só leitura) → `out/painel/index.html`, `out/painel/historico.jsonl` | 9 s* |

Depois do `make layoutcheck`: `python3 tools/v3/falhas.py` refaz `out/V3/falhas.tsv` (as falhas com a confiança de cada uma).

---

- Define de teste `JP983_SHOT_PREDICTION` (previsão de tacada do 645, Ctrl+R; desligado = 983): o pgbuild.py não lê defines do
  ambiente; o exe com ele sai de `DEFS="/DJP983_SHOT_PREDICTION" tools/v6/f4rastro/wt_build.sh TAG` + `make exe ... V6_PG="pg-TAG"`
  (detalhe em out/F4/fila_teste/LEIAME.md, seção C105).

## 3. Ferramentas (`tools/`)

Cada script tem o uso na primeira linha (`head -5 tools/x`). "Em uso" = faz parte do trabalho corrente; "histórico" =
serviu a uma tarefa fechada e fica como registro de como o número foi obtido (rodar de novo só para refazer a evidência).

### 3.1 Raiz de `tools/`
| Arquivo | Para quê | Estado |
|---|---|---|
| `vs.sh` | roda `cl`/`link`/`lib`/`dumpbin`/`undname` do VS2010 sob Wine; `run x.exe` executa um exe no mesmo prefixo | em uso (base de tudo) |
| `cmpfunc` | **o comparador** (seção 5) | em uso |
| `cmpfunc_selftest.sh` | autoteste do comparador; rodar depois de mexer nele | em uso |
| `st.py` | altera o `status.json` (seção 4.3) | em uso |
| `painel.py`, `painel_modelo.html` | painel de progresso (dona: frente C) | em uso |
| `checar_ambiente.sh` | confere o ambiente (seção 1) | em uso |
| `v4/pk.py`, `rx.py`, `ids.py`, `iff.py`, `lib.py` | V4 (frente C): pacotes enviados/recebidos e tabelas `.iff` do exe 983 contra o fonte (`make v4`); o `rx.py` lê a ÚLTIMA definição do despachante no arquivo (a do `#else` de `REBANG_SEMANTIC_ONLY`, que é a que compila) Desde a C63 o `DISP` aceita um 4º campo (`'D4'` = sub-switch sobre o 1º Decode4, como o `CItemBuff::ProcessPacket`) e o id pode vir em registro (`mov ecx,id; cmp ax,cx`). | em uso |
| `v5/rb.py` | V5 (frente C): rugburn × exe 983 — patches por endereço, ganchos de API, rede e constantes (`make v5`); se houver clone do rugburn em `build/C/v5/rugburn`, refaz o trecho guardado | em uso |
| `v6/prontidao.py` | V6 (frente C): prontidão por bloco do roteiro de teste do exe (`make v6`); usa `tools/painel.py` (mesma conta de cobertura); a divisão das unidades por bloco é a lista `PASSOS` no começo do arquivo | em uso |
| `v6/simbolos.py` | V6/F4 (frente C): conferência de link sem rodar o link (`make v6-link`); `V6_EXTRA=".obj …"` soma .obj a mais (rodada "e se", ex.: unidade fora do units.txt) e `V6_OUT=pasta` grava em outro lugar; `V6_SEM="pg-a154 …"` ignora builds da A em andamento (C84); o .obj de uma unidade também pode vir de `build/C/f4/troca/obj/` (linhas do F4 que a C editou sob lock; vale enquanto for o mais novo; frente `C` no objs.tsv); `undname` do VS2010 sob Wine para os nomes legíveis | em uso |
| `v6/define.py` | V6/F4 (frente C): `python3 tools/v6/define.py PADRAO…` — quem DEFINE / CITA / apelida (`/alternatename`) um símbolo nos mesmos .obj do `make v6-link` (7 s) | em uso |
| `v6/linkprova.py` | F4 (frente C): o `make f4-link` (link de prova, import libs por nome, .rc em UTF-16 para o rc do VC7.1, cruzamento com o `v6-link`, imports e recursos × 983) | em uso |
| `v6/portoes.py` | F4 (frente C): o `make f4-portoes` (A1 exe, A2 chave do GameGuard, A3 ijl15, A4 constantes de partida, A5 imports × dlls reais, A6 ijl15 de teste, A7 valores do 983 × 645 QA — chave XTEA dos .pak/updatelist, textos do QA; `portoes.py --a7 EXE` confere um exe avulso) | em uso |
| `v6/strxref.py` | F4 (frente C, C84): `python3 tools/v6/strxref.py EXE 'texto' …` — VA das strings (cp949) e instruções do código que as citam (imm32), no dump do 983 ou no nosso exe | em uso |
| `v6/disexe.py` | F4 (frente C, C84): `python3 tools/v6/disexe.py EXE VA N` — desmonta N bytes de qualquer PE a partir de VA, com as strings cp949 ao lado (o nome `dis.py` colidia com o módulo da stdlib) | em uso |
| `v6/localize983.py` | F4 (frente C, C84): emula o `InitLocalizeSystem` do 983 (00a7a9b0) e lista os conteúdos ligados × `localize_kor.h` → `out/F4/s7/localize983.tsv` | em uso |
| `v6/updatelist.py`, `v6/updatelist_teacheck.cpp` | F4 (frente C, C-F4.8): cifra/decifra a updatelist do 983 e gera a de teste (`make f4-updatelist`, `entrega.py`); o .cpp decifra com o `src/shared/tea.cpp` real | em uso |
| `v6/terc.py` | F4 (frente C): o `make f4-terc` (zlib/libpng com o VS2010) | em uso |
| `v6/stubs.py`, `v6/f4stub/falta983.cpp` | F4 (frente C): o `make f4-stubs` (gerador de stubs + o tempo de execução deles); `linkprova.py --stubs` liga com eles sem `/FORCE` | em uso |
| `v6/entrega.py`, `v6/f4dll/*.txt` | F4 (frente C, C-F4.5): entrega condicionada aos portões; listas de exports reais das dlls do cliente (portão A5; `pe.py` ganhou `exports()`). O tampão `f4stub/mss32_983.asm` saiu na C-F4.6 (C82.1 da A) | em uso |
| `v6/ijl15teste/` | F4 (frente C, C-F4.6): `make f4-ijl15` — `build.sh` compila o rugburn público (build/C/v5/rugburn) com o VS2010; `sem_endereco.c` troca o dynamic_patch.c (nenhum patch de endereço fixo); `compat/` = cabeçalhos que faltam no SDK 2002 (windns/ws2tcpip/wspiapi/subauth). Saída `build/C/f4/ijl15teste/ijl15_teste.dll` | em uso |
| `v6/falta_exe.py` | F4 (frente C): o relatório do `make exe` (grafo de chamadas diretas no exe ligado, capstone; `out/F4/FALTA.md`). `stubs.py` usa o `ret N` do 983 quando um parâmetro por valor tem tamanho desconhecido | em uso |
| `v6/pe.py` | F4 (frente C): leitor mínimo de PE em Python (seções, imports por nome → slot do IAT, árvore de recursos) | em uso |
| `v6/impusers.py` | F4 (frente C): para cada import que só o 983 tem, a função/unidade do 983 que o usa e se ela já existe no nosso exe → `out/F4/link/imports_so_983_quem.tsv` | em uso |
| `v6/xcu983.py` | F4 (frente C): inicializadores estáticos — `.CRT$XCU` do 983 (`_initterm` em 00c3cc45, 00cfcd24–00cfe3b0) × o do exe de prova (contagem, chamadas a `K2L_Compatibility`, ordem por unidade) | em uso |
| `v6/f4def/`, `v6/f4res/` | F4 (frente C): .def (exports __stdcall decorados) das dlls importadas por nome; recursos extras do exe (manifesto ID 1 do 983) | em uso |
| `decomp983.sh <saída> <va>…` | pseudo-C do Ghidra para funções da **dll** 983 | em uso (dll) |
| `dis983.py VA [n]` | desmonta a **dll** 983 | em uso (dll) |
| `objfind.py`, `richhdr.py` | prova rápida de build por bytes; leitura do Rich header (ferramentas do build original) | histórico (F0.2) |
| `f04_*.py/.sh` | casamento da dll 983 com 839 e 645 → `map/wangreal_funcs.tsv` | histórico (F0.4) |
| `f12_*.py/.sh` | layout das classes da dll (votos de deslocamento, vtables) | histórico (F1.2); a versão do exe é `f34/` |
| `f13_*.py` | fronteiras das unidades sem fonte da dll (teste da "escada") | histórico (F1.3); `f37/lib.py` reaproveita a ideia |
| `f21_cover.py`, `f23_order.py`, `f26_*.py`, `f27_*.py` | cobertura e ordem das funções da dll por faixa | histórico (F2) |
| `f210_pe.py`, `f210_image.py` | dll inteira × 983 (`make image`) | em uso (`make image`) |
| `progress_json.py` | resumo antigo do progresso | histórico (substituído pelo `painel.py`) |

### 3.2 Pastas
| Pasta | Para quê | Estado |
|---|---|---|
| `hello/` | fontes do `make hello` | em uso |
| `f210/`, `f211/` | testes da dll sob Wine (`make smoke`, `make difftest`) | em uso |
| `f28/` | script Java do Ghidra da F2.8 | histórico |
| `f31/` | `map.py`, `load.py`: mapa unidade do 645 → faixa do 983 (`make units`) | em uso (refazer mapas) |
| `f32/` | **build do exe**: `pgbuild.py` (list/pch/obj/cmp), `import.py`/`merge3.py`/`seed.py` (`make pg-import`), `atlfix.py`, `variantes.sh`, `falhas.py`, e os **ajustes** `ajustes.py` + `ajustes_s<sessão>.py`/`ajustes_shareddoc*.py` | em uso |
| `f33/` | `mkmap.py` (`make pg-map`), `ltcg.py`, `semlugar.py` | em uso (`mkmap`) |
| `f34/` | **layout de classes do exe**: `votes.py`/`resumo.py`/`clsvotos.py`/`docvotos.py` (votos), `offs.py`/`co.py`/`layout.py` (deslocamentos como o compilador vê), `rtti.py`/`vt.py` (classe ↔ vtable no 983), `msgmap*.py`/`mapall.py`/`mapof.py`/`mapcls.py`/`initsweep.py`/`initoffs.py`/`initcmp.py` (mapas de mensagens das telas Fresh), `pgdis.py` (desmonte), `ab.py` (A/B de duas linhas de base), `funcsall.py` | em uso |
| `f35/` | apoio da onda 1: `wl.sh` (compila 1 unidade numa cópia e conta), `dv.py` (só as linhas que diferem de um `--diff`), `dx.py` (desmonta/procura bytes), `callers.py`, `acessos.py`, `campos.py`, `docrefs.py`, `mkinst.py` (sizeof das telas pelo `MakeInstance`), `quem.py` (cada chamada a um VA, com a função que a contém), `tabsalto.py` (tabela de saltos de um `switch` do 983 e textos cp949 já escapados), `k2l.py` (textos que o 983 passa por `K2L_Compatibility` × o literal do fonte; `--aplica` embrulha os crus), `rttiof.py`, `foradolugar.py`, `imediatos.py`, `lcids.py`, `fxicalls.py`; s98: `parfeat.py OBJ NOMES VAS` (pareia SEM_PAR × funções do 983 sem par pelo conteúdo: constantes float, textos, alvos de chamada — quando a ordem e as notas do cmpfunc não servem, ex. LTCG), `dispdiff.py OBJ FUNCS.tsv [MIN]` (por função pareada, deslocamentos [reg+disp] só do .obj × só do 983: acha campo errado no C do `#else` e campo novo); s130: `swtab.py BYTES ALVOS BASE N` (switch de duas tabelas do 983: alvo → ids da mensagem; ordem dos corpos = ordem dos `case` no fonte); s131: `antes.py out/F3.5/sNNN` (cada `funcs.tsv` da sessão × o mais novo anterior da mesma unidade: contagens, pioras e melhoras por função) | em uso |
| `f35/casodx.py` | resumo do desmonte de cada caso de um despachante de pacotes do exe 983 (`casodx.py 009c20a0 0x1dd 0x1de`): chamadas, push de imediato, cadeias; usa out/V4/pacotes_recebe_983.tsv | em uso (s64) |
| `f37/` | frente B: `jpbuild.py` (`make jp`), `dec.sh` (pseudo-C do exe 983), `dz.py` (desmonte com nomes), `res.sh` (resumo do `jp-cmp`), `sum.py` (resumo por função de uma saída do `dz.py`: tamanho, chamadas, strings — ler antes de qualquer corpo), `cp.sh` (recorte compacto de uma faixa do desmonte), `gemeo.py`, `gemeo2.py` (par gêmeo de qualquer par já escrito: nome, endereços pela ordem das funções, habilidade), `ini.py`, `vd.sh`, `df.sh` (lado a lado do cmpfunc de uma função), `enx.py` (desmonte sem o molde dos pares), `norm.py` (desmonte normalizado para diff entre unidades gêmeas); e as do mapa `refs.py`, `inits.py`, `unidades.py`, `sistemas.py`, `calibra.py`, `lib.py`; `dfull.sh` + `seq.py` + `consts.py` (B21: lado a lado completo de uma função e comparação por script da sequência de `call`, dos acessos a um objeto global e das constantes dos dois lados — para quando o `--diff` do cmpfunc perde o alinhamento) | em uso |
| `f37/za.sh`, `f37/undef.py`, `f37/cstr.py` | frente B (B79): `za.sh ini fim` desmonte sem prólogo/epílogo/montagem de std::string; `undef.py <obj> [cabeçalhos]` externos do .obj que faltam no build/B/mapa.tsv, com o VA proposto pelo comentário `// VA` dos cabeçalhos; `cstr.py VA…` string do exe como literal C (octal) | em uso |
| `pkt/` | frente C, pacotes (C-PKT): `wl.sh unidade…` (compila em build/pg-c — antes `pgbuild.py pch --tag c` — e conta), `cm.sh unidade [--diff Nome]` (comparador com `map/projectg.tsv` + `map/pkt_c.tsv`); `str.py VA…` (texto cp949 do exe 983 já como literal C com `\x`; `-b VA n` despeja bytes de tabela de switch); `subsw.py INICIO FIM arquivo.cpp 'Classe::Funcao/case 0xNN'` (sub-switch de avisos de um caso: sub-código → texto do 983 × `case` → literal do fonte; `--varre [Classe::Funcao]` passa em todos os casos de out/V4/pacotes_recebe_983.tsv, ~4 min — pega renumeração de sub-código que o `rx.py` não vê; desde a C20 lê switch aninhado — escolhe no fonte o switch que mais casa com cada tabela —, texto por `push` e desvio de 32 bits; o rótulo do caso é o menos recuado da função); `pid.py` (mensagem de erro com id de pacote como parâmetro diferente do `case` em volta: id do 645 que escapou da renumeração; conferir no 983); `quem.py VA…` (C27: quem referencia cada VA no exe 983 — `call`/`jmp` rel32 e o VA como dword —, com a função que contém cada referência ou, em vtable, a classe pela RTTI e o slot; ~10 s para vários VAs de uma vez; achar a classe/o chamador de uma função nova do 983); `subdisp.py [saída.tsv]` (C63: varre o exe 983 atrás de sub-despachantes — funções fora do `DISP` do `tools/v4/rx.py` que leem o tipo com Decode2 e o comparam com um id fixo, inclusive `mov ecx,id; cmp ax,cx` —, ~55 s; achou o 0x62 do `CProjectG::OnPacket`) | em uso |
| `p1/` | `teste_dom.js`: carrega o painel sem navegador e confere os blocos | em uso |
| `w/` | frente W (wangreal.dll, W1): `hybrid.py SAIDA.dll NOME/VA…` (dll de TESTE: nossa wangreal-full com funções do 983 copiadas para a seção `.w983` e relocadas pelos pares da F2.11; `EXTRA=va983:nosso,…` para .data sem par; pula funções com EH), `teste_dll.sh DLL DIR` (smoke + difftest de qualquer dll contra a do 983), `vtcmp.py VT983 VTNOSSA N` (vtable slot a slot), `vadiff.py VA983 VANOSSA N N` (diff de instruções 983 × dll ligada), `fieldref.py OFF…` (quem usa `[reg+OFF]` nas duas dlls, por função), `cullscan.py DLL [estado]` (`SetRenderState` de um estado); W3–W4: `difftex.sh [DLL] [DIR]` (upload de textura, 8.300 casos), `diffmv.sh [DLL] [DIR]` (ModifyVertices com `this` falso, 6.000 casos), `swcases.py VA983 VANOSSA N N [DLL]` (diff caso a caso de switch por tabela), `st.py ID ESTADO "evento" ["nota"]` (status.json, sob `flock status.lock`); `vadiff.py [DLL]` traduz endereços pelos pares do `make image` (`VADIFF_IMG`, padrão out/W4/image), imports por nome e strings | em uso |
| `v2/` | `asmscan.py`, `prepro.py`: asm/`_emit` herdado do 645 que ainda compila | histórico (V2); rodar de novo antes da F4 |
| `v3/` | asserts de layout: `sizes983.py`, `sizes_obj.py`, `anot.py`, `gen.py`, `layoutcheck.py`, `falhas.py`, `poda.py`; `jpunits.py` (V7: unidades novas do JP para o gen e o layoutcheck), `ctor_max.py` (V7: alcance do construtor do 983 em cada sizeof que falha → `out/V3/falhas_ctor.tsv`; roda no fim do `make layoutcheck` sem filtro); listas à mão `manual.tsv` e `unidade.tsv` | em uso |

Os `ajustes*.py` de `f32/` merecem explicação: são listas de **trocas de texto exatas** (`antes` → `depois`, com o motivo
e o endereço do 983 que prova) aplicadas aos arquivos que ainda são cópia do rebang. Assim o `make pg-import` pode
recopiar do rebang e reaplicar tudo. Texto não encontrado = erro (o arquivo mudou; rever o ajuste). Um arquivo que
precisa de edição livre é **adotado**: entra em `map/adotados.txt`, passa a ser editado direto e o import não toca mais nele.
Como o rebang foi encerrado, hoje tanto faz ajustar por `ajustes_sNN.py` ou adotar; adotar é mais simples.

### 3.3 Ver o 983 (as quatro consultas do dia a dia)
```
python3 tools/f37/dz.py 00c03010 40          # desmonta o exe 983 a partir do VA (nomes do mapa nos alvos)
tools/f37/dec.sh /tmp/x/dec.txt 00c03010 …   # pseudo-C do Ghidra (já usa o ghidra.lock; 10 s para 1 função)
python3 -I tools/f37/exports.py > x.tsv         # tabela de exportação do exe 983 (VA, nome decorado; a RF é exportada: B149)
python3 tools/f34/rtti.py FrGuiItemDefault   # vtable da classe pelo RTTI e onde ela é gravada (= construtores)
python3 tools/f35/callers.py 00c02ec0        # quem chama por `call` direto (função virtual dá 0: ver a vtable com tools/f34/vt.py)
python3 tools/f35/replayoffs.py src/projectg/X.cpp [--aplica]   # (s88) troca deslocamentos crus do 645 do bloco de replay do CSharedDoc (0x5b94..0x5bd4) pelos membros
python3 tools/f35/golfdocoffs.py [--aplica] src/projectg/X.cpp  # (s94/s95) CGolfDoc cru do 645 → 983 (só linhas iguais às do rebang; invólucros GolfInt/GOLFDOC_FIELD…)
python3 tools/f35/campos645.py CGolfDoc      # (s94) deslocamento dos campos m_* NO LAYOUT DO 645 (cl do VC7.1 do rebang, só leitura)
python3 tools/f35/achata.py 645|983 sUserInfo [--onde 0x1524]   # (s95) folhas de um struct (bases/arrays/aninhados) no layout do 645 ou do 983
python3 tools/f35/shareddocoffs.py [--aplica] src/projectg/X.cpp # (s95) CSharedDoc cru do 645 → 983 (sUserInfo 0xb92→0x31c6, invólucros, estáticos, list/vector)
python3 tools/f35/campos645.py CGolfRule /DREBANG_GOLFRULE_PCH       # (s96) campos645 aceita /D
python3 tools/f35/thisoffs.py [--aplica] [--valida] --extra T --t645 base,classe --t983 base,classe src/projectg/golfrule.cpp  # (s96) this + N do 645 -> 983 (CGolfRule; --valida confere no par do 983)
python3 tools/f35/pdoffs.py [--aplica] src/projectg/X.cpp...        # (s96) sPlayerData cru do 645 (0xb98) -> 983 (0xdb0); achata.py agora lê golfdoc.h
python3 tools/f35/histclasse.py CGolfRule [lo hi]                   # (s96) histograma/usos de [reg + disp] nos métodos da classe no 983
python3 tools/f35/singacc.py e74d30 [N]                              # (s97) acessos [reg + disp] logo depois de mov reg, [GLOBAL] (layout de singleton visto de fora)
python3 tools/f35/histfaixa.py 6cde30 6dcae1 [min max]                # (s97) histograma de [reg + disp] numa faixa do 983 (unidade inteira, sem mapa)
# ATENÇÃO (s96): golfdocoffs/shareddocoffs/thisoffs/pdoffs NÃO são idempotentes — rodar --aplica UMA vez por arquivo.
python3 tools/f35/rivaloffs.py [--aplica] [--golfdoc] src/projectg/X.cpp  # (s95) sRivalData 400→0x1b8 nos registros de m_rivalList; --golfdoc NÃO é idempotente
```
Peça ao `dec.sh` só as funções que vai ler (cada uma são centenas de linhas).

---

## 4. Formato dos arquivos

### 4.1 `map/` — exe
| Arquivo | Linhas | Formato | Quem escreve |
|---|---|---|---|
| `projectg.tsv` | 13.063 | `nome decorado<TAB>VA no 983`. **Mapa forte**: é onde o comparador procura a função. | `make pg-map` (de uma linha de base) e `cmpfunc --update-map`; editar à mão é permitido |
| `pkt_c.tsv` | 11 | mesmo formato do `projectg.tsv`: pares das funções de pacote escritas pela frente C que ainda não estão no mapa da A | à mão (frente C); lido por `tools/pkt/cm.sh` |
| `projectg_manual.tsv` | 226 | `nome decorado<TAB>VA<TAB>evidência`. Entradas à mão; vencem as automáticas. | à mão (frente A) |
| `projectg_fora.tsv` | 283 | `nome decorado<TAB>VA vetado<TAB>motivo`. Pares que o `mkmap.py` não pode pôr no mapa (função igual por bytes num lugar que não é o dela). VA `*` (s109) = nenhum par para o nome (nem por vizinho no `cmpfunc`, nem no `mkmap.py`). | `tools/f35/foradolugar.py` + à mão |
| `projectg_seed.tsv` | 2.219 | `nome decorado<TAB>VA`. **Mapa fraco** (par vindo do 645): só vale se as instruções parecerem ≥ 30%. | `tools/f32/seed.py` |
| `projectg_funcs.tsv` | 74.156 | uma linha por função do exe 983 (colunas abaixo) | `make units` |
| `projectg_units.tsv` | 571 | uma linha por unidade do 645 (colunas abaixo) | `make units` |
| `projectg_msgmaps.tsv` | 269 | mapas de mensagens Fresh do 983: `mapa, getmessagemap, classes, entradas, mapa_base, classes_base, controles` | `tools/f34/mapall.py` |
| `pacotes_ids_envio.tsv`, `pacotes_ids_recebe.tsv` | 96 / 139 | `id_645<TAB>id_983`. Conversão dos ids de pacote (KR 645 → JP 983) usada na troca da sessão 61; congelada (depois da troca o out/V4 não mostra mais a diferença). Id fora da tabela: ver `out/F3.5/s61/pendentes_{envio,recebe}.tsv`. | `tools/f35/pkids.py`, `tools/f35/rxids.py` (rodam uma vez só; recusam se a tabela existe) |
| `shareddoc_layout.txt` | 253 | `deslocamento membro` do `CSharedDoc` no 983 | à mão (F3.4) |
| `adotados.txt` | 38 | `caminho<TAB>sessão/motivo`: arquivos que deixaram de ser cópia do rebang | à mão |
| `rebang_base.txt` | 1 | commit do rebang da última importação (base da mescla de 3 vias) | `make pg-import` |

`projectg_funcs.tsv`: `f983` (VA), `tam` (bytes), `onde` (`nucleo` = dentro da faixa firme de uma unidade; `fronteira` =
entre duas; `vao_novo` = trecho sem unidade do 645, código novo do JP), `unidade` (caminho no rebang), `trecho` (nº do
trecho contíguo), `par645` (VA no 645), `nome645` (nome ou nome decorado), `fonte` (de onde veio o par: `alta`/`media`/`str` =
ponte 839; `obj_viz` = achada pelos nossos `.obj`), `unidade_da_ancora`, `j3j7` (tipo de hash que casou com o 839), `nome983`
(nome no projeto Ghidra).

`projectg_units.tsv`: `unidade` (caminho no rebang), `grupo` (ProjectG/Fresh/Wangreal/…), `estado_rebang`, `modulo645`,
`obj645`, `ini645`, `bytes645`, `funcs645`, `ancoras` (funções com par firme), `classe_mapa` (`forte`/`fraco`/sem lugar),
**`ini983`/`fim983`/`bytes983`/`funcs983`** (a faixa no 983), `concorda`/`discorda` (âncoras a favor/contra a faixa),
`novas_j7`/`alteradas`/`identicas_839` (quanto mudou), `outros_trechos`, **`onda`** (1 mudou pouco, 2 alterada, 4 sem fonte),
`proprias_obj`/`bytes_obj`/`pct_bytes_igual_quase`/`pct_bytes_sem_par` (resultado do comparador na linha de base usada).
As faixas marcadas "≈" no painel são as sem faixa firme (tamanho do 645).

Frente B: `src/projectg/jp/jp.tsv` (mesmo formato do `projectg.tsv`, símbolos das unidades novas; vence o mapa da A) e
`src/projectg/jp/units.txt` (lista de unidades). O mapa das unidades novas é `out/F3.7/s1/unidades_novas.tsv`.

### 4.2 `map/` — dll
| Arquivo | Formato |
|---|---|
| `wangreal.tsv` | `nome decorado<TAB>VA no 983` (mapa do comparador para a dll) |
| `wangreal_funcs.tsv` | por função da dll 983: `va, sz, ni, kind, d839, va839, conf839, va645, conf, via, obj, obj_via, cmp, nome, decorado, cls` (par no 839, par no 645, `.obj` dono, resultado do comparador). Gerado por `tools/f04_map.py`; não editar. |
| `wangreal_983_839.tsv` | pares 983↔839 (sem cabeçalho): `va983, va839, confiança, como casou, hash, nome, origem do nome, nº instr. 983, nº instr. 839` |
| `wangreal_gaps.tsv` | trechos de código fora do mapa de funções: `va, sz, obj, tipo, funcao_anterior` |

### 4.3 Estado: `status.json`, diários, pedidos
`status.json` (sempre via `flock status.lock python3 tools/st.py …`):
```
{"updated": ISO-8601, "fase": "F3",
 "tarefas": [{"id": "F3.5", "titulo": "...", "estado": "pendente|em_andamento|feito|bloqueado", "nota": "...", "atualizado": ISO}],
 "eventos": [{"quando": ISO, "texto": "..."}]}        # só os 30 últimos
```
- `st.py add <id> <título>` cria; `st.py task <id> <estado> "<nota>"` muda (nota vazia `""` mantém a anterior);
  `st.py ev "<texto>"` soma um evento; dá para encadear vários num comando só.
- Campos opcionais por tarefa, lidos pelo painel: `"frente": "A|B|C"` e `"fase": "F4"`. Sem eles a frente sai do id
  (`F3.7*` = B; `V3`+, `D*`, `P2`+ = C; resto = A) e a fase do prefixo `F<n>` (sem prefixo = F3).
- A nota deve dizer o resultado **e onde está a evidência** (`out/<tarefa>/…`).

Outros arquivos de estado:
- `HANDOFF.md`: as tarefas e as decisões do dono; o fim do arquivo é o mais recente. `PLANO.md`: fases F0–F5.
- `NOTES.md` (A), `NOTES-B.md`, `NOTES-C.md`: diário por sessão — o que fez, descobriu, errou, o que é provisório, onde parou.
- `out/PEDIDOS.md`: pedidos entre frentes. Título `## X → Y (data, sessão) — texto`; quem atende acrescenta
  `[ATENDIDO dd/mm]` no fim do título (o painel conta como aberto o que não tem a marca).
- `runs/runner{,-B,-C}.log` e `runs/{,B-,C-}session-N.log`: registro dos executores automáticos.
- Marcas na raiz: `STOP` (para as três frentes), `DONE[-B|-C]`, `NEEDS_HUMAN[-B|-C].md`.
- Travas (`flock`): `status.lock` (status.json), `git.lock` (commit), `/root/jp983/ghidra.lock` (Ghidra).

### 4.4 Painel: `out/painel/`
- `index.html`: página única com os dados embutidos (`window.PROGRESS`), sem nada externo.
- `historico.jsonl`: uma linha JSON por mudança —
  `{"date", "dll_total", "dll_igual", "dll_iq", "exe_total", "exe_igual", "exe_iq", "commit", "sessao"}` (bytes de código
  próprio do 983; `_igual` = cobertos por função IGUAL; `_iq` = IGUAL + QUASE). Só ganha linha quando um número ou o commit muda.
- De onde o painel tira os números: dll = o `out/**/image/funcoes.tsv` mais novo; exe = o `funcs.tsv` mais novo de cada
  unidade em `out/**/cmp/src_*/` (frente B: `out/F3.7/**/cmp/<unidade>/`), contado por endereço do 983 sobre
  `map/projectg_funcs.tsv`; compilação = `out/**/base.tsv` mais novo; asserts = `out/V*/layoutcheck.tsv` mais novo.
- O serviço `jp983-painel` regera a cada 2 min: edição pela metade em `tools/painel.py`/`painel_modelo.html` vai ao ar.

### 4.5 Saída do comparador e do build
- `cmp/<unidade>/funcs.tsv`: `arquivo, funcao (nome decorado), propria (1 = definida neste .cpp; 0 = inline/modelo que veio
  de cabeçalho), classe, pct_instr (0–1), va983, origem, n_obj, n_983 (instruções), bytes_obj, bytes_983, hx, hr, hm,
  bytes_iguais, nota`.
- `base.tsv` (uma linha por unidade): `unidade, estado (ok|nao_compila|cmp_falhou), proprias, IGUAL, QUASE, DIFERENTE,
  SEM_PAR, B_IGUAL…B_SEM_PAR (bytes), pct_instr`. `compila.tsv`: `unidade, compila (sim|nao), primeiro_erro`.
- `out/V3/layoutcheck.tsv`: `unidade, cabecalho, tipo (SIZE|OFF|ANOT), classe, membro, valor_983, resultado, valor_nosso,
  erro, evidencia`.
- Evidência de cada tarefa: `out/<id da tarefa>/` (na F3.5 e F3.7, uma pasta por sessão: `out/F3.5/s40/`), sempre com `RELATORIO.md`.

---

## 5. O comparador (`tools/cmpfunc`)

Compila um `.cpp` (ou recebe um `.obj`) e compara **cada função do `.obj`** com a função do 983 que é o par dela.
Compara instrução por instrução, mascarando o que muda só por causa do endereço (relocações).

```
tools/cmpfunc src/engine/bitmap.cpp                      # dll: compila e compara (ref e mapa escolhidos sozinhos)
tools/cmpfunc src/engine/bitmap.cpp --diff Save          # mostra lado a lado as funções cujo nome contém "Save"
tools/cmpfunc src/engine/bitmap.cpp --diff all           # todas as que não são IGUAL
tools/cmpfunc X.obj --no-build --ref ref/ProjectG_983_dump.exe --map map/projectg.tsv \
      --seed map/projectg_seed.tsv --funcs map/projectg_funcs.tsv --out DIR      # exe: é o que o pgbuild.py cmp chama
```
Para o exe, na prática: `python3 tools/f32/pgbuild.py cmp <filtro> --out DIR` (ou `make pg-base U=<filtro> OUT=DIR`);
para ver uma função, a linha longa acima com `--diff Nome` no lugar de `--out`.

Como ler uma linha da saída:
```
classe    %instr 983      origem   n.obj n.983 bytes hash  função
IGUAL     100.0% 00c02cd0 mapa         4     4    25 xrm=  ??1FrGaugeBar@@UAE@XZ
QUASE      98.0% 00c03fc0 mapa       101   101   332 ---   ?OnProc@FrGaugeBarImage@@MAEXM@Z
IGUAL     100.0% -        bytes*6      2     2     4 xrm=  (inline) ?GetRect@FrWnd@@QAEABVWRect@@XZ   [em 6 lugares: …]
```
- **classe**: `IGUAL` (mesmas instruções, registradores, imediatos e desvios, alvos coerentes); `QUASE` (≥ 90% das
  instruções alinhadas iguais); `DIFERENTE`; `SEM_PAR` (não achou onde a função está no 983).
- **%instr**: semelhança das instruções. **983**: VA do par (`-` = sem lugar único).
- **origem**: como o par foi achado — `mapa` (do `map/…tsv`), `bytes` (achada por bytes; `bytes*N` = em N lugares, sem
  lugar único), `alvo` (pelo destino de quem chama), `vizinho` (pela ordem do fonte), `semente` (mapa fraco).
- **n.obj / n.983**: nº de instruções de cada lado; **bytes**: tamanho da nossa.
- **hash**: `x` exato, `r` sem imediatos/deslocamentos, `m` só mnemônicos, `=` bytes idênticos fora das relocações.
  `-rm` (só `x` falha) quase sempre significa **só um deslocamento de campo ou imediato diferente → layout de classe**.
- **(inline)**: função que veio de cabeçalho (não é "própria" da unidade); só as próprias contam nos totais.
- nota `alvo:` no fim: um símbolo chamado aponta para um endereço diferente do que o mapa diz (rebaixa IGUAL para QUASE).

O `--diff` mostra as duas colunas (nossa à esquerda, 983 à direita): `<` só na nossa, `>` só no 983, `|` diferente.
`python3 tools/f35/dv.py ARQ.diff Nome` filtra só essas linhas.

Limites: não compara dados (vtables, tabelas de exceção) nem funclets de exceção; "IGUAL por `bytes*N`" numa função
pequena não prova que o lugar é o dela. `--update-map` grava no mapa o que achou sem ambiguidade (usar com critério no exe).

**Critério (decisão do dono, 11/10/2026): funcional, não idêntico.** Pronta = compila + layout certo + IGUAL ou QUASE, ou
DIFERENTE com a mesma lógica justificada em uma linha no relatório. Não gastar sessão para subir QUASE a IGUAL.

---

## 6. Exemplo completo: adaptar `src/fresh/source/frgaugebar.cpp` (sessão 40 da F3.5)

Unidade pequena da biblioteca Fresh (barras de progresso): 37 funções próprias, 11 kB. Estava com 18 IGUAL; ficou com
32 IGUAL + 3 QUASE + 2 DIFERENTE, 0 SEM_PAR. Relatório original: `out/F3.5/s40/RELATORIO.md`; commit `f353530`.
Os comandos abaixo foram rodados de novo na sessão C3 e dão os mesmos números.

**Passo 0 — cópia de trabalho própria** (não mexe no build da frente A; `d1` é um nome qualquer):
```
python3 tools/f32/pgbuild.py pch --tag d1                 # 17 pch em build/pg-d1/pch (1–2 min; uma vez)
T=/tmp/d1/tmp; mkdir -p $T                                # /tmp/ no caminho: o painel ignora
```

**Passo 1 — achar a unidade no 983:**
```
grep gaugebar map/projectg_units.tsv
```
→ `ini983 00c02d00`, `fim983 00c05a9a`, `bytes983 11146`, `funcs983 46`, onda "1 cpp, mudou pouco". As funções da faixa,
com o par no 645 e o nome: `awk -F'\t' '$1>="00c02d00" && $1<"00c05a9a"' map/projectg_funcs.tsv`.

**Passo 2 — compilar e comparar** (4 s + 6 s):
```
python3 tools/f32/pgbuild.py obj fresh/source/frgaugebar.cpp --tag d1 --out $T
python3 tools/f32/pgbuild.py cmp fresh/source/frgaugebar.cpp --tag d1 --out $T
```
→ `pg-base: 1 unidades comparadas, 37 funções próprias (11046 B): IGUAL 32 …; QUASE 3 …; DIFERENTE 2 …; SEM_PAR 0`.
Se não compilar, o erro está em `build/pg-d1/obj/src/fresh/source/frgaugebar.log`.

**Passo 3 — listar as próprias que não são IGUAL:**
```
awk -F'\t' 'NR>1 && $3==1 && $4!="IGUAL"{print $4,$5,$6,$7,$2}' $T/cmp/src_fresh_source_frgaugebar/funcs.tsv
```
→ `QUASE 0.9802 00c03fc0 mapa ?OnProc@FrGaugeBarImage@@MAEXM@Z`, `DIFERENTE 0.8487 00c03e10 vizinho ?OnDraw@FrGaugeBarImage…`, etc.
Começar pelas `SEM_PAR` (função que não existe mais ou mudou muito) e pelas `-rm` (layout).

**Passo 4 — ver a diferença de uma função:**
```
tools/cmpfunc build/pg-d1/obj/src/fresh/source/frgaugebar.obj --no-build --ref ref/ProjectG_983_dump.exe \
   --map map/projectg.tsv --funcs map/projectg_funcs.tsv --diff 'OnProc@FrGaugeBarImage' > /tmp/d1/diff.txt
python3 tools/f35/dv.py /tmp/d1/diff.txt 'OnProc@FrGaugeBarImage'
```
→ as únicas linhas diferentes são um `fstp/fld dword ptr [ebp + 8]` que no nosso código vem duas instruções antes do
lugar em que o 983 o põe: mesmo cálculo, arredondamento para `float` em outro ponto. É um QUASE aceito (uma linha no relatório).

**Passo 5 — ler o 983 quando a lógica mudou.** Na sessão 40 a `FrGaugeBar::OnProc` (00c03010) não batia:
```
python3 tools/f37/dz.py 00c03010 200          # desmonte
tools/f37/dec.sh /tmp/d1/dec.txt 00c03010     # pseudo-C do Ghidra (10 s)
```
O pseudo-C mostra `param_1[0x41]` etc.: índice × 4 = deslocamento (0x41 → `this+0x104` = `m_pos`). O 983 calcula o passo
numa expressão só, sem variável intermediária arredondada. O fonte ficou assim (e a função deu IGUAL):
```cpp
void FrGaugeBar::OnProc(float elapsed)
{
	float step;
	if (m_achillesRun && m_destPos != m_srcPos)
		step = (m_destPos - m_pos) * (m_speed * elapsed) / (m_destPos - m_srcPos);
	else
		step = m_speed * elapsed;
	if (m_pos > m_destPos)
		m_pos = m_pos - step > m_destPos ? m_pos - step : m_destPos;
	else if (m_pos < m_destPos)
		m_pos = m_pos + step < m_destPos ? m_pos + step : m_destPos;
	CalcBarRect(0);
}
```
Formas que o VS2010 distingue e que resolveram esta unidade (valem para as outras): sem `fstp/fld` no 983 = a conta era
uma expressão só; `fdiv` por constante double = `/ 100.0` e não `* 0.01f`; `movzx` de byte direto da memória = acesso
por ponteiro de bytes, não `>>`; `0.0f == x ? 0.0f : x / n` deixa o zero na pilha como o 983.

**Passo 6 — quando é o layout da classe que mudou.** A `FrGaugeBarImage` perdeu um membro no 983. Como se mede:
```
python3 tools/f34/rtti.py FrGaugeBarImage     # vtable e os endereços que a gravam = construtor(es)
python3 tools/f37/dz.py <construtor> 200      # o construtor zera os campos na ordem: dá o deslocamento de cada um
python3 tools/f34/co.py FrGaugeBarImage       # o layout como o NOSSO cabeçalho gera, para comparar
```
O `sizeof` vem do `push N` antes do `call operator new` de quem cria a classe (`out/V3/sizes_983.tsv` já tem 510 classes).
Acerta-se o cabeçalho (`src/fresh/include/frgaugebar.h`); campo novo de função desconhecida ganha nome `unk983_<desloc>`.
Classe nova achada pelo RTTI (aqui `FrGuiItemDefault`, vtable 00d5ee08) é declarada onde a base está.

**Passo 7 — onde editar.** `frgaugebar.cpp/.h` estão em `map/adotados.txt`: edita-se direto. Se o arquivo ainda fosse
cópia do rebang, ou se entra na lista de adotados (uma linha), ou a troca vai num `tools/f32/ajustes_s<sessão>.py`.

**Passo 8 — repetir os passos 2–4** até sobrar só QUASE/DIFERENTE justificado. Função que continua DIFERENTE com a
mesma lógica: anotar no relatório o que difere (ordem na pilha, registradores) e parar.

**Passo 9 — conferir que nada piorou no resto** (um cabeçalho da Fresh entra em centenas de unidades):
```
make pg-obj  OUT=out/F3.5/sNN/depois          # tudo; 15–25 min
make pg-base OUT=out/F3.5/sNN/depois          # tudo; 20–45 min
python3 tools/f34/ab.py out/F3.5/s<anterior>/depois out/F3.5/sNN/depois      # o que entrou e o que saiu de IGUAL
make layoutcheck                              # os static_assert de layout (4–5 min; U=jp_ só as unidades do JP)
make base && make pilot && make cmp-selftest  # se mexeu em include/engine: a dll não pode regredir
```
Na sessão 40: +14 IGUAL, todas no frgaugebar; 0 saíram.

**Passo 10 — registrar:** `out/F3.5/sNN/RELATORIO.md` (o que mudou, com o endereço do 983 que prova; números medidos; o
que é provisório), diário, `status.json` (`tools/st.py`), `make painel`, e o commit só dos próprios caminhos:
```
flock git.lock git commit -m "..."            # depois de git add dos caminhos da frente; nunca git add -A
```

Para uma unidade **nova do JP** (sem fonte no 645) o roteiro é o da frente B: seção "FRENTE B" do HANDOFF e
`out/F3.7/s2/RELATORIO.md` (layout pelo construtor, cabeçalho em `include/jp/`, `.cpp` em `src/projectg/jp/`, linha em
`units.txt`, símbolos em `jp.tsv`, `make jp-cmp`).

---

## 7. Problemas comuns
| Sintoma | Causa provável / o que fazer |
|---|---|
| todo `make` falha com `g++ Makefile.C -o Makefile` | regra embutida `%: %.C` quando o `Makefile.C` fica mais novo que o `Makefile`; o `Makefile.C` tem a regra vazia `Makefile: ;` para impedir — não apagar |
| `C1902` (gerenciador de PDB) | alguém pôs `/Zi`; aqui é sempre `/Z7` |
| `.obj` "em dia" mas com código velho | o pch falhou; ver `build/pg/pch/*.log` e recompilar com `--force` |
| unidade compila sozinha e falha no `make pg-obj` | outra frente está editando um cabeçalho agora; esperar e repetir |
| muitas funções `-rm` de uma classe | layout da classe diferente do 983: `make pg-votes U=<unidade>` e `tools/f34/clsvotos.py` |
| IGUAL em função pequena num endereço estranho | casou por bytes em lugar errado: vetar em `map/projectg_fora.tsv` ou fixar em `projectg_manual.tsv`, depois `make pg-map` |
| painel com o exe zerado | faltam os `out/**/cmp/` (clone novo): `make pg-obj` + `make pg-base` |
| painel com número estranho depois de um teste | um experimento gravou `cmp/` fora de `/tmp/`, `/antes/`, `/ab/`; apagar a pasta |
| Ghidra parado | outro Ghidra segura o `ghidra.lock`; esperar (nunca abrir os projetos sem `-readOnly`) |
| `static_assert` falhando no `make layoutcheck` | cabeçalho com layout diferente do 983: é pedido para a frente dona em `out/PEDIDOS.md`, não se "conserta" o assert |
- `tools/f37/rd.py f<VA>|d<VA>|u<VA>|s<VA>…` (frente B, B24): lê do dump do 983 um float, double, dword ou texto em cada endereço.
- `tools/f37/delta.py <sessão anterior> <sessão nova> [unidade]` (frente B, B24): totais das funções próprias, mudanças de classe
  entre duas sessões de out/F3.7 e a lista das não IGUAL de uma unidade (gera o resumo.txt da sessão).
