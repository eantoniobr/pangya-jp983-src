# Guia de método: reconstruir o código-fonte de um jogo de Windows a partir do binário

Escrito em 15/10/2026, a partir de dois projetos reais: a decomp "matching" do PangYa KR 645 (rebang, 09–11/10/2026) e
a reconstrução funcional do PangYa JP 983 (jp983src, 09/10/2026 em diante). Os exemplos citam esses projetos, mas o método vale
para outros jogos antigos de Windows em C++.

Leia nesta ordem: §1 (vale a pena?), §2 (as duas metas possíveis), §11 (checklist). O resto é consulta.

---

## 1. Quando vale a pena (pré-requisitos)

| Item | Por quê | Como foi no PangYa |
|---|---|---|
| Binário sem proteção pesada, ou um dump limpo | Ghidra e o comparador precisam do código real | JP 983 era Themida; usamos um dump do dono. Só 5 funções ficaram virtualizadas (telemetria do anticheat), irrelevantes |
| O compilador exato (versão e service pack) | Sem ele não há como comparar função por função | VS2010 SP1 (cl 16.00.40219.01) sob Wine; o 645 era VC7.1 |
| Uma "ponte": versão mais antiga com fonte/PDB/nomes, ou outra versão com símbolos | Dá nomes, tipos e estrutura de arquivos | rebang (645, fonte) e KR 839 (exe sem proteção) |
| Um jeito de rodar o jogo: servidor (oficial, comunidade ou emulador próprio) e os dados do cliente | Sem rodar não há teste funcional | Servidor C# próprio do dono, com camada JP 983 |
| Uma máquina de build Linux com bastante RAM/CPU (Wine + Ghidra) | Ghidra headless e builds em paralelo | Container Linux, 32 GB, 40 núcleos |

Se faltar a ponte, o projeto continua possível, mas cada função tem de ser decompilada e nomeada do zero (muito mais lento).

## 2. Escolha a meta antes de começar

1. **Matching (byte a byte).** O exe recompilado é idêntico ao original. Ótimo para provar que o fonte está certo, ruim para
   editar: truques de matching (asm embutido, chamadas fixas, `_emit`) quebram quando o layout muda.
2. **Funcional.** O fonte compila com o compilador original e o jogo funciona como o original; "igual" vira só régua.
   É o que serve para modificar o jogo. **Foi a meta do JP 983.**

Regra que aprendemos: decidir isso por escrito no início (o dono rejeitou depois "remendos pós-link" e "desvios por jmp" como
gambiarra — o caminho certo para editar é o fonte completo, não remendar o binário).

## 3. Pipeline de análise (uma vez por binário)

1. **Rich header / strings** → versão do compilador, flags (/O2, /Ob2, LTCG em partes), bibliotecas.
2. **Ghidra headless** (`analyzeHeadless`, projeto por binário; abrir só com `-readOnly` e sob `flock` quando vários agentes
   usam). Se o dump tiver seções renomeadas, renomeie para o Ghidra achar o RTTI.
3. **Exportar**: funções (endereço, tamanho, hash dos bytes), vtables, RTTI (nomes de classe), strings e quem as usa, grafo de
   chamadas.
4. **Parear funções entre versões** (antiga ↔ ponte ↔ alvo), do mais forte para o mais fraco: vtables pela RTTI → strings únicas
   → hash dos bytes normalizado → posição no grafo de chamadas → vizinhança (ordem das funções dentro da unidade).
5. **Mapa de unidades**: cada `.cpp` da versão antiga → faixa de endereços no alvo, com estado (igual / mudou pouco / alterada /
   nova / sem fonte). Isso vira a fila de trabalho ("ondas").
6. **Diferenças de versão**: tabela de pacotes de rede (id → handler → struct), tamanhos das structs de dados (no PangYa, os .iff),
   constantes (portas, URLs, chaves de cifra).

## 4. Reconstruir uma unidade

1. Parta do fonte da ponte; o binário do alvo manda.
2. **Layout primeiro**: tamanhos e offsets das classes do alvo. É o que mais quebra o jogo (um campo deslocado = crash longe dali).
   Trave com `static_assert(sizeof(X)==0x…)` e `offsetof` → erro de layout vira erro de compilação.
