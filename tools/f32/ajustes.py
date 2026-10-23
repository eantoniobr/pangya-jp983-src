#!/usr/bin/env python3
# F3.2: ajustes aplicados aos arquivos importados do rebang (tools/f32/import.py chama no fim). Cada ajuste é uma troca de
# texto exata com o motivo; texto não achado = erro (o rebang mudou: rever o ajuste). Relatório em <out>/ajustes.tsv.
# Tipos: ('sub', arquivo, antes, depois, motivo) | ('corte', arquivo, marca_inicial, marca_final_inclusive, depois, motivo)
#        ('todos', glob, antes, depois, motivo)  aplica onde o texto existir (conta os arquivos)
import os, sys, glob, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
WISZERO = "inline int WisZero(const float& f, float epsilon = g_EPSILON)\n{\n\treturn Wabs(f) < epsilon;\n}\n"
AJ = [
 ('corte', 'src/projectg/stdafx.h', '#ifndef REBANG_SEMANTIC_ONLY\n// HACK: RotMat only differs',
  '\t\treturn WMatrix(c, 0.0f, s, 0.0f, 1.0f, 0.0f, -s, 0.0f, c);\n\t}\n}\n#endif\n',
  '// 983: RotMat(float, char) fica em wmath.inl (include/engine, layout do 983)\n',
  'RotMat(float,char) já tem corpo no wmath.inl do 983 (C2084)'),
 ('corte', 'src/projectg/stdafx.h', '// HACK: math helpers follow the STL main pass',
  'inline int WisEqual(const float& left, const float& right, float epsilon)\n{\n\treturn Wabs(left - right) < epsilon;\n}\n',
  '// 983: Wabs/WisZero/WisEqual ficam em wmath.h (include/engine, layout do 983)\n',
  'Wabs/WisZero/WisEqual já têm corpo no wmath.h do 983 (C2084)'),
 ('todos', 'src/**/*.cpp', WISZERO, '', 'cópia local de WisZero (ordem de emissão no VC7.1); no 983 está em wmath.h (C2084)'),
 ('todos', 'src/**/*.h', WISZERO, '', 'idem'),
 ('sub', 'src/projectg/golfcadie.cpp', 'int __fastcall WisZero(const float& v, float e = 0.00001f);\n', '', 'declaração local de WisZero com valor padrão (C2572); no 983 vem de wmath.h'),
 ('sub', 'src/projectg/itemwindow.cpp', 'int WisZero(const float& f, float epsilon = 0.00001f);\n', '', 'idem'),
 ('sub', 'src/projectg/exhibition.cpp', 'int WisZero(const float& f, float epsilon = g_EPSILON);\n', '', 'idem'),
 ('sub', 'src/fresh/source/frwnd.cpp', 'inline int WisZero(const float& v, float e)\n{\n\treturn Wabs(v) < e;\n}\n', '', 'cópia local de WisZero (C2084)'),
 ('sub', 'src/engine/wbone.cpp', 'inline int WisZero(const float& v, float e)\n{\n\treturn Wabs(v) < e;\n}\n', '', 'cópia local de WisZero (C2084)'),
 ('sub', 'src/projectg/compounddlg.cpp', '#include "../../Wangreal/include/wfont.h"', '#include "wfont.h"',
  'caminho relativo que não existe (no rebang resolve pelo /I)'),
 ('sub', 'src/projectg/compounddlg.cpp', '#include "../../Wangreal/include/wresrcmng.h"', '#include "wresrcmng.h"', 'idem'),
 # ---- F3.4: classes centrais no layout do 983 (evidência em out/F3.4/classes_983.tsv e RELATORIO.md) ----
 ('sub', 'src/fresh/include/frwnd.h', 'class FrWnd : public IObject, public FrCmdTarget\n{',
  '// 983: base nova do FrWnd (RTTI .?AVFrModalRenderer@@, vtable 00d5e5e4, 1 slot = destrutor 00be7e90; 0x14 bytes).\n'
  '// Nomes dos campos são provisórios.\n'
  'class FrModalRenderer\n{\npublic:\n\tFrModalRenderer() { ResetModal(); }\n\tvirtual ~FrModalRenderer() { ResetModal(); }\n'
  '\tvoid ResetModal()\n\t{\n\t\tm_modalPos = WPoint(0, 0);\n\t\tm_modalUnk_c = 0;\n\t\tm_modalOn = false;\n\t}\n\n'
  '\tWPoint m_modalPos;\n\tint m_modalUnk_c;\n\tbool m_modalOn;\n};\n\n'
  'class FrWnd : public IObject, public FrCmdTarget, public FrModalRenderer\n{',
  '983: FrWnd tem a 3ª base FrModalRenderer em +8 (construtor 00be8cd0; sizeof 0xd0 = push em 00be9143)'),
 ('sub', 'src/fresh/include/frwnd.h', '\t\tWPoint posFixWnd;\n\t\tunsigned long style;\n\t};',
  '\t\tWPoint posFixWnd;\n\t\tunsigned long style;\n\t\tstd::string text; // 983: o texto da dica mora aqui (new de 0x2c em 00be9056)\n\t};',
  '983: sToolTipData tem 0x2c bytes, com a std::string do texto em +0x10 (FrWnd::SetToolTipText 00be9040)'),
 ('sub', 'src/fresh/include/frwnd.h', '\tstd::string GetToolTipText() const { return m_wndToolTip; }',
  '\tconst std::string* GetToolTipText() const; // 983: 00be76c0 devolve ponteiro (NULL sem dica)',
  '983: GetToolTipText devolve &m_pToolTipData->text ou NULL (00be76c0)'),
 ('sub', 'src/fresh/include/frwnd.h', 'private:\n\tstd::string m_wndToolTip;\n',
  'private:\n\tint m_unk_c8; // 983: 4 bytes zerados no construtor no lugar da std::string m_wndToolTip (nome provisório)\n',
  '983: FrWnd não tem m_wndToolTip (0xc8 = 4 bytes; m_pToolTipData em 0xcc)'),
 ('sub', 'src/fresh/source/frwnd.cpp', '\t  m_accHoverTime(0.0f),\n\t  m_pToolTipData(NULL)\n',
  '\t  m_accHoverTime(0.0f),\n\t  m_unk_c8(0),\n\t  m_pToolTipData(NULL)\n', '983: construtor zera 0xc8 (00be8dd1)'),
 ('sub', 'src/fresh/source/frwnd.cpp',
  '\tm_wndToolTip = text;\n\tm_nFlags.Enable(FWF_TOOLTIPS);\n\tif (m_pToolTipData == NULL)\n\t{\n\t\tm_pToolTipData = new sToolTipData;\n'
  '\t\tm_pToolTipData->style = 0;\n\t\tm_pToolTipData->bFixWnd = FALSE;\n\t\tm_pToolTipData->posFixWnd = WPoint(0, 0);\n\t}\n}\n',
  '\tm_nFlags.Enable(FWF_TOOLTIPS);\n\tif (m_pToolTipData == NULL)\n\t{\n\t\tm_pToolTipData = new sToolTipData;\n'
  '\t\tm_pToolTipData->style = 0;\n\t\tm_pToolTipData->bFixWnd = FALSE;\n\t\tm_pToolTipData->posFixWnd = WPoint(0, 0);\n\t}\n'
  '\tm_pToolTipData->text = text;\n}\n\n'
  'const std::string* FrWnd::GetToolTipText() const\n{\n\tif (m_pToolTipData)\n\t\treturn &m_pToolTipData->text;\n\treturn NULL;\n}\n',
  '983: SetToolTipText grava em m_pToolTipData->text (00be9040); GetToolTipText fora de linha (00be76c0)'),
 ('sub', 'src/fresh/source/frwnd.cpp', '\t\tm_pToolTip->SetToolTipText(m_wndToolTip);\n',
  '\t\tm_pToolTip->SetToolTipText(m_pToolTipData->text);\n', '983: texto da dica em m_pToolTipData'),
 ('sub', 'src/fresh/source/frwndmanager.cpp', 'FrWnd::ToolTip()->SetToolTipText(pTopWnd->GetToolTipText());',
  'FrWnd::ToolTip()->SetToolTipText(*pTopWnd->GetToolTipText());', '983: GetToolTipText devolve ponteiro'),
 ('sub', 'src/fresh/include/frform.h', '\teFormRet m_retCode;\n\tFRESH_PFN_RESULT m_pFnResult;\n\tFrCmdTarget* m_pCmdDest;',
  '\teFormRet m_retCode;\n\tFrCmdTarget* m_pCmdDest;', '983: m_pFnResult foi para o fim do FrForm (0x100; FrForm::Close 00be6098)'),
 ('sub', 'src/fresh/include/frform.h', '\tfloat m_dt;\n\teFormRet m_defaultRetCode;\n',
  '\tfloat m_dt;\n\teFormRet m_defaultRetCode;\n\tint m_unk_f8; // 983: campo novo (nome e tipo provisórios)\n\tFRESH_PFN_RESULT m_pFnResult;\n',
  '983: FrForm = 0x110 (push em 0048b8ca): m_defaultRetCode 0xf4, campo novo 0xf8, m_pFnResult 0x100'),
 ('sub', 'src/fresh/include/frwndmanager.h', '\tstd::string m_layoutID;\n\tFrWnd* m_pCaptured;',
  '\tstd::string m_layoutID;\n\tstd::string m_unk_64; // 983: 2ª string (construtor 00be4e06..0c; nome provisório)\n\tFrWnd* m_pCaptured;',
  '983: FrWndManager tem uma std::string nova em 0x64 (m_pCaptured vai para 0x80)'),
 ('sub', 'src/fresh/include/frwndmanager.h', '\tWPoint m_caretPos;\n\tbool m_hidePrivacy;\n};',
  '\tWPoint m_caretPos;\n\tbool m_hidePrivacy;\n\tbool m_unk_a9; // 983: 2 bools e 1 dword novos, zerados no construtor (nomes provisórios)\n'
  '\tbool m_unk_aa;\n\tint m_unk_ac;\n};',
  '983: FrWndManager = 0xb0 (push antes de 00bea297)'),
 # ---- F3.4 (sessão 30): CSharedDoc ----
 ('sub', 'src/projectg/shareddoc.cpp', '\tfor (unsigned char i = 0; i < 18; i++)\n\t{\n\t\tm_holeRandom[i] = rand();',
  '\tunsigned char i;\n\tfor (i = 0; i < 18; i++)\n\t{\n\t\tm_holeRandom[i] = rand();',
  'cl 16: escopo do for (C2065 em m_holeOrder[i] = 19 depois do laço); o VC7.1 do 645 aceitava'),
 ('sub', 'src/projectg/shareddoc.cpp', '\tfor (std::list<sCardStack>::iterator it = Doc()->m_cardStackList.begin();\n\t\tit != Doc()->m_cardStackList.end(); ++it)\n\t{\n\t\tif (card.typeId == (*it).typeId && card.bValid == 1)',
  '\tstd::list<sCardStack>::iterator it;\n\tfor (it = Doc()->m_cardStackList.begin();\n\t\tit != Doc()->m_cardStackList.end(); ++it)\n\t{\n\t\tif (card.typeId == (*it).typeId && card.bValid == 1)',
  'cl 16: escopo do for (C2065 em AddCardStack)'),
 ('todos', 'src/projectg/shareddoc.cpp', 'it._Myptr->', 'it->', 'cl 16: o iterador de vector não tem _Myptr público com esse nome (C2039); it-> gera o mesmo acesso'),
 # ---- F3.5 s43: ghostmain.cpp (rebang 1c4a127) ----
 ('sub', 'src/projectg/ghostmain.cpp', 'if (pMascot->PCBangMascot)', 'if (REBANG_983_PCBANG_MASCOT(*pMascot))',
  'campo PCBangMascot saiu do sMascotInfo no 983 (62 bytes); mesma troca do mascotinfodlg.cpp'),
 # ---- F3.5 sessão 45: import do rebang 77ebe17 ----
 ('sub', 'src/projectg/ghostgamedlg.cpp', 'x = *(volatile float*)&x + rb_real_43020000;', 'x += 130.0f;	// 983/VS2010: literal direto',
  'rb_real_43020000 só é declarado no ramo sem REBANG_SEMANTIC_ONLY (truque de COMDAT do VC7.1 com o carddlg.cpp): C2065'),
 ('sub', 'src/projectg/user_info.cpp', '*(volatile float*)&pItem->pos.x + rb_real_43020000,', 'pItem->pos.x + 130.0f,	// 983/VS2010: literal direto',
  'idem'),
 ('sub', 'src/projectg/recycledlg.h', 'typedef char rb_size_check_0x630[sizeof(FrRecycleDlg) == 0x630 ? 1 : -1];\n',
  '// 983: sizeof(FrRecycleDlg) do 645 (0x630) não vale aqui (FrWnd/FrForm no layout do 983, std::map do VS2010)\n',
  'conferência de tamanho do 645 falha com as bases no layout do 983 (C2118)'),
]
_g = {}
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_shareddoc.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW']
_g = {}
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_shareddoc2.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW2']
_g = {}
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_shareddoc3.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW3']
_g = {}
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s32.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW4']
_g = {}
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s33.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW5']
_g = {}
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s34.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW6']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s35.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW7']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s36.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW8']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s37.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW9']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s38.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW10']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s39.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW11']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s41.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW12']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s45.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW13']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s46.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW14']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s47.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW15']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s48.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW16']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s49.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW17']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s50.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW18']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s51.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW19']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s52.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW20']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s53.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW21']
# F3.5 sessão 54: ids de IsLocalContent do 983 nas chamadas naked
_g['ROOT'] = ROOT
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s54.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW22']
# F3.5 sessão 55: CParticleEffect/CLightColumn do 983, PlayFx983
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s55.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW23']
# F3.5 sessão 56: CGolfPlayer no layout do 983
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s56.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW24']
# F3.5 sessão 57: CPetFrame no layout do 983
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s57.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW25']
# F3.5 sessão 58: WBone no layout do 983
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajustes_s58.py'), encoding='utf-8').read(), _g)
AJ += _g['NEW26']
def adotados():
    # F3.5: arquivos adotados (map/adotados.txt) são editados à mão; nenhum ajuste de texto vale mais para eles
    p = os.path.join(ROOT, 'map/adotados.txt')
    return set(l.split('\t')[0].strip() for l in open(p) if l.strip() and not l.startswith('#')) if os.path.exists(p) else set()
