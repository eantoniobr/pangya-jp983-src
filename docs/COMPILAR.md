# Como compilar e rodar

Guia de build do `ProjectG.exe` e da `wangreal.dll` a partir deste fonte. Resume o [TECNICO.md](TECNICO.md), que tem
cada alvo e cada ferramenta em detalhe. Tudo o que está aqui foi tirado dos documentos e do código do projeto; o que
não pôde ser conferido está marcado com **(a confirmar)**.

## 1. Visão geral

- Compila-se no **Linux**, com o **VS2010 SP1** rodando sob **Wine**. Não existe (ainda) uma solução `.sln` do Visual
  Studio para o jogo: o build é dirigido pelo `make` e por scripts Python.
- O `tools/vs.sh` chama `cl`, `link`, `lib`, `dumpbin`, `undname` e `rc` do VS2010 no prefixo do Wine e troca todo
  caminho `/root/...` dos argumentos por `Z:\root\...`. Por isso **o repositório e as dependências precisam ficar
  sob `/root`**, e os caminhos passados devem ser absolutos.
- Muitas ferramentas (cerca de 85 arquivos em `tools/`) usam o caminho fixo **`/root/jp983src`**. Clone o repositório
  nesse caminho, ou crie um link simbólico com esse nome.

## 2. O que precisa estar instalado

| Item | Onde o build procura | Para quê |
|---|---|---|
| VS2010 SP1: `cl` 16.00.40219.01, `link` 10.00.40219.01 | `/root/kr839/local/vs2010` (variável `VS=`): `VC10/` (bin, include, lib), `compat/`, `sdklib/`, prefixo do Wine em `wine/` | compilar e ligar tudo |
| Wine 9.0 | `/usr/bin/wine` | rodar o compilador |
| rebang (decomp do KR 645), **commit `f0a85b5`** | `/root/rebang` (variável `REBANG=`), só leitura | `build-projectg.json` (lista e configuração das 499 unidades do exe), Platform SDK de agosto/2002, DirectX 9, WTL 7.5, ATL 7.1, `rc.exe`; fontes e `.lib` de terceiros (lua, freetype, zlib, libpng, ijl15, mss32, NPGameLib) |
| Python 3 + `capstone` 5 | sistema | comparador, build do exe, link, portões |
| GNU make, bash, `flock` | sistema | alvos e scripts |
| Ghidra 12.1.4 + JDK 21 (opcional) | `/opt/ghidra_12.1.4_PUBLIC` | só para ler o pseudo-C do 983 ao reconstruir funções |
| node (opcional) | sistema | só o teste do painel (`tools/p1/teste_dom.js`) |

Detalhes do ambiente que custaram tempo:

- **Sem PDB.** O `mspdb100` não funciona sob Wine (erro `C1902`). Compila-se com `/Z7` (símbolos dentro do `.obj`) e
  liga-se sem `/DEBUG`. Nunca use `/Zi`.
- **ATL.** O VS2010 instalado não traz o ATL. O `make pg-atl` (chamado pelo `make pg-obj`) gera `build/atl71` a partir
  do ATL 7.1 do rebang, com correções para o `cl` 16.
- **kernel32.** Usa-se o `kernel32.lib` do SDK 7.1 (em `$(VS)/sdklib/`), porque o do SDK de 2002 não tem
  `EncodePointer`/`DecodePointer`, que o CRT do VS2010 usa. As outras bibliotecas do Windows vêm do SDK de 2002.
- **zlib e libpng.** As `.lib` do rebang são do VC7.1 e a libpng cita `__iob` (o `msvcr100` só tem `__iob_func`).
  O `make f4-terc` recompila as duas com o VS2010 (`/MD /O2 /Gr`).
- **Memória.** Builds grandes usam muita RAM; recomenda-se no máximo `-j8` por build. Antes de começar, confira se não
  há outro build rodando (`pgrep -a make; pgrep -af wine`).

Para conferir tudo de uma vez:

```
tools/checar_ambiente.sh        # imprime OK / AVISO / FALTA por item; sai com 1 se houver FALTA
tools/checar_ambiente.sh -r     # o mesmo, sem os testes que rodam o Wine
```

O script foi escrito para o repositório de trabalho. Nesta cópia ele marca `FALTA` para `HANDOFF.md` e `status.json`
(arquivos do fluxo interno, que não vêm aqui) e `AVISO` para as tags `jp983-F*` e para os resultados do comparador em
`out/`; por causa desses `FALTA` ele sai com código 1. Esses itens não são usados pelo build e podem ser ignorados.

## 3. Binários de referência (`ref/`)

