# PangYa JP 983 — código-fonte reconstruído do cliente (ProjectG.exe + wangreal.dll)

> **Aviso importante.** Este é um projeto independente de **preservação e estudo**, **sem fins comerciais**. Não tem
> nenhuma afiliação com a Ntreev Soft, a Kakao Games ou qualquer publicadora do PangYa; PangYa e as marcas
> relacionadas pertencem aos seus donos. O repositório **não contém nenhum arquivo do jogo** (executáveis, DLLs, `.pak`,
> `.iff`, imagens, sons ou textos do jogo): quem quiser usar o código precisa do próprio cliente, obtido de forma legal.
> Não use em servidores oficiais nem para trapaça. Pedidos de remoção dos detentores de direitos serão atendidos:
> abra uma issue neste repositório. Texto completo e licenças de terceiros em [NOTICE.md](NOTICE.md).
>
> **Notice.** Independent, non-commercial **preservation and study** project. Not affiliated with Ntreev Soft, Kakao
> Games or any PangYa publisher; PangYa and related trademarks belong to their owners. This repository contains **no
> game files** (executables, DLLs, `.pak`, `.iff`, images, sounds or game text); you need your own, legally obtained
> client. Do not use it on official servers or for cheating. Takedown requests from rights holders will be honored:
> please open an issue. No license is granted over the reconstructed code; see [NOTICE.md](NOTICE.md).

Este repositório guarda o **código-fonte C++ reconstruído** do cliente do PangYa japonês, build **JP.R7.983.00**
(compilado em 09/11/2017): o executável do jogo, `ProjectG.exe`, e a biblioteca gráfica `wangreal.dll`.

O fonte compila com o mesmo compilador do original (**Visual Studio 2010 SP1**, `cl` 16.00.40219.01), executado sob
Wine no Linux. A meta é que o resultado **se comporte como o original**: mesmas telas, mesmas funções e os mesmos
pacotes de rede. **Não** buscamos um binário byte a byte idêntico; a comparação com o original serve só de régua
para conferir o trabalho.

## Estado atual

