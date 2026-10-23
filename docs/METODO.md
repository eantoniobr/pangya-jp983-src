# Como a reconstrução é feita

Este documento explica o método usado para reconstruir o fonte do PangYa JP 983. A versão longa, escrita para servir
a outros jogos, está em [METODO_RECONSTRUCAO_JOGOS.md](METODO_RECONSTRUCAO_JOGOS.md); os comandos estão em
[TECNICO.md](TECNICO.md).

## 1. A meta: funcional, não idêntico

Há duas metas possíveis numa reconstrução:

- **matching (byte a byte):** o binário recompilado é idêntico ao original. Prova que o fonte está certo, mas é ruim
  para editar, porque os truques de matching (assembly embutido, chamadas fixas) quebram quando o layout muda;
- **funcional:** o fonte compila com o compilador original e o jogo funciona como o original. É o que serve para
  modificar o jogo.

**A meta deste projeto é a funcional.** A comparação com o 983 continua sendo feita, mas como régua. Por decisão do
dono do projeto, uma função está **pronta** quando compila, usa o layout de classe certo e dá IGUAL ou QUASE no
comparador, ou dá DIFERENTE com a mesma lógica, justificada em uma linha. Não se gasta tempo transformando QUASE em
IGUAL. Remendos no binário depois do link foram rejeitados: o caminho para editar é o fonte completo.

## 2. Três versões do jogo, três papéis

| Versão | Papel | O que dá |
|---|---|---|
| **JP 983** (alvo, 2017) | **o código** | o binário diz o que cada função faz; é sempre ele que manda |
| **KR 645** (rebang, decomp com PDB) | **a estrutura** | arquivos, classes, nomes, tipos e boa parte do C++ inicial |
| **KR 839** (exe sem proteção) | **a ponte** | liga as duas pontas: pares de funções 645↔839 e 839↔983 |

Entre o 645 e o 983 há seis anos de desenvolvimento e cerca de 45% do código mudou. Por isso o 839, intermediário, foi
usado para parear as funções antes de começar.

Para cada função:

1. achar a função no 983 e o par dela no 839 e no 645 (mapas em `map/`);
2. se for igual à do 645: usar o código do rebang como está;
3. se mudou: partir do código do rebang e corrigir pelo 983;
4. se for nova (sem par): decompilar do 983 e escrever em C++ limpo, com os nomes da RTTI e da ponte;
5. compilar e comparar com a função do 983.

## 3. Análise dos binários (feita uma vez)

1. **Rich header e strings** → versão exata do compilador (VS2010 SP1), flags, bibliotecas, partes com LTCG.
2. **Ghidra** em modo headless, um projeto por binário: funções, vtables, RTTI, strings e grafo de chamadas.
3. **Pareamento** entre versões, do sinal mais forte ao mais fraco: vtables pela RTTI → strings únicas → hash dos bytes
   normalizado → posição no grafo de chamadas → vizinhança (ordem das funções dentro da unidade).
4. **Mapa de unidades:** cada `.cpp` do 645 vira uma faixa de endereços no 983, com o estado (igual, mudou pouco,
   alterada, nova, sem fonte). É a fila de trabalho (`map/projectg_units.tsv`, `map/projectg_funcs.tsv`).
5. **Diferenças de versão:** ids de pacotes de rede, tamanhos das structs de dados (`.iff`), constantes (portas, URLs,
   chaves de cifra).

## 4. Reconstruir uma unidade

1. **Layout primeiro.** Tamanhos e deslocamentos das classes do 983 são o que mais quebra o jogo: um campo fora do
   lugar dá queda longe dali. Os layouts são travados com `static_assert(sizeof(X) == 0x…)` e `offsetof` em
   `include/asserts/`, e o `make layoutcheck` transforma erro de layout em erro de compilação. O tamanho de uma classe
   no 983 sai do `push N` antes do `operator new` de quem a cria; os campos saem do construtor.
2. **Compilar com o compilador original** e **comparar função por função** (seção 5).
3. Ler o 983 quando a lógica mudou: desmonte (`tools/f37/dz.py`) e pseudo-C do Ghidra (`tools/f37/dec.sh`).
4. Repetir até sobrar só QUASE ou DIFERENTE justificado.
5. Conferir que nada piorou no resto (um cabeçalho comum entra em centenas de unidades): `make pg-obj` + `make pg-base`
   inteiros e a comparação "antes × depois" (`tools/f34/ab.py`).

Um exemplo completo, passo a passo, está na seção 6 do [TECNICO.md](TECNICO.md) (`frgaugebar.cpp`).

