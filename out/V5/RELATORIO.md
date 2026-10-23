# V5 — Patches do rugburn no JP 983: o que vira código no exe compilado

Frente C, sessão C5 (11/10/2026). Refazer: `make v5` (≈15 s, só leitura; tools/v5/rb.py). Saída do comando: out/V5/make_v5.log.

## 0. Limite desta sessão (ler primeiro)

**O rugburn do dono não está no container.** Ele fica no PC de teste (`E:\dev\pangya-test\JP983\ijl15.dll` + `rugburn.json`,
docs/RETOMAR.md §11). `find /` por `ijl15*`/`*rugburn*` só acha `ijl15.lib` do rebang. Por isso:

- O que está **conferido** aqui é o rugburn **público** (github.com/pangbox/rugburn, commit `7158511`, 28/05/2025, que
  declara suporte a "PangYa JP 983"), lido em build/C/v5/rugburn (clone, fora do git) e conferido byte a byte contra
  `ref/ProjectG_983_dump.exe`. O trecho usado está guardado em out/V5/rugburn_jp983_trecho.c.
- O que é **do dono** (login 10803→30101, web 30090, "regra 8080 removida") vem do HANDOFF/RETOMAR, não de arquivo lido.
  Está marcado como *informado, não conferido*. Perguntas no fim (§6). Nada do PangYa Relic foi tocado.

## 1. O que o rugburn faz (visão geral)

`ijl15.dll` falsa: o exe importa 4 funções dela (`ijlInit/Read/Write/Free`; a wangreal.dll não importa), então o Windows a
carrega junto com o jogo. No `DllMain` ela (a) lê `rugburn.json`, (b) põe a variável de ambiente `PANGYA_ARG`, (c) instala
ganchos em APIs do Windows. Só **uma** parte usa endereços fixos do exe: o desarme do GameGuard.

| # | O que faz | Como | Depende de endereço do exe? |
|---|---|---|---|
| 1 | Desarma o GameGuard | 6 `Patch()` em endereços fixos, aplicados na 1ª `GetStartupInfoW` vinda do exe (partida do CRT) | **sim** |
| 2 | Finge que `GameGuard.des` rodou | gancho em `CreateProcessA` / `GetExitCodeProcess` (devolve 0x755) | não |
| 3 | Dispensa o atualizador | `PANGYA_ARG={E69B65A2-7A7E-4977-85E5-B19516D885CB}` (JP) | não |
| 4 | Desvia o login/jogo | gancho em `connect`: `PortRewrites` (porta de origem → endereço:porta) | não |
| 5 | Desvia a web | ganchos em wininet (13 funções) e no WebBrowser (ole32): `UrlRewrites` (regex) | não |
| 6 | Tira "sempre no topo" | gancho em `CreateWindowExA` (remove `WS_EX_TOPMOST`) | não |
| 7 | Conserto para Wine | gancho em `_stricmp` só se detectar o defeito | não |
| 8 | Patches livres | `PatchAddress` do `rugburn.json` (endereço → bytes) | **sim** |

## 2. Endereço → efeito no exe 983 (out/V5/patches_983.tsv)

O rugburn reconhece o 983 por `*(DWORD*)0x00A5CF80 == 0x1C143D83` — **bate** (são os 4 primeiros bytes de `_GGC_Init`:
`cmp dword [0x00f01c14], 0`).

| Endereço | Bytes do rugburn | O que há ali no 983 | Veredito |
|---|---|---|---|
| 00a5cf80 | `C3 90×6` | início de `_GGC_Init` (ggc_wrapper.cpp) | **certo**: a função vira `ret` |
| 00a5c010 | `C3 90×6` | meio de `GGC_Helper::GGC_Helper` (+0x170), **no meio de uma instrução** | **endereço errado** |
| 00a5c030 | `C3 90×6` | meio de `GGC_Helper::GGC_Helper` (+0x190) | **endereço errado** |
| 00a5c050 | `90×7` | meio de `GGC_Helper::GGC_Helper` (+0x1b0) | **endereço errado** |
| 00a5ce80 | `C3` | byte 196 da tabela do `switch` de `GGC_Helper::StackError` (erro 306 do GameGuard) | **endereço errado** |
| 00a5ceb0 | `C3` | byte 244 da mesma tabela (erro 354) | **endereço errado** |

