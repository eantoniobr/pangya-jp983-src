# F3.5 (sessão 39): trocas em arquivos ainda importados pedidas pelas unidades Fresh adotadas. Lido por tools/f32/ajustes.py no fim.
NEW11 = [
 ('sub', 'src/projectg/chatmsg.h', '\tbool IME_IsCandWinOpened();\n',
  '\tconst char* GetCompStr983() const { return m_szComp; } // 983: FrWndManager::ProcessHotKey (00be58e0) lê m_szComp[0] (+0x4c0); nome meu\n'
  '\tbool IME_IsCandWinOpened();\n',
  '983: FrWndManager::ProcessHotKey olha o 1º byte da composição do IME (CChatMsg+0x4c0) antes do ESCAPE'),
 ('sub', 'include/engine/wfont.h', '\tvirtual float GetTextWidth(WView* view, const char* text);\n',
  '\tvirtual float GetTextWidth(WView* view, const char* text); // 983: slot 5 (00b5ddc0), mede pela variante nova 00b5dc90 (ainda não escrita)\n'
  '\tvirtual float GetTextWidthOld983(WView* view, const char* text); // 983: slot 6 (00b61870), mede pelo PrintOut antigo 00b611f0; nome meu\n',
  '983: a vtable do WFont (16 slots) tem um virtual a mais depois do GetTextWidth; GetFontHeight passa a +0x24 (FrGraphicInterface::GetFontHeight 00bec500)'),
 ('sub', 'src/engine/wfont.cpp', 'float WFont::GetTextWidth(WView* view, const char* text)\n{\n\treturn PrintOut(view, 0, 0, text, 0, 0, false, 0);\n}\n',
  'float WFont::GetTextWidth(WView* view, const char* text)\n{\n\treturn PrintOut(view, 0, 0, text, 0, 0, false, 0);\n}\n\n'
  '// 983 (00b61870): slot 6 da vtable, mede pelo PrintOut antigo (00b611f0). Nome meu.\n'
  'float WFont::GetTextWidthOld983(WView* view, const char* text)\n{\n\treturn PrintOut(view, 0, 0, text, 0, 0, false, 0);\n}\n',
  '983: corpo do virtual novo do WFont (00b61870)'),
]