O comparador, os mapas e vários portões leem os binários originais do 983. Eles **não** vêm no repositório: coloque-os
em `ref/` com estes nomes.

| Arquivo | Tamanho (bytes) | md5 | Data do PE |
|---|---|---|---|
| `ref/ProjectG_983_dump.exe` | 21.671.936 | `8c76194bf825391f63fc951d3d4b09da` | 2017-11-09 01:33:21 UTC |
| `ref/wangreal_983.dll` | 454.656 | `8b3e48084718ecc10c9a699063d7cb54` | 2017-11-09 01:27:33 UTC |

O `ProjectG_983_dump.exe` é um *dump* do exe protegido do JP 983 (o original vem com um protetor parecido com o
Themida). Só 5 funções ficaram virtualizadas no dump, todas de telemetria do GameGuard, sem efeito no jogo.
A `wangreal.dll` original não tem proteção.

Sem `ref/` dá para compilar os `.obj`, mas não comparar, refazer mapas nem passar pelos portões do `make exe`.

## 4. Flags de compilação

Provadas por variantes contra o 983:

- **comum:** `/MD /W3 /EHsc /Z7 /O2 /Ob1 /GF- /Gr /GS /Oy- /DNDEBUG /DWIN32 /D_WINDOWS /D_MBCS`
  - `/GF-`: o 983 não funde literais de texto iguais.
  - `/Gr`: convenção `__fastcall` como padrão, como no original.
- **exe:** mais `/Zm200 /DREBANG_SEMANTIC_ONLY /DJP983_POSTEFFECT` (definidos em `tools/f32/pgbuild.py`).
  `REBANG_SEMANTIC_ONLY` escolhe a versão em C das funções que o rebang tinha em assembly.
- a biblioteca Fresh (`src/fresh/`) usa `/Ob2`; a dll (`src/wangreal/`) define `/DWANGREAL_DEVICE`.
- **link:** `/NOLOGO /MACHINE:X86 /INCREMENTAL:NO /OPT:REF /OPT:ICF /NODEFAULTLIB`, com o CRT do VS2010
  (`msvcr100`/`msvcp100`, como o 983).
- a interface nova "RF" do 983 foi compilada com LTCG (`/GL`); nela não se espera IGUAL no comparador.

A configuração de cada unidade do exe (qual pch, `/FI`, includes extras) vem de `/root/rebang/build-projectg.json`,
lida por `tools/f32/pgbuild.py` (`python3 tools/f32/pgbuild.py list` mostra as unidades).

## 5. Alvos do make

Tudo roda da raiz do repositório. O `Makefile` inclui o `Makefile.B` e o `Makefile.C`.

### 5.1 Compilador e wangreal.dll

| Alvo | O que faz | Tempo aprox. |
|---|---|---|
| `make info` | versões do `cl`/`link` e flags | 1 s |
| `make hello` | teste do compilador: dll e exe mínimos (`tools/hello/` → `build/hello/`), e roda o exe | ~20 s |
| `make obj F=src/x.cpp` | compila um arquivo da dll ou da engine → `build/obj/src/x.obj` | ~5 s |
| `make cmp F=src/x.cpp ARGS="..."` | compila e compara cada função com o 983 | ~3 s |
| `make wangreal-full` | **a wangreal.dll completa** (14 `.cpp` + recursos, na ordem de link do 983) → `build/wangreal-full/wangreal.dll` + `.map` | ~1 min |
| `make image` | dll ligada × dll do 983: PE, imports, código e dados | ~1 min |
| `make smoke` | carrega a nossa dll e a do 983 no Wine, chama os 4 exports e compara | ~20 s |
| `make difftest` | 4 funções puras chamadas nas duas dlls com as mesmas entradas | ~20 s |
| `make cmp-selftest` | autoteste do comparador | ~1 min |
| `make clean` | apaga `build/obj`, `build/hello`, `build/wangreal` (não toca em `build/pg*`) | — |

O alvo `make wangreal` (sem `-full`) é uma dll parcial antiga, mantida só por histórico.

### 5.2 ProjectG.exe