**Achado: dos 6 patches do rugburn público para o JP 983, só o primeiro cai no lugar.** Os outros cinco deviam cair em
`_GGC_SetHwnd` 00a5**d**010, `_GGC_SendUserID` 00a5**d**030, `_GGC_CheckGameMon` 00a5**d**050, `_GGC_End` 00a5**d**080 e
`_GGC_CSAuth2` 00a5**d**0b0 (mesmas distâncias do ramo "JP 972": +0x90, +0xb0, +0xd0, +0x100, +0x130). O ramo "JP 974" tem
os mesmos números.

Por que o jogo funciona mesmo assim (conferido no desmonte, out/V5/ggc_chamadas.tsv):

- Com `_GGC_Init` virando `ret`, o ponteiro do GameGuard (`00f01c14`) fica nulo. As outras cinco funções da cola **já**
  começam com "se o ponteiro é nulo, sai" (`_GGC_CheckGameMon` devolve 1). Ou seja: **o primeiro patch sozinho basta**.
- O `ret` devolve o que estava em `eax`. O WinMain (00a72a30) testa `eax != 0` logo depois; `eax` ali é o resultado de
  `CheckRelatedDLL` (≠ 0, senão nem chamaria). Funciona, mas por coincidência do registrador.
- Os 5 patches errados estragam código que **só roda em erro do GameGuard**: o construtor de `GGC_Helper` só é chamado por
  `GGC_GetHelper`, que só é chamado por `_GGC_Init` (anulado), pelo diálogo de erro `GGC_Dlg` (00a59ef0) e por
  `GameGuardMsgHandler::Process` (retorno de chamada do GameGuard, que nunca sobe). Dano dormente, não aparece no teste.

Chamadas da cola no jogo: `_GGC_Init` e `_GGC_End` no WinMain (00a72d09, 00a72d90); `_GGC_SetHwnd`/`_GGC_End` em
`RunProjectG` (00a727d0); `_GGC_SendUserID` em `CLobbyTask::OnPacket` (00ac21a6); `_GGC_CheckGameMon` em
`CMainFrame::Main` (00a6186f); `_GGC_CSAuth2` via 00a5d150 em 009cc61a.

## 3. APIs interceptadas × exe 983 (out/V5/ganchos_api.tsv)

22 APIs; o exe importa 21 (não importa `GetStartupInfoA`; o CRT dele usa a `W`, que é o gatilho do patch).

- `CreateProcessA`, `GetExitCodeProcess`: **0 usos no código do jogo**, 5 e 3 dentro da NPGameLib/CRT. Só servem ao GameGuard.
- `connect`: 1 uso no jogo — `WSocket::Connect` (00a4ef70). Todo servidor (login, jogo, mensageiro) passa por ele.
- wininet: `GenericHTTPClient` (Connect/RequestGet/RequestPost/RequestPostMultiParts), `GetUrlFile` (rssmanager),
  `CPPL::IsPPLEnable`, `FrGuildDlg::DownLoad`, chttp.cpp (00a4c1c0…), 0053f9c0.
- `CoCreateInstance`/`CoGetClassObject`: browser.cpp (0086dd70) e ATL do winmain — páginas web dentro do jogo.
- `CreateWindowExA`: 7 usos; só o da tela de abertura (splash.cpp 009958b4, estilo 0x80088) pede `WS_EX_TOPMOST`.

## 4. O que o exe 983 traz embutido (out/V5/constantes.tsv, out/V5/rede_983.tsv)

