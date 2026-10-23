# Estado do projeto

Retrato de **23/10/2026**, tirado do repositório de trabalho no commit `00f572bb5`. Os relatórios usados estão nesta
cópia:

- `out/F5/SISTEMAS.tsv`: sistemas;
- `out/F6/CMP_983.tsv`: comparação função a função;
- `out/F4/falta_exe.tsv` e `out/F4/stubs_resumo.txt`: stubs (do último `make exe` registrado);
- `out/F4/regressao.tsv`: regressão automática;
- `out/F4/TESTE_DONO.md`: testes manuais do dono.

Nesses arquivos, os nomes das contas de teste foram trocados por `conta-teste`.

## 1. Resumo

- O exe compilado deste fonte **abre, faz login, escolhe servidor e canal e chega ao lobby**. A regressão automática
  (o mesmo roteiro no exe original e no nosso, comparando fotos e pacotes) aprovou a entrega `reg-20261023-1520`:
  roteiro inteiro fora da partida, 1.738 s, sem queda.
- **Sistemas fora da partida: 20 de 27 prontos.** Sete estão em andamento, cinco deles reabertos pelo dono depois do teste
  de 19/10 (botão direito em listas e no My Room, por exemplo).
- **A partida está com uma regressão grave** na entrega de 23/10 (seção 2). Ela é escrita em código, mas o robô não a
  joga; até 23/10 o teste era manual, feito pelo dono, que avisou que não vai mais testar à mão.
- A **wangreal.dll** está completa desde 10/10/2026 (90,6% dos bytes iguais aos da original).

## 2. Problemas conhecidos

Estado em 23/10/2026, segundo os testes do dono com a entrega `reg-20261023-1030` (Practice, campo Abbot Mine, com o
Play Assist ligado) e os registros dos sistemas. São problemas em aberto; não há prazo para eles.

**Partida**

1. **Personagem, bola, taco e caddie não carregam.** O personagem aparece como silhueta preta, sem taco; bola e
   caddie não aparecem. Isso funcionava em testes anteriores do dono. Verificações de ponteiro nulo acrescentadas em
   correções recentes evitam a queda, mas escondem a causa: o conjunto de tacos, ossos e peças não está sendo
   carregado. A causa ainda não foi achada.
2. **Vista de cima (tecla 0) derruba o jogo:** violação de acesso em `CFrameSetHost983::FindNamed` (com `this`
   nulo), chamada por `CMouseCursor::Display`.
3. **O botão Assist** muda de estado, mas fica travado depois. Há uma correção no código (B1137, 23/10), ainda não
   conferida no jogo.
4. **"Pang: 0" é desenhado por cima do medidor de vento**; no 983 ele fica em outro lugar.
5. **Ícones das tacadas especiais errados.**
6. Aparecem três linhas de texto vermelho em japonês à esquerda da tela; ainda não se sabe se o 983 também as mostra.

Em 22/10, o Practice com o Play Assist ligado também caiu, com violação de acesso em `CGolfPlayer::HandleMsg`; as
correções dessa queda são parte das mudanças que agora estão sendo revistas.

**Sistemas reabertos ou em andamento** (detalhes na seção 3)

- **salas:** queda com o botão direito na primeira sala da lista (corrigida no código, falta a prova contra o original);
- **mascotes:** botão direito no mascote do My Room deve abrir a janela `mascot_info`, como no 983;
- **caddies:** a janela de detalhes já abre igual; falta conferir o "Rehire" (aviso de salário);
- **loja:** botão direito na lista da loja tem duas diferenças em relação ao 983;
- **My Room:** botão direito nas abas (itens desequipavam ou perdiam a seleção); Caddie já igual, faltam Item, Clothes
  e Mascot;
- **salas especiais:** o personagem não anda no clique do chão do Lounge;
- **sala de evento GM:** a abertura é igual; o interior exige uma conta GM no servidor de teste.

Outro ponto que o dono já tinha apontado e que ainda não foi confirmado como resolvido: a queda quando o tempo da
tacada acaba (há uma correção no código, B751, ainda não conferida no jogo).

## 3. Sistemas fora da partida

Estados: **PRONTO** = igual ao original nas telas e nos pacotes conferidos; **PRONTO COM RESSALVA** = igual, com uma
diferença que depende do servidor; **andamento** = em comparação ou reaberto. "Telas" = telas conferidas / telas do
sistema.

