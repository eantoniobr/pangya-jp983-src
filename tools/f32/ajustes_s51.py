# F3.5 (sessão 51): conferência função a função do privatetradedlg.cpp contra o 983. Lido por tools/f32/ajustes.py no fim.
_P = 'src/projectg/privatetradedlg.cpp'
_SJ = ('// 983 (cliente japonês): 1º byte de caractere duplo em Shift-JIS (0x80-0x9f, 0xe0-0xfc); no 645 era `c & 0x80`. Nome provisório\n'
       '// (mesma macro de src/engine/wfont.cpp).\n#ifndef W_SJISLEAD983\n'
       '#define W_SJISLEAD983(c) (((unsigned char)(c) >= 0x80 && (unsigned char)(c) < 0xa0) || (unsigned char)((c) - 0xe0) <= 0x1c)\n#endif\n')
NEW19 = [
 # FrForm: todas as telas derivadas de FrForm têm sizeof múltiplo de 16 no 983 (77 de 77 MakeInstance com construtor conferido;
 # FrNumEdit 0x130, FrMyWareHouse 0x170, FrPrivateTrade 0x180, FrTradeToolTip 0x140); os controles derivados só de FrWnd não.
 ('sub', 'src/fresh/include/frform.h', '\nclass FrForm : public FrWnd\n',
  '\n// 983: alinhamento de 16 (sizeof de toda tela derivada é múltiplo de 16; o membro que o causa não foi identificado)\n'
  'class __declspec(align(16)) FrForm : public FrWnd\n',
  '983: sizeof das telas FrForm múltiplo de 16 (push antes do operator new nos MakeInstance/CreateForm)'),
 # FrEdit::SetLine é virtual no 983: último slot (24, +0x60) da vtable 00d5eb94 = 00bfaf60; as chamadas são `call [vtbl+0x60]`
 ('sub', 'src/fresh/include/fredit.h', '\tconst char* SetLine(int line, const char* text, unsigned long color,\n',
  '\tvirtual const char* SetLine(int line, const char* text, unsigned long color, // 983: virtual (slot 24 da vtable 00d5eb94)\n',
  '983: FrEdit::SetLine chamada pela vtable (+0x60) em 008d0410, 008d12f0, 008d1420'),
 # SAFE_RANGEVALUE/IS_INRANGE: o 983 (/Ob1) as expande em linha em FrNumEdit::SetValue (008d12f0) e OnEditEnter (008d1560)
 ('sub', 'src/projectg/wtemplate.h', 'bool SAFE_RANGEVALUE(T& value, const U& min, const U& max, const U& newValue)',
  'inline bool SAFE_RANGEVALUE(T& value, const U& min, const U& max, const U& newValue) // 983: em linha',
  '983: SAFE_RANGEVALUE expandida em linha (008d12f0, 008d1560); com /Ob1 isso exige `inline`'),
 ('sub', _P, '\nIMPLEMENT_OBJECT(FrNumEdit, FrForm)\n', '\n' + _SJ + '\nIMPLEMENT_OBJECT(FrNumEdit, FrForm)\n', 'macro do teste Shift-JIS'),
 ('todos', _P, '\t\t\tif ((text[i] & 0x80) == 0)\n', '\t\t\tif (!W_SJISLEAD983(text[i]))\n',
  '983: FrNumEdit::OnProc (008d5d90) e FrPangEdit::OnProc (008d5f00) testam 1º byte Shift-JIS em vez de `& 0x80`'),
]

