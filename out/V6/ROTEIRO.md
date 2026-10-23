# V6 — Roteiro de teste do ProjectG.exe compilado (JP 983)

Escrito pela frente C na sessão C6 (11/10/2026). **O exe compilado ainda não existe** (é a fase F4); este roteiro fica
pronto para o dia em que existir. Quem testa é o dono, no PC com Windows; os agentes nunca rodam o jogo.

- Parte A: o que tem de estar verde no container **antes** de mandar um exe para teste.
- Parte B: preparação no PC (guardar o original, trocar o exe, rugburn).
- Parte C: os 42 passos, em 8 blocos (abrir, login, lobby, sala, partida, loja, my room, sair).
- Parte D: como voltar ao exe original.
- Parte E: o que anotar e mandar de volta.
- Parte F: **dúvida em aberto — qual servidor usar** (decisão do dono).

Arquivos de apoio nesta pasta: `PRONTIDAO.md` (números do dia, por bloco; refeito por `make v6`), `pacotes_por_passo.tsv`
(ids de pacote do 983 por bloco), `bat/USAR_EXE_NOSSO.bat` e `bat/VOLTAR_EXE_ORIGINAL.bat`.

---

## Parte A — antes de mandar um exe para teste (conferido no container)

Cada linha é um portão. Se um portão está fechado, o bloco indicado **vai falhar** e testar antes disso só gasta o tempo do dono.

| # | Portão | Como conferir | Hoje (11/10/2026) | Sem ele falha |
|---|---|---|---|---|
| A1 | O exe liga (F4) | existe `ProjectG.exe` compilado + md5 anotado (`make f4-portoes`) | 13/10: **ok** — `make exe` (C-F4.4) liga SEM /FORCE com os stubs e o `ggc_wrapper.obj` sem GameGuard: `build/C/f4/ProjectG_983.exe`, 11.035.136 bytes, md5 `a0c076bff61ab61317b3962b49d3264a` (C83; teste 2 = 4c78b7d4…, teste 1 = a112550c…), 0 não resolvidos; entrega em `out/F4/entrega/` (`ProjectG_nosso.exe`); o que falta em `out/F4/FALTA.md` | tudo |
| A2 | GameGuard desligado por compilação (V5 §5 item 1) | `make f4-portoes`: `ggc_wrapper.cpp` com `CL=/DJP983_SEM_GAMEGUARD` → `_GGC_Init` = `mov eax,1; ret`; o `make exe` tem de usar `build/C/f4/gg/ggc_wrapper.obj` | 13/10: **ok** (chave escrita na C-F4.2; sem a chave segue IGUAL ao 983) | bloco 1 (não passa da abertura) |
| A3 | Importa `ijl15.dll` (é por ela que o rugburn carrega) | lista de importações do exe ligado (`make f4-portoes`) | 13/10: **ok** no exe de prova (4 nomes × 4 do 983) | bloco 2 (o desvio de porta não acontece) |
| A4 | Login com as constantes do 983: `157.7.173.48`, portas `{10803, 10803}`; checagem do `PANGYA_ARG` | `make v5` → `out/V5/constantes.tsv` sem `DIFERE` | 13/10: **ok** (6 de 6 iguais; checagem do `PANGYA_ARG` no WinMain escrita na C-F4.2) | bloco 2 |
| A5 | Todo import de dll que não é do Windows existe na dll real do cliente (pedido do dono após o teste 1, C-F4.5) | `make exe` (portoes.py `a5`): imports de mss32/ijl15/msvcr100/msvcp100 × `tools/v6/f4dll/*.txt` (Mss32.dll do cliente JP 983, rugburn, redistribuível VS2010) → `out/F4/exe/imports_a5.tsv`; fechado = `make exe` falha e não entrega | 13/10 (C82): **ok** — o teste 1 parou no carregador (`_AIL_set_DirectSound_HWND@8` não existe no Mss32.dll do cliente); C83: o miles.cpp do 983 (C82.1 da A) saiu do tampão; as funções `_AIL_file_*_info` vêm de uma import lib complementar (`build/C/f4/mss32x.lib`, linkprova.py) | bloco 1 (o Windows nem carrega o exe) |
| A6 | O `ijl15.dll` que vai com o exe é o DE TESTE (pedido do dono após o teste 2, C-F4.6) | `make exe` (portoes.py `a6`): `ijl15_teste.dll` = rugburn público (`make f4-ijl15`) sem patch de endereço fixo, exporta os `ijl*` do exe; os `.bat` trocam o ijl15 (guardam `ijl15.dll.orig`) e o `ABRIR_COM_STUBS.bat` confere com `fc /b` e não abre se for outro | 13/10 (C83): **ok** — o `ijl15.dll` da pasta do cliente é um rugburn de TERCEIRO com patches em endereços do exe original (out/V5/RELATORIO.md §8) | bloco 1 (escreve lixo no exe compilado; teste 2) |
| A7 | Valores do 983 que o 645 QA/KR tinha diferentes (pedido C87, teste 5) | `make exe` (portoes.py `a7`): a chave XTEA da tabela dos `.pak` no `OpenPAKFILE2` (983 00bad6d0) é a do 983 (= chave da updatelist 00d3d60c) e nenhuma palavra da chave do 645 nem texto do QA (`Pangya_QA`, `ProjectG_ReleaseQA.exe`, `patch.pangya.ntreev.com`) está no exe; controle: o dump do 983 passa | 13/10 (C87): **ok** — a 4ª entrega reprova (tinha a chave do 645 no westpak: nenhum arquivo dos `projectg*.pak` era achado → `WFile("chat.bin")` lançou no `ChatManager::Load`, "fechou no carregamento") | carregamento (teste 5) |
| A8 | Ids de pacote do 983 no fonte (o fonte tem os do KR 645) | `make v4` → `difere_id` = 0 em `out/V4/pk_cmp_resumo.txt`; coluna "Só no fonte" de `PRONTIDAO.md` perto de 0 | `difere_id` 57; "Só no fonte" 97 no despachante comum | blocos 3 a 7 (lê o pacote errado) |
| A9 | Tabelas `.iff` com o tamanho de registro do 983 | `make layoutcheck U=shared_itemmanager` sem FALHA | 7 FALHA | blocos 2 a 7 (itens errados ou trava ao carregar) |
| A10 | Layout das classes (V3) | `make layoutcheck` sem FALHA | 1.043 ok, 48 FALHA | o bloco da classe (lista por bloco em `PRONTIDAO.md`) |
| A11 | Código de cada bloco escrito | `make v6` → coluna "Escrito" de `PRONTIDAO.md` | 38% no total (26% a 60% por bloco) | o bloco; **o exe nem liga sem 100%** (ou sem tampões declarados na F4) |

