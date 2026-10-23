# F3.5 (sessao 54): ids de IsLocalContent do 983 nas chamadas em asm "naked" (mov ecx, N + call rb_IsLocalContent), que os ajustes
# da s53 nao alcancavam (la so as chamadas em C++). Mesma tabela da s53 (out/F3.5/s53/lc): +1 de 0x15 a 0x66, -1 em 0x71/0x72/0x76,
# -3 de 0x7d a 0x87. Duas formas no fonte: `mov ecx, 58h` e `_emit 0xb9 ; mov ecx, 58h` + 4 bytes em _emit.
# A troca marca a linha com "983: era"; linha marcada nao e trocada de novo. Lido por tools/f32/ajustes.py no fim.
import re as _re, glob as _glob, os as _os
def lc983(n):
    if 0x15 <= n <= 0x66: return n + 1
    if n in (0x71, 0x72, 0x76): return n - 1
    if 0x7d <= n <= 0x87: return n - 3
    return n
_ECX = _re.compile(r'(mov|lea|pop|xor|movzx|add|sub|and|or)\s+ecx\b')
_MOV = _re.compile(r'^(\s*)mov ecx, ([0-9A-Fa-f]+h|[0-9]+)(\s*)$')
_EMI = _re.compile(r'^(\s*_emit 0xb9\s*; mov ecx, )([0-9A-Fa-f]+h|[0-9]+)(\s*)$')
def _num(t): return int(t[:-1], 16) if t.endswith('h') else int(t)
def _fmt(n, como): return ('%02Xh' % n if n < 0xa0 else '0%02Xh' % n) if como.endswith('h') else str(n)
LC_NAKED = []   # (arquivo, linha, de, para, forma): preenchido ao aplicar, para o relatorio
def lc_naked_texto(s, arq=''):
    L = s.split('\n')
    for i, l in enumerate(L):
        if not _re.search(r'^\s*call\s+rb_IsLocalContent\b', l): continue
        for k in range(1, 12):
            if i - k < 0: break
            t = L[i - k].rstrip('\r'); b = t.strip()
            m = _MOV.match(t)
            if m:
                n = _num(m.group(2)); r = lc983(n)
                if r != n:
                    L[i - k] = '%smov ecx, %s ; 983: era %s' % (m.group(1), _fmt(r, m.group(2)), m.group(2)) + ('\r' if L[i - k].endswith('\r') else '')
                    LC_NAKED.append((arq, i - k + 1, n, r, 'mov'))
                break
            m = _EMI.match(t)
            if m:
                n = _num(m.group(2)); r = lc983(n); e = L[i - k + 1].rstrip('\r')
                if r != n and _re.match(r'^\s*_emit 0x%02x\s*$' % n, e) and n < 0x100:
                    L[i - k] = '%s%s (983: era %s)' % (m.group(1), _fmt(r, m.group(2)), m.group(2)) + ('\r' if L[i - k].endswith('\r') else '')
                    L[i - k + 1] = e.replace('0x%02x' % n, '0x%02x' % r) + ('\r' if L[i - k + 1].endswith('\r') else '')
                    LC_NAKED.append((arq, i - k + 1, n, r, 'emit'))
                break
            if _re.match(r'^_emit 0x[0-9a-f]{2}$', b): continue   # bytes do imediato
            if _ECX.match(b) or '983: era' in b or b.endswith(':') or b.startswith(('call', 'j', 'ret', 'case ', '_emit', '}', '{')): break
    return '\n'.join(L)
_R = ROOT   # posto por ajustes.py antes do exec
NEW22 = []
for _p in sorted(_glob.glob(_os.path.join(_R, 'src/projectg/*.cpp'))):
    if 'rb_IsLocalContent' in open(_p, encoding='latin-1').read():
        _a = _os.path.relpath(_p, _R)
        NEW22.append(('renum', _a, _a, '\0nunca', r'(?s)\A.*\Z', (lambda a: lambda m: lc_naked_texto(m.group(0), a))(_a),
                      '983: ids de IsLocalContent nas chamadas naked (mov ecx, N)'))

