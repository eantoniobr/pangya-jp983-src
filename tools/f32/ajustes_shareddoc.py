# F3.4 (sessão 30): CSharedDoc e structs de usuário no layout do 983 — 1ª metade (até 0x10464).
# Evidência: out/F3.4/s30/ (construtor 006498d0 desmontado, pares de deslocamento, docvotos). Lido por tools/f32/ajustes.py.
G='src/shared/globalgamedefine.h'; H='src/projectg/shareddoc.h'; C='src/projectg/shareddoc.cpp'
P=' (provisório: tamanho medido, lugar/nome não)'
NEW = [
 ('sub', G, '\tchar szEmblemName[12];\n\tunsigned long school;\n',
  '\tchar szEmblemName[12];\n\tunsigned char unk983_4d[31]; // 983: +31 entre sNick e dwIdentity (lugar provisório)\n\tunsigned long school;\n',
  '983: sPangYaUserInfo 269 -> 301: dwIdentity anda +31 (m_myInfo+0x53 -> 0x812, 15 votos)'+P),
 ('sub', G, '\tunsigned char Reserved : 7;\n\tshort iBongdariShopUsableTimes;',
  '\tunsigned char Reserved : 7;\n\tunsigned char unk983_flag; // 983: +1 entre dwGuid e dwUID (lugar provisório)\n\tshort iBongdariShopUsableTimes;',
  '983: dwUID anda +32 (m_myInfo+0x10b -> 0x8cb, 6 votos)'+P),
 ('sub', G, '\tfloat fLongestChipIn;\n\tunsigned long dwExp;\n',
  '\tfloat fLongestChipIn;\n\tunsigned long unk983_46; // 983: +4 antes de Level (lugar provisório)\n\tunsigned long dwExp;\n',
  '983: sPangYaUserStatistics 235 -> 265 (m_oldSeasonStatistics 0x10779 .. m_oldSeasonTrophy 0x10882); Level anda +4 (9 votos)'+P),
 ('sub', G, '\tunsigned long dwSeasonCount;\n\t__int64 i64SumPang;\n};',
  '\tunsigned long dwSeasonCount;\n\t__int64 i64SumPang;\n\tunsigned char unk983_tail[26]; // 983: +26 depois de dwSkinsWin (lugar provisório)\n};',
  '983: sPangYaUserStatistics +26 na cauda'+P),
 ('sub', G, '\tunsigned long tidSkin[6];\n\tunsigned long guidMascot;\n};',
  '\tunsigned long tidSkin[6];\n\tunsigned long guidMascot;\n\tunsigned long poster[2]; // 983: +8 depois de guidMascot (nome provisório)\n};',
  '983: sUserEquip 108 -> 116 (guidMascot +62, mapStat +70 dentro do sMyInfo)'),
 ('sub', G, '\tunsigned long tid;\n\tunsigned long guid;\n\tunsigned long tidParts[24];\n\tunsigned char hairClr;\n\tunsigned char shirtsClr : 4;\n\tunsigned char gift_flag : 4;\n\tchar PCL[5];\n\tchar Purchase;\n\tunsigned long tidAuxParts[5];\n\tchar UccIndexList[24][9];\n\tunsigned long ItemIdList[24];\n',
  '\t// 983: 513 bytes (nó do m_charMap = 0x218); tidParts em +12 e tidAuxParts em +420 (votos). A ordem dos campos\n'
  '\t// sem voto (os 4 bytes de +8, ItemIdList/UccIndexList, cutIn, PCL, mastery, cards) é provisória.\n'
  '\tunsigned long tid;\n\tunsigned long guid;\n\tunsigned char hairClr;\n\tunsigned char shirtsClr : 4;\n\tunsigned char gift_flag : 4;\n\tunsigned char unk983_a;\n\tchar Purchase;\n'
  '\tunsigned long tidParts[24];\n\tunsigned long ItemIdList[24];\n\tchar UccIndexList[24][9];\n\tunsigned long tidAuxParts[5];\n'
  '\tunsigned long cutIn[4];\n\tchar PCL[5];\n\tunsigned long mastery;\n\tunsigned long card[3][4];\n',
  '983: sCharacterInfo 444 -> 513 (push 0x218 no nó do m_charMap, 00649a4f)'),
 ('sub', G, '\tsMapStatistics mapStat[20];\n\tsMapStatistics classicMapStat[20];\n};\n\nstruct sCaddieInfo',
  '\tsMapStatistics mapStat[20];\n\tsMapStatistics classicMapStat[20];\n'
  '\tsMapStatistics unk983MapStat[224]; // 983: 264 no total, num laço só (00649a00); a divisão em vetores é provisória\n};\n\nstruct sCaddieInfo',
  '983: sMyInfo tem 0x108 sMapStatistics (laço de 0x108 x 0x2b em 006499f1); sizeof 2412 -> 12114'),
 ('sub', G, '\tunsigned long tid;\n\tshort PCL[5];\n};',
  '\tunsigned long tid;\n\tshort PCL[5];\n\tshort unk983_12[5]; // 983: +10 (nome provisório)\n};',
  '983: sClubInfo 18 -> 28 (mascotInfo.tid anda +10 a mais que clubInfo.tid no sUserInfo)'),
 ('sub', G, '\t_SYSTEMTIME endDate;\n\tbool PCBangMascot;\n};',
  '\t_SYSTEMTIME endDate;\n\t// 983: 62 bytes (sUserInfo = 12742); o byte que saiu é provisoriamente o PCBangMascot\n};',
  '983: sMascotInfo 63 -> 62 (4 x sUserInfo = 0x38b0..0xffc8)'+P),
 ('sub', 'src/projectg/mascotinfodlg.cpp', 'CLoginInfo::Instance()->IsPcBang() && m_mascotInfo.PCBangMascot)',
  'CLoginInfo::Instance()->IsPcBang() && REBANG_983_PCBANG_MASCOT(m_mascotInfo))', '983: sMascotInfo sem PCBangMascot; condição a rever no 983'),
 ('sub', G, 'struct sUserInfo : public sMyInfo\n{',
  '#define REBANG_983_PCBANG_MASCOT(info) false // 983: campo saiu do sMascotInfo; rever FrMascotInfoDlg no 983\n\nstruct sUserInfo : public sMyInfo\n{',
  'idem'),
 ('sub', G, '\tunsigned short CharacterSlotNum;\n\tunsigned short CaddieSlotNum;\n\n\tsItemInfo()',
  '\tunsigned short CharacterSlotNum;\n\tunsigned short CaddieSlotNum;\n\tunsigned char unk983_tail[28]; // 983: +28 (lugar provisório)\n\n\tsItemInfo()',
  '983: sItemInfo 168 -> 196 (nó de list<sItemInfo> = 0xcc em 00649b36 e mais 9 listas; sRecordedItemInfo 0x104)'+P),
 ('sub', G, 'struct sGuildMatchFlagInfo\n{\n\tunsigned char reserved[0x2e];', 'struct sGuildMatchFlagInfo\n{\n\tunsigned char reserved[0x32]; // 983: nó de 0x3c',
  '983: nó de list<sGuildMatchFlagInfo> 0x38 -> 0x3c (push em 0x10460 do construtor)'+P),
 ('sub', 'src/shared/itemmanager.h', '\tbool IsNonVisibleItem(unsigned long typeId);\n\tbool IsSubScriptionCoupon(unsigned long typeId);\n};',
  '\tbool IsNonVisibleItem(unsigned long typeId);\n\tbool IsSubScriptionCoupon(unsigned long typeId);\n\n'
  '\tunsigned char m_unk983_tail[784]; // 983: sizeof 644 -> 1428; os campos novos ficam no meio (não medido)\n};',
  '983: CItemManager ocupa 0x20c..0x7a0 no CSharedDoc (m_myInfo começa em 0x7a0)'+P),
 ('sub', H, '\tCPartTidList partTidList;\n\tsCharacterInfo charInfo;\n\n',
  '\tCPartTidList partTidList;\n\tsCharacterInfo charInfo;\n\tunsigned long unk983[2]; // 983: +8 além do sCharacterInfo (lugar provisório)\n\n',
  '983: nó do m_roomSlotMap 0x2a4 -> 0x2f0'+P),
 ('sub', H, '\tsGameTypeInfo m_gameTypeInfo[15];', '\tsGameTypeInfo m_gameTypeInfo[20]; // 983: +40 entre m_roomDetail e m_serverTime',
  '983: strings de 0x168/0x188/0x1a8 em 0x190/0x1b0/0x1d0 (construtor 0064994e)'+P),
 ('sub', H, '\tunsigned char m_unused1c4;\n\tint m_gachaTicket[2];', '\tint m_gachaTicket[2]; // 983: 0x1ec/0x1f0, sem o byte de 0x1c4',
  '983: m_refreshGuidList em 0x1f4 (+36, não +40)'),
 ('sub', C, '\tm_unused1c4 = 0;\n', '', '983: campo não existe'),
 ('sub', H, '\tsMyInfo m_myInfo;\n\tunsigned char m_userInfoExt[0x400];\n', '\tsMyInfo m_myInfo; // 983: 0x7a0..0x36f2; o bloco de 0x400 que vinha depois saiu\n',
  '983: m_stringMap em 0x36f4, logo depois do sMyInfo'),
 ('sub', H, '\tstd::list<sGiftInfo> m_giftList;\n\tstd::list<sGiftInfo> m_sendGiftList;\n',
  '\t// 983: entre m_setItemList (0x3780) e m_specialTrophyList (0x37a4) há só 2 listas, as duas com nó de 0xcc.\n'
  '\t// PROVISÓRIO: quais duas das quatro do 645 ficaram não foi medido; as de presente viram estáticas só para o\n'
  '\t// resto do CSharedDoc cair no lugar (rever em giftalarmdlg/realmyroomtask do 983).\n'
  '\tstatic std::list<sGiftInfo> m_giftList;\n\tstatic std::list<sGiftInfo> m_sendGiftList;\n',
  '983: 2 listas a menos nessa faixa (construtor 00649c62..00649cc8)'+P),
 ('sub', C, '\nCSharedDoc::CSharedDoc()', '\nstd::list<sGiftInfo> CSharedDoc::m_giftList; // provisório (ver shareddoc.h)\nstd::list<sGiftInfo> CSharedDoc::m_sendGiftList;\n\nCSharedDoc::CSharedDoc()',
  'idem'),
 ('sub', H, '\tstd::list<sQuest> m_questList;\n\t__int64 m_cookie;\n',
  '\tstd::list<sQuest> m_questList;\n'
  '\t// 983: 5 listas em 0x381c..0x3858 (nós 0x4c, 0x14, 0x18, 0x18, 0x110); qual delas é a m_questList não foi medido\n'
  '\tstruct sUnk983_c { unsigned char b[12]; };\n\tstruct sUnk983_10 { unsigned char b[16]; };\n\tstruct sUnk983_108 { unsigned char b[264]; };\n'
  '\tstd::list<sUnk983_c> m_unk983_3828;\n\tstd::list<sUnk983_10> m_unk983_3834;\n\tstd::list<sUnk983_10> m_unk983_3840;\n\tstd::list<sUnk983_108> m_unk983_384c;\n'
  '\t__int64 m_cookie;\n\t__int64 m_unk983_3860; // 983: zerado junto com m_cookie (0x3858) e m_cash (0x3868)\n',
  '983: 4 listas novas depois de m_cardAbilityList e 8 bytes entre m_cookie e m_cash (construtor)'+P),
 ('sub', H, '\tstd::vector<sCaddieReportData> m_caddieReportList;\n\tstd::vector<sGuildMatchup> m_guildMatchupList;',
  '\tstd::vector<sCaddieReportData> m_caddieReportList;\n\tint m_unk983_1044c; // 983: 4 bytes entre os dois vetores\n\tstd::vector<sGuildMatchup> m_guildMatchupList;',
  '983: m_guildMatchupList em 0x10450 (+48772), m_caddieReportList em 0x1043c (+48768)'+P),
]