3. Compile com o compilador original e **compare função por função** com o alvo (ferramenta `cmpfunc`: IGUAL / QUASE / DIFERENTE /
   SEM_PAR, normalizando endereços e relocações).
4. Critério funcional: pronto = compila + layout certo + IGUAL/QUASE, ou DIFERENTE com a mesma lógica justificada em uma linha.
   Não gaste tempo transformando QUASE em IGUAL.
5. Funções novas (sem par): decompile do alvo e escreva em C++ limpo, com os nomes da RTTI e da ponte.

## 5. Do fonte ao exe que abre

1. **Link de prova cedo**, com **tampões (stubs)** no lugar das funções ainda não escritas. Cada stub registra o nome num log
   e, por padrão, mostra uma caixa e fecha; com um arquivo-chave na pasta ("modo continuar") só anota e devolve 0.
2. **Portões antes de entregar** (o `make exe` falha se algum fechar), cada um nasceu de um erro real:
   - todo import existe nas dlls reais do cliente (o 1º exe não abriu: o som pedia funções do Miles antigo);
   - chaves/constantes do alvo e não da versão antiga (registro, URL da lista de arquivos, chave XTEA dos paks);
   - CRC do exe calculado pelo **algoritmo do jogo**, conferido primeiro no exe original (supor CRC32 padrão custou um teste);
   - manifesto igual ao original (sem admin, o 983 dava "erro de arquivo"); dll de terceiro que altera o exe → fora.
3. **Ordem típica do que quebra**, do PangYa: carregador do Windows (imports) → inicializadores estáticos → checagens de
   instalação/arquivos (registro, paks, CRC) → leitura de pacotes de dados → telas (XML/UI) → texto/IME → login → lista de
   servidores → lobby → sala → partida.

## 6. Teste automático com comparação (o que mais acelerou)

- **Robô no PC de teste** (PowerShell): lê uma fila de pedidos na máquina de build, baixa a entrega, confere md5, troca os
  arquivos, abre o jogo, fotografa a janela (PrintWindow, só a janela do jogo), lê o texto de caixas de diálogo (UIAutomation)
  e aperta OK, executa ações (clique/texto/tecla/espera), fecha o jogo, devolve os originais e manda tudo de volta.
  Arquivos de referência: `out/F4/fila_teste/robo_teste.ps1` e `LEIAME.md` no repositório jp983src.
- Detalhes que custaram horas: o jogo roda como administrador → o robô também precisa (senão o Windows bloqueia teclado,
  mouse e o fechamento); esperar o processo sair antes de trocar o exe; encerrar o teste cedo quando as ações acabam ou quando um
  pacote-alvo aparece (fila menor).
- **Sempre rodar o ORIGINAL nos mesmos passos** (`exe=original`) e comparar fotos.
- **Registro de pacotes no servidor** (decifrados, por conexão): compare a sequência original × nosso; o **primeiro pacote
  diferente** aponta a função errada. Muito mais rápido que olhar fotos.
- Peça ao dono só o que é decisão dele; o resto o robô faz.

## 7. Organização com agentes (frentes em paralelo)

- **Executor por frente** (`run-frente.sh X`): uma sessão `claude -p` por vez, prompt fixo curto, teto de tokens, `timeout`,
  30 s entre sessões, detecção de limite de uso (espera sem custo), modelo por frente (`runs/modelo-X`), `STOP` para todas.
- **Territórios**: cada frente edita só os seus caminhos; o resto vai por pedido (`out/PEDIDOS.md`). Reserva de unidade
  (`claims.tsv`) + trava por arquivo (`flock lock/<arq>.lock`) + `flock git.lock` no commit, `git add` só dos próprios caminhos.
- **Divisão que funcionou no JP 983 (5 frentes)**: A = caminho do jogo e o estrutural (Opus); B = biblioteca de UI nova (Sonnet);
  C = monta o exe, testa no robô, mantém a lista de PRIORIDADE (Opus); D e E = volume, divididos por assunto (jogo × interface)
  para não disputar arquivos (Sonnet).
- **Prioridade guiada pelo jogo**: uma lista curta do que para o exe no caminho login → lobby → sala → partida, cada item com
  dono; as frentes pegam dela antes da fila normal. Funções que o jogo não alcança ficam para depois.
