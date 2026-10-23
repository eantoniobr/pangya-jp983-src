# Como retomar o projeto jp983src

Guia para quem assumir o trabalho (pessoa ou agente). Leia este arquivo inteiro antes de mexer em qualquer coisa.
Última revisão: 11/10/2026.

## 0. ATUALIZAÇÃO 15/10/2026 — leia primeiro (o resto do arquivo é de 11/10 e vale onde não for contrariado aqui)

**Regras fixas: REGRAS.md (restaurado de /root/jp983src-guarda/ antes de cada sessão; mudar a regra = editar lá). HANDOFF.md = só estado.**

**Estado.** O exe compilado do nosso fonte abre, passa da lista de arquivos (updatelist com o CRC do jogo), faz login no servidor
C# local, abre a escolha de servidor/canal e chega ao LOBBY do 983 (ainda com crashes ao entrar e "Loading..." no lugar do
personagem). wangreal.dll pronta desde 10/10. Métrica do painel (bytes IGUAL) ≈ 33% do ProjectG; o critério é funcional.

**Frentes (cinco), executor `run-frente.sh X`** (X = A..E; `tools/reiniciar_frentes.sh` sobe todas; `touch STOP` para todas):
| Frente | Faz | Modelo (runs/modelo-X; sem arquivo = Opus) |
|---|---|---|
| A | caminho do jogo (login → lobby → sala → partida) e o estrutural (layout, UI pela resolução do 983, RF ligada) | Opus |
| B | biblioteca de telas do 983 (Refresh/RF, F3.7.13) e sistemas novos do JP | Sonnet |
| C | monta o exe (`make exe ENTREGA=…`), testa pelo robô, mantém out/F4/PRIORIDADE.md, painel | Opus |
| D | onda 2 lado JOGO (out/F3.6/fila_D.tsv) | Sonnet |
| E | onda 2 lado INTERFACE (out/F3.6/fila_E.tsv) | Sonnet |
Reserva de unidade: out/F3.6/claims.tsv + lock/<arq>.lock.

**Documentos curtos (14/10).** HANDOFF.md tem ~10 kB (regras, PRIORIDADE, um bloco de estado por frente, regras de tamanho);
diários NOTES*.md só com as 3 últimas sessões; out/PEDIDOS.md só pedidos abertos. Histórico inteiro em docs/arquivo/ (grep, não
ler inteiro). Motivo: cada sessão relia ~1,4 MB a cada passo e gastava a cota nisso.

**Robô de teste no PC do dono** (os agentes testam sozinhos; o dono não testa à mão):
- Script `E:\dev\pangya-test\JP983\exe_teste\robo_teste.ps1` (cópia em out/F4/fila_teste/). Liga com `ROBO_INICIAR.bat`
  (roda COMO ADMINISTRADOR: o jogo é requireAdministrator e sem isso o Windows bloqueia teclado/mouse); para com `ROBO_PARAR.bat`.
  Não liga sozinho se o PC reiniciar.
- Fila: `out/F4/fila_teste/pedidos/<id>.txt` → resultado em `out/F4/resultados/<id>/` (ESTADO, eventos.txt, fotos, logs do jogo,
  `pacotes/` = pacotes decifrados do servidor por conexão). Formato e chaves (`exe=original`, `entrega=`, `acao=`,
  `parar_no_pacote=`, `tempo_cheio=`): out/F4/fila_teste/LEIAME.md.
- Método: rodar o mesmo roteiro no exe ORIGINAL e no nosso e comparar fotos e a sequência de pacotes; o 1º pacote diferente aponta
  a função errada.