Regra prática: **A1 a A7 fechados = não mandar exe nenhum.** Com A1–A7 abertos e A8–A11 parciais dá para testar só os
blocos 1 e 2 (abrir e login) — avise o dono de até onde vale a pena ir.

---

## Parte B — preparação no PC (uma vez por exe recebido)

Pasta do cliente de teste: `E:\dev\pangya-test\JP983` (a mesma do teste da wangreal.dll).

- **B1.** Feche o jogo. Copie o exe recebido para a pasta onde estão os `.bat` desta entrega, com o nome `ProjectG_nosso.exe`.
- **B2.** Anote o md5 do exe recebido (vem na mensagem da entrega). O exe original é o dump do 983:
  md5 `8c76194bf825391f63fc951d3d4b09da`, 21.671.936 bytes.
- **B3.** Rode `USAR_EXE_NOSSO.bat`. Ele guarda o original em `ProjectG.exe.orig` e o `ijl15.dll` em `ijl15.dll.orig` (só
  na primeira vez), copia o exe nosso e o `ijl15_teste.dll` por cima e mostra os md5 e "portao A6 ok". Se o nome do exe na sua pasta não for `ProjectG.exe`, ajuste a linha `set EXE=` dos dois `.bat`.
- **B4.** `rugburn.json`: o `PatchAddress` (endereços do exe original) é IGNORADO pelo `ijl15_teste.dll` (anotado no
  gglog.txt). **Nunca** abra o exe compilado com o `ijl15.dll` de terceiro da pasta (ver A6). As regras de porta (`10803` → servidor) e de URL continuam iguais: não dependem de endereço.
- **B5.** Qual `wangreal.dll` usar: comece com a **original** (`VOLTAR_WANGREAL_ORIGINAL.bat`), para testar uma peça nova
  de cada vez. Só depois de o exe passar, repita com a nossa dll.
- **B6.** Apague (ou renomeie) o `gglog.txt` antigo, para o novo ter só esta rodada.
- **B7.** **Linha de base**: antes do exe novo, faça os mesmos blocos com o exe **original** no mesmo servidor e anote até
  onde ele vai. Se o original também para num passo, a falha é do servidor, não do exe.