def run(out=None):
    rep = []; ADOT = adotados()
    for a in AJ:
        if a[0] != 'todos' and a[1] in ADOT: rep.append((a[1], a[-1] + ' (arquivo adotado: não aplicado)')); continue
        if a[0] == 'todos':
            n = 0
            for p in glob.glob(os.path.join(ROOT, a[1]), recursive=True):
                if os.path.relpath(p, ROOT) in ADOT: continue
                s = open(p, encoding='latin-1', newline='').read()
                if a[2] in s:
                    open(p, 'w', encoding='latin-1', newline='').write(s.replace(a[2], a[3])); n += 1
                    rep.append((os.path.relpath(p, ROOT), a[4]))
            continue
        p = os.path.join(ROOT, a[1]); s = open(p, encoding='latin-1', newline='').read()
        if a[0] == 'renum':   # ('renum', arquivo, cabeçalho, marca, regex, função, porquê): troca por regex uma vez só; a marca no cabeçalho (posta por um 'sub' posterior) diz que já foi feita
            if a[3] in open(os.path.join(ROOT, a[2]), encoding='latin-1', newline='').read(): rep.append((a[1], a[6] + ' (já aplicado)')); continue
            s = re.sub(a[4], a[5], s); why = a[6]
        elif a[0] == 'sub':
            if a[3] and a[3] in a[2] and a[2] in s: pass   # retirada (o novo é pedaço do antigo): vale o antigo
            elif (a[3] and a[3] in s) or a[2] not in s:   # o texto novo pode conter o antigo: olhar o novo primeiro
                if not a[3] or a[3] in s: rep.append((a[1], a[4] + ' (já aplicado)')); continue   # troca por vazio: sem como distinguir
                # o texto novo deste ajuste foi retocado por um ajuste posterior do mesmo arquivo que já está aplicado
                if any(b[0] == 'sub' and b[1] == a[1] and b[2] in a[3] and b[3] in s for b in AJ[AJ.index(a) + 1:]):
                    rep.append((a[1], a[4] + ' (já aplicado, retocado depois)')); continue
                sys.exit('ajustes: texto não achado em %s: %r' % (a[1], a[2][:60]))
            s = s.replace(a[2], a[3]); why = a[4]
        else:
            if a[2] not in s:
                if a[4] in s: rep.append((a[1], a[5] + ' (já aplicado)')); continue
                sys.exit('ajustes: marca não achada em %s: %r' % (a[1], a[2][:60]))
            i = s.index(a[2]); j = s.index(a[3], i) + len(a[3]); s = s[:i] + a[4] + s[j:]; why = a[5]
        open(p, 'w', encoding='latin-1', newline='').write(s); rep.append((a[1], why))
    if out:
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, 'ajustes.tsv'), 'w').write('arquivo\tmotivo\n' + ''.join('%s\t%s\n' % r for r in rep))
    print('ajustes: %d aplicados em %d arquivos' % (len(rep), len({r[0] for r in rep})))
if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv) > 1 else None)
