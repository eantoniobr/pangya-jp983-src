# Build do jp983src com o VS2010 SP1 (cl 16.00.40219.01) sob Wine. Saída em build/ (fora do git).
#   make hello            olá: build/hello/hello.dll + hello.exe, e roda o exe
#   make wangreal         build/wangreal/wangreal.dll com os .cpp de WANGREAL_SRC
#   make obj F=src/x.cpp  só compila um arquivo -> build/obj/src/x.obj
#   make cmp F=src/x.cpp  compila e compara cada função com o 983 (tools/cmpfunc; ARGS="--diff Nome" etc.)
#   make pilot            compara os arquivos do piloto F0.5 (PILOT_SRC) com o 983
#   make base             compara os 9 .cpp da dll (BASE_SRC, a partir de src/) com o 983 -> out/base (linha de base F1.1)
#   make cmp-selftest     autoteste do comparador (tools/cmpfunc_selftest.sh)
#   make wangreal-full    wangreal.dll completa (14 .cpp de src/ + recursos) -> build/wangreal-full/wangreal.dll
#   make image            dll completa × 983: PE/imports, código, alvos e dados -> out/image (OUT=dir)
#   make smoke            carrega a nossa dll e a do 983 no Wine, chama os 4 exports e compara a saída
#   make info             versão do cl/link e flags
# ProjectG.exe (F3.2; tools/f32/pgbuild.py, configuração por unidade lida de /root/rebang/build-projectg.json):
#   make pg-import        copia do rebang as unidades .cpp do exe + cabeçalhos para src/ e include/, mescla (3 vias) o que o rebang
#                         mudou nos arquivos que já existem aqui (tools/f32/merge3.py) e aplica tools/f32/ajustes.py
#   make pg-obj           build/atl71 (ATL 7.1 consertado para o cl 16) + 8 pch + as 468 unidades -> build/pg/obj (U="filtro ...")
#   make pg-base          cmpfunc de cada unidade × ref/ProjectG_983_dump.exe -> out/pg-base (OUT=dir): base.tsv, base_resumo.txt
#   make pg-variantes     flags do exe por variantes em 6 unidades da onda 1 -> out/pg-base/variantes.txt
# Painel (P1):
#   make painel           out/painel/index.html (página de artifact) + ponto no histórico; PARGS=--sem-historico ou --reconstruir
# Antes de builds grandes: pgrep -a make; pgrep -a wine (RAM compartilhada; no máximo -j8).
ROOT   := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
VS     ?= /root/kr839/local/vs2010
REBANG ?= /root/rebang
B      := $(ROOT)/build
VSRUN  := VS=$(VS) $(ROOT)/tools/vs.sh

# Flags do 983: as do 645 (build-wangreal.json, sem /G7) + /Ob1, ajustadas na A3 do kr839 contra a dll 839;
# o Rich header da wangreal.dll 983 tem as mesmas ferramentas da 839 (out/F0.2/rich.txt).
# /GF-: o 983 não funde literais de texto iguais (3 cópias de "w%d h%d b%d" na .rdata, na ordem do fonte; sessão 15).
# /Z7 no lugar de /Zi: o mspdb100 não funciona sob Wine (C1902); os símbolos saem no .obj e no .map.
CFLAGS_BASE := /nologo /c /MD /W3 /EHsc /Z7 /O2 /Ob1 /GF- /Gr /GS /Oy- /DNDEBUG /DWIN32 /D_WINDOWS /D_MBCS
INC_SYS := /I$(VS)/VC10/include /I$(VS)/compat /I$(REBANG)/tools/PlatformSDK-Aug2002/include \
           /I$(REBANG)/tools/DirectX9/include
INC     := /I$(ROOT)/include /I$(ROOT)/include/engine /I$(ROOT)/src/shared $(INC_SYS)
CFLAGS  := $(CFLAGS_BASE) $(INC) $(EXTRA)

SDKLIB  := $(REBANG)/tools/PlatformSDK-Aug2002/lib
CRTLIBS := $(VS)/VC10/lib/msvcprt.lib $(VS)/VC10/lib/msvcrt.lib $(VS)/VC10/lib/oldnames.lib
# kernel32 do SDK 7.1 (o de 2002 não tem EncodePointer/DecodePointer, que o CRT do VS2010 usa)
WINLIBS := $(VS)/sdklib/kernel32.lib $(SDKLIB)/user32.lib $(SDKLIB)/gdi32.lib
LFLAGS  := /NOLOGO /MACHINE:X86 /INCREMENTAL:NO /OPT:REF /OPT:ICF /NODEFAULTLIB

