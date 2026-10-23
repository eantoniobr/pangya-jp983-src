# F3.4 (sessão 32): classes do ranking de votos no layout do 983. Lido por tools/f32/ajustes.py no fim.
# Evidência por classe: out/F3.4/s32/classes_983.md.
U='src/projectg/uccdrawdlg.h'
NEW4 = [
 # FrUccDrawDlg: construtor 007e5380, Init 007e2690, On*Init (tools/f34/initoffs.py), 007e58b0 ("selfdesigndescimg")
 ('sub', U, '\tbool m_bCloseAfterSave;\n\tFrArea* m_pCanvas;',
  '\tbool m_bCloseAfterSave;\n\tint m_unk983_2c8; // 983: o construtor guarda aqui [g+0x1e8] (007e5492); o destrutor compara com 0\n\tFrArea* m_pCanvas;',
  '983: FrUccDrawDlg dword novo em 0x2c8 (m_pCanvas 0x2cc, 5 votos)'),
 ('sub', U, '\tFrButton* m_pTempSaveBtn;\n\tFrButton* m_pGridBtn;',
  '\tFrButton* m_pTempSaveBtn;\n\tFrButton* m_pUnk983_2ec; // 983: controle novo (OnInit 007e3670); lugar entre TempSave e Grid pelos votos\n\tFrButton* m_pGridBtn;',
  '983: FrUccDrawDlg ponteiro novo em 0x2ec (m_pGridBtn 0x2f0, m_pTabDrawBtn 0x300)'),
 ('sub', U, '\tFrForm* m_pAskCompleteDlg;\n',
  '\tFrForm* m_pAskCompleteDlg;\n\tFrForm* m_pDescImgDlg; // 983: 0x3a4, form "selfdesigndescimg" (007e58b0); nome meu\n',
  '983: FrUccDrawDlg form novo em 0x3a4 (m_pToolBox 0x3a8)'),
 ('sub', U, '\tCFadingText m_fadingText;\n',
  '\tCFadingText m_fadingText;\n\tint m_unk983_8a4; // 983: 4 dwords novos na cauda (Init 007e2690 zera 0x8a4 e 0x8b0)\n'
  '\tint m_unk983_8a8;\n\tint m_unk983_8ac;\n\tint m_unk983_8b0;\n',
  '983: FrUccDrawDlg cauda 0x8a4..0x8b0'),
 # WMilesSoundSystem: construtor 00925cc0 (m_hDriver 0x1c zerado, WList 2D em 0x20, 3D em 0xd0, m_lastHandle 0xd1c0)
 ('sub', 'src/projectg/miles.h', '\tHDIGDRIVER m_hDriver;\n\tint m_unknown20;\n', '\tHDIGDRIVER m_hDriver;\n',
  '983: WMilesSoundSystem sem m_unknown20 (m_sample2DList em 0x20; 167 votos com -4)'),
 ('sub', 'src/projectg/miles.cpp', '\t: m_hDriver(NULL),\n\t  m_unknown20(0),\n', '\t: m_hDriver(NULL),\n', 'idem'),
 # WFixedFont: construtor 00b63b30 (WList em 0xb0, árvore em 0xd0 com operator new(0x30), cor/nil em +0x2c/+0x2d), destrutor
 # 00b63640 (m_clone 0xb18, m_font 0xafc, m_bitmap 0xaf4)
 ('sub', 'include/engine/wfont.h', '\tWList<w_fixedtext*> m_textList;\n\tw_flush_area m_flush_list[128];',
  '\tWList<w_fixedtext*> m_textList;\n\tstd::map<std::string, w_fixedtext*> m_unk983_d0; // 983: árvore nova, nó de 0x30 (par de 32 B); tipo do par provisório\n\tw_flush_area m_flush_list[128];',
  '983: WFixedFont +16 a partir de m_flush_list (0xe0; 58 votos)'),
 # TZip: iztimes com time_t de 64 bits (VS2010): votos times.mtime 0x34->0x38, ctime 0x38->0x40, timestamp 0x3c->0x48
 ('sub', 'src/engine/xzip.cpp', 'struct iztimes\n{\n\tint atime;\n\tint mtime;\n\tint ctime;\n};',
  'struct iztimes\n{\n\ttime_t atime; // 983: time_t de 64 bits (cl 16), como no XZip original\n\ttime_t mtime;\n\ttime_t ctime;\n};',
  '983: TZip +4/+8/+12 em times/timestamp (50 votos com +12 depois)'),
 # FrEdit: construtor 00bf90c0 (m_OldCaretPos 0x11c, byte novo 0x120 zerado por último, m_align 0x124, dword 0x128, m_editText 0x12c)
 ('sub', 'src/fresh/include/fredit.h', '\tint m_OldCaretPos;\n', '\tint m_OldCaretPos;\n\tbool m_unk983_120; // 983: zerado no fim do construtor (00bf90c0)\n',
  '983: FrEdit byte novo em 0x120; m_align 0x124 (68 votos com +4)'),
 ('sub', 'src/fresh/include/fredit.h', '\tbool m_vCenterAlign;', '\tint m_vCenterAlign; // 983: gravado como dword (0x128)',
  '983: FrEdit m_vCenterAlign é de 4 bytes (mov dword [esi+0x128], 0 no construtor)'),
 ('sub', 'src/fresh/source/fredit.cpp', '\tm_OldCaretPos = 0;\n}', '\tm_OldCaretPos = 0;\n\tm_unk983_120 = false;\n}', 'idem (gravação no fim do construtor)'),
 # CTimerManager::sTimer 0x2c -> 0x30: ClearTimer 0099cba0 grava active em +0x2c; votos name +0xc -> +0x10, degrau de +4 por elemento
 ('sub', 'src/projectg/wtimer.h', '\t\tCTimerEvent* event;\n\t\tstd::string name;', '\t\tCTimerEvent* event;\n\t\tint unk983_c; // 983: dword novo antes de name (lugar pelos votos)\n\t\tstd::string name;',
  '983: sTimer 0x30 (99 votos em degraus de +4)'),
]