- Servidor C# local do dono: roda numa worktree (`<pasta do servidor C# local>`, trocar em
  exe_teste\servidor_dir.txt); login 30101, web 30080; web do JP (updatelist/Translation) em 30090 (web-jp-30090.ps1, serve
  `www_teste\` com prioridade quando o exe compilado está em uso). Conta de teste: [removido na exportação].
- O ijl15.dll original da pasta de teste é um rugburn de TERCEIRO com patches de endereço do exe original: nunca usar com o
  compilado (a entrega traz ijl15_teste.dll = rugburn público).

**Painel:** igual (seção 9), agora com as cinco frentes e o modelo de cada uma.

## 1. O que é o projeto
Reconstrução do **código-fonte C++ do PangYa JP 983** (build `JP.R7.983.00`, compilado em 09/11/2017): o `ProjectG.exe`
e a `wangreal.dll`. A meta é **compilar com o compilador original (VS2010 SP1) e funcionar como o original**.
Não precisa ser byte a byte: "idêntico" é só a régua de verificação (ver seção 6).

Método:
- **o binário do 983 dá o código** de cada função;
- **o rebang (decomp do KR 645) dá a estrutura**: arquivos, classes, nomes, tipos;
- **o KR 839 é a ponte** entre os dois (mapeamento de funções 645↔839↔983).

Repositório privado: código reconstruído de jogo comercial. **Sem remoto, sem push, sem distribuição.**

## 2. Estado (no momento desta revisão)
| Fase | Estado |
|---|---|
| F0 base, F1 tipos | feitas |
| F2 wangreal.dll | **feita**: dll inteira do código; 90,6% byte a byte igual. Teste no PC: abre, login e UI ok; lobby/partida não testados |
| F3 ProjectG | em andamento em 3 frentes (seção 7). ProjectG ~17% igual, todas as 499 unidades compilam |
| F4 exe completo, F5 limpeza | não começaram |

Estado ao vivo: `status.json` (tarefas), `runs/runner*.log` (sessões), painel web (seção 9).
Marcos: tags `jp983-F0`, `jp983-F1`, `jp983-F2`, `jp983-F3.4` (uma tag por fase/onda daqui em diante).

## 3. Onde está cada coisa (máquina de build)
Acesso: por SSH à máquina de build (endereço, salto e chave removidos na exportação).

| Caminho | O que é | No git deste repo? |
|---|---|---|
| `/root/jp983src` | **este repositório** | sim |
| `/root/jp983src/ref/` | binários de referência: `ProjectG_983_dump.exe` (md5 `8c76194b…`), `wangreal_983.dll` (md5 `8b3e4808…`) | **não** (.gitignore) |
| `/root/jp983src/build/` | saídas de build (2,7 GB) | não |
| `/root/kr839/local/vs2010` | **o compilador** VS2010 SP1 (cl 16.00.40219.01) sob Wine, 1,8 GB | não (outro diretório) |
| `/root/rebang` | decomp do KR 645, **encerrada**; usar o commit `f0a85b5` (HEAD final; a tag kr645-decomp-2026-10-11 citada no HANDOFF não existe neste clone) | outro repo |
| `/root/jp983` | análise J1–J10 (983×839): projeto Ghidra `proj` (983 com nomes e pares), `proj839`, `out/RELATORIO.md` | outro repo |
| `/root/kr839` | análise do KR 839 e migração antiga (pausada); scripts de casamento de funções | outro repo |
| `/opt/ghidra_12.1.4_PUBLIC` | Ghidra (JDK 21 do sistema) | — |
| `/root/backups/` | cópias (seção 10) | — |

Origem dos binários de referência: o `ProjectG` é um **dump** feito pelo dono do projeto a partir do exe protegido
(Themida-like) do JP 983; o protegido é idêntico ao usado pelo servidor privado PangYa Relic. A `wangreal.dll` não tem
proteção. Só 5 funções estão virtualizadas no exe, todas telemetria do GameGuard (irrelevantes para o jogo).

## 4. Primeiros passos para quem chega
1. Ler, nesta ordem: este arquivo, `PLANO.md`, `README.md`, `docs/TECNICO.md` (ferramentas, alvos do make, formatos),
   o fim do `HANDOFF.md` (decisões mais recentes) e o fim dos diários `NOTES.md`, `NOTES-B.md`, `NOTES-C.md`.
2. Conferir o ambiente: `tools/checar_ambiente.sh` (compilador, Wine, Ghidra, referências com md5, commit do rebang; imprime OK/AVISO/FALTA por item).
3. Antes de trabalhar, **parar os agentes** se for mexer nos mesmos arquivos (seção 8).

## 5. Como se trabalha numa unidade (resumo; detalhes no docs/TECNICO.md)
1. Achar a unidade e a faixa de funções no 983: `map/projectg_units.tsv` (unidade do 645 → faixa no 983, estado, onda).
2. Para cada função: o par no 839/645 está em `map/` e nos comentários do projeto Ghidra `/root/jp983/proj`.
3. Igual ao 645 → código do rebang como está; mudou → partir do rebang e corrigir pelo 983; nova → decompilar o 983.
4. Ajustar o layout das classes para o do 983 (é o que mais destrava funções).
5. Compilar e comparar com `tools/cmpfunc` (IGUAL / QUASE / DIFERENTE / SEM_PAR).

## 6. Critério de "pronto" (decisão do dono, 11/10/2026)
**FUNCIONAL, não idêntico.** Função pronta = compila + layout certo + IGUAL ou QUASE, ou DIFERENTE com a mesma lógica
justificada em uma linha. Não gastar tempo transformando QUASE em IGUAL. Prioridade: layout certo → todas as funções
escritas → pacotes/IFF → link do exe (F4) → teste no jogo.

## 7. Organização do trabalho: três frentes
| Frente | Executor | Fila | Território | Diário |
|---|---|---|---|---|
| A | `run.sh` | F3.5 → F3.6 → F3.8 | src/projectg (menos jp/), src/engine, src/fresh, src/shared, include/ (menos asserts/), map/ | NOTES.md |
| B | `run-B.sh` | F3.7 sistemas novos do JP | src/projectg/jp/, include/jp/ | NOTES-B.md |
| C | `run-C.sh` | V3–V6 (asserts de layout, pacotes/IFF, rugburn, roteiro de teste) | include/asserts/, tools/v* | NOTES-C.md |
Regras completas na seção "TRÊS FRENTES" do HANDOFF: cada frente só edita o seu território; pedidos entre frentes em
`out/PEDIDOS.md`; commits sob `flock git.lock`, adicionando só os próprios caminhos; Ghidra sob `flock /root/jp983/ghidra.lock`.

## 8. Os agentes automáticos
- Cada executor (`run*.sh`) roda uma sessão `claude -p` por vez, com o prompt `prompt*.txt` (uma tarefa por sessão, teto
  de ~300k tokens, `timeout 3h`). Ao fim, espera 2 min e começa outra. Se o log da sessão indicar limite de uso, espera 45 min.
- **Parar tudo:** `touch /root/jp983src/STOP` (a sessão em andamento termina, nenhuma nova começa). Retomar: apagar o
  `STOP` e rodar `setsid -f ./run.sh` (e `run-B.sh`, `run-C.sh`).
- Uma frente para sozinha com `DONE[-B|-C]` (fila acabou) ou `NEEDS_HUMAN[-B|-C].md` (precisa de decisão do dono).
- Sem os agentes, o trabalho é o mesmo à mão: seguir o HANDOFF e registrar no `status.json` e no diário da frente.

## 9. Painel de progresso
- `make painel` gera `out/painel/index.html` (dados embutidos) e soma um ponto em `out/painel/historico.jsonl` quando
  algum número ou o commit mudou. Mostra as três frentes, pedidos entre frentes e sistemas novos do JP (P2; dona: frente C).
- **Web (celular):** serviço systemd `jp983-painel` neste container (`painel_web/server.py`, porta 18983, regera a cada
  120 s; credenciais fora do git). Detalhes do acesso externo removidos na exportação.
- Também há uma cópia local no PC do dono (`http://localhost:8765/jp983/`, loop no WSL) e um artifact do claude.ai.

## 10. Backups
- `/root/backups/jp983src-AAAAMMDD.bundle`: `git bundle` com todo o histórico e as tags. Restaurar:
  `git clone /root/backups/jp983src-AAAAMMDD.bundle jp983src`.
- `/root/backups/jp983src-externos-AAAAMMDD.tar`: o que o git não guarda e não se recria fácil: `ref/`, `painel_web/.env`
  e o manifesto de dependências (md5 das referências, tag do rebang, versões).
- O compilador (`/root/kr839/local/vs2010`) tem cópia em `/root/backups/vs2010-AAAAMMDD.tar.zst`.
- Cópias também no PC do dono, em `E:\dev\backups\jp983\`.
- Backup diário automático (cron 04:30 no container): `/root/backups/diario/` (bundle + status e diários; guarda 7 dias; script `/root/backups/backup_diario.sh`). As cópias no PC NÃO são automáticas: copiar de vez em quando.

## 11. Testes no PC do dono (Windows)
- Cliente JP 983 de teste: `E:\dev\pangya-test\JP983` (cópia do dump + `ijl15.dll` + `rugburn.json`). **O `ijl15.dll` da
  pasta é um rugburn MODIFICADO DE TERCEIRO** (veio com a pasta do cliente; origem desconhecida; o dono não o fez; cópia em
  out/F4/ijl15_rugburn_terceiro.dll): patches em endereços fixos do exe ORIGINAL + checagens "Anti-Cheat" de memória.
  **Nunca usar com o exe compilado** (escreve lixo no .text/.data dele; teste 2, out/F4/RESPOSTA_USUARIO_2a.md): o exe
  compilado vai com o `ijl15_teste.dll` da entrega (rugburn público só com ganchos de API; `make f4-ijl15`, portão A6). `ABRIR_JP983_CS.bat` abre o web do JP (porta 30090) e o cliente apontado para o servidor C# local
  (porta 30101), que ainda não faz o login do JP. Para jogar de verdade, o dono usa o servidor da comunidade.
- Troca da dll: `USAR_WANGREAL_NOSSA.bat` / `VOLTAR_WANGREAL_ORIGINAL.bat`.
- Os testes no jogo são sempre feitos pelo dono; os agentes nunca rodam o jogo.

## 12. Decisões importantes (histórico curto)
- 09/10: o alvo passou a ser o JP 983 (a migração 645←839 ficou pausada em `/root/kr839`).
- 09/10: objetivo = código-fonte editável, não matching. Plano F0–F5 aprovado (`PLANO.md`).
- 10/10: wangreal.dll concluída; F3 começou antes do teste completo no jogo, por decisão do dono.
- 11/10: rebang encerrado e reimportado (F3.R). Critério funcional reforçado. Três frentes.
- Proibido: alterar /root/rebang, os binários de `ref/`, a instalação do PangYa Relic, ou usar clientes modificados
  em servidores de terceiros.