Os dois `.bat` foram escritos no container e **não foram executados em Windows**; leia antes de rodar (são curtos).

---

## Parte C — os passos

Para cada passo: faça, olhe o que está na coluna "O que observar" e marque **OK / FALHOU / NÃO DEU PARA TESTAR**.
Ao primeiro FALHOU: anote o número do passo, tire uma captura, guarde os registros da Parte E e **continue só se o jogo
ainda responder** (uma falha visual não impede os passos seguintes; um fechamento sim).

### Bloco 1 — Abrir o jogo
| # | Fazer | O que observar |
|---|---|---|
| 1 | Abrir pelo `ABRIR_JP983_CS.bat` (ou o `.bat` do servidor escolhido na Parte F) | Não aparece janela do GameGuard nem a mensagem do `PANGYA_ARG` ("PangYa" + texto e o jogo fecha) |
| 2 | Esperar a tela de abertura | Imagem de abertura aparece e some; a janela do jogo é criada no tamanho configurado |
| 3 | Olhar o `gglog.txt` | Tem as linhas do rugburn carregando. **Não deve** ter "Patched GG check routines (JP 983)" (essa linha só aparece no exe original; se aparecer, o exe em uso é o original) |
| 4 | Esperar os logotipos e a tela de login | Fundo, logotipo, caixas de usuário e senha, cursor do jogo, música |
| 5 | Mover o mouse e clicar nas caixas; digitar | Cursor acompanha; texto aparece; teclado japonês (IME) abre a janela de composição |

Mensagem "PangYa" com texto pedindo para rodar o atualizador e o jogo fecha (passo 1) = o `PANGYA_ARG` não chegou ao exe
(o exe original faz igual): conferir se o rugburn/`.bat` põe `PANGYA_ARG` no ambiente, como no teste do exe original.

Se falhar aqui, suspeitar de: `winmain`, `projectg`, `ggc_wrapper`, `clientsetting`, `mainframe`, `splash`, `logo`,
carga dos `.iff` (`itemmanager`), `pakedresource`.

### Bloco 2 — Login e escolha de servidor
| # | Fazer | O que observar |
|---|---|---|
| 6 | Entrar com usuário e senha | No `gglog.txt`: uma linha `connect(…:10803 => …)` com o desvio para o servidor. No servidor: chega o pacote de login (id `0x1`, com usuário e senha) |
| 7 | Errar a senha de propósito (uma vez) | Mensagem de erro do jogo, sem fechar; dá para tentar de novo |
| 8 | Conta nova (se o servidor pedir): criar apelido e personagem | Tela de apelido aceita o texto; escolha de personagem mostra os bonecos (ids `0x6`, `0x7` ao servidor de login) |
| 9 | Lista de servidores | Nomes e lotação aparecem certos (não lixo); escolher um servidor (id `0x3`) |
| 10 | Lista de canais | Canais aparecem; entrar em um |
| 11 | Senha secundária, se a conta tiver | Teclado na tela funciona |

Se falhar aqui, suspeitar de: `loginunit`, `logindlg`, `serverdlg`, `networksystem`, `clientsocket`, `packet`,
`shareddoc` (dados da conta), ids de pacote (portão A8). Lista de servidores com lixo = struct de pacote com tamanho errado.

### Bloco 3 — Lobby
| # | Fazer | O que observar |
|---|---|---|
| 12 | Entrar no lobby | Cenário, seu personagem, nome, nível e dinheiro (pang/cookie) com os valores da conta |
| 13 | Lista de salas | Salas existentes aparecem com nome, modo e nº de jogadores; rolar a lista |
| 14 | Lista de jogadores do canal | Nomes legíveis; clicar em um abre as informações do jogador |
| 15 | Chat do lobby: escrever em letras normais e em japonês | A mensagem aparece para você (e para outro cliente, se houver) |
| 16 | Abrir e fechar: opções, correio, amigos/mensageiro, ranking, missões/presença | Cada janela abre, mostra dados e fecha sem travar |
| 17 | Trocar de canal e voltar | Volta ao lobby sem cair |

Se falhar aqui, suspeitar de: `lobbymain` (**CLobbyMain tem tamanho errado hoje**), `lobbytask`, `userlistdlg`,
`chatmsg`, e os sistemas novos do JP da frente B (salas, atores do lobby, UI base, diálogos RF — 483 kB, a maior parte
ainda não escrita).

