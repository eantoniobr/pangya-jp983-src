# RUGBURN — o que ele faz no 983 e o que o nosso exe precisa para rodar sem ele (frente A, A193; pedido do dono 20:40)

Base: out/V5/RELATORIO.md (C, rugburn público commit 7158511 × exe 983) e o fonte em build/C/v5/rugburn.
O ijl15.dll da pasta do jogo é o rugburn de TERCEIRO (out/F4/ijl15_rugburn_terceiro.dll): além do público, grava em
endereços fixos do exe ORIGINAL (BIG Papel Shop/F8, World Tour/F9, Wind Cap, linha de troca de apelido, Scratchy, jardas
"%.2f", Caliper) e faz checagens "Anti-Cheat". Isso é "gosto" do terceiro: não entra no nosso código (REGRAS 7).

## Inventário do rugburn público
| # | O que faz | No nosso código? | Precisa sem rugburn? | Como (chave) |
|---|---|---|---|---|
| 1 | Desarma o GameGuard (6 patches em endereço fixo) | sim: `JP983_SEM_GAMEGUARD` em ggc_wrapper.cpp (`_GGC_Init` devolve TRUE sem CNPGameLib); o `make exe` já liga a chave | sim | pronto |
| 2 | Finge que GameGuard.des rodou (CreateProcessA/GetExitCodeProcess = 0x755) | some com o item 1 (ninguém cria o processo) | não | — |
| 3 | `PANGYA_ARG={E69B65A2-…}` (dispensa o atualizador) | a checagem do 983 está no WinMain (winmain.cpp:420) | sim | `JP983_SERVER_CONFIG` (A213): sem PANGYA_ARG no ambiente vale o {E69B65A2-…} que o rugburn põe (winmain.cpp) |
| 4 | Desvia login/jogo (`connect`: PortRewrites 10803 → servidor local) | endereço fixo do 983 (157.7.173.48:10803, loginunit.cpp) | sim | **novo (A193)**: `JP983_SERVER_CONFIG` → `JP983_LOGIN=host:porta` no ambiente troca o endereço do login; sem a variável vale 127.0.0.1:30101 (A213: o robô não passa ambiente, C116.1). O servidor de jogo vem da lista que o login manda (sem desvio) |
| 5 | Desvia a web (wininet + WebBrowser: UrlRewrites) | URLs do 983 no fonte (out/V5/rede_983.tsv) | sim para a updatelist (DownloadUpdateList, sem ela o 983 avisa e não abre); páginas web (cupom, gacha, pagamento) depois | updatelist (A213; A214: caminho `/patch/updatelist`, como o rugburn reescreve) e textos `Translation/Read.aspx` (A214: sem ela o Ready para em "string load failed.", a213-1/002; 983 fixo 157.7.172.65:50007, gamestringmanager.cpp): `JP983_WEB=http://host:porta`, senão http://127.0.0.1:30091 (web da 2ª pasta do robô); emblemas de guild (A240): o rugburn do robô desvia `http://www5.pangya.jp/...` -> `localhost:30080`, mesmo caminho (gglog a212-1) -> `JP983_WWW=http://host:porta`, senão http://127.0.0.1:30080 (netresourcemanager.cpp); Report/SelfDesign (157.7.172.65:50007) e páginas `https://www5` o rugburn NÃO desvia (gglog: no rewrite rules matched) = igual sem ele |
| 6 | Tira "sempre no topo" (CreateWindowExA) | não | não (cosmético da abertura) | — |
| 7 | Conserto `_stricmp` do Wine | não | não (Windows) | — |
| 8 | `PatchAddress` do rugburn.json | não | não (endereços do exe original) | nunca usar com o exe compilado |
| 9 | É o ijl15.dll (Intel JPEG 1.5 embutida estática) | o exe importa ijlInit/Read/Write/Free (commonutil.cpp, engine/wresrcmng.cpp) | sim: a DLL tem de existir | ijl15 LIMPO abaixo |

## ijl15.dll de verdade (sem remendos)
- O rugburn liga a biblioteca da Intel estática (`third_party/ijl/ijl15l.lib`) e exporta as 6 funções por embrulhos
  (`src/ijl15.c`, `export.def`). `tools/f35/ijl15limpo.sh` monta SÓ isso: ijl15.c + ijl15l.lib + stubs.asm (CRT mínimo),
  sem DllMain, sem ganchos, sem rugburn.json → build/A/ijl15limpo/ijl15.dll (303.616 B, md5 aec92e0a44989d74f0d710973ee99737;
  importa só KERNEL32 e msvcrt; exporta ijlGetLibVersion/Init/Free/Read/Write/ErrorStr como o IJL15 original).
- O ijl15.dll ORIGINAL da Intel (o que vinha no cliente antes do rugburn) não está no container; se o dono tiver um cliente
  JP limpo, pode trocar por ele (mesmas 6 exportações).

## Para o teste da C (exe nosso sem rugburn, login → lobby)
1. Exe com `JP983_SEM_GAMEGUARD` (padrão do `make exe`) e `JP983_SERVER_CONFIG`: `DEFS=/DJP983_SERVER_CONFIG bash out/F3.5/s195/build.sh TAG`.
2. Entrega: ijl15_teste.dll = build/A/ijl15limpo/ijl15.dll (não o rugburn público nem o de terceiro), MD5.txt refeito.
3. Sem .bat nem ambiente: login 127.0.0.1:30101, PANGYA_ARG e updatelist 127.0.0.1:30091 são o padrão do define
   (JP983_LOGIN / JP983_WEB / PANGYA_ARG no ambiente ainda mandam, se existirem). A213: entrega a213r + pedido a213-1.
4. **PROVADO a214-2 (16/10, exe a214 + ijl15 limpo aec92e0a, sem rugburn)**: login conta-teste -> canal -> LOBBY (012: lobby
   completo, barra de baixo, Arin, cash/pontos); 0x004E visto no servidor; sem "string load failed." (o a213-1 parava aí).
   Falta à C: pôr o exe sem rugburn no roteiro de regressão (A193.2) — a ETAPA 3 começa daqui.
