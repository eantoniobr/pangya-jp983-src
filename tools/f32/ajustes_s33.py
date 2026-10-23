# F3.4 (sessão 33): CTaskMain (base das telas principais), CTutorial e CItemWindow no layout do 983.
# Lido por tools/f32/ajustes.py no fim. Evidência: out/F3.4/s33/classes_983.md.
T='src/projectg/taskmain.h'
NEW5 = [
 # CTaskMain 0x1e0 -> 0x218: nome do controle -> handler de FRCMD_INIT -> campo gravado (tools/f34/msgmap.py ccfdda),
 # InitControls 00650f10, construtor em linha no do CTutorial (007cda30: vector 0x1b0, string 0x1f0)
 ('sub', T, '\tFrButton* m_pUnderBarScratch;\n\tFrGroupBox* m_pOverBar;',
  '\tFrButton* m_pUnderBarScratch;\n\tFrButton* m_pUnderBarCombine; // 983: "utab.combine" 0x74 (handler 00652210); nome meu\n'
  '\tFrButton* m_pUnderBarPointShop; // 983: "utab.point_shop" 0x78 (00652520); nome meu\n\tFrGroupBox* m_pOverBar;',
  '983: CTaskMain 2 botões novos em 0x74/0x78 (m_pOverBar 0x7c, m_pUnderTab 0x80, m_pUnderBar 0x84)'),
 ('sub', T, '\tFrViewer* m_pOverBarMascot;\n\tFrViewer* m_pOverBarCharSel;',
  '\tFrViewer* m_pOverBarMascot;\n\tFrViewer* m_pOverBarEqItem; // 983: "obar.eqitem" 0xcc (00656700); nome meu\n'
  '\tvoid* m_unk983_d0[10]; // 983: 10 dwords zerados no InitControls (00650f10); tipo não medido\n\tFrViewer* m_pOverBarCharSel;',
  '983: CTaskMain +44 B entre m_pOverBarMascot (0xc8) e m_pOverBarCharSel (0xf8)'),
 ('sub', T, '\tFrButton* m_pMessengerBtn;\n\tFrButton* m_pMessengerAlarmBtn;\n\tFrButton* m_pMessengerGiftAlarmBtn;\n',
  '\tFrButton* m_pMessengerBtn;\n\tstatic FrButton* m_pMessengerAlarmBtn; // 983: saiu ("obar.messenger_alarm" não está no mapa); static provisório para o código compilar\n'
  '\tstatic FrButton* m_pMessengerGiftAlarmBtn; // 983: saiu ("obar.gift_alarm")\n',
  '983: CTaskMain sem os 2 botões de alarme (m_pMessengerBtn 0x13c, m_pTreasureAlarm 0x140)'),
 ('sub', T, '\tFrBirthdayEventMissionDlg* m_pMissionDlg[5];', '\tFrBirthdayEventMissionDlg* m_pMissionDlg[8]; // 983: 0x190..0x1ac são 32 B (eram 20); quais 3 são novos não foi medido',
  '983: CTaskMain +12 B entre m_pMaketDlg (0x18c) e m_levelupForms (0x1b0)'),
 # CTutorial: construtor 007cda30 grava byte 0xda8 (m_bInputBlocked) e dword 0xdac
 ('sub', 'src/projectg/tutorial.h', '\tbool m_bInputBlocked;\n', '\tbool m_bInputBlocked;\n\tint m_unk983_dac; // 983: zerado no fim do construtor (007cdc98)\n',
  '983: CTutorial dword novo em 0xdac'),
 # CItemWindow: no 983 só há um WRect entre m_pOverlay (0x28) e m_curX (0x3c); 0075d9d0 (ResetUiPosition) monta o recorte
 # numa variável local (ebp-0x14) e grava m_dst em 0x2c..0x38
 ('sub', 'src/projectg/itemwindow.h', '\tWRect m_dst;\n\tWRect m_clip;\n', '\tWRect m_dst;\n', '983: CItemWindow sem m_clip (m_curX 0x3c, m_pUI 0x54, m_bActive 0x86)'),
 ('sub', 'src/projectg/itemwindow.cpp', '\tfloat barY = COption::Instance()->gGetBar_Y();\n\n\tif (m_pOverlay)\n\t{\n\t\tm_clip.x = 65.0f;',
  '\tfloat barY = COption::Instance()->gGetBar_Y();\n\tWRect m_clip; // 983: o recorte é local (0075d9d0); o corpo do 983 difere (fica para a onda 2)\n\n\tif (m_pOverlay)\n\t{\n\t\tm_clip.x = 65.0f;',
  'idem (m_clip local)'),
 # CLobbyMain: nome de controle -> Init -> campo (tools/f34/initcmp.py ... ccfdda TOPPAGE): "TOPPAGE.oneday_quest" grava 0x234
 # (handler 00593900), entre notice (0x230) e server (0x238); treasureisland continua em 0x26c, logo um dos 3 dwords de
 # 0x260..0x268 (KoohBirthday, reservado, ValEvent — nenhum tem Init no 983) saiu
 ('sub', 'src/projectg/lobbymain.h', '\tFrButton* m_pToppageNotice;\n\tFrButton* m_pToppageServer;',
  '\tFrButton* m_pToppageNotice;\n\tFrButton* m_pToppageOneDayQuest; // 983: "TOPPAGE.oneday_quest" 0x234 (00593900); nome meu\n\tFrButton* m_pToppageServer;',
  '983: CLobbyMain ponteiro novo em 0x234 (server 0x238 ... BingoEvent 0x260)'),
 ('sub', 'src/projectg/lobbymain.h', '\tFrButton* m_pToppageKoohBirthdayEvent;\n\tunsigned long m_reserved22c;\n', '\tFrButton* m_pToppageKoohBirthdayEvent;\n',
  '983: CLobbyMain um dword a menos entre BingoEvent (0x260) e TreasureIsland (0x26c); PROVISÓRIO: tirei o reservado, pode ter sido Kooh ou Val'),
 # FrListBox: construtor 00bf1400 grava m_multiSelect como byte em 0xf8, m_useRightButton como DWORD em 0xfc, m_rollOver
 # como byte em 0x100, m_pItemUnderCursor 0x104, m_pSelected 0x108; destrutor 00bf1130: m_noRButtonMap 0x118
 ('sub', 'src/fresh/include/frlistbox.h', '\tbool m_useRightButton;\n\tbool m_rollOver;', '\tint m_useRightButton; // 983: gravado como dword (0xfc)\n\tbool m_rollOver;',
  '983: FrListBox m_useRightButton de 4 bytes (m_rollOver 0x100, m_pItemUnderCursor 0x104; 27 votos com +8)'),
 # CTrajectory: construtor 0079bec0 zera 0x28..0x3c (m_pComet..m_pWindTrack), depois 0x1c, 0x20, 0x24 (m_pActive), 0xc0
 # (m_pCurPutt) e 0x40.. (m_pPutt): m_pActive tem 3 elementos
 ('sub', 'src/projectg/trajectory.h', '\tCBallTrace* m_pActive[2];', '\tCBallTrace* m_pActive[3]; // 983: 3 elementos (0x1c, 0x20, 0x24)',
  '983: CTrajectory m_pActive[3] (m_pComet 0x28, m_pCurPutt 0xc0; 28 votos com +4)'),
 ('sub', 'src/projectg/trajectory.cpp', '\tfor (int k = 0; k < 2; k++)\n\t\tm_pActive[k] = NULL;', '\tfor (int k = 0; k < 3; k++)\n\t\tm_pActive[k] = NULL;',
  'idem (o construtor do 983 zera os 3; os outros laços de 2 não foram conferidos)'),
]