### Bloco 4 — Sala de espera
| # | Fazer | O que observar |
|---|---|---|
| 18 | Criar sala (stroke, 3 buracos, 1 jogador basta) | Janela de criação: modos, campos e nº de buracos listados; a sala abre |
| 19 | Na sala: trocar campo, nº de buracos e tempo | As opções mudam e ficam |
| 20 | Com um segundo cliente (se houver): entrar na sala | Os dois personagens aparecem; chat da sala; "pronto" funciona |
| 21 | Sair da sala para o lobby e entrar de novo | Sem queda |
| 22 | Sala de bate-papo (lounge), se o servidor tiver | Andar, sentar, balão de fala |

Se falhar aqui, suspeitar de: `makeroomdlg`, `changeroominfodlg`, `avatar_*` (ntAvatarChatMain com tamanho errado hoje),
unidades novas `gameroomdlg`, `roomlistdlg`, `multiplayroomdlg`, Grand Prix.

### Bloco 5 — Partida
| # | Fazer | O que observar |
|---|---|---|
| 23 | Começar a partida (stroke, 3 buracos) | Tela de carga; aparece o campo, o céu, a água, o personagem e o caddie |
| 24 | Olhar a interface | Barra de força, vento (direção e número), distância, taco, placar, minimapa |
| 25 | Mirar: girar, trocar de taco, ver a linha de trajetória e a visão de cima | Câmera obedece; números mudam com o taco |
| 26 | Dar a tacada (barra de força + acerto) | Animação, som, bola voa e cai onde o original cairia com a mesma força (comparar com a linha de base) |
| 27 | Usar um item e um power shot | O item é gasto; o efeito aparece |
| 28 | Green: putt com a grade de inclinação | Grade aparece; a bola rola e entra (ou para) |
| 29 | Fim do buraco | Animação de resultado (par, birdie…), placar atualizado, próximo buraco carrega |
| 30 | Fim da partida | Tela de resultado com pang e experiência; volta à sala ou ao lobby |
| 31 | Durante a partida: Alt+Tab para fora e de volta; uma captura de tela | Volta sem tela preta; o arquivo da captura é criado |
| 32 | Um modo sozinho (prática/treino ou tutorial), se o servidor permitir | Abre e fecha |

Se falhar aqui, suspeitar de: `golfdoc`, `golftask`, `golfrule*`, `golfplayer`, `ball`, `camera`, `powergauge`, `wind`,
`sky` (CSky com tamanho errado hoje), `guideline`, `shotpreview`/`shotreview`, controladores de item (frente B),
`sPlayerData` (0xdb0 no 983). Tacada que cai em lugar diferente = regra/física; anote taco, força, vento e onde caiu.

### Bloco 6 — Loja
| # | Fazer | O que observar |
|---|---|---|
| 33 | Entrar na loja pelo lobby | Categorias e itens com nome, imagem e preço certos (vêm dos `.iff`) |
| 34 | Provar uma roupa no personagem | O boneco troca a peça |
| 35 | Comprar um item barato com pang | Confirmação; o saldo diminui; o item fica no inventário |
| 36 | Sair da loja | Volta ao lobby |

Se falhar aqui, suspeitar de: `shopmain` (CShopMain com tamanho errado hoje), `shoptask`, `checkoutdlg`,
`itemmanager` (portão A9). Preço ou nome trocado = registro de `.iff` desalinhado.

### Bloco 7 — My Room e equipamento
| # | Fazer | O que observar |
|---|---|---|
| 37 | Entrar no My Room | O quarto e o personagem aparecem; câmera gira |
| 38 | Trocar roupa, taco, bola, caddie e mascote | Cada troca aparece no boneco e continua depois de sair e voltar |
| 39 | Abrir o inventário e as cartas | Listas completas, sem item vazio ou com nome errado |
| 40 | Mexer num móvel (se a conta tiver) | Pega, gira e solta |

Se falhar aqui, suspeitar de: `realmyroommain` (CRealMyRoomMain com tamanho errado hoje), `realmyroomtask`, `equipdlg`,
`itemwindow`, `cardsystem`, oficina de tacos e cartas (frente B).

### Bloco 8 — Sair
| # | Fazer | O que observar |
|---|---|---|
| 41 | Sair pelo menu do jogo | Fecha sem mensagem de erro; o processo some do Gerenciador de Tarefas |
| 42 | Abrir de novo e entrar até o lobby | As opções e o que foi comprado/equipado continuam |