## 5. O comparador (`tools/cmpfunc`)

Compila um `.cpp` (ou recebe um `.obj`) e compara **cada função do `.obj`** com o par no 983, instrução por instrução,
mascarando o que muda só por causa do endereço (relocações).

- **IGUAL:** mesmas instruções, registradores, imediatos e desvios, com alvos coerentes.
- **QUASE:** pelo menos 90% das instruções alinhadas iguais.
- **DIFERENTE:** abaixo disso.
- **SEM_PAR:** o par não foi localizado no 983.

O par é procurado pelo mapa (`map/projectg.tsv`: nome decorado → endereço), por bytes, pelo destino de quem chama e
pela ordem do fonte. Um hash `-rm` (só o hash exato falha) quase sempre significa um deslocamento de campo diferente,
ou seja, layout de classe. O comparador ainda não compara dados (vtables, tabelas de exceção).

## 6. Do fonte ao exe que abre

1. **Link de prova cedo**, com **stubs** no lugar das funções ainda não escritas. Cada stub registra o nome num log e,
   por padrão, mostra uma caixa e fecha o jogo; no modo "continuar" só anota e devolve 0. Assim o exe roda antes de
   estar completo e cada stub alcançado aponta o que escrever em seguida.
2. **Portões antes de entregar** (o `make exe` falha se algum fechar). Cada um nasceu de um erro real:
   - todo import existe nas dlls reais do cliente (o primeiro exe não abriu: o som pedia funções de uma versão antiga
     do Miles);
   - chaves e constantes do 983, não as do 645 (registro, URL da lista de arquivos, chave XTEA dos `.pak`);
   - CRC do exe calculado pelo **algoritmo do jogo**, conferido antes no exe original;
   - manifesto igual ao original (sem pedir administrador, o 983 dava "erro de arquivo");
   - nenhuma dll de terceiro que altere o exe por endereço fixo.
3. **A ordem típica do que quebra:** carregador do Windows (imports) → inicializadores estáticos → checagens de
   instalação (registro, `.pak`, CRC) → leitura dos dados → telas (XML/UI) → texto e IME → login → lista de
   servidores → lobby → sala → partida.

## 7. Teste por pares: original × nosso

O que mais acelerou o trabalho foi comparar **sempre** o nosso exe com o original, nos mesmos passos:

- Um **robô de teste** no PC do dono (PowerShell) lê uma fila de pedidos, troca os arquivos do cliente, abre o jogo,
  fotografa só a janela do jogo, lê o texto das caixas de diálogo, executa as ações do roteiro (cliques, texto,
  teclas), fecha o jogo e devolve os arquivos originais.
- Cada roteiro roda também no **exe original** (`exe=original`), e as fotos dos dois são comparadas.
- O servidor de teste **registra os pacotes decifrados** de cada conexão. Comparando a sequência original × nossa, o
  **primeiro pacote diferente** aponta a função errada, muito mais rápido do que olhar fotos.
- Detalhes que custaram horas: o jogo roda como administrador, então o robô também precisa (senão o Windows bloqueia
  teclado, mouse e o fechamento); é preciso esperar o processo sair antes de trocar o exe.

## 8. Regressão

A cada lote de mudanças, um exe novo é montado de uma revisão inteira (worktree próprio, sem misturar `.obj` de
revisões diferentes) e passa pelo **roteiro de regressão** completo fora da partida. A entrega só é aprovada se:

- o roteiro inteiro roda sem queda;
- os tipos e as contagens de pacotes (GAME, LOGIN, RANK) e a ordem dos envios do cliente batem com a última entrega
  aprovada;
- as fotos de cada ação, em ordem, ficam dentro de um limite de diferença (RMSE) em relação à entrega anterior.

Entrega reprovada nunca vai para o dono; a aprovada anterior continua valendo. A **partida** fica fora do robô: até
23/10/2026 o dono a jogava e comparava com o original à mão; daí em diante ela precisa de uma validação repetível
(veja [CONTINUAR.md](CONTINUAR.md), seção 2.2).

## 9. Métricas que importam

Medir só a porcentagem de bytes iguais engana. O projeto acompanha também:

- o número de funções por classe (IGUAL / QUASE / DIFERENTE / SEM_PAR) e de onde veio o C++ (645 ou 983);
- os stubs restantes e se algum é alcançado ao abrir o jogo;
- os sistemas do jogo conferidos contra o original (tela e pacote);
- até onde o exe chega no roteiro (login → lobby → sala → partida).

O estado atual dessas métricas está em [ESTADO.md](ESTADO.md).
