# Aviso legal e licenças de terceiros

*English summary at the end.*

## 1. Natureza do projeto

Este é um projeto **independente**, feito para **preservação e estudo** de um cliente de jogo antigo para Windows
(PangYa, versão japonesa JP.R7.983.00, de 2017). O objetivo é entender e documentar como o programa funciona,
reconstruindo o seu código-fonte em C++ a partir do binário. O projeto **não tem fins comerciais**: não vende nada,
não aceita pagamentos e não oferece serviço de jogo.

## 2. Sem afiliação

O projeto **não tem nenhuma afiliação** com a Ntreev Soft, a Kakao Games, a Gungho, a Gametree ou qualquer outra
desenvolvedora ou publicadora do PangYa, e não foi aprovado nem patrocinado por elas. **PangYa** e todas as marcas,
nomes e logotipos relacionados pertencem aos seus respectivos donos e são citados aqui apenas para identificar o
programa estudado.

## 3. O que o repositório não contém

O repositório **não contém nenhum arquivo do jogo**: nenhum executável ou DLL original, nenhum `.pak` ou `.iff`, nenhuma
imagem, modelo, som, música, vídeo ou texto do jogo, e nenhuma ferramenta para obtê-los. Também não há dados de
jogadores. O código aqui só faz algo útil junto com uma cópia do cliente que **cada pessoa precisa ter obtido de forma
legal** por conta própria.

O ícone e os três bitmaps que o `ProjectG.rc` referencia (`src/projectg/ProjectG.ico`, `111.bmp`, `113.bmp`,
`123.bmp`) são **substitutos neutros** (cinza, do mesmo tamanho dos originais), só para o build funcionar.

O código reconstruído contém, como literais, alguns textos e constantes que fazem parte do próprio programa original
(mensagens, nomes de arquivo, endereços) e que são necessários para que ele se comporte como o original (veja a seção
6). O arquivo `out/F4/updatelist_web_local_original`, usado pelo `make exe`, é uma lista cifrada de nomes, tamanhos e
CRCs de arquivos do cliente, sem o conteúdo de nenhum deles.

## 4. Uso

- **Não use** este código, nem programas compilados a partir dele, em servidores oficiais ou de terceiros sem
  autorização, nem para trapacear, burlar proteções ou prejudicar outros jogadores.
- O código é oferecido **"no estado em que se encontra"**, sem garantia de nenhum tipo. Quem compilar e executar o
  resultado faz isso por sua conta e risco.

## 5. Direitos sobre o código reconstruído

**Nenhuma licença é concedida** sobre o código reconstruído do jogo (tudo o que não é biblioteca de terceiros listada
na seção 7). Ele é publicado apenas para leitura e estudo; por isso o repositório não tem um arquivo `LICENSE`
concedendo direitos de uso, cópia, modificação ou redistribuição. As ferramentas e a documentação escritas para o
projeto seguem a mesma regra.

### Pedidos de remoção

Se você é titular de direitos sobre o PangYa e quer que algum conteúdo seja retirado, **abra uma issue** neste
repositório no GitHub explicando o pedido. Pedidos legítimos dos detentores de direitos serão atendidos.

## 6. Endereços e textos do programa original presentes no código

O código reconstruído mantém endereços que estão gravados no binário original do 983 (e, em comentários, do 645),
porque o cliente os usa como valores padrão. Nenhum deles é um servidor do projeto. Para testar com um servidor local,
o build tem a chave `JP983_SERVER_CONFIG` e as variáveis `JP983_LOGIN`, `JP983_WEB` e `JP983_WWW` (ver
[docs/COMPILAR.md](docs/COMPILAR.md)).

