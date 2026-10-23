# Frente C (V3…V6). Incluído pelo Makefile com `-include Makefile.C`.
#   make layoutcheck      V3: cada unidade + include/asserts/<unidade>.h com cl /Zs (build/C) -> out/V3/layoutcheck.tsv
#                         (U="filtro ..." confere só alguns cabeçalhos; sai com erro se algum static_assert falha;
#                         sem filtro, refaz também out/V3/falhas_ctor.tsv — alcance do construtor do 983 em cada sizeof que falha)
#   make layout-gen       V3: refaz out/V3/sizes_*.tsv (exe 983 e nossos .obj; OBJS=build/pg/obj + build/B/obj), anot.tsv e os include/asserts/*.h
#                         (V7: as unidades de src/projectg/jp/units.txt entram nos dois alvos — tools/v3/jpunits.py)
#   make v4              V4: pacotes e .iff do exe 983 × nosso fonte/.obj (tools/v4; só leitura, ~15 s) -> out/V4/*.tsv
#   make pkt-sizeof      C-PKT: sizeof dos blocos lidos pelos despachantes, medido pelo compilador (tools/pkt/sz.py; cl /Zs, ~40 s)
#                         -> out/V4/sizeof_fonte.tsv, que o rx.py do `make v4` usa para conferir o TAMANHO de cada DecodeBuffer
#   make v5              V5: patches do rugburn × exe 983, APIs interceptadas, rede e constantes de partida (tools/v5; só leitura, ~15 s) -> out/V5/*.tsv
#   make v6-link         V6/F4: o exe liga? símbolos citados pelos .obj (A + B) que nenhum .obj/.lib define, visões com o
#                         mesmo endereço já definido sob outro nome e LNK2005 (tools/v6/simbolos.py; só leitura, ~20 s) -> out/V6/link/
#   make f4-link         F4: link de PROVA do exe com o link.exe do VS2010 e /FORCE (refaz o v6-link antes; tools/v6/linkprova.py;
#                         ~1 min) -> build/C/f4/ProjectG_983_prova.exe (NÃO roda: símbolo que falta vira chamada a 0) e out/F4/link/
#   make f4-portoes      F4: portões A1–A6 do out/V6/ROTEIRO.md (refaz o v5 antes; tools/v6/portoes.py; ~30 s; compila o
#                         ggc_wrapper.cpp com CL=/DJP983_SEM_GAMEGUARD em build/C/f4/gg/, fora de build/pg*) -> out/F4/portoes.tsv
#   make f4-terc         F4: zlib 1.2.2 + libpng 1.2.8 do rebang recompiladas com o VS2010 (/MD /Gr; tools/v6/terc.py; ~5 s)
#                         -> build/C/f4/terc/{zlib,libpng}.lib (as do rebang são VC7.1 e citam __iob, que o msvcr100 não tem)
#   make f4-stubs        F4: stubs para os não resolvidos do f4-link (refaz o f4-link antes; tools/v6/stubs.py; ~1 min) ->
#                         build/C/f4/stubs/stubs983.obj (/alternatename: o símbolo real, quando existir, ganha sozinho),
#                         out/F4/stubs.tsv e stubs_resumo.txt; depois liga SEM /FORCE com stubs + terc -> build/C/f4/ProjectG_983_stubs.exe
#                         e out/F4/link_stubs/ (linkprova.py --stubs)
#   make exe             C-F4.4: f4-stubs + ggc_wrapper.obj com JP983_SEM_GAMEGUARD (portoes.py --so-a2) + link --exe SEM /FORCE
#                         -> build/C/f4/ProjectG_983.exe (+ .map/.log), out/F4/exe/; falta_exe.py -> out/F4/FALTA.md e falta_exe.tsv
#                         (stubs por frente/passo, os alcançados pelo .CRT$XCU e pelo WinMain); portoes.py -> A1–A5 (~4 min)
#                         C-F4.5: + tools/v6/f4stub/mss32_983.asm no link; A5 = imports × exports das dlls reais (tools/v6/f4dll);
#                         entrega.py copia para out/F4/entrega/ SÓ com todos os portões ok (portão fechado = make exe falha)
#                         C-F4.6: mss32_983.asm saiu (C82.1 da A); + f4-ijl15 e portão A6; a entrega leva ijl15_teste.dll e os .bat
#                         C-F4.8 (C85): entrega.py gera também out/F4/entrega/www_teste/patch/updatelist (ver f4-updatelist)
#   make f4-updatelist   C-F4.8 (pedido C85): out/F4/updatelist_web_local_original (a lista que o web local do PC serve) com a
#                         linha ProjectG.exe trocada (fcrc int32 com sinal = CRC do jogo, tools/v6/crc983.py — C86: NÃO é o zlib; fsize), recifrada (XTEA 16
#                         rodadas, chave do 983 00d3d60c) e conferida decifrando de volta -> out/F4/entrega/www_teste/patch/updatelist
#                         + out/F4/updatelist_resumo.txt (tools/v6/updatelist.py; <1 s; `dec` decifra uma lista para .xml)
#   make f4-ijl15        C-F4.6: ijl15_teste.dll = rugburn PÚBLICO (build/C/v5/rugburn) com o VS2010, SEM patch de endereço
#                         fixo (tools/v6/ijl15teste/build.sh; ~30 s) -> build/C/f4/ijl15teste/ (o ijl15 do cliente é de terceiro
#                         e escreve em endereços do exe original)
#   make exe ENTREGA=out/F4/entregas/<id> [V6_PG="pg-a168"] [V6_SEM=...] [V6_BOBJ=build/B/obj]
#                        C-ROBO (C94): exe de teste de QUALQUER frente sem pisar no da C: link/stubs/gg em build/f4e/<id>/,
#                         relatórios em build/f4e/<id>/out/ (portoes.txt, FALTA.md, exe/resumo.txt), entrega (exe + ijl15 +
#                         updatelist + .bat + MD5.txt + 3 resumos) em ENTREGA (fora do git). V6_PG = build(s) da A preferida(s)
#                         (senão vale o .obj mais novo de cada unidade). NÃO refaz terc/ijl15teste/mss32x (compartilhados, da C).
#                         Guarda só as 6 build/f4e/* mais novas. Depois: pedido ao robô com entrega=<ENTREGA> (fila_teste/LEIAME.md)
#   make v6              V6: prontidão do exe por passo do roteiro de teste (tools/v6; só leitura, ~5 s; junta comparador, V3 e V4) -> out/V6/PRONTIDAO.md
OBJS ?= build/pg-s58b/obj
# C-ROBO (C94): ENTREGA=out/F4/entregas/<id> -> pastas próprias da rodada (tools/v6/f4cfg.py lê as variáveis)
ifneq ($(strip $(ENTREGA)),)
F4ID := $(notdir $(patsubst %/,%,$(ENTREGA)))
ifeq ($(filter out/F4/entregas/%,$(patsubst $(ROOT)/%,%,$(abspath $(ROOT)/$(ENTREGA)))),)
$(error ENTREGA=$(ENTREGA): use out/F4/entregas/<id> (a out/F4/entrega é da C, sem ENTREGA=))
endif
override ENTREGA := $(abspath $(ROOT)/$(ENTREGA))
export ENTREGA
export F4_BUILD := $(ROOT)/build/f4e/$(F4ID)
export F4_OUT := $(F4_BUILD)/out
export V6_OUT := $(F4_OUT)/v6link
F4_TERC := f4-comp
F4_IJL := f4-comp
else
F4_TERC := f4-terc
F4_IJL := f4-ijl15
endif
# Sem isto, com o Makefile.C mais novo que o Makefile, a regra embutida `%: %.C` (C++) faz o make tentar
# "compilar" o Makefile a partir deste arquivo (g++ Makefile.C -o Makefile) e todo `make` falha. Regra vazia = não refazer.
Makefile: ;
.PHONY: layoutcheck layout-gen v4 v5 v6 v6-link pkt-sizeof f4-link f4-portoes f4-terc f4-stubs f4-ijl15 f4-updatelist exe f4-comp
layoutcheck:
	@python3 $(ROOT)/tools/v3/layoutcheck.py -j8 $(U); rc=$$?; [ -n "$(U)" ] || python3 $(ROOT)/tools/v3/ctor_max.py; exit $$rc