| O quê | Exe 983 | Nosso fonte hoje |
|---|---|---|
| Login: endereço | `157.7.173.48` (global 00e30834, lido por `LoginUnit::Connect` 00a51f40) | `211.44.251.73` (KR 645) |
| Login: porta | tabela de 2: `10803, 10803` (00e30838; sorteia com `rand() & 1`) | `10101`, tabela de 1 |
| Nome no GameGuard | `"PangyaJP"` | `"PangyaTest"` |
| `PANGYA_ARG` | WinMain 00a72b45: se não é login web e `IsLocalContent(13)`, exige `{E69B65A2-…}` (zera o byte 00e33f56) ou `{2D0FA99B-336B-4e99-0D34-5987431EFDA0}`; senão mostra "rode o atualizador" e sai | **não existe** no winmain.cpp (WinMain compara DIFERENTE, 57,7%) |
| Mutex de instância | `{071784A2-EE35-4e6a-92D0-6E7A4B985171}` | igual |

Rede: 30 URLs e 3 IPs no exe; **30 das 33 strings não existem no nosso fonte** (o fonte tem as do KR 645). 13 URLs não
casam com a regra de exemplo do rugburn (`http://[a-zA-Z0-9:.]+/(.*)`): as 10 `https://www3/www5.pangya.jp/…` (pagamento,
entrada, gacha, clube, eventos) e 3 sem barra final (`http://www.pangya.jp`, `http://dl.pangya.jp`, …). Para o servidor
local atender essas páginas, o `rugburn.json` precisa de regra própria para `https://`.

## 5. Decisão para o exe compilado

Ponto de partida: **no exe compilado os endereços mudam**. A checagem `*(00A5CF80) == 0x1C143D83` deixa de bater, o rugburn
público não aplica nenhum patch de GameGuard e o jogo tentaria iniciar o GameGuard de verdade. E qualquer `PatchAddress`
escrito para o exe original passaria a escrever em lugar errado.

| # | Item | Decisão | Onde | Estado |
|---|---|---|---|---|
| 1 | Desarme do GameGuard | **vira código**: chave de compilação (sugestão `JP983_SEM_GAMEGUARD`) em `_GGC_Init` → `return TRUE` sem criar `CNPGameLib`. O resto da cola já se anula com o ponteiro nulo. Sem a chave, o código fica fiel ao 983 (`"PangyaJP"`) | src/projectg/ggc_wrapper.cpp (frente A) | pedido C→A |
| 2 | `GameGuard.des` falso | **some**: sem `CNPGameLib` ninguém chama; e a NPGameLib de 2016 nem precisa entrar no link (a do rebang é a do 645) | link (F4) | anotar na F4 |
| 3 | `PANGYA_ARG` | **código fiel + valor externo**: escrever a checagem do 983 no WinMain; o valor continua vindo do rugburn (ou de `set PANGYA_ARG=…` no .bat) | src/projectg/winmain.cpp (A) | pedido C→A |
| 4 | Endereço/porta do login | **constantes do 983 no fonte** (`157.7.173.48`, `{10803, 10803}`); o **desvio continua externo** (`PortRewrites`). Com 10803 no exe, a regra que o dono já usa continua valendo sem mexer no json | src/projectg/loginunit.cpp (A) | pedido C→A |
| 5 | URLs | **strings do 983 no fonte** (lista em rede_983.tsv); **desvio externo** (`UrlRewrites`) | várias unidades (A/B) | pedido C→A, informativo |
| 6 | Sempre no topo | **externo** (cosmético; só a tela de abertura) | — | nada a fazer |
| 7 | `_stricmp` do Wine | **não se aplica** no Windows | — | nada a fazer |
| 8 | `PatchAddress` | **não reaproveitar**: no teste do exe compilado o `rugburn.json` não pode ter `PatchAddress` do exe original | roteiro de teste (V6) | levar para a V6 |
| 9 | Carga do rugburn | **manter a importação de `ijl15.dll`** no exe (commonutil.cpp e engine/wresrcmng.cpp usam `ijl`; ligar com `ijl15.lib`). Sem ela o rugburn não carrega e nada é desviado | link (F4) | anotar na F4 |