| Alvo | O que faz | Tempo aprox. |
|---|---|---|
| `make pg-atl` | ATL 7.1 corrigido para o `cl` 16 → `build/atl71` | segundos |
| `make pg-obj [U="filtro"]` | compila os pch e as unidades → `build/pg/obj/<caminho>.obj` (+ `.log` com o erro, se houver) | 4 s por unidade; tudo 15–25 min |
| `make pg-base [U=…] [OUT=…]` | comparador em cada `.obj` × exe 983 → `$(OUT)/cmp/…`, `base.tsv` | tudo 20–45 min |
| `make jp` | unidades novas do JP (`src/projectg/jp/units.txt`) → `build/B/obj/` | ~5 s por unidade |
| `make jp-cmp JPOUT=…` | `jp` + comparador | ~6 s por unidade |
| `make layoutcheck [U=…]` | compila cada unidade com o seu `include/asserts/<unidade>.h`; falha se um `static_assert` de layout do 983 falhar | ~3 min |
| `make v6-link` | confere o link sem ligar: o que ninguém define, duplicados | ~20 s |
| `make f4-link` | link de prova com `/FORCE` (o exe não roda) | ~45 s |
| `make f4-terc` | zlib e libpng recompiladas com o VS2010 | ~5 s |
| `make f4-stubs` | gera um stub por símbolo ainda não resolvido e liga **sem** `/FORCE` | ~1,5 min |
| `make f4-ijl15` | `ijl15_teste.dll` a partir do rugburn público, sem patches de endereço fixo | ~30 s |
| `make exe [ENTREGA=out/F4/entregas/<id>]` | **o exe final**: stubs + GameGuard desligado + link + relatório de stubs + portões A1–A7 + pasta de entrega | 2–4 min |

O `make pg-import` (copiar e mesclar do rebang) também existe, mas o rebang foi encerrado e boa parte dos arquivos
já foi "adotada" (editada direto; lista em `map/adotados.txt`). Só rode se souber o que está fazendo.

### 5.3 O que o `make exe` faz

1. `f4-stubs`: liga com um stub para cada símbolo que falta. Um stub de função grava o nome em `jp983_stubs.log`,
   mostra uma caixa com o nome e fecha o jogo; no modo "continuar" ele só anota e devolve 0 (veja a seção 6).
2. Recompila `src/projectg/ggc_wrapper.cpp` com `/DJP983_SEM_GAMEGUARD` (o `_GGC_Init` devolve TRUE sem chamar o
   GameGuard).
3. Liga o exe sem `/FORCE` (`tools/v6/linkprova.py --exe`) → `build/C/f4/ProjectG_983.exe` (+ `.map`, `.log`).
4. `tools/v6/falta_exe.py`: quais stubs são alcançados pelos inicializadores estáticos e pelo `WinMain`.
5. Portões (`tools/v6/portoes.py`, A1–A7): imports existem nas dlls reais do cliente, GameGuard desligado, ijl15 de
   teste, constantes de partida, chave XTEA dos `.pak`/updatelist do 983 (e não a do 645 QA). **Se algum portão
   fechar, o `make exe` falha.**
6. `tools/v6/entrega.py`: monta a pasta de entrega (exe, `ijl15_teste.dll`, `.bat`, updatelist de teste, `MD5.txt`).

Com `ENTREGA=out/F4/entregas/<id>` o link, os stubs e os relatórios vão para `build/f4e/<id>/`, sem pisar em outro
build. `V6_PG="pg-TAG"` escolhe qual build do ProjectG usar (senão vale o `.obj` mais novo de cada unidade).

### 5.4 Build coerente de uma revisão (receita usada para os exes de teste)

O repositório de trabalho monta cada exe de teste com esta sequência (copiada de um script interno, sem mudanças de
lógica):

```
TAG=meuteste
DEFS="/DJP983_SERVER_CONFIG" tools/v6/f4rastro/wt_build.sh $TAG HEAD   # worktree + pch + 499 .obj -> build/pg-$TAG
cd /root/jp983-$TAG && python3 tools/f37/jpbuild.py obj -j 8          # unidades do JP no mesmo worktree
mkdir -p /root/jp983src/build/bobj-$TAG && cp build/B/obj/*.obj /root/jp983src/build/bobj-$TAG/
cd /root/jp983src
SEM=$(ls -d build/pg-* | sed 's|build/||' | grep -vx "pg-$TAG" | tr '\n' ' ')
make exe ENTREGA=out/F4/entregas/$TAG V6_PG="pg-$TAG" V6_SEM="$SEM" V6_BOBJ=build/bobj-$TAG
```

- O `wt_build.sh` cria um `git worktree` em `/root/jp983-$TAG` e compila tudo de uma revisão só, para não misturar
  `.obj` de revisões diferentes.
- A variável `DEFS` acrescenta defines ao pch e aos `.obj` **só dentro do worktree**. `JP983_SERVER_CONFIG` é a chave
  que permite rodar sem o rugburn (seção 6). Se ela também chega às unidades compiladas pelo `jpbuild.py` (por
  exemplo `src/projectg/jp/gamestringmanager.cpp`) **(a confirmar)**.
