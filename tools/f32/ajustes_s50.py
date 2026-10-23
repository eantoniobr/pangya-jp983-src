# F3.5 (sessão 50): mais unidades cujo ramo REBANG_SEMANTIC_ONLY não compilava (símbolos que só existem no ramo de bytes
# do rebang, ou VC7.1 -> VC10). Lido por tools/f32/ajustes.py no fim.
NEW18 = [
 # realmyroommain: os 3 apelidos de linker rb_InitMyRoom* só são declarados no ramo de bytes (C3861); são os métodos da classe
 ('sub', 'src/projectg/realmyroommain.cpp',
  '\n\trb_InitMyRoomControls(this);\n\trb_InitMyRoomDialogs(this);\n\trb_InitMyRoomVariables(this);\n',
  '\n\tInitMyRoomControls(); // ramo semântico: os rb_InitMyRoom* são apelidos destes 3 métodos\n\tInitMyRoomDialogs();\n\tInitMyRoomVariables();\n',
  'ramo semântico: rb_InitMyRoom* só existem no ramo de bytes (C3861)'),
 # giftdlg: no 645 a tabela `days` é a do checkoutdlg.cpp, alcançada por apelido de linker; aqui cada unidade tem a sua
 ('sub', 'src/projectg/giftdlg.cpp',
  '#pragma comment(linker, \\\n\t"/alternatename:_rb_days_base=?m_RTTI@FrCheckoutDlg@@2VWRTTI@@B")\n#define days ((days_t*)(rb_days_base + 12))\n',
  '#ifndef REBANG_SEMANTIC_ONLY\n#pragma comment(linker, \\\n\t"/alternatename:_rb_days_base=?m_RTTI@FrCheckoutDlg@@2VWRTTI@@B")\n#define days ((days_t*)(rb_days_base + 12))\n'
  '#else\n// PROVISÓRIO: cópia da tabela do checkoutdlg.cpp (645); no 983 não foi lido onde a tabela mora nem os textos\n'
  'struct sGiftDayInfo\n{\n\tconst char* name;\n\tint value;\n};\n'
  'static sGiftDayInfo days[6] = {\n\t{ "1\\xc0\\xcf", 1 },\n\t{ "7\\xc0\\xcf", 7 },\n\t{ "15\\xc0\\xcf", 15 },\n\t{ "30\\xc0\\xcf", 30 },\n'
  '\t{ "365\\xc0\\xcf", 365 },\n\t{ "\\xb9\\xab\\xc1\\xa6\\xc7\\xd1", 0 }\n};\n#endif\n',
  'ramo semântico: rb_days_base só existe no ramo de bytes (C2065)'),
 # hatmanager: no VC10 deste build wchar_t é tipo nativo; no 645 WCHAR == unsigned short (nomes decorados com PAG)
 ('sub', 'src/projectg/hatmanager.cpp', '\nextern unsigned short FakeTable[28];',
  '\n#ifdef REBANG_SEMANTIC_ONLY // VC10: wchar_t nativo (C2664); as chamadas passam WCHAR[]\n#include <direct.h> // _mkdir (C3861)\n'
  'namespace BABO_STR\n{\n\tinline bool WStrStr(char* out, wchar_t* str, int strLen, wchar_t* key, int keyLen, bool bCheckOnly)\n'
  '\t{\n\t\treturn WStrStr(out, (unsigned short*)str, strLen, (unsigned short*)key, keyLen, bCheckOnly);\n\t}\n'
  '\tinline bool WStrCmp(wchar_t* a, int aLen, wchar_t* b, int bLen)\n\t{\n\t\treturn WStrCmp((unsigned short*)a, aLen, (unsigned short*)b, bLen);\n\t}\n}\n#endif\n'
  '\nextern unsigned short FakeTable[28];',
  'VC10: WCHAR[] não converte para unsigned short* (C2664); _mkdir precisa de <direct.h>'),
 # golftask (rebang 8688871): FrWnd::OnDisplay do 983 tem 4 argumentos; o 4º como nas outras tarefas (realmyroomtask, avatar_task)
 ('sub', 'src/projectg/golftask.cpp', 'g_pFresh->GetDesktop()->OnDisplay(true, false, true);', 'g_pFresh->GetDesktop()->OnDisplay(true, false, true, true);',
  '983: FrWnd::OnDisplay tem 4 argumentos (00be8400, ret 0x10)'),
 # avatar_avatar: conferência de tamanho do 645; ntAvatar herda de classes já no layout do 983 (tamanho do 983 não medido)
 ('sub', 'src/projectg/avatar_avatar.h', 'typedef char ntAvatarSizeCheck[sizeof(ntAvatar) == 0xb04 ? 1 : -1];\n',
  '// 983: sizeof(ntAvatar) do 645 (0xb04) não vale aqui (bases no layout do 983; tamanho do 983 não medido)\n',
  'conferência de tamanho do 645 falha com as bases no layout do 983 (C2118)'),
 # ucclibrary: dados de EH escritos à mão para o CreateItemThumbnail em `naked`; no ramo semântico o compilador gera os seus
 ('sub', 'src/projectg/ucclibrary.cpp', '\n#pragma section(".xdata$x", read)\n#pragma code_seg(".text$x")\nextern "C" __declspec(naked) void __cdecl rb_createitemthumbn_ehfunclets()',
  '\n#ifndef REBANG_SEMANTIC_ONLY // dados de EH à mão: só para o ramo de bytes\n#pragma section(".xdata$x", read)\n#pragma code_seg(".text$x")\nextern "C" __declspec(naked) void __cdecl rb_createitemthumbn_ehfunclets()',
  'ramo semântico: rb_createitemthumbn_ehfunclets_code só existe no ramo de bytes (C2065)'),
 ('sub', 'src/projectg/ucclibrary.cpp', '\tCreateItemThumbnail(*(const Bitmap**)0, *(const Bitmap**)0, *(Bitmap**)0);\n}\n#pragma code_seg()\n',
  '\tCreateItemThumbnail(*(const Bitmap**)0, *(const Bitmap**)0, *(Bitmap**)0);\n}\n#pragma code_seg()\n#endif // ramo de bytes\n',
  'idem (fecha o #ifndef)'),
 # fontinfo: bloco morto `if (0)` (truque de ordem de emissão do VC7.1) usa classes só declaradas no ramo de bytes
 ('corte', 'src/projectg/fontinfo.cpp', '\t// HACK: direct references keep the inline naked functions (nakedify: their\n',
  '\t\t((CCalipers*)0)->KeyCheck(0.0f);\n\t}\n',
  '\t// 983: bloco `if (0)` de ordem de emissão do 645 retirado (classes só declaradas no ramo de bytes)\n',
  'ramo semântico: CFxSprayEx/CExtendedEffect/... não declarados (C2065, 48 erros)'),
]
# realmyroommainui (ramo semântico; 47 erros de 6 tipos)
_R = 'src/projectg/realmyroommainui.cpp'
for _x in ('imgNames, 5', 'imgNames, 6', 'imgNames, i - 1', 'names, 0x15', 'names, 0x16', 'names, 0x17', 'names, 0x18', 'names, 0x1a', 'names, 0x1b',
           'names, 0x20', 'names, 0x21', 'names, 0x22', 'names, 0xc', 'names, 10', 'names, i - 1', 'names, i'):
    NEW18.append(('todos', _R, 'AddTab(%s, NULL)' % _x, 'AddTab(%s)' % _x, '983: FrTabButton::AddTab de lista de imagens não recebe mais o tamanho (00c07e10)'))