Resumo: **1 coisa vira código de verdade (GameGuard desligado por chave de compilação)**; 3 viram *constantes certas* no
fonte (login, `PANGYA_ARG`, URLs); o desvio de rede e o resto continuam no rugburn, que segue funcionando com o exe
compilado porque essas partes não dependem de endereço.

## 6. Perguntas ao dono (não bloqueiam; a V6 segue)

1. Copiar para o container o `rugburn.json` do cliente de teste (e, se possível, o `gglog.txt` de uma partida e o
   tamanho/data do `ijl15.dll`). Com isso confiro: regras de porta (10803→30101?), regras de URL (30090; pega `https://`?),
   e **se há `PatchAddress`** (item 8).
2. O `ijl15.dll` do dono é o rugburn público compilado ou tem mudança própria (em especial nos 6 endereços do §2)?
3. No teste do exe compilado, o GameGuard fica **desligado por compilação** (item 1)? É o que o PLANO prevê para a F5;
   a proposta é antecipar para a F4, porque sem isso o exe compilado não passa da abertura.

## 7. Incerto / não feito

- Tudo sobre o rugburn **do dono** (§0). O `gglog.txt` mostraria quais patches e desvios de fato acontecem.
- "Dano dormente" dos 5 patches errados: concluído pelas chamadas diretas (ggc_chamadas.tsv); não procurei chamada
  indireta ao construtor de `GGC_Helper` (não há ponteiro para 00a5bea0 no código, só o `call` de `GGC_GetHelper`).
- A coluna `regra_exemplo_casa` testa a string literal; várias URLs são prefixos ou formatos (`%s`) completados em execução.
- `usos_jogo` conta referência ao endereço da importação (inclui `mov reg, [iat]`); não segue `call reg`.
- 3 das URLs são lidas por tabela de dados (00e0d034…), e 4 por código fora de função do mapa (00594ac3…): sem nome.

## 8. Atualização (13/10/2026, C-F4.6): o `ijl15.dll` da pasta de teste é de TERCEIRO

- Resposta ao §6 item 2 (out/F4/RESPOSTA_USUARIO_2a.md): o `ijl15.dll` de `E:\dev\pangya-test\JP983` **não é do dono nem o
  rugburn público** — é um rugburn modificado de terceiro (veio junto com a pasta do cliente; origem desconhecida). Cópia:
  out/F4/ijl15_rugburn_terceiro.dll (494.592 bytes); textos em out/F4/ijl15_rugburn_terceiro_strings.txt.
- Além dos patches de GameGuard do público, grava em **endereços fixos do exe ORIGINAL** (BIG Papel Shop/F8, World Tour/F9,
  Wind Cap 9m→15m, linha de troca de apelido, Scratchy Card, distância "%.2f" em jardas, Caliper) e faz checagens
  "Anti-Cheat" de memória (Sempre Pangya "D8 80 E8"/"D9 98 E4", Alpha, Círculo Raio, Deslocamento X/Y, ShotType).
- **Nunca usar com o exe compilado**: nele esses endereços caem em código/dados quaisquer (teste 2: duas caixas
  "Anti-Cheat ... Sempre Pangya" e o modo "continuar" dos stubs não pegou). O exe compilado vai com
  `ijl15_teste.dll` = rugburn **público** (commit 7158511) com o VS2010 do container, **sem nenhum patch de endereço fixo**
  (dynamic_patch.c trocado por tools/v6/ijl15teste/sem_endereco.c; ranking US 852 fora; `PatchAddress` do json ignorado e
  anotado no gglog.txt). `make f4-ijl15`; portão A6 (tools/v6/portoes.py) e os .bat da entrega trocam/conferem o ijl15.
- Com o exe ORIGINAL, o dono continua com o ijl15 de terceiro (`VOLTAR_EXE_ORIGINAL.bat` devolve o `ijl15.dll.orig`).