# F3.1: mapa unidade do 645 -> faixa/funções do ProjectG 983 (map/projectg_units.tsv, map/projectg_funcs.tsv)
# F3.3: com as âncoras da linha de base (funções dos nossos .obj achadas no 983); `make units BASE=` refaz o da F3.1
BASE ?= out/F3.4/funcs_all.tsv.gz
units:
	python3 tools/f31/map.py --out $(if $(OUT),$(OUT),$(if $(BASE),out/F3.3,out/F3.1)) --map map $(if $(BASE),--base $(BASE))
# F3.3: mapa forte do exe (nome decorado -> VA no 983) a partir da linha de base
pg-map:
	python3 tools/f33/mkmap.py $(BASE) map/projectg.tsv

pg-ltcg:
	python3 tools/f33/ltcg.py --out out/F3.3
# P1: painel de progresso (só leitura; < 5 s) -> out/painel/index.html + 1 linha em out/painel/historico.jsonl
painel:
	@python3 tools/painel.py $(PARGS)

.PHONY: units pg-map pg-ltcg painel all hello wangreal obj cmp pilot base wangreal-full image smoke difftest cmp-selftest info clean
all: hello wangreal

# regra geral: qualquer .cpp do repositório -> build/obj/<mesmo caminho>.obj (log ao lado)
# todo .obj depende de todos os cabeçalhos do repositório (são poucos; evita .obj velho depois de mexer em .h)
# (só os da dll: src/projectg, src/fresh e terceiros são do exe e têm o build próprio em tools/f32/pgbuild.py)
HDRS := $(shell find $(ROOT)/include $(ROOT)/src/wangreal $(ROOT)/src/engine -maxdepth 2 \( -name '*.h' -o -name '*.inl' \))
$(B)/obj/%.obj: $(ROOT)/%.cpp $(HDRS)
	@mkdir -p $(dir $@)
	@$(VSRUN) cl $(CFLAGS) $(if $(filter src/wangreal/%,$*),$(CFLAGS_device)) /Fo$@ $< > $(@:.obj=.log) 2>&1 \
	  || { echo "FALHOU $*.cpp"; cat $(@:.obj=.log); rm -f $@; exit 1; }
	@echo "cl   $*.cpp"

obj: $(B)/obj/$(F:.cpp=.obj)

# ---- comparador (F0.3) ----
cmp:
	@$(ROOT)/tools/cmpfunc $(F) $(ARGS)
pilot:
	@$(ROOT)/tools/cmpfunc $(PILOT_SRC) $(ARGS)
base:
	@$(ROOT)/tools/cmpfunc $(BASE_SRC) --out $(or $(OUT),$(ROOT)/out/base) $(ARGS)
cmp-selftest:
	@$(ROOT)/tools/cmpfunc_selftest.sh

# ---- olá ----
HELLO := $(B)/hello
hello: $(HELLO)/hello.exe
	cd $(HELLO) && $(VSRUN) run hello.exe
$(HELLO)/hello.dll: $(B)/obj/tools/hello/hello_dll.obj $(ROOT)/tools/hello/hello.def
	@mkdir -p $(HELLO)
	@$(VSRUN) link $(LFLAGS) /DLL /SUBSYSTEM:WINDOWS /DEF:$(ROOT)/tools/hello/hello.def /OUT:$@ /MAP:$(@:.dll=.map) \
	  $< $(WINLIBS) $(CRTLIBS) > $(@:.dll=.link.log) 2>&1 || { cat $(@:.dll=.link.log); exit 1; }
	@echo "link $(notdir $@)"
$(HELLO)/hello.exe: $(B)/obj/tools/hello/hello.obj $(HELLO)/hello.dll
	@$(VSRUN) link $(LFLAGS) /SUBSYSTEM:CONSOLE /OUT:$@ /MAP:$(@:.exe=.map) \
	  $< $(WINLIBS) $(CRTLIBS) > $(@:.exe=.link.log) 2>&1 || { cat $(@:.exe=.link.log); exit 1; }
	@echo "link $(notdir $@)"