| Sistema | Estado | Telas | Resumo |
|---|---|---|---|
| quedas fora da partida | PRONTO | a medir | nenhuma queda fora da partida em aberto |
| mapa de layouts | PRONTO | a medir | `docs/LAYOUTS.md` + `C_ASSERT` de layout no build |
| salas (criar/entrar/Versus/Tourney/chat) | **andamento** | 5/6 | reaberto: queda do botão direito na 1ª sala da lista (corrigida, falta a prova) |
| mensageiro/amigos | PRONTO | 3/3 | pares nosso × original nas três telas |
| guild | PRONTO | 1/1 | 0 px de diferença; pacotes iguais |
| ranking | PRONTO | 1/1 | par de regressão × original |
| correio/presente | PRONTO | 3/3 | Inbox e leitura da carta iguais; pacotes iguais |
| inventário/equipar | PRONTO | 9/9 | regressão OK; "abrir box" igual ao original |
| mascotes | **andamento** | 2/3 | reaberto: botão direito no mascote do My Room |
| caddies | **andamento** | 1/3 | janela de detalhes igual; falta o Rehire |
| cartas | PRONTO | 5/5 | lista Pack e descrição como no original; opcodes iguais |
| loja | **andamento** | 12/13 | reaberto: botão direito na lista (2 diferenças) |
| Papel Shop/Bongdari | PRONTO | 5/5 | Memorial, Gacha, Cauldron e Rare Shop no roteiro |
| opções | PRONTO | 6/6 | telas e áudio iguais |
| login bônus/conquistas/scratch | PRONTO | 6/6 | mesma sequência de pacotes; regressão aprovada |
| login/servidor/lobby | PRONTO | 7/7 | sombra e tom do lobby iguais ao original |
| My Room | **andamento** | 3/4 | reaberto: botão direito nas abas (Caddie igual; faltam Item, Clothes, Mascot) |
| inventário do rugburn | PRONTO | a medir | `docs/RUGBURN.md`; exe nosso + ijl15 limpo chega ao lobby sem rugburn |
| troca de personagem (My Room) | PRONTO | 1/1 | pacotes byte a byte iguais |
| Club Workshop | PRONTO | 7/7 | Rank Up, Recover e Transfer iguais |
| efeitos dos itens | PRONTO | 1/1 | efeitos na loja, lobby e My Room iguais |
| material/luz da prévia 3D | PRONTO | 1/1 | ciclo de cor animado igual |
| sala de espera (dentro da sala) | PRONTO | 8/8 | layout e Switch Teams iguais; no roteiro de regressão |
| salas especiais (Lounge/Shuffle/Battle/evento) | **andamento** | 3/4 | Event, Shuffle e Battle iguais; Lounge não anda no clique |
| sala de evento GM | **andamento** | a medir | abertura igual; interior exige conta GM |
| eventos especiais | PRONTO COM RESSALVA | 1/1 | fotos idênticas; depende do servidor |
| console do jogo | PRONTO | 1/1 | igual; no 983 o console é código morto |

Total: 27 sistemas; 19 PRONTO, 1 PRONTO COM RESSALVA, 7 em andamento.

## 4. Comparação função a função com o 983

Cada função **própria** de `src/projectg` (definida no `.cpp`, sem contar inline de cabeçalho) é compilada e
comparada com a função par no exe 983 pelo `tools/cmpfunc`.

| Classe | Funções | % |
|---|---|---|
| IGUAL | 8.522 | 64,6% |
| QUASE (≥ 90% das instruções alinhadas) | 1.373 | 10,4% |
| DIFERENTE | 2.039 | 15,4% |
| SEM_PAR (par não localizado no 983) | 1.265 | 9,6% |
| **Total** | **13.199** | em 376 unidades |

Origem do C++ de cada função (heurística de `tools/f6/cmp983.py`: "645" = o nome `Classe::Função` aparece no `.cpp` de
mesmo nome do rebang; "983" = escrita a partir do 983):

| Origem | Total | IGUAL | QUASE | DIFERENTE | SEM_PAR |
|---|---|---|---|---|---|
| 645 | 9.758 | 6.049 | 1.068 | 1.573 | 1.068 |
| 983 | 3.441 | 2.473 | 305 | 466 | 197 |

### 4.1 As 20 unidades com mais funções DIFERENTE