# ---- FxInterpreter do 983: objeto por dono (new 0x1e0 + construtor 0088e520(pet, n)), nao mais o global do 645 ----
# RTTI da vtable 00d34928: FxInterpreter : CFxKeeper (2 slots: destrutor 0088e830, EmptyFx 00884e10). 9 donos criam o seu
# (tools/f35/fxicalls.py): CGolfCaddie +0x74, CMascot +0x7c, CScreen +0x4d0, 00740dd5 +0x20, ntAvatar, particle, 00877f9d +0x548 e 2 da UI RF.
_FH = 'src/projectg/fxinterpreter.h'
_FC = 'src/projectg/fxinterpreter.cpp'
_CH = 'src/projectg/golfcadie.h'
_CC = 'src/projectg/golfcadie.cpp'
_MH = 'src/projectg/mascot.h'
_MC = 'src/projectg/mascot.cpp'
_SH = 'src/projectg/gui_control.h'
_SC = 'src/projectg/gui_control.cpp'
NEW22 += [
 ('sub', _FH, '#include <list>\n\nstruct Attacher;\n\nclass FxInterpreter\n{\n\tfriend FxInterpreter* GetFxInterpreter();\n',
  '#include <list>\n#include <map>\n#include <string>\n#include <vector>\n#include "fxbox.h"\n\nstruct Attacher;\nclass WPuppet;\n\n'
  '// 983: a classe tem 0x1e0 bytes, deriva de CFxKeeper e cada dono cria a sua (construtor 0088e520). Os membros abaixo saem do\n'
  '// construtor (tamanho do no de cada arvore/lista); nomes e tipos de valor sao provisorios. O corpo da unidade do 983\n'
  '// (0087f2d0..0088e8b0) ainda nao foi escrito: so o construtor, DetachFx e DetachFxAll. As funcoes do 645 seguem abaixo com o\n'
  '// sufixo 645 e a lista antiga como membro estatico, ate a unidade ser portada (F3.7).\n'
  'class FxInterpreter : public CFxKeeper\n{\n\tfriend FxInterpreter* GetFxInterpreter();\n',
  '983: FxInterpreter : CFxKeeper (RTTI da vtable 00d34928)'),
 ('sub', _FH, 'protected:\n\tFxInterpreter();\n\npublic:\n\tvirtual ~FxInterpreter();\n\n'
  '\tint ParseBoundingBoxScript_fx(WPuppet* pet, eScripFormat format);\n',
  'public:\n\tFxInterpreter(WPuppet* pet, int n); // 983: 0088e520\n\tvirtual ~FxInterpreter();\n'
  '\tvirtual void EmptyFx(void* fx); // 983: 00884e10 (slot 1; corpo nao escrito)\n\n'
  '\tint ParseBoundingBoxScript_fx(WPuppet* pet); // 983: 0088e860, 1 argumento (corpo nao escrito)\n'
  '\tvoid SetUnk983_1cc(int v); // 983: 0088c460 (corpo nao escrito)\n'
  '\tvoid DetachFx(int id); // 983: 00889df0\n\tvoid DetachFxAll(int kind = -1); // 983: 0088c420\n\n'
  '\t// 645 (global; sem par no 983)\n\tint ParseBoundingBoxScript_fx(WPuppet* pet, eScripFormat format);\n',
  '983: construtor publico de 2 argumentos; DetachFxAll(int), ParseBoundingBoxScript_fx(pet)'),
 ('sub', _FH, '\tvoid DetachFx(int id);\n\tvoid DetachFxAll();\n\nprotected:\n',
  '\tvoid DetachFx645(int id);\n\tvoid DetachFxAll645();\n\nprotected:\n'
  '\t// 983: auxiliares chamados pelo construtor e pelos Detach (corpos nao escritos; nomes pelo endereco)\n'
  '\tvoid Init983(); // 0088c6b0\n\tvoid Unk983_880d40(WPuppet* pet);\n\tvoid Unk983_87f2d0(WPuppet* pet);\n'
  '\tvoid DetachA983(int kind); // 0088b140\n\tvoid DetachB983(int kind); // 00887cb0\n\tvoid DetachC983(int kind); // 0088b8d0\n'
  '\tvoid DetachSlot983(int id, int slot); // 00888f00\n',
  '983: Detach do 645 renomeados; auxiliares do 983 declarados'),
 ('sub', _FH, '\tstd::list<sFxInfo> m_fxList;\n\tint m_nextID;\n};',
  '\tstatic std::list<sFxInfo> ms_fxList645; // 645: era membro (m_fxList); fora do objeto para o sizeof ser o do 983\n'
  '\tstatic int ms_nextID645; // 645: era m_nextID\n'
  '\tstatic int ms_count983; // 983: 00e7d634, somado no fim do construtor\n\n'
  '\tstruct sUnk983_8 { int a, b; };\n\tstruct sUnk983_c { int a, b, c; };\n\tstruct sUnk983_10 { int a, b, c, d; };\n'
  '\tstruct sUnk983_24 { int a[9]; };\n'
  '\tstd::vector<void*> m_unk983_08[2]; // 0x08: 2 x 0x10 (construtor 00448780 zera 3 ponteiros)\n'
  '\tstd::map<int, sUnk983_c> m_unk983_28[4]; // 0x28: 4 arvores, no de 0x20 (0088c4b0)\n'
  '\tstd::list<unsigned long> m_unk983_68[4]; // 0x68: 4 listas, no de 0xc (005b51c0)\n'
  '\tstd::map<int, sUnk983_8> m_unk983_98; // 0x98: no de 0x1c\n'
  '\tstd::map<int, sUnk983_24> m_unk983_a8[4]; // 0xa8: no de 0x38 (0088c520)\n'
  '\tstd::map<int, sUnk983_24> m_unk983_e8[4]; // 0xe8: idem\n'
  '\tstd::list<sUnk983_8> m_unk983_128; // 0x128: no de 0x10\n'
  '\tstd::map<int, sUnk983_10> m_unk983_134; // 0x134: no de 0x24\n'
  '\tstd::list<sUnk983_8> m_unk983_144; // 0x144: no de 0x10\n'
  '\tWPuppet* m_pPet983; // 0x150: 1o argumento do construtor\n'
  '\tint m_unk983_154; // 0x154: 2o argumento + 1; DetachFxAll(-1) volta a 1\n'
  '\tint m_unk983_158; // 0x158: 1\n'
  '\tstd::string m_unk983_15c[4]; // 0x15c\n'
  '\tint m_unk983_1cc; // 0x1cc: nao tocado pelo construtor; comparado e gravado por 0088c460\n'
  '\tstd::map<int, std::string> m_unk983_1d0; // 0x1d0: no de 0x30; sizeof 0x1e0\n};',
  '983: layout do FxInterpreter pelo construtor 0088e520 (sizeof 0x1e0 = push em 0073a6ab)'),
 ('sub', _FC, 'FxInterpreter* GetFxInterpreter()\n{\n\tstatic FxInterpreter fxInterpreter;\n',
  'std::list<FxInterpreter::sFxInfo> FxInterpreter::ms_fxList645;\nint FxInterpreter::ms_nextID645;\nint FxInterpreter::ms_count983;\n\n'
  '// 645: global. No 983 cada dono cria o seu; fica so para as chamadas naked que ainda o usam (gui_control.cpp).\n'
  'FxInterpreter* GetFxInterpreter()\n{\n\tstatic FxInterpreter fxInterpreter(NULL, 0);\n',
  '983: sem FxInterpreter global (o do 645 fica para as chamadas naked)'),
 ('sub', _FC, 'FxInterpreter::FxInterpreter()\n{\n\tm_nextID = 0;\n}\n\nFxInterpreter::~FxInterpreter()\n{\n\tif (!m_fxList.empty())\n\t\tDetachFxAll();\n}\n',
  '// 983: 0088e520\nFxInterpreter::FxInterpreter(WPuppet* pet, int n)\n{\n\tm_pPet983 = pet;\n\tm_unk983_154 = n + 1;\n\tm_unk983_158 = 1;\n'
  '\tInit983();\n\tUnk983_880d40(pet);\n\tif (pet)\n\t\tUnk983_87f2d0(pet);\n\tms_count983++;\n}\n\n'
  '// 983: o destrutor e 0088dee0 (nao escrito); este e o do 645\nFxInterpreter::~FxInterpreter()\n{\n\tif (!ms_fxList645.empty())\n\t\tDetachFxAll645();\n}\n\n'
  '// 983: 00889df0\nvoid FxInterpreter::DetachFx(int id)\n{\n\tfor (int i = 0; i < 4; i++)\n\t\tDetachSlot983(id, i);\n}\n\n'
  '// 983: 0088c420\nvoid FxInterpreter::DetachFxAll(int kind)\n{\n\tDetachA983(kind);\n\tDetachB983(kind);\n\tDetachC983(kind);\n'
  '\tif (kind == -1)\n\t\tm_unk983_154 = 1;\n}\n',
  '983: construtor 0088e520, DetachFx 00889df0, DetachFxAll 0088c420'),
 ('todos', _FC, 'void FxInterpreter::DetachFx(int id)\n{\n\tif (id < 0)', 'void FxInterpreter::DetachFx645(int id)\n{\n\tif (id < 0)', '645: DetachFx -> DetachFx645'),
 ('todos', _FC, 'void FxInterpreter::DetachFxAll()\n', 'void FxInterpreter::DetachFxAll645()\n', '645: DetachFxAll -> DetachFxAll645'),
 ('todos', _FC, 'm_fxList', 'ms_fxList645', '645: m_fxList -> estatico'),
 ('todos', _FC, 'm_nextID', 'ms_nextID645', '645: m_nextID -> estatico'),
 # donos
 ('sub', _CH, '\tvoid* m_pUnk983_74;             // 983: ponteiro novo = objeto de 0x1e0 bytes criado no construtor (operator new + 0088e520(0, 0); a mesma classe do CScreen +0x4d0). Classe não identificada; o nosso construtor NÃO o cria\n',
  '\tFxInterpreter* m_pFxInterpreter983; // 983: 0x74 = new FxInterpreter(NULL, 0) no fim do construtor (0073a6ab..0073a6d4)\n',
  '983: CGolfCaddie +0x74 e o FxInterpreter do caddie'),
 ('sub', _CH, '#include "scenemanager.h"\n', '#include "scenemanager.h"\n#include "fxinterpreter.h"\n', '983: o construtor em linha cria o FxInterpreter'),
 ('sub', _CH, '\tCGolfCaddie()\n\t{\n', '\tCGolfCaddie()\n\t\t: m_bVisible(true), m_pRing(0), m_pCaddieTalk(0) // 983: gravados antes de construir o map de 0xac (0073a63e)\n\t{\n',
  '983: construtor do CGolfCaddie: os 3 membros na lista de inicializacao'),
 ('sub', _CH, '\t\tm_pRing = 0;\n\t\tm_pCaddieTalk = 0;\n\t\tm_bVisible = true;\n\t}',
  '\t\tm_pFxInterpreter983 = new FxInterpreter(NULL, 0);\n\t}',
  '983: construtor do CGolfCaddie (0073a5d0) cria o FxInterpreter'),
 ('todos', _CC, 'GetFxInterpreter()->ParseBoundingBoxScript_fx(\n\t\t\t\tm_pCaddie->m_pBody->GetPet(), FxInterpreter::eSF_FX);',
  'm_pFxInterpreter983->ParseBoundingBoxScript_fx(\n\t\t\t\tm_pCaddie->m_pBody->GetPet());', '983: 0073bc0f, 1 argumento'),
 ('todos', _CC, 'GetFxInterpreter()->', 'm_pFxInterpreter983->', '983: FxInterpreter do caddie (+0x74: 0073b6b4, 0073bbf6, 0073bd05)'),
 ('sub', _MH, '#include "npc.h"\n', '#include "npc.h"\n#include "fxinterpreter.h"\n', '983: o construtor do CMascot cria o FxInterpreter'),
 ('sub', _MH, '\tCMascot() { }\n\n\tsMascot m_mascot[4];\n\tint m_unk7c;\n};',
  '\tCMascot() { m_pFxInterpreter983 = new FxInterpreter(NULL, 0); } // 983: 00761d47..00761d63\n\n\tsMascot m_mascot[4];\n'
  '\tFxInterpreter* m_pFxInterpreter983; // 983: 0x7c\n\tint m_unk7c; // 983: 0x80 (00761b7e); sizeof 0x84\n};',
  '983: CMascot 0x80 -> 0x84 (FxInterpreter em +0x7c)'),
 ('todos', _MC, 'GetFxInterpreter()->', 'm_pFxInterpreter983->', '983: FxInterpreter do mascote (+0x7c: 00761b74)'),
 ('sub', _SH, '\tvoid* m_pUnk983_4d0; // 983: objeto de 0x1e0 bytes criado no construtor (operator new + 0088e520(0, 0))\n',
  '\tFxInterpreter* m_pFxInterpreter983; // 983: 0x4d0 = new FxInterpreter(NULL, 0) no construtor (00751670)\n',
  '983: CScreen +0x4d0 e o FxInterpreter da tela'),
 ('sub', _SH, '#include "wflag.h"\n', '#include "wflag.h"\nclass FxInterpreter;\n', '983: CScreen tem FxInterpreter*'),
 ('sub', _SC, '\tm_dispPriority = DISP_PRIORITY_4;\n\tAddSkipList(0x400);\n}',
  '\tm_dispPriority = DISP_PRIORITY_4;\n\tm_pFxInterpreter983 = new FxInterpreter(NULL, 0); // 983: 00751670\n\tAddSkipList(0x400);\n}',
  '983: construtor do CScreen cria o FxInterpreter'),
 ('todos', _SC, 'GetFxInterpreter()->ParseBoundingBoxScript_fx(pPuppet,\n\t\tFxInterpreter::eSF_FX);',
  'm_pFxInterpreter983->ParseBoundingBoxScript_fx(pPuppet);', '983: 0074bf3e'),
 ('todos', _SC, 'GetFxInterpreter()->ParseBoundingBoxScript_fx(\n\t\t\t\t\t\t\tpClubSet->pHeadSub[type],\n\t\t\t\t\t\t\t(FxInterpreter::eScripFormat)0);',
  'm_pFxInterpreter983->ParseBoundingBoxScript_fx(\n\t\t\t\t\t\t\tpClubSet->pHeadSub[type]);', '983: 1 argumento'),
 ('todos', _SC, 'GetFxInterpreter()->ParseBoundingBoxScript_fx(\n\t\t\t\tpClubSet->pHeadSub[type], (FxInterpreter::eScripFormat)0);',
  'm_pFxInterpreter983->ParseBoundingBoxScript_fx(\n\t\t\t\tpClubSet->pHeadSub[type]);', '983: 00752d06, 1 argumento'),
 ('todos', _SC, 'GetFxInterpreter()->DetachFx(', 'm_pFxInterpreter983->DetachFx(', '983: FxInterpreter da tela (+0x4d0: 0074dd1e, 00752caf)'),
]