- Outros defines de teste: `JP983_SHOT_PREDICTION` (previsão de tacada do 645, Ctrl+R; sem ele = HUD do 983).

## 6. Como rodar o exe compilado

O exe precisa de um **cliente JP 983 instalado** (os dados do jogo não vêm aqui) e de um **servidor** que fale o
protocolo do JP 983. O dono do projeto testa com um servidor C# local.

Arquivos da entrega (`out/F4/entregas/<id>/`): o exe, o `ijl15_teste.dll`, a updatelist de teste
(`www_teste/patch/updatelist`, com o tamanho e o CRC do exe novo), `.bat` para trocar o exe e voltar ao original
(`USAR_EXE_NOSSO.bat`, `VOLTAR_EXE_ORIGINAL.bat`, `ABRIR_COM_STUBS.bat`) e o `MD5.txt`.

### 6.1 ijl15.dll e rugburn

O exe importa as funções da Intel JPEG Library 1.5 (`ijlInit`, `ijlRead`, `ijlWrite`, `ijlFree`…), então um
`ijl15.dll` precisa existir na pasta do jogo.

- **Nunca use com o exe compilado um rugburn modificado que aplica patches em endereços fixos do exe original.** Ele
  escreve lixo nas seções do nosso exe. O `ijl15.dll` que veio na pasta de teste do dono é desse tipo (de terceiro).
- Opções seguras: o `ijl15_teste.dll` da entrega (rugburn público, só com ganchos de API, sem patch de endereço) ou o
  **ijl15 limpo**, montado por `tools/f35/ijl15limpo.sh` (só a biblioteca da Intel e os 6 exports, sem rugburn;
  `build/A/ijl15limpo/ijl15.dll`, 303.616 bytes, md5 `aec92e0a44989d74f0d710973ee99737`).
- Com o ijl15 limpo e um exe compilado com `JP983_SERVER_CONFIG`, o exe já foi do login até o lobby **sem rugburn**
  (16/10/2026).

### 6.2 Chaves de compilação e variáveis de ambiente

| Nome | Tipo | Efeito |
|---|---|---|
| `JP983_SEM_GAMEGUARD` | define (ligado pelo `make exe`) | `_GGC_Init` devolve TRUE sem criar o GameGuard (`src/projectg/ggc_wrapper.cpp`) |
| `JP983_SERVER_CONFIG` | define (via `DEFS`) | habilita as variáveis abaixo, no lugar dos endereços fixos do 983 |
| `JP983_LOGIN=host:porta` | ambiente | servidor de login (`src/projectg/loginunit.cpp`); sem a variável: `127.0.0.1:30101`. O 983 usa 157.7.173.48:10803 |
| `JP983_WEB=http://host:porta` | ambiente | updatelist (`/patch/updatelist`) e textos `Translation/Read.aspx`; sem a variável: `http://127.0.0.1:30091` |
| `JP983_WWW=http://host:porta` | ambiente | emblemas de guild (`netresourcemanager.cpp`); sem a variável: `http://127.0.0.1:30080` |
| `PANGYA_ARG` | ambiente | argumento que dispensa o atualizador; sem a variável vale o mesmo valor `{E69B65A2-…}` que o rugburn põe (`winmain.cpp`) |
| `JP983_STUB=continuar` | ambiente | stubs de função voltam 0 em vez de fechar o jogo (menos os fatais) |
| `jp983_stub_continuar.txt` | arquivo na pasta do exe | o mesmo que `JP983_STUB=continuar`, sem depender de como o exe foi aberto |

Sem a updatelist, o 983 avisa e não abre; sem os textos de `Translation/Read.aspx`, a tela de entrada para em
"string load failed.". O servidor de jogo vem da lista que o login manda (sem desvio).

### 6.3 Outros cuidados

- O exe do 983 pede **administrador** (manifesto `requireAdministrator`); sem isso o Windows dava "erro de arquivo".
  O manifesto do nosso exe é o mesmo do original.
- Feche o jogo e espere o processo sair antes de trocar o exe.
- Para trocar só a dll: `USAR_WANGREAL_NOSSA.bat` / `VOLTAR_WANGREAL_ORIGINAL.bat` no cliente de teste do dono
  **(a confirmar: esses `.bat` não estão neste repositório)**.

## 7. Problemas conhecidos