---

## Parte D — como voltar ao exe original

1. Feche o jogo.
2. Rode `VOLTAR_EXE_ORIGINAL.bat`: copia `ProjectG.exe.orig` e `ijl15.dll.orig` de volta, apaga `jp983_stub_continuar.txt`
   e mostra o md5 (tem de ser `8c76194bf825391f63fc951d3d4b09da`). Os `.orig` continuam guardados.
3. Se você tirou `PatchAddress` do `rugburn.json` para o teste, devolva a cópia guardada do json.
4. Se trocou a dll, `VOLTAR_WANGREAL_ORIGINAL.bat` (md5 da original `8b3e48084718ecc10c9a699063d7cb54`).
5. Abra o jogo com o original e vá até o lobby: no `gglog.txt` volta a aparecer "Patched GG check routines (JP 983)".

À mão, sem o `.bat`: apague `ProjectG.exe` e `ijl15.dll` e renomeie os `.orig` (`ProjectG.exe.orig`, `ijl15.dll.orig`).
Nada do teste mexe em outra pasta, no registro do Windows ou na instalação do PangYa Relic.

---

## Parte E — o que anotar e mandar de volta

- md5 do exe testado; qual dll (original ou nossa); qual servidor (Parte F); data.
- A lista dos 42 passos com OK / FALHOU / NÃO DEU, e até onde o exe **original** foi na linha de base (B7).
- No primeiro FALHOU e em cada fechamento:
  - captura de tela;
  - o `gglog.txt`;
  - os arquivos novos na pasta do jogo depois do teste (ordene por data): `exception.log` e qualquer `*.log` / `*.dmp`
    — o exe grava um registro e um despejo quando fecha por erro;
  - se o Windows mostrar o endereço do erro, copie o número (com o `.map` do exe ligado chega-se à função);
  - o `jp983_stubs.log` da pasta do jogo (exe da F4: uma linha por função sem corpo alcançada, `falta: <nome> (983 <VA>)`);
    se apareceu a caixa "funcao sem corpo (stub)", o nome que ela mostra (cada linha do log diz o modo: padrao/continuar);
  - o registro do servidor no mesmo minuto (último pacote recebido e enviado: o **id** resolve a maioria dos casos —
    compare com `pacotes_por_passo.tsv`).
- Falha visual sem fechamento (texto fora do lugar, janela vazia, item trocado): captura do exe nosso e do original na mesma tela.

---

## Parte F — dúvida em aberto: QUAL SERVIDOR usar (decisão do dono)

O roteiro acima vale para qualquer servidor que fale o protocolo do JP 983. O que existe hoje:

| Opção | Até onde dá para testar | Observação |
|---|---|---|
| 1. Servidor C# local do dono (login 30101, web 30090) | Blocos 1 e 2 até o envio do login | **Ainda não faz o login do JP**: nem o exe original passa do passo 6 (foi onde parou o teste da wangreal.dll) |
| 2. Servidor C# local depois de ganhar a camada do JP | Todos os blocos | Trabalho fora deste projeto; a V4 dá os ids e os campos dos pacotes do 983 (`out/V4/`), que servem de especificação |
| 3. Servidor da comunidade (o que o dono usa para jogar) | Todos os blocos | **Regra do projeto: não usar cliente modificado em servidor de terceiros** (docs/RETOMAR.md §12). O exe compilado é um cliente modificado. Só com decisão expressa do dono e do responsável pelo servidor |
| 4. Outro emulador local que já fale o JP 983 | Depende do emulador | Não há nenhum no container; seria escolha e instalação do dono |

Perguntas (não bloqueiam nada; respondam quando a F4 estiver perto):
1. Qual das opções acima vale para o teste do exe?
2. Se for a 1 ou a 2: há prazo para o servidor C# fazer o login do JP? Sem isso, o teste do exe para no passo 6.
3. Confirmam o GameGuard desligado por compilação já na F4 (portão A2)? Sem isso o exe compilado não passa do passo 1.
4. Dá para copiar para o container o `rugburn.json` e um `gglog.txt` do cliente de teste (perguntas da V5 §6)? Com eles
   os passos 3 e 6 passam a citar as linhas exatas do registro.

Enquanto não houver resposta, a frente C considera a **opção 1** (o que já está montado) e marca os blocos 3 a 8 como
"não dá para testar ainda".
