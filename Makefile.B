# Frente B (F3.7 — sistemas novos do JP). Incluído pelo Makefile com `-include Makefile.B`.
#   make jp        compila as unidades de src/projectg/jp/units.txt -> build/B/obj (tools/f37/jpbuild.py)
#   make jp-cmp    cmpfunc de cada uma contra o exe 983 -> $(JPOUT)/cmp/<unidade>/
#   make jp-mapa   refaz as fronteiras de unidade dos vãos novos (F3.7.1) em $(JPOUT)
JPOUT ?= out/F3.7/jp-base
.PHONY: jp jp-cmp jp-mapa
jp:
	@python3 $(ROOT)/tools/f37/jpbuild.py obj -j8 --out $(JPOUT)
jp-cmp: jp
	@python3 $(ROOT)/tools/f37/jpbuild.py cmp -j8 --out $(JPOUT)
jp-mapa:
	@test -s $(ROOT)/build/B/refs.tsv || python3 $(ROOT)/tools/f37/refs.py
	@python3 $(ROOT)/tools/f37/inits.py
	@python3 $(ROOT)/tools/f37/unidades.py --out $(JPOUT)
	@python3 $(ROOT)/tools/f37/sistemas.py $(JPOUT)