Retrato de **23/10/2026**, tirado do repositório de trabalho no commit `00f572bb5`. Detalhes em
[docs/ESTADO.md](docs/ESTADO.md); problemas conhecidos em [docs/ESTADO.md](docs/ESTADO.md#2-problemas-conhecidos).

| Indicador | Valor |
|---|---|
| Sistemas fora da partida prontos (comparados com o original) | **20 de 27** (19 PRONTO + 1 PRONTO COM RESSALVA) |
| Sistemas em andamento | 7: salas, mascotes, caddies, loja e My Room (reabertos pelo dono), salas especiais (Lounge) e sala de evento GM |
| Funções próprias do jogo (`src/projectg`) comparadas com o 983 | **13.199** em 376 unidades |
| IGUAL / QUASE / DIFERENTE / SEM_PAR | 8.522 (64,6%) / 1.373 (10,4%) / 2.039 (15,4%) / 1.265 (9,6%) |
| IGUAL + QUASE | 9.895 (75,0%) |
| Funções cujo C++ ainda parte do código do KR 645 (heurística por nome) | 9.758 (73,9%); as outras 3.441 (26,1%) foram escritas a partir do 983 |
| Stubs restantes no exe ligado | **1** stub de função (não fatal) + 31 stubs de dados com os valores do 983 |
| Blocos `__declspec(naked)` (assembly) em `src/projectg` | **0** (eram 1.339 em 19/10) |
| wangreal.dll | completa desde 10/10/2026; 90,6% dos bytes iguais aos da original |

O que isso quer dizer na prática:

- O exe compilado deste fonte abre, faz login num servidor local, passa pela escolha de servidor e canal e chega ao
  lobby. A última regressão automática aprovada (23/10) percorreu o roteiro inteiro fora da partida sem queda
  (1.738 s de roteiro).
- **A partida (o jogo de golfe em si) está com uma regressão grave** na entrega de 23/10: personagem, bola, taco e
  caddie não carregam, e a vista de cima (tecla 0) derruba o jogo. Veja os
  [problemas conhecidos](docs/ESTADO.md#2-problemas-conhecidos). O robô de teste não joga a partida.
- "DIFERENTE" não significa "errado": a régua é funcional. Uma função conta como pronta quando compila, usa o layout
  de classe certo e dá IGUAL ou QUASE, ou dá DIFERENTE com a mesma lógica justificada.

## Estrutura

| Pasta / arquivo | Conteúdo |
|---|---|
| `src/projectg/` | código do jogo (ProjectG.exe); `src/projectg/jp/` = sistemas novos do JP, sem fonte no 645 |
| `src/engine/` | biblioteca Wangreal (motor 3D), ligada estaticamente no exe |
| `src/fresh/` | biblioteca de interface Fresh, ligada no exe (inclui zlib 1.2.2 e libpng 1.2.8 em `third_party/`) |
| `src/shared/` | código comum a cliente e servidor (sistema Lua, minilzo, TEA, tabelas, localização) |
| `src/wangreal/` | a `wangreal.dll` (WDirect3D/WDirect3D8, entrada, IME) |
| `include/` | cabeçalhos do 983 comuns a mais de um módulo; `include/asserts/` = `static_assert` de layout; `include/jp/` = classes novas do JP; `include/packets/` = pacotes |
| `map/` | mapas função ↔ endereço (983, 839 e 645), unidades e layouts, usados pelo comparador e pelo build |
| `tools/` | build (`vs.sh`, `f32/pgbuild.py`), comparador (`cmpfunc`), link do exe (`v6/`), verificações e utilitários |
| `out/` | só os arquivos que o `make exe` lê e as fontes dos números do estado (lista em `docs/COMPILAR.md`) |
| `docs/` | documentação (lista abaixo) |
| `Makefile`, `Makefile.B`, `Makefile.C` | alvos de build e verificação (`Makefile` inclui os outros dois) |
| `NOTICE.md` | aviso legal e licenças das bibliotecas de terceiros |

Atenção ao nome: no código original, *Wangreal* é a biblioteca estática do exe (`src/engine/`); a **wangreal.dll** é
outro projeto (`src/wangreal/`).

## Início rápido

Requisitos (detalhes em [docs/COMPILAR.md](docs/COMPILAR.md)):

1. Linux x86-64 com **Wine 9.0**, Python 3 com `capstone` 5 e GNU make.
2. O **VS2010 SP1** já instalado num prefixo do Wine, em `/root/kr839/local/vs2010` (ou outro caminho em `VS=`).
3. O **rebang** (decomp do KR 645) em `/root/rebang`, no commit `f0a85b5`: dele vêm o Platform SDK 2002, o DirectX 9,
   o ATL 7.1, o `rc.exe`, a lista de unidades do exe e bibliotecas de terceiros.
4. Os **binários de referência** do 983 em `ref/`, tirados do seu próprio cliente (não vêm no repositório; md5 em
   `docs/COMPILAR.md`).
5. O repositório clonado em **`/root/jp983src`**: várias ferramentas usam esse caminho fixo.

Alvos principais:

```
tools/checar_ambiente.sh     # confere compilador, Wine, referências e rebang (OK / AVISO / FALTA)
make hello                   # teste do compilador: dll e exe mínimos
make wangreal-full           # wangreal.dll completa -> build/wangreal-full/wangreal.dll
make pg-obj                  # todas as unidades do ProjectG -> build/pg/obj (15–25 min)
make pg-base                 # compara cada .obj com o exe 983 (20–45 min)
make jp                      # unidades novas do JP -> build/B/obj
make exe ENTREGA=out/F4/entregas/<id>   # liga o ProjectG.exe e monta a pasta de teste
```

## Como continuar

O guia [docs/CONTINUAR.md](docs/CONTINUAR.md) conta o que já foi feito, fase por fase, lista os problemas conhecidos
e o próximo trabalho em ordem de prioridade: a regressão da partida, os sistemas reabertos, as funções que ainda vêm
do 645, o último stub, a solução do Visual Studio e a independência do rugburn. Também explica o fluxo de trabalho para
quem chega: montar o ambiente, compilar, comparar uma função e testar o exe.

## Documentação

| Documento | Para quê |
|---|---|
| [NOTICE.md](NOTICE.md) | aviso legal, endereços do programa original presentes no código, licenças de terceiros |
| [docs/COMPILAR.md](docs/COMPILAR.md) | guia de build completo: ferramentas, referências, flags, alvos, como rodar, problemas de build |
| [docs/CONTINUAR.md](docs/CONTINUAR.md) | **como continuar**: progresso por fase, problemas conhecidos, próximos trabalhos, fluxo de trabalho |
| [docs/ESTADO.md](docs/ESTADO.md) | estado detalhado: sistemas, problemas conhecidos, comparação por unidade, stubs, o que falta |
| [docs/METODO.md](docs/METODO.md) | como a reconstrução é feita (983 = código, 645 = estrutura, 839 = ponte) |
| [docs/TECNICO.md](docs/TECNICO.md) | manual técnico completo: cada alvo do make, cada ferramenta, formato dos mapas, o comparador |
| [docs/LAYOUTS.md](docs/LAYOUTS.md) | layouts de classes e structs do 983 corrigidos |
| [docs/RUGBURN.md](docs/RUGBURN.md) | o que o rugburn faz no 983 e como o exe compilado roda sem ele |
| [docs/RETOMAR.md](docs/RETOMAR.md) | guia de retomada do repositório de trabalho (histórico da organização) |
| [docs/METODO_RECONSTRUCAO_JOGOS.md](docs/METODO_RECONSTRUCAO_JOGOS.md) | o método geral, escrito para reaproveitar em outros jogos |

Os documentos `TECNICO.md`, `RETOMAR.md`, `LAYOUTS.md` e `RUGBURN.md` foram escritos para o repositório de trabalho e
citam pastas que não vêm nesta cópia (`out/`, `build/`, `ref/`, `HANDOFF.md`, `NOTES*.md`); valem como referência.

## O que não está aqui

| Fora do repositório | Por quê |
|---|---|
| Arquivos do jogo (exe, dll, `.pak`, `.iff`, imagens, sons, textos) | pertencem aos donos do jogo; cada pessoa usa o próprio cliente |
| `ref/` (exe e dll originais do 983) | binários do jogo; só servem de referência para o comparador |
| Ícone e bitmaps originais do exe | `src/projectg/ProjectG.ico`, `111.bmp`, `113.bmp` e `123.bmp` são **substitutos neutros** (cinza, do mesmo tamanho), só para o `ProjectG.rc` compilar |
| `build/` | saídas de compilação (vários GB); refeitas com o `make` |
| quase todo o `out/` | relatórios, evidências e resultados do comparador e do robô de teste (cheios de capturas do jogo) |
| `proj/` | projeto Ghidra da dll do 983 |
| O compilador VS2010 e o rebang | ficam em outros diretórios da máquina de build e têm licenças próprias |
| Arquivos de organização dos agentes (`HANDOFF.md`, `NOTES*.md`, `REGRAS.md`, `PEDIDOS.md`, `status.json`, `run*.sh`, travas) | servem só ao fluxo de trabalho interno |
| Histórico do git | esta é uma cópia limpa do estado atual, sem o histórico de trabalho |
| Imagens de teste de bibliotecas de terceiros (libpng, Lua) e a `docs/VERSION.DLL` do FreeType | removidas por regra (sem imagens e sem arquivos `.dll`); não são usadas no build |

Ficaram alguns arquivos pequenos de exemplo e teste das bibliotecas de terceiros (ícones, `DotZLib.chm`, dados de
teste da zlib em `contrib/`), que não entram no build.