# ---- wangreal.dll (device do 645 + bitmap/wdxtc da lib Wangreal) ----
# Lista cresce nas fases F1+. O .def (4 exports) só entra quando device.cpp estiver em WANGREAL_SRC.
# device.cpp e wime/wime.cpp já existem (piloto F0.5) mas só entram no link quando wd3d8/wdinput/wime estiverem
# completos (F2); por enquanto compilam e são comparados com `make cmp`/`make pilot`.
WANGREAL_SRC := src/engine/bitmap.cpp src/wangreal/langtable.cpp
# os 9 .cpp que o 645 tem para a dll, na ordem de link do 983 (map/wangreal_funcs.tsv), todos em src/ desde a F1.1
BASE_SRC     := src/wangreal/shparam.cpp src/wangreal/wd3d.cpp src/wangreal/wd3d8.cpp src/wangreal/wdinput/directinput.cpp \
                src/wangreal/wdinput/dikeyboard.cpp src/wangreal/wdinput/dimouse.cpp src/wangreal/wime/wime.cpp \
                src/wangreal/device.cpp src/engine/wxshadermtl.cpp src/engine/wvdshnames.cpp src/engine/wdxtc.cpp src/engine/wmath.cpp \
                src/engine/bitmap.cpp
PILOT_SRC    := src/wangreal/device.cpp src/wangreal/wime/wime.cpp src/wangreal/langtable.cpp src/engine/bitmap.cpp
# só o projeto device (src/wangreal) tem WANGREAL_DEVICE; src/engine é a lib Wangreal (F2.10)
CFLAGS_device := /DWANGREAL_DEVICE
WANGREAL_OBJ := $(patsubst %.cpp,$(B)/obj/%.obj,$(WANGREAL_SRC))
WANGREAL_DEF := $(if $(filter src/wangreal/device.cpp,$(WANGREAL_SRC)),$(ROOT)/src/wangreal/wangreal.def)
WR := $(B)/wangreal
wangreal: $(WR)/wangreal.dll
$(WR)/wangreal.dll: $(WANGREAL_OBJ) $(WANGREAL_DEF)
	@mkdir -p $(WR)
	@$(VSRUN) link $(LFLAGS) /DLL /SUBSYSTEM:WINDOWS /BASE:0x10000000 $(if $(WANGREAL_DEF),/DEF:$(WANGREAL_DEF)) \
	  /OUT:$@ /MAP:$(@:.dll=.map) $(WANGREAL_OBJ) $(WINLIBS) $(CRTLIBS) > $(@:.dll=.link.log) 2>&1 \
	  || { cat $(@:.dll=.link.log); exit 1; }
	@echo "link $(notdir $@)"

# ---- wangreal.dll completa (F2.10) ----
# Todos os .cpp da dll na ordem de link do 983 + recursos (versão do device.rc do 645 e manifesto do VS2010).
# /OPT:NOREF /OPT:NOICF explícitos (sem /DEBUG o padrão do link é REF+ICF), como o 983 (out/F0.5/RELATORIO.md);
# /DYNAMICBASE:NO: o 983 tem DllCharacteristics 0x100 (só NXCOMPAT). A ordem das libs dá a ordem das dlls na tabela
# de imports do 983 (d3dx9_31, d3d9, imm32, dinput8, winmm, kernel32, user32, msvcp100, msvcr100, gdi32).
# O d3dx9.lib do rebang já importa de d3dx9_31.dll. Sem /DEBUG (o mspdb100 não funciona sob Wine): a dll não tem
# o registro RSDS que a do 983 tem (out/F2.10/RELATORIO.md).
DEVICE_SRC := $(filter src/wangreal/%,$(BASE_SRC))
ENGINE_SRC := src/engine/wxshadermtl.cpp src/engine/wvdshnames.cpp src/engine/bitmap.cpp src/engine/wdxtc.cpp \
              src/wangreal/langtable.cpp src/engine/wmath.cpp
FULL_SRC := $(DEVICE_SRC) $(ENGINE_SRC)
FULL_OBJ := $(patsubst %.cpp,$(B)/obj/%.obj,$(FULL_SRC))
DXLIB    := $(REBANG)/tools/DirectX9/lib
FULL_LIBS := $(DXLIB)/d3dx9.lib $(DXLIB)/d3d9.lib $(DXLIB)/dxguid.lib $(SDKLIB)/imm32.lib $(DXLIB)/dinput8.lib \
             $(SDKLIB)/winmm.lib $(VS)/sdklib/kernel32.lib $(SDKLIB)/user32.lib $(CRTLIBS) $(SDKLIB)/gdi32.lib
RC       := $(REBANG)/tools/VC7.1/bin/rc.exe
WF := $(B)/wangreal-full
WRES := $(B)/obj/src/wangreal/wangreal.res
$(WRES): $(ROOT)/src/wangreal/wangreal.rc $(ROOT)/src/wangreal/wangreal.manifest
	@mkdir -p $(dir $@)
	@cd $(ROOT)/src/wangreal && $(VSRUN) run $(RC) /c949 /fo $@ wangreal.rc > $(@:.res=.rc.log) 2>&1 \
	  || { cat $(@:.res=.rc.log); exit 1; }
	@echo "rc   src/wangreal/wangreal.rc"
