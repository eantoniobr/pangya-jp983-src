# F3.4 (sessão 34): telas Fresh medidas pela varredura tools/f34/initsweep.py (nome do controle -> handler -> campo gravado,
# nosso .obj x 983) + CPetBody. Lido por tools/f32/ajustes.py no fim. Evidência: out/F3.4/s34/classes_983.md.
NEW6 = [
 # FrNoticeDlg: mapa 00e3a410 tem 11 entradas (a 11ª é "caption", FRCMD_INIT, handler 00ae48b0, grava 0x110 com o RTTI
 # 0xf1ab44 = FrArea); cancel 0x114, view 0x118; construtor 00ae5350 zera 0x110 depois de 0x140 e antes de 0x148
 ('sub', 'src/projectg/noticedlg.h', '\tFrButton* m_pCancel;\n\tFrViewer* m_pViewer;',
  '\tFrArea* m_pCaption; // 983: "caption" 0x110 (handler 00ae48b0); nome meu\n\tFrButton* m_pCancel;\n\tFrViewer* m_pViewer;',
  '983: FrNoticeDlg ponteiro novo em 0x110 (m_pCancel 0x114 ... m_startIndex 0x148, sizeof 0x14c)'),
 ('sub', 'src/projectg/noticedlg.h', 'class FrListBox;\n', 'class FrListBox;\nclass FrArea;\n', 'idem (declaração)'),
 ('sub', 'src/projectg/noticedlg.h', '\tvoid OnCancelInit(int param);\n', '\tvoid OnCaptionInit(int param); // 983: 00ae48b0\n\tvoid OnCancelInit(int param);\n', 'idem (handler novo)'),
 ('sub', 'src/projectg/noticedlg.cpp', 'ON_FRESH_VV("next", FRCMD_LBUTTONUP, FrNoticeDlg::OnNextBtnUp)\n',
  'ON_FRESH_VV("next", FRCMD_LBUTTONUP, FrNoticeDlg::OnNextBtnUp)\nON_FRESH_VI("caption", FRCMD_INIT, FrNoticeDlg::OnCaptionInit)\n', 'idem (11ª entrada do mapa do 983)'),
 ('sub', 'src/projectg/noticedlg.cpp', '\tm_bScrollBar = false;\n\tm_startIndex = -1;\n}\n',
  '\tm_bScrollBar = false;\n\tm_pCaption = NULL;\n\tm_startIndex = -1;\n}\n', 'idem (construtor 00ae5350)'),
 ('sub', 'src/projectg/noticedlg.cpp', 'void FrNoticeDlg::OnCancelInit(int param)\n{',
  'void FrNoticeDlg::OnCaptionInit(int param)\n{\n\tm_pCaption = DYNAMIC_CAST(FrArea, param);\n}\n\nvoid FrNoticeDlg::OnCancelInit(int param)\n{', 'idem (corpo do handler 00ae48b0)'),
 # CPost_ReciveDlg: "receive_1page" (Init 005b1e90, RTTI de FrButton) grava 0x11c; write_letter 0x120 ... index_list 0x1ec
 ('sub', 'src/projectg/post_recivedlg.h', '\tFrButton* m_pDeleteAll;\n',
  '\tFrButton* m_pDeleteAll;\n\tFrButton* m_pReceive1Page; // 983: "receive_1page" 0x11c (005b1e90); nome meu\n',
  '983: CPost_ReciveDlg botão novo em 0x11c (13 handlers com +4)'),
 # FrBirthdayEventDlg: "Help" ganhou Init (00b12c10, FrButton) que grava 0x114; Gift 0x118, boardNumber 0x11c, bg1 0x120
 ('sub', 'src/projectg/birthdayeventdlg.h', '\tFrBirthdayEventHelpDlg* m_pHelpDlg;\n',
  '\tFrBirthdayEventHelpDlg* m_pHelpDlg;\n\tFrButton* m_pHelpBtn; // 983: "Help" FRCMD_INIT 0x114 (00b12c10); nome meu\n',
  '983: FrBirthdayEventDlg botão novo em 0x114 (PROVISÓRIO: pode ser antes de m_pHelpDlg; o handler de Help do 983 não grava 0x110)'),
 # FrTreasureCourse: 3 mapas novos no mapa de mensagens (demon_land_map, abbot_mine, luna); votos: m_gaugePos 0x138 (+0),
 # m_pCurrMapViewer 0x1d8 -> 0x1e8 (+16), m_pMapBmp 0x200 -> 0x210, m_pRandomSmallBmp 0x250 -> 0x268 (+24),
 # m_gauge 0x284 -> 0x29c, m_pCloudOverlay 0x2d4 -> 0x2f4 (+32): os três vetores passam de 20 a 22
 ('sub', 'src/projectg/treasuredlg.h', '\tWPoint m_gaugePos[20];', '\tWPoint m_gaugePos[22]; // 983: 22', '983: FrTreasureCourse m_gaugePos[22] (+16)'),
 ('sub', 'src/projectg/treasuredlg.h', '\tconst Bitmap* m_pMapBmp[20];', '\tconst Bitmap* m_pMapBmp[22]; // 983: 22', '983: FrTreasureCourse m_pMapBmp[22] (+24)'),
 ('sub', 'src/projectg/treasuredlg.h', '\tunsigned long m_gauge[20];', '\tunsigned long m_gauge[22]; // 983: 22', '983: FrTreasureCourse m_gauge[22] (+32 no fim)'),
 # FrMakeRoomDlg: nome do controle -> Init: make_event 0x124 (6º botão), classictype_btn 0x15c, map_ctrl 0x180,
 # map_ctrl.text_map 0x184, artifact_ctrl 0x188 + 7 filhos 0x18c..0x1a4, overgauge 0x1a8, holetype grava 0x1ac..0x1c8
 ('sub', 'src/projectg/makeroomdlg.h', '\tFrButton* m_pMakeBtn[5];', '\tFrButton* m_pMakeBtn[6]; // 983: [5] = "make_event" 0x124 (00aded00)',
  '983: FrMakeRoomDlg 6º botão de modo (m_pPicture 0x128 ... m_pTimeLimit 0x158)'),
 ('sub', 'src/projectg/makeroomdlg.h', '\tFrViewer* m_pCourse;\n', '\tFrButton* m_pClassicTypeBtn; // 983: "classictype_btn" 0x15c (00adea20); nome meu, tipo não medido\n\tFrViewer* m_pCourse;\n',
  '983: FrMakeRoomDlg ponteiro novo em 0x15c (m_pCourse 0x160 ... m_pHoleMax 0x17c)'),
 ('sub', 'src/projectg/makeroomdlg.h', '\tFrGaugeBarImage* m_pOverGauge;\n',
  '\tFrWnd* m_pMapCtrl; // 983: "map_ctrl" 0x180 (00ade540); nomes meus, tipos não medidos\n\tFrWnd* m_pMapCtrlText; // "map_ctrl.text_map" 0x184\n'
  '\tFrWnd* m_pArtifactCtrl; // "artifact_ctrl" 0x188\n\tFrWnd* m_pArtiFrame; // 0x18c\n\tFrWnd* m_pArtiIcon; // 0x190\n\tFrWnd* m_pArtiBan; // 0x194\n'
  '\tFrWnd* m_pArtiName; // 0x198\n\tFrWnd* m_pArtiDesc; // 0x19c\n\tFrWnd* m_pArtiPrev; // 0x1a0\n\tFrWnd* m_pArtiNext; // 0x1a4\n\tFrGaugeBarImage* m_pOverGauge;\n',
  '983: FrMakeRoomDlg 10 ponteiros novos em 0x180..0x1a4 (m_pOverGauge 0x1a8, m_pHoleTypeBtn 0x1ac, m_chatHole 0x1e8; 28 votos com +48)'),
 # FrWorldTourEventDlg: votos m_mapRect 0x160 -> 0x174 (+20 = 5 x 4), m_mapImage 0x270 -> 0x2d4 (+100), m_pMarkImage
 # 0x408 -> 0x4e4 (+220) e os 10 handlers com +220: MAP_COUNT 17 -> 22
 ('sub', 'src/projectg/worldtoureventdlg.h', '\tstatic const int MAP_COUNT = 17;', '\tstatic const int MAP_COUNT = 22; // 983: 22 (era 17)',
  '983: FrWorldTourEventDlg MAP_COUNT 22 (os 4 vetores crescem; m_pGiftButtonCover 0x4e8, m_pDescDlg 0x50c)'),
 # CPetBody: SetPos (0070a020) grava m_pos em 0x8c e SetRotate m_rot em 0x74 -> 12 B novos em 0x80; Reset (00709e90):
 # `if (byte 0x188) 0x80..0x88 = 1.0f`; SetNextMotion grava m_bNextMotionMove em 0x178, LookUp m_pLookAt em 0x18c
 ('sub', 'src/projectg/petbody.h', '\tWVector m_rot;\n\tWVector m_pos;', '\tWVector m_rot;\n\tWVector m_scaleVec983; // 983: 0x80, posto em (1,1,1) no Reset se m_bScaleVec983; nome meu\n\tWVector m_pos;',
  '983: CPetBody WVector novo em 0x80 (m_pos 0x8c, m_flag 0xd4, m_nextMotion 0x158; 49 votos com +12)'),
 ('sub', 'src/projectg/petbody.h', '\tstd::list<sTexturePart*> m_texPart;\n', '\tstd::list<sTexturePart*> m_texPart;\n\tbool m_bScaleVec983; // 983: byte 0x188 testado no Reset (00709ecc); nome meu\n',
  '983: CPetBody byte novo em 0x188 (m_pLookAt 0x18c, m_lookAngle 0x194, m_lookDest 0x19c)'),
 ('sub', 'src/projectg/petbody.cpp', '\tm_aniSpeed = m_moveScale = 1.0f;\n\tm_nextMotion[0] = \'\\0\';\n}\n#endif',
  '\tm_aniSpeed = m_moveScale = 1.0f;\n\tm_nextMotion[0] = \'\\0\';\n\tif (m_bScaleVec983) // 983: 00709ecc\n\t\tm_scaleVec983.x = m_scaleVec983.y = m_scaleVec983.z = 1.0f;\n}\n#endif',
  '983: CPetBody::Reset repõe o vetor novo'),
 # FrUserInfoForm: "es0_4", "es0_5", "es0_6" (Init 0089b4d0/0089b550/0089b5d0, RTTI de FrEdit) gravam 0x19c, 0x1a0, 0x1a4,
 # logo depois de es0_3 (0x198); es1 passa a 0x1a8 e tudo até m_trophyType (0x278) anda +12: são 19 edits e os 3 novos
 # entram no MEIO do vetor. Um invólucro com operator[] foi testado e piorou o código (8 QUASE -> DIFERENTE): ficam 3 ponteiros no fim do vetor (PROVISÓRIO)
 ('sub', 'src/projectg/userinfoform.h', '\tFrEdit* m_pSpecialEdit[16];\n',
  '\tFrEdit* m_pSpecialEdit[16];\n\tFrEdit* m_pSpecialEdit983[3]; // 983: o vetor tem 19; os 3 novos ("es0_4".."es0_6") são os índices 3..5 DO MEIO.\n'
  '\t// PROVISÓRIO: postos no fim para acertar o que vem depois (+12) sem renumerar os ~70 usos; es1..mh5 seguem 12 B atrás (onda 2)\n',
  '983: FrUserInfoForm +12 depois de m_pSpecialEdit (m_pSpecListBox 0x1dc ... m_trophyType 0x278)'),
 # FrHalloweenEventDlg: votos m_pMapImage 0x254 -> 0x274 (+32 = 2 WRect), m_mapMarkRect 0x2ec -> 0x31c (+48),
 # m_mapFlagVector 0x41c -> 0x46c (+80), m_mapFlag 0x468 -> 0x4c0 (+88): os quatro vetores passam de 19 a 21
 ('sub', 'src/projectg/frhalloweendlg.h', '\tWRect m_mapImageRect[19];', '\tWRect m_mapImageRect[21]; // 983: 21', '983: FrHalloweenEventDlg m_mapImageRect[21] (+32)'),
 ('sub', 'src/projectg/frhalloweendlg.h', '\tconst Bitmap* m_pMapImage[19][2];', '\tconst Bitmap* m_pMapImage[21][2]; // 983: 21', '983: FrHalloweenEventDlg m_pMapImage[21][2] (+48)'),
 ('sub', 'src/projectg/frhalloweendlg.h', '\tWRect m_mapMarkRect[19];', '\tWRect m_mapMarkRect[21]; // 983: 21', '983: FrHalloweenEventDlg m_mapMarkRect[21] (+80)'),
 ('sub', 'src/projectg/frhalloweendlg.h', '\tunsigned long m_mapFlagVector[19];', '\tunsigned long m_mapFlagVector[21]; // 983: 21', '983: FrHalloweenEventDlg m_mapFlagVector[21] (+88)'),
]