NEW19 += [
 # FrEdit::SetLine do 983 tem 6 argumentos (ret 0x18 em 00bfaffc); nas chamadas lidas o novo é 0 (4 `push eax` com eax = 0 em 008d1335)
 ('sub', 'src/fresh/include/fredit.h', '\t\tbool enter, unsigned long animTime);\n\tconst char* GetLine(',
  '\t\tbool enter, unsigned long animTime, int unk983 = 0); // 983: 6º argumento (posição e nome provisórios; corpo não lido)\n\tconst char* GetLine(',
  '983: FrEdit::SetLine com 6 argumentos (ret 0x18)'),
 ('sub', 'src/fresh/source/fredit.cpp', 'const char* FrEdit::SetLine(int line, const char* text, unsigned long color,\n\tbool marginAlign, unsigned long animTime)',
  'const char* FrEdit::SetLine(int line, const char* text, unsigned long color,\n\tbool marginAlign, unsigned long animTime, int unk983)', 'idem'),
 # FrRecycleAboutDlg: conferência de tamanho do 645 (0x138) não vale com FrForm alinhada a 16
 ('sub', 'src/projectg/recycledlg.h', 'typedef char rb_size_check_0x138[sizeof(FrRecycleAboutDlg) == 0x138 ? 1 : -1];\n',
  '// 983: sizeof(FrRecycleAboutDlg) do 645 (0x138) não vale aqui (FrForm alinhada a 16; tamanho do 983 não medido)\n',
  'conferência de tamanho do 645 falha com FrForm alinhada a 16 (C2118)'),
 # Cabeçalho comum dos registros do pangya.iff no 983: 0x90 -> 0xc0. Name[64] (Icon 0x31 -> 0x49 em 008d5cb0; bits de venda 0x68 -> 0x80
 # em 008d3770); 0x18 bytes novos antes das datas (CItemManager::MakePartMap 00a29130: SalePrice 0x78, New/Hit 0x81, saleStart.wYear 0xa0,
 # saleEnd.wYear 0xb0).
 ('sub', 'src/shared/classdefine.h', '\tchar Name[40];\n\tunsigned char Level : 7;', '\tchar Name[64]; // 983: 40 -> 64\n\tunsigned char Level : 7;',
  '983: IFF_ITEM_COMMON::Name[64]'),
 ('sub', 'src/shared/classdefine.h', '\tunsigned int Point;\n\t_SYSTEMTIME saleStart;',
  '\tunsigned int Point;\n\tunsigned int unk983_88[6]; // 983: 0x18 bytes novos entre 0x88 e saleStart (0xa0); podem estar antes de Point (provisório)\n\t_SYSTEMTIME saleStart;',
  '983: IFF_ITEM_COMMON = 0xc0 (saleStart em 0xa0)'),
 # sPart do 983 = 0x238 (push em 00a29163): 3ª contagem de slots de carta em 0x22c, depois de CaddieSlot (lida em 008d3070)
 ('sub', 'src/shared/classdefine.h', '\t\tshort CharacterSlot;\n\t\tshort CaddieSlot;\n\t\tunsigned int RentalPrice;',
  '\t\tshort CharacterSlot;\n\t\tshort CaddieSlot;\n\t\tshort NpcSlot983; // 983: 3ª contagem de slots (0x22c; cartas com kind == 5); nome provisório\n\t\tunsigned int RentalPrice;',
  '983: sPart = 0x238, short novo em 0x22c'),
 ('todos', _P, '\t\tfor (int i = 0; i < 8; ++i)\n\t\t{\n\t\t\tif (pItem->cards[i].slot == slot + 1', '\t\tfor (int i = 0; i < 10; ++i)\n\t\t{\n\t\t\tif (pItem->cards[i].slot == slot + 1',
  '983: 10 cartas por item (cmp ebx, 0xa em 008d3070)'),
]
NEW19 += [
 ('sub', _P, '\n\tfor (int i = 0; i < 8; i++)\n\t{\n\t\tunsigned long cardId = m_pItem->cards[i].typeId;', '\n\tfor (int i = 0; i < 10; i++)\n\t{\n\t\tunsigned long cardId = m_pItem->cards[i].typeId;',
  '983: 10 cartas por item (FrTradeToolTip::SetToolTip 008da5e0; conferido pelo diff)'),
]
NEW19 += [
 ('sub', _P, '\tcase SET_ITEM_BUTTON_PART:\n\t\tfor (int i = 0; i < 10; i++)\n\t\t{\n\t\t\tIFF_ITEM_COMMON* common =\n\t\t\t\tItemManager()->FindCommonItem(i | 0x4000000);',
  '\tcase SET_ITEM_BUTTON_PART:\n\t\tfor (int i = 0; i < 15; i++) // 983: 15 personagens\n\t\t{\n\t\t\tIFF_ITEM_COMMON* common =\n\t\t\t\tItemManager()->FindCommonItem(i | 0x4000000);',
  '983: FrMyWareHouse::InitSortList percorre 15 personagens (cmp esi, 0xf em 008d39d0)'),
 ('todos', _P, '<< MsgObject(0, 0x247, ', '<< MsgObject(0, 0x2c3, ', '983: a mensagem de troca é 0x2c3 (008d3f40, 008d44e0, 008d45d0)'),
 ('sub', _P, '\t\t\tpTrade->m_pCompanionTradeWnd->DoTradeUnLock();\n\t\t\tpTrade->m_pMyTradeWnd->DoTradeUnLock();\n\t\t}\n\t}\n}\n\nvoid FrPrivateTradeWnd::OnProc(',
  '\t\t\tpTrade->SetTradeUnLockAll(); // 983: chama o método (008d26b0) em vez dos 2 DoTradeUnLock\n\t\t}\n\t}\n}\n\nvoid FrPrivateTradeWnd::OnProc(',
  '983: OnSendItemUpdate (008d3f40) chama FrPrivateTrade::SetTradeUnLockAll'),
 ('sub', _P, '\t\tpTrade->m_pMyTradeWnd->GetTradeItems(items);', '\t\tpTrade->GetMyTradeItems(items); // 983: pelo método de FrPrivateTrade (008d0810)',
  '983: FrMyWareHouse::SetItemList (008d99a0) chama FrPrivateTrade::GetMyTradeItems'),
]