layout-gen:
	@python3 $(ROOT)/tools/v3/sizes983.py $(ROOT)/out/V3
	@python3 $(ROOT)/tools/v3/sizes_obj.py $(ROOT)/out/V3 --objs $(OBJS)
	@python3 $(ROOT)/tools/v3/anot.py $(ROOT)/out/V3
	@python3 $(ROOT)/tools/v3/gen.py $(ROOT)/out/V3
v4:
	@python3 $(ROOT)/tools/v4/pk.py 983 nosso cmp
	@python3 $(ROOT)/tools/v4/rx.py
	@python3 $(ROOT)/tools/v4/ids.py
	@python3 $(ROOT)/tools/v4/iff.py
pkt-sizeof:
	@python3 $(ROOT)/tools/pkt/sz.py
v5:
	@python3 $(ROOT)/tools/v5/rb.py
v6:
	@python3 $(ROOT)/tools/v6/prontidao.py
v6-link:
	@python3 $(ROOT)/tools/v6/simbolos.py
f4-link: v6-link
	@python3 $(ROOT)/tools/v6/linkprova.py
f4-portoes: v5
	@python3 $(ROOT)/tools/v6/portoes.py
f4-terc:
	@python3 $(ROOT)/tools/v6/terc.py
f4-stubs: f4-link $(F4_TERC)
	@python3 $(ROOT)/tools/v6/stubs.py
	@python3 $(ROOT)/tools/v6/linkprova.py --stubs
f4-comp:
	@for f in terc/zlib.lib terc/libpng.lib ijl15teste/ijl15_teste.dll mss32x.lib ws2_32.lib; do \
	  [ -f $(ROOT)/build/C/f4/$$f ] || { echo "f4-comp: falta build/C/f4/$$f (compartilhado: pedir à C um make exe)"; exit 1; }; done
	@mkdir -p $(F4_BUILD) $(F4_OUT); touch $(F4_BUILD); ls -dt $(ROOT)/build/f4e/*/ | tail -n +7 | xargs -r rm -rf
	@echo "f4-comp: rodada $(F4ID): build $(F4_BUILD), entrega $(ENTREGA) (V6_PG=$(V6_PG) V6_SEM=$(V6_SEM))"
f4-ijl15:
	@$(ROOT)/tools/v6/ijl15teste/build.sh
f4-updatelist:
	@python3 $(ROOT)/tools/v6/updatelist.py troca $(ROOT)/out/F4/updatelist_web_local_original $(ROOT)/out/F4/entrega/ProjectG_nosso.exe $(ROOT)/out/F4/entrega/www_teste/patch/updatelist $(ROOT)/out/F4/updatelist_resumo.txt
exe: f4-stubs $(F4_IJL)
	@python3 $(ROOT)/tools/v6/portoes.py --so-a2
	@python3 $(ROOT)/tools/v6/linkprova.py --exe
	@python3 $(ROOT)/tools/v6/falta_exe.py
	@python3 $(ROOT)/tools/v6/portoes.py
	@python3 $(ROOT)/tools/v6/entrega.py