# ---- CScore 0x9c -> 0xa0 e GroundItemMan 0xa34 -> 0xa38 (out/F3.5/s54/raw: votos; construtores 00799f10 e 0085dc70) ----
_SBH = 'src/projectg/scoreboard.h'
_SBC = 'src/projectg/scoreboard.cpp'
_GH = 'src/projectg/grounditemman.h'
_GC2 = 'src/projectg/grounditemman.cpp'
NEW22 += [
 ('sub', _SBH, '\tFrRankFormEx* m_pRankEx;                   // 0x44\n',
  '\tFrRankFormEx* m_pRankEx;                   // 0x44\n'
  '\tvoid* m_pUnk983_48;                        // 983: ponteiro novo, zerado no construtor (00799f10); os membros seguintes andam +4 (votos: 0x48 -> 0x4c, 0x50 -> 0x54, 0x74 -> 0x78, 0x80 -> 0x84). Tipo provisorio\n',
  '983: sizeof(CScore) = 0xa0: ponteiro novo em +0x48'),
 ('sub', _SBC, '\t  m_pRankEx(NULL),\n\t  m_pAward(NULL),\n', '\t  m_pRankEx(NULL),\n\t  m_pUnk983_48(NULL),\n\t  m_pAward(NULL),\n', '983: construtor do CScore zera +0x48'),
 ('sub', _GH, '\tstd::string m_sceneElemName;\n\tPlayerStats* m_pPlayerStats;\n',
  '\tstd::string m_sceneElemName;\n\tint m_unk983_a30; // 983: 4 bytes novos; o construtor nao os toca. Tipo provisorio\n'
  '\tPlayerStats* m_pPlayerStats; // 983: 0xa34 (0085d650); sizeof 0xa38\n',
  '983: sizeof(GroundItemMan) = 0xa38: m_pPlayerStats 0xa30 -> 0xa34'),
 ('sub', _GC2, 'GetContainer((localContentType_t)0xa3,\n\t\tm_pGimmickContainer);\n}',
  'GetContainer((localContentType_t)0x9b, // 983: era 0xa3 (push 0x9b no 0085dc70)\n\t\tm_pGimmickContainer);\n'
  '\tm_dispPriority = DISP_PRIORITY_5; // 983\n\tm_pPlayerStats = NULL; // 983\n}',
  '983: construtor do GroundItemMan (0085dc70): id 0x9b, prioridade 5, m_pPlayerStats = NULL'),
]