| Sintoma | Causa / o que fazer |
|---|---|
| todo `make` falha com `g++ Makefile.C -o Makefile` | regra embutida `%: %.C` quando o `Makefile.C` fica mais novo que o `Makefile`; o `Makefile.C` tem a regra vazia `Makefile: ;` para impedir isso: não apague |
| `C1902` (gerenciador de PDB) | alguém pôs `/Zi`; aqui é sempre `/Z7` |
| `.obj` "em dia" mas com código velho | o pch falhou; veja `build/pg/pch/*.log` e recompile com `--force` (`pgbuild.py`) |
| unidade compila sozinha e falha no `make pg-obj` | um cabeçalho comum está sendo editado ao mesmo tempo; espere e repita |
| `LNK1104` no `make exe` | um `.obj` estava sendo regravado por outro build; espere o `pgbuild` terminar |
| muitas funções `-rm` numa classe | layout da classe diferente do 983 (campo deslocado): `make pg-votes U=<unidade>` |
| IGUAL em função pequena num endereço estranho | casou por bytes no lugar errado: vete em `map/projectg_fora.tsv` ou fixe em `map/projectg_manual.tsv`, depois `make pg-map` |
| `static_assert` falhando no `make layoutcheck` | cabeçalho com layout diferente do 983: corrija o cabeçalho, nunca o assert |
| ferramenta não acha arquivos | o repositório não está em `/root/jp983src` (caminho fixo em muitas ferramentas) |

## 8. Arquivos de `out/` incluídos

O `out/` do repositório de trabalho é quase todo relatório e evidência, e fica de fora (`.gitignore`). Vêm nesta cópia
só os arquivos que o caminho do `make exe` **lê** (rastreados no `Makefile.C` e em `tools/v5`, `tools/v6`):

| Arquivo | Quem lê | Para quê |
|---|---|---|
| `out/V6/ROTEIRO.md` | `portoes.py`, `falta_exe.py` (referência) | roteiro de teste e definição dos portões A1–A7 |
| `out/V6/bat/USAR_EXE_NOSSO.bat`, `VOLTAR_EXE_ORIGINAL.bat`, `ABRIR_COM_STUBS.bat` | `entrega.py` | os `.bat` copiados para a entrega (ajuste a variável `PASTA` para a pasta do seu cliente) |
| `out/F4/updatelist_web_local_original` | `entrega.py`, `make f4-updatelist` | updatelist **cifrada** (XTEA do 983) que o servidor web local serve; a entrega troca nela a linha do `ProjectG.exe` |
| `out/V5/constantes.tsv` | `portoes.py` (portão A4) | constantes de partida do 983 × fonte; o `make v5` refaz |
| `out/V5/rugburn_jp983_trecho.c` | `tools/v5/rb.py` (`make v5`) | trecho do rugburn público usado quando não há clone em `build/C/v5/rugburn` |
| `out/V5/*.tsv`, `resumo.txt`, `RELATORIO.md` | consulta | saída do `make v5` de referência (as URLs internas do 983 foram trocadas por `<IP interno do 983>` no `rede_983.tsv`) |

Os outros arquivos que essas ferramentas usam em `out/` (`out/V6/link/`, `out/F4/link/`, `out/F4/stubs.tsv`,
`out/F4/exe/`, `out/F4/portoes.*`) são **gerados** pelos passos anteriores do próprio `make exe`.

Ainda ficam de fora, de propósito:

- `out/F4/ijl15_rugburn_terceiro.dll`: o portão A6 só a usa, se existir, para garantir que a dll de teste não é a de
  terceiro; sem ela o portão segue;
- o clone do rugburn público (`github.com/pangbox/rugburn`, commit `7158511`) em `build/C/v5/rugburn`: o
  `make f4-ijl15` precisa dele; clone-o nesse caminho antes do primeiro `make exe`;
- `out/F3.4/funcs_all.tsv.gz` (1,3 MB): só para refazer os mapas (`make units`, `make pg-map`); os mapas prontos já
  estão em `map/`.

Também vêm, como fonte dos números do [ESTADO.md](ESTADO.md), `out/F5/SISTEMAS.tsv`, `out/F6/CMP_983.tsv`,
`out/F4/falta_exe.tsv`, `out/F4/stubs_resumo.txt`, `out/F4/regressao.tsv` e `out/F4/TESTE_DONO.md` (com os nomes das
contas de teste trocados por `conta-teste`). O `make exe` regrava `falta_exe.tsv` e `stubs_resumo.txt`.

O ícone e os bitmaps de `src/projectg/ProjectG.rc` (`ProjectG.ico`, `111.bmp`, `113.bmp`, `123.bmp`) são substitutos
neutros do mesmo tamanho dos originais: o `rc` compila igual, mas o exe sai sem o ícone e as imagens do jogo. Quem
quiser o visual original extrai esses recursos do próprio `ProjectG.exe`.