NEW18 += [
 ('sub', _R, '\n\tconst char** ppFile = &rb_shop_dot_files[0];\n', '\n\textern const char* dot_files[5][2]; // de shopmain.cpp (o ramo de bytes usa o apelido rb_shop_dot_files)\n\tconst char** ppFile = &dot_files[0][0];\n',
  'ramo semântico: rb_shop_dot_files só existe no ramo de bytes (C2065)'),
 ('sub', _R, '\n\t} while (ppFile < &rb_shop_dot_files[10]);\n', '\n\t} while (ppFile < &dot_files[5][0]);\n', 'idem'),
 ('todos', _R, 'pMascot->PCBangMascot', 'REBANG_983_PCBANG_MASCOT(*pMascot)', 'campo PCBangMascot saiu do sMascotInfo no 983 (mesma troca do ghostmain/mascotinfodlg)'),
 ('todos', _R, '((CTaskMain*)this)->GetCategoryFlag(subTab)', 'CTaskMain::GetCategoryFlag(subTab)', 'membro protegido da base chamado por ponteiro da base (C2248); pela classe derivada é o mesmo call'),
 ('todos', _R, '((RbTaskMainAccess*)this)->OnOverBar_OptionUp();', 'CTaskMain::OnOverBar_OptionUp();', 'RbTaskMainAccess só existe no ramo de bytes (C2065)'),
 ('corte', _R, '\t// HACK: keeps the literal holders of the naked functions compiled (see LoadMyRoomImages)\n\tif (0)\n',
  '\t\tWSingleton<CHelpMsg>::IsInstantiated();\n\t}\n',
  '\t// 983: bloco `if (0)` de WSingleton<...>::IsInstantiated retirado (classes não declaradas no ramo semântico)\n',
  'ramo semântico: CShadowManager/CBrowser/... não declarados (C2065)'),
]
# _sPrivateTradeItemSingle do 983: 0xd8 -> 0x108 (rep movsd 0x36 -> 0x42 em SetItemList 008d99a0; _sPrivateTradeItem 0x368 -> 0x428);
# slotStats em 0xfc e laço de cartas até 10 no Formator (008d6fb0): cards[8] -> cards[10]
NEW18 += [
 ('sub', 'src/projectg/privatetradedlg.h', '\t_sPrivateTradeCardInfo cards[8];\n', '\t_sPrivateTradeCardInfo cards[10]; // 983: 10 cartas (slotStats em 0xfc; Formator 008d6fb0)\n',
  '983: _sPrivateTradeItemSingle tem 0x108 bytes (10 cartas de 0x18)'),
 ('sub', 'src/projectg/privatetradedlg.cpp', '\t\t\t\tif (i >= 8)\n\t\t\t\t{\n\t\t\t\t\tbreak;\n\t\t\t\t}\n\n\t\t\t\tsSCardAvilityPeriodInfo* pCard = *it;\n\t\t\t\tsingle.cards[i].id',
  '\t\t\t\tif (i >= 10) // 983: cmp edi, 0xa\n\t\t\t\t{\n\t\t\t\t\tbreak;\n\t\t\t\t}\n\n\t\t\t\tsSCardAvilityPeriodInfo* pCard = *it;\n\t\t\t\tsingle.cards[i].id',
  '983: Formator copia até 10 cartas (008d6fb0)'),
]