| Unidade | DIFERENTE | IGUAL | QUASE | SEM_PAR | Total |
|---|---|---|---|---|---|
| lobbymain | 104 | 135 | 87 | 149 | 475 |
| golfrule | 103 | 99 | 32 | 23 | 257 |
| realmyroommainui | 82 | 84 | 100 | 147 | 413 |
| fontinfo | 65 | 45 | 15 | 49 | 174 |
| ingameguildlobbydlg | 61 | 13 | 5 | 32 | 111 |
| user_info | 58 | 132 | 23 | 7 | 220 |
| taskmain | 52 | 98 | 22 | 38 | 210 |
| npc | 45 | 75 | 25 | 0 | 145 |
| offlinetradedlg | 43 | 30 | 23 | 41 | 137 |
| shopmain | 39 | 114 | 26 | 8 | 187 |
| quadtree | 34 | 43 | 6 | 58 | 141 |
| polysoup | 33 | 151 | 18 | 10 | 212 |
| avatar_avatar | 30 | 12 | 9 | 13 | 64 |
| bongdarishopdlg | 29 | 168 | 14 | 36 | 247 |
| gmtoolkit | 29 | 16 | 9 | 0 | 54 |
| realmyroom_avatar | 26 | 8 | 8 | 17 | 59 |
| scoreboard | 26 | 209 | 36 | 18 | 289 |
| shareddoc | 23 | 109 | 14 | 21 | 167 |
| gui_control | 22 | 50 | 13 | 14 | 99 |
| particleparty | 20 | 50 | 13 | 0 | 83 |

Lembrete: a régua é funcional. DIFERENTE com a mesma lógica (ordem de registradores, pilha, arredondamento de float
em outro ponto) é aceito quando justificado; o que importa é o layout das classes e o comportamento no jogo.

## 5. Stubs restantes

Stubs são funções ou dados que o link ainda não encontrou no fonte e que são preenchidos por código gerado
(`make f4-stubs`). No último exe registrado:

| Stub | VA no nosso exe | VA no 983 | Fatal? | Observação |
|---|---|---|---|---|
| `?Error983@LuaScriptManagerJp983@lua_system@@QAEXPBD@Z` (`lua_system::LuaScriptManagerJp983::Error983`) | `00c220e0` | — | **não** (volta 0 no modo continuar) | em `luautilitylib.obj`; não é alcançado pelos inicializadores estáticos nem por chamada direta a partir do `WinMain` |

Além dele há **31 stubs de dados** (30 símbolos em 27 áreas de armazenamento, mais um literal `""`), que levam o valor
inicial do 983 e não param o jogo.

## 6. Assembly restante

**Nenhum** bloco `__declspec(naked)` sobrou em `src/projectg` (eram 1.339 no começo de 19/10; os 76 de
`golfrule.cpp` saíram na noite de 19/10). Fora dele restam 4:

- 3 em `include/engine/` (`wmathutil.h`: `RayIntersectAABBSolid`; `wmath.inl`: `WMatrix::operator~` e `RotMat`),
  versões em assembly do matching do 645 com a versão em C no `#else`;
- 1 em `src/shared/exceptionreport.cpp` (`SnapCurrentContext`), que já era assembly no fonte original: lê os
  registradores antes de qualquer prólogo e não tem equivalente em C++.

## 7. Regressão automática

`out/F4/regressao.tsv` tem 99 rodadas desde 15/10. Na última semana:

| Entrega | Resultado |
|---|---|
| `reg-20261023-1030` | telas OK, 1.729 s, sem queda; é a entrega em que o dono achou a regressão da partida (seção 2) |
| `reg-20261023-1520` | telas OK, 1.738 s, sem queda; diferenças nas fotos explicadas (itens novos em Packages, curso aleatório, detalhe de Set Item corrigido depois) |
| `reg-20261023-1900` | na fila no momento deste retrato |

O roteiro cobre tudo fora da partida; a partida não entra no robô.

## 8. O que falta

1. **Resolver a regressão da partida** (seção 2) pela análise do código contra o 983, função a função.
2. **Fechar os sete sistemas em andamento.**
3. **Converter para o 983 o C++ que ainda vem do 645**: cerca de 74% das funções próprias ainda partem do código do
   KR 645 adaptado; as DIFERENTE e SEM_PAR dessas unidades são o principal trabalho restante (tabela 4.1).
4. **Fechar os stubs**: escrever `Error983` e os dados restantes no fonte.
5. **Validar a partida** de forma repetível, já que o dono não vai mais testá-la à mão.
6. **Solução do Visual Studio**: ainda não existe um `.sln` para abrir e compilar o jogo no VS; hoje o build é feito
   pelo `make` sob Wine (veja [COMPILAR.md](COMPILAR.md)).
7. **Limpeza final**: código organizado e documentado, GameGuard removido do fonte (hoje só desligado pela chave
   `JP983_SEM_GAMEGUARD`).