- **Modelo certo no lugar certo**: investigação de crash e decisões estruturais = modelo mais forte; transcrição e lotes = modelo
  mais rápido/barato (rendeu 6–10 sessões por hora por frente).

## 8. Economia de contexto e cota (o erro mais caro)

- Documentos que toda sessão lê crescem sem parar (HANDOFF de 500 kB, diários de 400 kB) e **cada passo reenvia tudo**:
  uma sessão começava com ~290 mil tokens. Depois de enxugar, ~46–50 mil (6× menos no início, ~40% menos por passo).
- Regras: HANDOFF ≤ ~25 kB com um bloco de estado por frente (substituído, não acrescentado); diário só com as 3 últimas sessões;
  pedidos só abertos; histórico em `docs/arquivo/` consultado com `grep`, nunca lido inteiro.
- Proibir "sessões vazias" (só triagem, esperando outra frente): pegar o próximo item ou encerrar.
- Nunca esperar parado: build e teste em segundo plano, seguir com outro item.

## 9. Operação

- Disco: cada build completo ocupa centenas de MB; manter só os 3 últimos por frente e limpar abaixo de 15 GB livres.
- Nunca `pkill` por padrão de nome (soltou travas de outras frentes); matar só pids próprios.
- Backups: `git bundle` diário na máquina de build + cópia periódica fora dela (o compilador e os binários de referência
  também, à parte do git). Guia de retomada (`docs/RETOMAR.md`) atualizado a cada mudança de organização.
- Painel de progresso servido na web (atualiza sozinho) para acompanhar pelo celular.
- Repositório privado, sem remoto: é código reconstruído de jogo comercial. Nunca usar clientes modificados em servidores de terceiros.

## 10. Erros que cometemos (e como evitar)

| Erro | Custo | Como evitar |
|---|---|---|
| CRC "padrão" sem conferir no original | um ciclo de teste | todo valor que o cliente confere: validar contra o par original (exe × lista original) antes de entregar |
| dll de terceiro (rugburn modificado) alterando o exe por endereço fixo | testes inválidos e caixas "anti-cheat" | conferir o que a pasta de teste carrega; usar só componentes conhecidos |
| robô sem admin com jogo que exige admin | login "travado" por horas | checar o manifesto do exe e rodar o robô no mesmo nível |
| documentos crescendo sem limite | ~6× mais cota no início de cada sessão | regras de tamanho desde o dia 1 |
| frente em laço de sessões vazias | 14 sessões sem código | regra "sem trabalho novo = não repetir" |
| trocar a conta/processo várias vezes | sessões interrompidas, trabalho pela metade | decidir a organização e só mexer se algo quebrar; medir 1×/semana |
| métrica errada (só % de bytes iguais) | não saber se o volume rende | medir também funções adaptadas, stubs restantes e até onde o exe chega no jogo |

## 11. Checklist para começar um jogo novo

1. [ ] Meta escrita: matching ou funcional (§2).
2. [ ] Binário limpo (ou dump) + md5 guardado; compilador exato instalado e testado (compilar um arquivo e comparar uma função).
3. [ ] Ponte escolhida (fonte/PDB/outra versão) e pareamento feito (§3), com o mapa de unidades.
4. [ ] Ferramenta de comparação por função funcionando.
5. [ ] Servidor e dados para rodar o jogo; conta de teste local.
6. [ ] Robô de teste + modo "original" + registro de pacotes no servidor (§6), antes do primeiro exe.
7. [ ] Repositório privado com: HANDOFF curto, PLANO, RETOMAR, regras de tamanho, PEDIDOS, PRIORIDADE (§7–8).
8. [ ] Executor por frente com detecção de limite, modelo por frente, STOP; começar com 3 frentes e crescer se a cota permitir.
9. [ ] Link de prova com stubs o quanto antes; portões de entrega (§5).
10. [ ] Backups diários + cópia fora da máquina; painel de progresso.

## Onde ver o projeto de referência

- Repositório: `/root/jp983src` no container de build (guia `docs/RETOMAR.md`, regras `HANDOFF.md`, robô em `out/F4/fila_teste/`).
- Cópias no PC: `E:\dev\backups\jp983\` (bundle do git, externos, robô, RETOMAR).
- Decomp matching de referência (645): `/root/rebang`, commit `f0a85b5`.