wangreal-full: $(WF)/wangreal.dll
$(WF)/wangreal.dll: $(FULL_OBJ) $(WRES) $(ROOT)/src/wangreal/wangreal.def
	@mkdir -p $(WF)
	@$(VSRUN) link $(filter-out /OPT:REF /OPT:ICF,$(LFLAGS)) /OPT:NOREF /OPT:NOICF /DYNAMICBASE:NO /DLL /SUBSYSTEM:WINDOWS \
	  /BASE:0x10000000 /DEF:$(ROOT)/src/wangreal/wangreal.def /OUT:$@ /MAP:$(@:.dll=.map) $(FULL_OBJ) $(WRES) $(FULL_LIBS) \
	  > $(@:.dll=.link.log) 2>&1 || { cat $(@:.dll=.link.log); exit 1; }
	@echo "link $(notdir $@) (completa)"

# comparação da dll ligada inteira com a do 983 (código, alvos, dados) + cabeçalho PE/imports + teste de carga no Wine
image: $(WF)/wangreal.dll
	@mkdir -p $(or $(OUT),$(ROOT)/out/image)
	@python3 $(ROOT)/tools/f210_pe.py $< $(ROOT)/ref/wangreal_983.dll > $(or $(OUT),$(ROOT)/out/image)/pe.txt
	@python3 $(ROOT)/tools/f210_image.py $< $(WF)/wangreal.map $(ROOT)/ref/wangreal_983.dll --out $(or $(OUT),$(ROOT)/out/image) \
	  > $(or $(OUT),$(ROOT)/out/image)/image.log
	@grep -A8 '^# código' $(or $(OUT),$(ROOT)/out/image)/codigo_resumo.txt; cat $(or $(OUT),$(ROOT)/out/image)/dados_resumo.txt
smoke: $(WF)/wangreal.dll
	@$(ROOT)/tools/f210/smoke.sh
# teste diferencial (F2.11): 4 funções internas puras chamadas por RVA na nossa dll e na do 983, mesmas entradas
difftest: $(WF)/wangreal.dll
	@$(ROOT)/tools/f211/difftest.sh

# ---- ProjectG.exe (F3.2) ----
PGOUT := $(or $(OUT),$(ROOT)/out/pg-base)
.PHONY: pg-import pg-atl pg-obj pg-base pg-variantes
pg-import:
	@python3 $(ROOT)/tools/f32/import.py $(PGOUT)
	@python3 $(ROOT)/tools/f32/merge3.py $(PGOUT)/mescla
	@python3 $(ROOT)/tools/f32/ajustes.py $(PGOUT)/mescla
	@python3 $(ROOT)/tools/f32/seed.py
pg-atl:
	@python3 $(ROOT)/tools/f32/atlfix.py $(B)/atl71
pg-obj: pg-atl
	@python3 $(ROOT)/tools/f32/pgbuild.py pch
	@python3 $(ROOT)/tools/f32/pgbuild.py obj $(U) -j8 --out $(PGOUT)
pg-base:
	@python3 $(ROOT)/tools/f32/pgbuild.py cmp $(U) -j8 --out $(PGOUT)
pg-variantes:
	@mkdir -p $(PGOUT)
	@$(ROOT)/tools/f32/variantes.sh $(PGOUT)/variantes.txt projectg/golfdoc.cpp projectg/tinyxml.cpp projectg/ball.cpp \
	  projectg/pool.cpp fresh/source/frlistbox.cpp engine/woverlay.cpp

info:
	@$(VSRUN) cl 2>&1 | head -1; $(VSRUN) link 2>&1 | head -1
	@echo "CFLAGS_BASE = $(CFLAGS_BASE)"; echo "LFLAGS = $(LFLAGS)"

clean:
	rm -rf $(B)/obj $(B)/hello $(B)/wangreal

# F3.4: votos de deslocamento de campo (.obj do exe × 983) por classe; ranking e degraus em $(VOUT)
VOUT ?= out/pg-votos
pg-votes:
	@python3 $(ROOT)/tools/f34/votes.py all $(VOUT)/raw -j 8 $(U)
	@python3 $(ROOT)/tools/f34/votes.py sum $(VOUT)/raw $(VOUT)/votos.tsv
	@python3 $(ROOT)/tools/f34/resumo.py $(VOUT)/raw $(VOUT) atual

# Frente C (V3…V6): alvos em Makefile.C
-include Makefile.C

# Frente B (F3.7): alvos em Makefile.B
-include Makefile.B
