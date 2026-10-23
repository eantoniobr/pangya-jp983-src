# Como continuar o projeto

Guia para quem vai assumir o código: o que já foi feito, o que fazer em seguida (em ordem de prioridade), como
trabalhar no dia a dia e onde achar cada informação. Retrato de 23/10/2026. Os números vêm dos relatórios em `out/`
(ver [ESTADO.md](ESTADO.md)); as datas vêm do histórico do repositório de trabalho (4.519 commits entre 09/10 e
23/10/2026) e do plano original.

Sumário:

1. [Progresso](#1-progresso)
2. [Como continuar](#2-como-continuar)
3. [Fluxo de trabalho](#3-fluxo-de-trabalho)
4. [Onde está cada coisa](#4-onde-está-cada-coisa)

---

## 1. Progresso

### 1.1 Linha do tempo

| Quando | Fase | O que aconteceu |
|---|---|---|
| 09/10 | **F0 Base** | repositório, VS2010 SP1 rodando sob Wine (`tools/vs.sh`, `make hello`), comparador função a função (`tools/cmpfunc`) |
| 09/10 | **F1 Tipos** | fontes do 645 da dll em `src/`, cabeçalhos da engine; primeira linha de base da dll (144 funções IGUAL) |
| 09/10–10/10 | **F2 wangreal.dll** | dll reconstruída por partes; em **10/10** a dll ficou **completa**: 133 de 133 imports, recursos iguais, 90,2% IGUAL + 5,3% QUASE na comparação da imagem ligada (90,6% dos bytes iguais) |
| 10/10 | **F3.1–F3.3** mapas | mapa unidade do 645 → faixa no 983 (301 unidades com faixa firme, depois 382); base do exe: 990 arquivos do rebang em `src/` e `include/`, 438 de 468 unidades compilando |
| 10/10–11/10 | **F3.4** layouts | classes centrais (FrWnd, CTaskMain, WPolySoup, WPuppet…) no layout do 983, medido pelos construtores e pelos mapas de mensagens |
| 11/10 | **F3.R** | importação final do rebang (commit `f0a85b5`); o rebang foi encerrado; todas as 499 unidades compilam |
| 11/10 em diante | **F3.5 / F3.7** | adaptação das unidades do 645 para o 983 (F3.5) e sistemas novos do JP, sem fonte no 645 (F3.7: 278 unidades novas propostas nos vãos do 983) |
| 13/10 | **F4 Exe** | primeiro link de prova (`make f4-link`); primeiro exe sem `/FORCE`, com **437 stubs de função** (`make exe`) |
| 14/10 | F4 | primeira sessão do **robô de teste** no PC do dono; modo `exe=original` para comparar; à noite o **exe chega ao lobby**, com os pacotes iguais aos do original até o 0x009C |
| 15/10 | F4/F5 | regressão automática diária começa; método **por sistema**: cada sistema do jogo é comparado com o original (tela e pacote) em `out/F5/SISTEMAS.tsv` |
| 16/10 | F5 | **login → canal → lobby sem rugburn** (exe com `JP983_SERVER_CONFIG` + ijl15 limpo); primeiros sistemas PRONTO (salas, guild, correio, ranking, opções) |
| 16/10–19/10 | F5 | ondas de sistemas PRONTO: inventário, mascotes, cartas, loja, Papel Shop, My Room, Club Workshop, sala de espera, efeitos, console… **25 de 27** no fim |
| 17/10 | F4 | stubs de função: 437 → **56** |
| 19/10 | **F6** limpeza do 645 | ramos `__declspec(naked)` mortos (herdados do matching do 645, fora do build por `REBANG_SEMANTIC_ONLY`) tirados, sempre com o `.obj` conferido igual: **1.339 → 745 → 76 → 0** em `src/projectg` (os últimos 76, de `golfrule.cpp`, à noite); stubs de função: **56 → 1**; nasce o `out/F6/CMP_983.tsv`, a comparação de todas as funções próprias de `src/projectg` |
| 19/10 | F5 | teste manual do dono reabre sistemas por causa do **botão direito** em listas e no My Room (salas, mascotes, caddies, loja, My Room) |
| 20/10–21/10 | — | pausa no trabalho automático |
| 22/10 | partida | frente da partida retomada: funções de `golfrule.cpp`, `golfplayer` e do Play Assist (ShotPreview) refeitas pelo 983; o dono acha uma queda no Practice com o Play Assist ligado |
| 23/10 | partida | entrega `reg-20261023-1030`: fora da partida a regressão passa, mas o dono acha uma **regressão grave na partida** (personagem, bola, taco e caddie não carregam; vista de cima cai). O dono avisa que não vai mais testar à mão; a correção passa a ser por análise do código contra o 983 |

No plano original a F5 era "limpeza" (GameGuard fora, código organizado). Na prática, a pasta `out/F5/` passou a
guardar a comparação por sistema, e a limpeza do código herdado do 645 virou a F6.

### 1.2 Onde está agora (23/10/2026)

- **Exe:** abre, faz login, escolhe servidor e canal, chega ao lobby e percorre todo o roteiro fora da partida sem
  queda. A última entrega aprovada pela regressão (`reg-20261023-1520`) rodou 1.738 s.
- **Sistemas fora da partida:** 20 de 27 prontos (19 PRONTO + 1 com ressalva); 7 em andamento.
- **Funções (`src/projectg`):** 13.199 próprias. IGUAL 8.522 (64,6%), QUASE 1.373 (10,4%), DIFERENTE 2.039 (15,4%) e
  SEM_PAR 1.265 (9,6%). 9.758 (73,9%) ainda partem do C++ do 645.
- **Stubs:** 1 de função (`lua_system::LuaScriptManagerJp983::Error983`, não fatal) e 31 de dados.
- **Assembly:** nenhum bloco `naked` em `src/projectg`; restam 4 fora dele (seção 6 do [ESTADO.md](ESTADO.md)).
- **Partida:** escrita em código, mas com a regressão grave descrita abaixo.

---

## 2. Como continuar

Em ordem de prioridade. Os itens 2.1 e 2.2 são os problemas abertos; o resto é o caminho para um fonte "limpo" e
editável.

### 2.1 Problemas conhecidos

Situação em 23/10/2026, a partir dos testes do dono com a entrega `reg-20261023-1030` (Practice no campo Abbot Mine,
com o Play Assist ligado) e do quadro de sistemas. Nenhum deles tem prazo; a lista é o que se sabe hoje.

**Partida (prioridade máxima)**

| Problema | O que se sabe |
|---|---|
| **Personagem, bola, taco e caddie não carregam** (silhueta preta, sem taco; bola e caddie ausentes) | funcionava em testes anteriores; verificações de ponteiro nulo acrescentadas em correções de 22/10 escondem a queda, mas a causa (conjunto de tacos, ossos e peças não carregados) não foi achada |
| **Vista de cima (tecla 0) cai** | violação de acesso em `CFrameSetHost983::FindNamed` com `this` nulo, chamada por `CMouseCursor::Display` |
| **Botão Assist trava** depois de mudar de estado | há uma correção no código (B1137), ainda não conferida no jogo |
| **"Pang: 0" por cima do medidor de vento** | no 983 o texto fica em outro lugar |
| **Ícones das tacadas especiais errados** | sem diagnóstico ainda |
| Três linhas de texto vermelho em japonês à esquerda | não se sabe se o 983 também mostra |
| Queda quando o tempo da tacada acaba | correção no código (B751), ainda não conferida no jogo |

Como atacar, já que não há uma entrega antiga "boa" conhecida para comparar por bisseção: seguir o caminho de carga do
jogador na partida (OnLoad, AddPlayer, carga do conjunto de tacos, peças e ossos) **função a função contra o 983**,
achar quem preenche cada estrutura no 983 e por que no nosso ela fica nula, e corrigir a causa (não a verificação de
nulo). Para a vista de cima, achar no 983 qual objeto é o "host" que o `CMouseCursor::Display` usa. Cada correção deve
citar o endereço do 983 que a prova.

**Sistemas em andamento (7)**

- **salas:** queda do botão direito na primeira sala da lista (corrigida no código, falta a prova contra o original);
- **mascotes:** botão direito no mascote do My Room deve abrir `mascot_info` (portado no B746, falta a prova);
- **caddies:** a janela de detalhes já abre igual; falta conferir o "Rehire" (aviso de salário);
- **loja:** botão direito na lista da loja tem duas diferenças em relação ao 983;
- **My Room:** botão direito nas abas; Caddie já igual, faltam Item, Clothes e Mascot;
- **salas especiais:** o personagem não anda no clique do chão do Lounge;
- **sala de evento GM:** a abertura é igual; o interior exige uma conta GM no servidor de teste.

### 2.2 Validar a partida sem teste manual

O dono avisou em 23/10 que não vai mais testar a partida à mão. O robô de teste cobre tudo fora da partida, mas não
joga. É preciso um jeito repetível de validar a partida: por exemplo, estender o roteiro do robô para entrar no
Practice, esperar a carga e fotografar (personagem visível, bola, caddie), e comparar os pacotes da partida com os do
original. As listas "A410" e "A478" do `out/F4/TESTE_DONO.md` dizem o que conferir em cada parte da partida.

### 2.3 Funções DIFERENTE que vêm do 645

São as 1.573 funções com `origem = 645` e `classe = DIFERENTE` em `out/F6/CMP_983.tsv` (mais 1.068 SEM_PAR da mesma
origem). É o principal trabalho restante para o fonte refletir o 983.

**Como escolher.** Comece pelas unidades do caminho do jogo e pelas que concentram DIFERENTE (tabela 4.1 do
[ESTADO.md](ESTADO.md): `lobbymain`, `golfrule`, `realmyroommainui`, `fontinfo`, `ingameguildlobbydlg`…). Para listar:

```
awk -F'\t' '$6=="645" && $4=="DIFERENTE"{print $1"\t"$5"\t"$3"\t"$2}' out/F6/CMP_983.tsv | sort -k1,1 -k2,2n | less
```

Dentro de uma unidade, comece pelas de `pct_instr` mais baixo (lógica mais diferente) e pelas que o jogo de fato
chama. DIFERENTE com `pct_instr` alto costuma ser só ordem de registradores ou de pilha: aceitável se a lógica for a
mesma (anote em uma linha e siga).

**Como portar uma função a partir do 983, passo a passo.**

1. **Cópia de trabalho própria**, para não pisar em outro build:
   ```
   python3 tools/f32/pgbuild.py pch --tag eu          # pch em build/pg-eu/pch (1–2 min, uma vez)
   ```
2. **Ache a função e o par.** O VA do 983 está na coluna `va983` do `CMP_983.tsv` e em `map/projectg.tsv`. Veja a
   faixa da unidade em `map/projectg_units.tsv` e as funções vizinhas em `map/projectg_funcs.tsv`.
3. **Leia o 983:**
   ```
   python3 tools/f37/dz.py <VA> 200               # desmonte com os nomes do mapa
   tools/f37/dec.sh /tmp/eu/dec.txt <VA>          # pseudo-C do Ghidra (precisa do projeto Ghidra do 983)
   python3 tools/f34/rtti.py <Classe>             # vtable e construtores da classe
   python3 tools/f35/callers.py <VA>              # quem chama
   ```
4. **Confira o layout antes do código.** Muitas diferenças são um campo fora do lugar: `-rm` no hash do comparador
   quase sempre é layout. Meça pelo construtor do 983 e compare com `python3 tools/f34/co.py <Classe>`; acerte o
   cabeçalho e o `include/asserts/<unidade>.h`.
5. **Reescreva a função** pelo 983, com os nomes e tipos do fonte. Deixe o VA do 983 num comentário acima da função
   (`// 00xxxxxx`), como no resto do código.
6. **Compile e compare:**
   ```
   python3 tools/f32/pgbuild.py obj projectg/<unidade>.cpp --tag eu --out /tmp/eu
   python3 tools/f32/pgbuild.py cmp projectg/<unidade>.cpp --tag eu --out /tmp/eu
   tools/cmpfunc build/pg-eu/obj/src/projectg/<unidade>.obj --no-build --ref ref/ProjectG_983_dump.exe \
      --map map/projectg.tsv --funcs map/projectg_funcs.tsv --diff '<Nome>' > /tmp/eu/diff.txt
   python3 tools/f35/dv.py /tmp/eu/diff.txt '<Nome>'      # só as linhas que diferem
   ```
   Repita até dar IGUAL ou QUASE, ou DIFERENTE com a mesma lógica. Use `/tmp/` no `--out` dos experimentos: o
   painel e os relatórios ignoram essas pastas.
7. **Confira que nada piorou:**
   - a unidade toda: compare o `funcs.tsv` novo com o anterior (`python3 tools/f35/antes.py <pasta>`), ou
     `python3 tools/f34/ab.py <antes> <depois>` para a base inteira;
   - se mexeu num cabeçalho comum: `make pg-obj` + `make pg-base` inteiros e `make layoutcheck`;
   - se a mudança não deveria alterar o código gerado (limpeza, renomeação), o `.obj` tem de sair igual:
     `python3 tools/f6/objeq.py antes.obj depois.obj` (iguais fora de `.debug$*`; `objeq_sym.py` ignora a ordem das
     seções COMDAT);
   - antes de publicar uma entrega: `make exe ENTREGA=…` e o roteiro de regressão (fotos e pacotes iguais aos da última
     entrega aprovada).
8. **Regenere o relatório** do 983: `python3 tools/f6/cmp983.py <saída do pgbuild cmp>` refaz o `out/F6/CMP_983.tsv`.

### 2.4 O último stub

`?Error983@LuaScriptManagerJp983@lua_system@@QAEXPBD@Z`, chamado de `luautilitylib.obj`, sem VA conhecido no 983. Ache o
corpo no 983 pelos chamadores (`tools/pkt/quem.py`, `tools/f35/callers.py`) ou pelas strings de erro da Lua
(`tools/v6/strxref.py`), escreva o corpo e rode `make exe`: o `/alternatename` faz o símbolo real vencer sozinho, e o
`out/F4/FALTA.md` deve mostrar 0 stubs de função. Os 31 stubs de dados levam os valores do 983; o ideal é declará-los
no fonte também (lista em `out/F4/stubs.tsv`, gerado pelo `make f4-stubs`).

### 2.5 O assembly que sobrou

Em `src/projectg` não há mais nenhum bloco `naked`. Restam 4 fora dele: 3 em `include/engine/` (`wmathutil.h` e
`wmath.inl`), versões em assembly do matching do 645 com a versão em C no `#else`, e 1 em
`src/shared/exceptionreport.cpp`, que já era assembly no original e deve ficar. Os 3 de `include/engine/` saem do
mesmo jeito que os de `src/projectg` saíram:

```
python3 tools/f6/tira_naked.py <arquivo> 'Classe::Funcao' [N|todas]
python3 tools/f6/tira_sem.py <arquivo>          # todos os ramos REBANG_SEMANTIC_ONLY de uma vez
```

Confira sempre com `tools/f6/objeq.py` que os `.obj` saíram iguais fora de `.debug$*`. Um cabeçalho de `include/engine/`
entra em muitas unidades: compare todas as que o incluem. Sobram também, em alguns arquivos, aliases e comentários
`HACK` do matching (`nakedify`), que podem sair.

### 2.6 Solução do Visual Studio (`.sln` / `.vcxproj`)

Ainda não existe. Hoje o build é o `make` sob Wine, e a configuração de cada unidade (pch, `/FI`, includes, flags)
vem do `build-projectg.json` do rebang, lido por `tools/f32/pgbuild.py`. Um caminho possível:

1. gerar, a partir do `pgbuild.py list` e das flags do `Makefile`/`pgbuild.py`, um `.vcxproj` do VS2010 para cada
   módulo (ProjectG.exe com Fresh e Wangreal estáticas; wangreal.dll), com os mesmos pch e a mesma ordem de link
   (`out/V6/link/objs.tsv` dá a ordem usada hoje);
2. apontar os includes e as `.lib` para cópias locais do Platform SDK 2002, DirectX 9, ATL 7.1 corrigido
   (`build/atl71`) e das bibliotecas de terceiros, em vez de `/root/rebang`;
3. trocar `/Z7` por `/Zi` (no Windows o PDB funciona) e conferir que o `.obj` continua igual (`objeq.py`);
4. comparar o exe do VS com o do `make exe` (tamanho, imports, portões).

Até lá, trate qualquer afirmação sobre build no Windows como **não testada**.

### 2.7 Independência do rugburn

O inventário está em [RUGBURN.md](RUGBURN.md). Já resolvido no fonte: GameGuard desligado (`JP983_SEM_GAMEGUARD`),
`PANGYA_ARG`, endereço do login, updatelist, textos de `Translation/Read.aspx` e emblemas de guild
(`JP983_SERVER_CONFIG` + variáveis de ambiente), e um `ijl15.dll` limpo (só a biblioteca da Intel). Falta:

- tornar `JP983_SERVER_CONFIG` parte do build normal (hoje entra pela variável `DEFS` do `wt_build.sh`);
- pôr o exe sem rugburn no roteiro de regressão (item A193.2 do RUGBURN.md);
- as páginas web que o rugburn também não desvia (Report/SelfDesign, páginas `https://www5`) ficam como no original;
- entregar o `ijl15` limpo no lugar do `ijl15_teste.dll` (rugburn público) quando o dono aprovar.

### 2.8 Limpeza final

GameGuard removido do fonte (hoje só desligado pela chave), código organizado, comentários atualizados. Faça isso
depois que a partida estiver conferida, para não misturar limpeza com correção.

---

## 3. Fluxo de trabalho

### 3.1 Montar o ambiente

Siga o [COMPILAR.md](COMPILAR.md): Wine 9.0, VS2010 SP1 em `/root/kr839/local/vs2010`, rebang no commit `f0a85b5` em
`/root/rebang`, Python 3 com `capstone`, os binários de referência em `ref/` (confira o md5) e o repositório em
`/root/jp983src`. Para o pseudo-C do 983, um projeto Ghidra do `ProjectG_983_dump.exe` (o `tools/f37/dec.sh` espera
`/root/jp983/proj`). Depois:

```
tools/checar_ambiente.sh
make hello
```

### 3.2 Compilar

```
make wangreal-full                     # a dll
make pg-obj                            # todas as unidades do exe (15–25 min)
make jp                                # unidades novas do JP
make exe ENTREGA=out/F4/entregas/t1    # o exe e a pasta de teste
```

Para um exe coerente de uma revisão (sem misturar `.obj` antigos), use a receita da seção 5.4 do COMPILAR.md
(`wt_build.sh` + `jpbuild.py` + `make exe`).

### 3.3 Comparar uma função

O ciclo é sempre o mesmo: `pgbuild.py obj` → `pgbuild.py cmp` → `cmpfunc --diff` → `dv.py` (seção 2.3, passo 6).
Para a dll, basta `make cmp F=src/wangreal/x.cpp ARGS="--diff Nome"`. Leia a saída assim: classe, % de instruções,
VA do par, como o par foi achado (`mapa`, `bytes`, `alvo`, `vizinho`), tamanhos e hash (`x` exato, `r` sem
imediatos, `m` só mnemônicos). Detalhes na seção 5 do [TECNICO.md](TECNICO.md).

### 3.4 Testar o exe com um servidor local

1. Tenha um **cliente JP 983** instalado (os dados do jogo não vêm no repositório) e um **servidor** que fale o
   protocolo do JP 983 rodando na sua máquina ou na sua rede.
2. Compile o exe com `JP983_SERVER_CONFIG` e aponte as variáveis para o seu servidor:
   `JP983_LOGIN=host:porta`, `JP983_WEB=http://host:porta` (updatelist e textos), `JP983_WWW=http://host:porta`
   (emblemas). Sem as variáveis, valem os padrões `127.0.0.1` (portas 30101, 30091 e 30080).
3. Sirva pelo web local a updatelist da entrega (`www_teste/patch/updatelist`, que já tem o tamanho e o CRC do exe
   novo); sem ela o 983 não abre.
4. Copie a entrega para a pasta do cliente com `USAR_EXE_NOSSO.bat` (ajuste a variável `PASTA`); volte com
   `VOLTAR_EXE_ORIGINAL.bat`. Use só o `ijl15_teste.dll` da entrega ou o ijl15 limpo, **nunca** um rugburn que
   remenda endereços do exe original.
5. O jogo pede administrador. Se aparecer a caixa de um stub, o nome dele está no `jp983_stubs.log`; para seguir
   mesmo assim, crie `jp983_stub_continuar.txt` na pasta do exe.

### 3.5 Comparar original × nosso

- Rode **exatamente os mesmos passos** no exe original e no nosso, na mesma conta e no mesmo servidor.
- Compare **fotos** da janela do jogo (mesma resolução) e, principalmente, a **sequência de pacotes** que o servidor
  registra: o primeiro pacote diferente aponta a função errada.
- Só comparar depois de esperar o processo do jogo sair; trocar o exe com o jogo aberto invalida o teste.
- O dono usa um robô em PowerShell que faz isso sozinho a partir de uma fila de pedidos; ele não vem neste
  repositório. Sem ele, o mesmo método vale à mão.

### 3.6 Convenções

- **O 983 manda.** Nunca mude comportamento sem a referência do 983: cada mudança cita o VA que a prova (no
  comentário acima da função e na mensagem do commit).
- **Um commit por função ou por correção**, com o VA e o resultado do comparador na mensagem
  (por exemplo: `CFoo::Bar 983 00abcdef: IGUAL`).
- **Portão do comparador:** nada entra se piorar uma função que estava IGUAL/QUASE (confira com `ab.py`/`antes.py`)
  ou se quebrar o `make layoutcheck`.
- **Limpeza sem mudança de código** (tirar ramo morto, renomear) só entra com o `.obj` igual (`objeq.py`).
- **Layout primeiro:** `static_assert` falhando é sinal de cabeçalho errado; corrija o cabeçalho, nunca o assert.
- **Arquivos adotados** (`map/adotados.txt`) são editados direto; o rebang foi encerrado, então adote em vez de criar
  novos `ajustes_s*.py`.
- Código em inglês (nomes do original); comentários em português, curtos, com o VA do 983.
- Experimentos sempre em pastas com `/tmp/` no caminho.
- Nunca use clientes modificados em servidores de terceiros.

---

## 4. Onde está cada coisa

| Informação | Onde |
|---|---|
| Estado geral e números | `README.md`, [ESTADO.md](ESTADO.md) |
| Sistemas fora da partida (estado e evidência) | `out/F5/SISTEMAS.tsv` |
| Cada função própria do jogo × 983 | `out/F6/CMP_983.tsv` (gerado por `tools/f6/cmp983.py`) |
| Stubs que faltam no exe | `out/F4/falta_exe.tsv`, `out/F4/stubs_resumo.txt` (regravados pelo `make exe`) |
| Testes manuais do dono e as respostas | `out/F4/TESTE_DONO.md` |
| Histórico da regressão automática | `out/F4/regressao.tsv` |
| Roteiro de teste e portões da entrega | `out/V6/ROTEIRO.md` |
| Função 983 → nome decorado (mapa forte) | `map/projectg.tsv`, `map/projectg_manual.tsv`, `map/projectg_fora.tsv` |
| Cada função do 983: unidade, par no 645, nome | `map/projectg_funcs.tsv` |
| Unidade do 645 → faixa no 983 | `map/projectg_units.tsv` |
| Mapas da dll | `map/wangreal*.tsv` |
| Símbolos das unidades novas do JP | `src/projectg/jp/jp.tsv`, `src/projectg/jp/units.txt` |
| Ids de pacotes 645 → 983 | `map/pacotes_ids_envio.tsv`, `map/pacotes_ids_recebe.tsv` |
| Layouts de classes | cabeçalhos em `include/` e `src/*/include/`, asserts em `include/asserts/`, notas em [LAYOUTS.md](LAYOUTS.md) |
| Arquivos que deixaram de ser cópia do rebang | `map/adotados.txt` |
| Rugburn, GameGuard e variáveis de ambiente | [RUGBURN.md](RUGBURN.md), `src/projectg/ggc_wrapper.cpp`, `loginunit.cpp`, `commonutil.cpp`, `winmain.cpp` |
| Constantes de rede do 983 × fonte | `out/V5/constantes.tsv`, `out/V5/rede_983.tsv` (`make v5`) |
| Cada alvo do make e cada ferramenta | [TECNICO.md](TECNICO.md) |
| Build e execução | [COMPILAR.md](COMPILAR.md) |
| O método | [METODO.md](METODO.md), [METODO_RECONSTRUCAO_JOGOS.md](METODO_RECONSTRUCAO_JOGOS.md) |
| Histórico da organização do trabalho | [RETOMAR.md](RETOMAR.md) |