| Onde no código | Valor | Origem |
|---|---|---|
| `src/projectg/loginunit.cpp` | `157.7.173.48`, portas 10803 (comentário: `211.44.251.73`, porta 10101 do KR 645) | servidor de login do JP 983 (do 645 no comentário) |
| `src/projectg/jp/gamestringmanager.cpp`, `netresourcemanager.cpp`, `pangfbi.cpp` | `157.7.172.65:50007` | servidor web do JP 983 (textos, relatórios) |
| `src/projectg/jp/extraresource.cpp`, `commonutil.cpp` | `dl.pangya.jp` (e um ramo morto com `192.168.81.237:8888`) | atualização do JP 983; o IP privado é um texto do binário original |
| `taskmain.cpp`, `lobbymain.cpp`, `checkoutdlg.cpp`, `giftdlg.cpp`, `taskmanager.cpp`, `jp/webpageconnector.cpp`, `netresourcemanager.cpp` | `www.pangya.jp`, `www3.pangya.jp`, `www5.pangya.jp` | páginas web do JP 983 abertas pelo cliente |
| `logindlg.cpp`, `lobbymain.cpp`, `rssmanager.cpp`, `secondarypassword.cpp`, `ghostmanager.cpp`, `ingameguildmyroomdlg.cpp` | `qa.*.gametree.co.kr` | textos herdados do código do KR 645 |
| `ggc_dlg.cpp`, `guilddlg.cpp`, `ppl.cpp` | `pangya.ntreev.com`, `kwanny.ntreev.net`, `www.hjwon.com` | textos do binário original |
| `src/projectg/ggc_helper.cpp` | `game1@inca.co.kr` | contato de suporte do GameGuard numa mensagem original |
| `include/jp/refresh/…` | `e:\program_code\server_client_launcher\…` | caminhos de compilação gravados no binário original |

Os relatórios em `out/` que listam endereços internos do 983 (`out/V5/rede_983.tsv`) tiveram esses IPs privados
trocados por `<IP interno do 983>`.

## 7. Bibliotecas de terceiros incluídas

Estas bibliotecas vêm com o seu próprio código-fonte e **continuam sob as suas próprias licenças**, indicadas nos
arquivos de cada uma. A lista abaixo é um guia; vale sempre o texto de licença que está no próprio arquivo.

| Biblioteca | Onde | Licença (conforme os arquivos) |
|---|---|---|
| zlib 1.2.2 | `src/fresh/third_party/zlib-1.2.2/` | licença zlib |
| libpng 1.2.8 | `src/fresh/third_party/libpng-1.2.8/` | licença libpng |
| FreeType 2.2.1 | `src/engine/lib/freetype-2.2.1/` | FreeType License (FTL) ou GPL v2, à escolha |
| Lua 5.1 | `src/shared/LuaSystem/Lua/` | licença MIT (arquivo `COPYRIGHT`) |
| LuaTinker (Kwon-il Lee) | `src/shared/LuaSystem/lua_tinker/` | conforme o aviso no cabeçalho (o `Licence.txt` original não acompanha) |
| miniLZO (Markus F. X. J. Oberhumer) | `src/shared/minilzo/` | GNU GPL v2 |
| MersenneTwister.h 1.1 (Richard J. Wagner; algoritmo de Matsumoto e Nishimura) | `src/shared/mtrand1p1.h` | licença BSD de 3 cláusulas (no cabeçalho) |
| Mersenne Twister (Matsumoto e Nishimura, versão 1997) | `src/projectg/randomhouse.cpp` | GNU Library GPL v2 ou posterior (no cabeçalho) |
| TinyXML (Lee Thomason) | `src/projectg/tinyxml*`, `src/projectg/jp/rftinyxml*`, `include/jp/refresh/tinyxml/` | licença zlib |
| KMlocal 1.7.2 (David Mount; inclui partes da ANN) | `src/projectg/jp/km*.cpp`, `src/projectg/jp/kc*.cpp`, `include/jp/kmlocal/` | GNU GPL v2 (no cabeçalho) |
| XUnzip 1.3 (Lucian Wischik; zlib 1.1.3 e minizip 0.15) | `src/engine/xunzip.cpp` | conforme os avisos de zlib/minizip no arquivo |
| rugburn (John Chadwick) — trecho para conferência | `out/V5/rugburn_jp983_trecho.c` | licença ISC (aviso no arquivo) |

Essas bibliotecas fazem parte do programa original (que as ligava estaticamente) ou são usadas pelas ferramentas de
conferência. A presença delas não muda a regra da seção 5 para o restante do código.

---

## English summary

- **Independent preservation and study project**, non-commercial. It reconstructs, from the binary, the C++ source of
  the PangYa JP.R7.983.00 client (2017) to document how it works.
- **No affiliation** with Ntreev Soft, Kakao Games, Gungho, Gametree or any PangYa developer or publisher. PangYa and
  related trademarks belong to their respective owners.
- **No game files are included**: no original executables or DLLs, no `.pak`/`.iff`, images, models, sounds, music,
  video or game text, and no player data. Anyone who wants to use the code needs their own, legally obtained client.
- **Do not use** it on official or third-party servers without permission, nor for cheating.
- **No license is granted** over the reconstructed game code; it is published for reading and study only (there is no
  `LICENSE` file). Third-party libraries listed in section 7 keep their own licenses.
- **Takedown requests** from rights holders will be honored: please open an issue on this GitHub repository.
