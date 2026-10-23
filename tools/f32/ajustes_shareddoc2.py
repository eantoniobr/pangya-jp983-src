# F3.4 (sessão 31): CSharedDoc — 2ª metade (0x1058c em diante) no layout do 983. Lido por tools/f32/ajustes.py depois do
# ajustes_shareddoc.py. Evidência: out/F3.4/s31/shareddoc_983_2.md (construtor 006498d0, ClearCommonVars 0063d7e0,
# construtores de sRoomInfo 0062f330 e sFriend 0062f420, votos de out/F3.4/s31/docvotos_antes.txt).
G='src/shared/globalgamedefine.h'; H='src/projectg/shareddoc.h'; C='src/projectg/shareddoc.cpp'
P=' (provisório: tamanho medido, lugar/nome não)'
ST='\t// PROVISÓRIO: no 983 não está mais no CSharedDoc; fica estático só para o resto cair no lugar\n'
NEW2 = [
 ('sub', H, '\tunsigned long shotTimeLimit;\n\tunsigned long gameTimeLimit;\n\n\tsGolfGame()',
  '\tunsigned long shotTimeLimit;\n\tunsigned long gameTimeLimit;\n\tunsigned long unk983_118; // 983: zerado no construtor (0x106a4)\n\n\tsGolfGame()',
  '983: sGolfGame 0x118 -> 0x11c (construtor grava 0x1069c, 0x106a0 e 0x106a4)'),
 ('sub', H, '\t\t  gameTimeLimit(0),\n\t\t  holes(18)', '\t\t  gameTimeLimit(0),\n\t\t  unk983_118(0),\n\t\t  holes(18)', 'idem'),
 ('sub', H, '\tunsigned long m_unused47c8;\n\tunsigned long m_unused47cc;',
  '\tunsigned long m_unused47c8;\n\tbool m_unk983_106fc; // 983: o construtor grava 1 aqui (0064aba3)\n\tunsigned long m_unused47cc;',
  '983: m_unused47cc/d0 em 0x10700/0x10704 (construtor), m_replayTargetUID 0x10708 (ClearCommonVars)'+P),
 ('sub', H, '\tstd::list<sGuildTrophy> m_oldGuildTrophyList;\n',
  '\tstd::list<sGuildTrophy> m_oldGuildTrophyList;\n\tstd::list<sSpecialTrophy> m_unk983_108e8; // 983: lista nova, nó de 0x14 (tipo provisório)\n',
  '983: 3ª lista em 0x108e8 (construtor 0064a173); m_roomInfo em 0x108f4'),
 # sRoomInfo: construtor 0062f330
 ('sub', G, '\tchar title[32];\n\tchar password[16];\n\tbool bPublic;',
  '\tchar title[32];\n\tchar password[32]; // 983: +16 antes de bPublic (0x40); em qual dos dois textos, não medido\n\tbool bPublic;',
  '983: sRoomInfo bPublic 0x40, RoomKey 0x45, roomGuid 0x59, tidMatch 0x65, GuildInfo 0x6b (construtor 0062f330)'+P),
 # sessão 48: entrada reescrita — layout do 983 medido em LobbyMain (005092a5..005092eb: Reset(0)/Reset(1) em linha) e nas chamadas
 # de GetEmblem983 dos 2 times (movsx word [+0x20]/[+0x22]); nomes lidos em +0x24/+0x38 (00512343, 00512467, 00aefde8, 00aefe2f)
 ('sub', G, '\tunsigned long nGuildID[2];\n\tchar szName[2][21];\n\tchar szEmblemName[2][12];\n', '\tunsigned long nGuildID[2];\n\tchar szEmblemName[2][12]; // 983: emblemas antes dos nomes (Reset(i) em 005092a5: +8/+0x14)\n\tshort unk983_20[2]; // 983: número (versão?) do emblema de cada time, 2º argumento de GetEmblem983\n\tchar szName[2][20]; // 983: +0x24/+0x38; o total segue 76 (Reset zera 76 bytes só com dwords)\n',
  '983: sGuildRoomInfo 74 -> 76 no layout do 983 (ids, emblemas 2x12, 2 shorts, nomes 2x20)'),
 ('sub', G, '\t\tmemset(szName, 0, sizeof(szName));\n\t\tmemset(szEmblemName, 0, sizeof(szEmblemName));\n',
  '\t\tmemset(szEmblemName, 0, sizeof(szEmblemName));\n\t\tmemset(unk983_20, 0, sizeof(unk983_20));\n\t\tmemset(szName, 0, sizeof(szName));\n',
  '983: sGuildRoomInfo::Reset() zera os 76 bytes'),
 ('sub', G, '\t\tnGuildID[index] = 0;\n\t\tszName[index][0] = 0;\n', '\t\tnGuildID[index] = 0;\n\t\tunk983_20[index] = 0;\n\t\tszName[index][0] = 0;\n',
  '983: sGuildRoomInfo::Reset(i) zera também o short (005092b1, 005092de)'),
 ('sub', G, '\tint masterUID;\n\tunsigned char realGameType;\n\n\tsRoomInfo()',
  '\tint masterUID;\n\tunsigned char unk983_c3; // 983: +1 entre GuildInfo e realGameType (lugar provisório)\n\tunsigned char realGameType;\n'
  '\tunsigned long unk983_c5[6]; // 983: 24 bytes zerados no construtor\n\n\tsRoomInfo()',
  '983: realGameType 0xc4, 6 dwords novos em 0xc5; sizeof 178 -> 221 (m_directMoveType em 0x11375, 2 votos)'),
 ('sub', G, '\t\trealGameType = 0;\n\t\troomGuid = 0xffff;', '\t\trealGameType = 0;\n\t\tmemset(unk983_c5, 0, sizeof(unk983_c5));\n\t\troomGuid = 0xffff;', 'idem'),
 # (s47) o campo novo fica ANTES do nome do emblema: FrUserListDlg::OnUserListOwnerDraw (00af98f0) chama GetEmblem983([+0x2e], [+0x32])
 ('sub', G, '\tunsigned long m_GuildId;\n\tchar szEmblemName[12];\n\tunsigned short state;\n',
  '\tunsigned long m_GuildId;\n\tunsigned long unk983_32; // 983: numero do emblema, logo depois de m_GuildId (00af9bd4); state em +0x42\n'
  '\tchar szEmblemName[12];\n\tunsigned short state;\n',
  '983: sBriefUserInfo 196 -> 200 (nó do m_briefUserInfoMap 0xd8 -> 0xdc)'+P),
 ('sub', G, '\tunsigned long Type;\n\tint Property;\n\n\tbool operator==(const unsigned char& channel) const',
  '\tunsigned long Type;\n\tint Property;\n\tunsigned char unk983_4d[8]; // 983: +8 depois de Type (lugar provisório)\n\n\tbool operator==(const unsigned char& channel) const',
  '983: sChannelInfo 77 -> 85 (m_curChannel 0x10a54, m_curGameServer 0x10aa9; Type continua em +0x45)'+P),
 ('sub', G, '\tunsigned char IsInvite : 1;\n\tunsigned char guestReserved : 7;\n',
  '\tunsigned char IsInvite : 1;\n\tunsigned char guestReserved : 7;\n\tfloat unk983_155;          // 983 (sessão 45): cauda medida no construtor 00500360\n\tunsigned char unk983_159;\n\tunsigned short unk983_15a;\n',
  '983: nó de list<sSlotInfo> 0x15c -> 0x164'+P),
 ('sub', G, '\tunsigned long dwGuildId;\n\tchar szEmblemName[12];\n\tsUserPosition userPosition;',
  '\tunsigned long dwGuildId;\n\tunsigned long unk983_31; // 983: zerado no Clear (0062f457)\n\tchar szEmblemName[12];\n\tsUserPosition userPosition;',
  '983: sFriend 141 -> 145, userPosition em +0x41 (construtor 0062f420)'),
 ('sub', G, '\t\tdwGuildId = 0xffffffff;\n\n\t\tmemset(szEmblemName, 0, sizeof(szEmblemName));',
  '\t\tdwGuildId = 0xffffffff;\n\t\tunk983_31 = 0;\n\n\t\tmemset(szEmblemName, 0, sizeof(szEmblemName));', 'idem'),
 ('sub', 'src/projectg/hatmanager.h', '\tbool m_bUnused;\n\tunsigned char m_reserved[0x15];\n',
  '\tbool m_bUnused;\n\tunsigned char m_reserved[0x15];\n\tunsigned char m_unk983_tail[60]; // 983: sizeof 56 -> 116 (campos não medidos)\n',
  '983: m_chatManager 0x10c24, m_chatLineList 0x10c98'+P),
 ('sub', H, '\tstd::list<sGameServerInfo> m_gameServerList;\n\tstd::vector<sGameServerInfo> m_gameServerVector;',
  '\tstd::list<sGameServerInfo> m_gameServerList;\n\tstd::map<int, int> m_unk983_10a20; // 983: objeto novo de 16 B (construtor 006441a0; tipo provisório)\n'
  '\tstd::vector<sGameServerInfo> m_gameServerVector;', '983: m_gameServerVector em 0x10a30'+P),
 ('sub', H, '\tstd::string m_chatModeName;\n\tstd::string m_packetNickname;\n\tstd::string m_nicknameSuffix;\n\tunsigned long m_controlServerService;\n',
  '\tstd::string m_chatModeName;\n' + ST + '\tstatic std::string m_packetNickname;\n\tstatic std::string m_nicknameSuffix;\n'
  '\tunsigned long m_controlServerService;\n\tunsigned long m_unk983_10d28[2]; // 983: 12 B entre m_chatModeName e m_offlinePlay\n',
  '983: sem as duas strings (o construtor não as inicia); m_offlinePlay 0x10d30'+P),
 ('sub', C, '\t: m_maxWhisperPartner(8), m_nicknameSuffix(""), m_serverProperty(0)', '\t: m_maxWhisperPartner(8), m_serverProperty(0)', 'idem'),
 ('sub', C, '\nstd::list<sGiftInfo> CSharedDoc::m_giftList;',
  '\nstd::string CSharedDoc::m_packetNickname; // provisórios (ver shareddoc.h)\nstd::string CSharedDoc::m_nicknameSuffix("");\n'
  'unsigned long CSharedDoc::m_cardPackPageNum, CSharedDoc::m_cardPackSelPageNum, CSharedDoc::m_cardPackCurPage, CSharedDoc::m_cardPackMode;\n'
  'bool CSharedDoc::m_bCardPackRebuild, CSharedDoc::m_bRmrTabPending;\nunsigned char CSharedDoc::m_cardPackSlot, CSharedDoc::m_cardPackItem;\n'
  'unsigned short CSharedDoc::m_rmrTabValue;\nsStall CSharedDoc::m_stallItem;\nstd::list<sStall> CSharedDoc::m_listStallItem;\n'
  'std::list<sSaleItem> CSharedDoc::m_maketList;\nstd::list<sGiftInfo> CSharedDoc::m_giftList;', 'definições dos estáticos provisórios'),
 ('sub', H, '\tunsigned char m_guildTeam;\n\tstd::string m_authTicket;',
  '\tunsigned char m_guildTeam;\n\tstd::vector<int> m_unk983_10fe8; // 983: dois vetores novos (tipo provisório)\n\tstd::vector<int> m_unk983_10ff8;\n\tstd::string m_authTicket;',
  '983: m_authTicket 0x11008, m_pGolfDoc 0x11024 (134 votos)'),
 ('sub', H, '\tunsigned long m_cardPackPageNum;\n\tunsigned long m_cardPackSelPageNum;\n\tunsigned long m_cardPackCurPage;\n\tunsigned long m_cardPackMode;\n'
  '\tbool m_bCardPackRebuild;\n\tunsigned char m_cardPackSlot;\n\tunsigned char m_cardPackItem;\n\tunsigned short m_rmrTabValue;\n\tbool m_bRmrTabPending;\n',
  ST + '\tstatic unsigned long m_cardPackPageNum;\n\tstatic unsigned long m_cardPackSelPageNum;\n\tstatic unsigned long m_cardPackCurPage;\n\tstatic unsigned long m_cardPackMode;\n'
  '\tstatic bool m_bCardPackRebuild;\n\tstatic unsigned char m_cardPackSlot;\n\tstatic unsigned char m_cardPackItem;\n\tstatic unsigned short m_rmrTabValue;\n\tstatic bool m_bRmrTabPending;\n',
  '983: ClearCommonVars (0063d7e0) só zera 0x11028, 0x11030, 0x11034 (byte) e 0x11038 entre m_pGolfDoc e m_realEquip; m_mapEventList 0x110b0'),
 ('sub', H, '\tunsigned char m_tradeMode;\n\tsStall m_stallItem;\n\tstd::list<sStall> m_listStallItem;\n\tstd::list<sSaleItem> m_maketList;\n',
  '\tunsigned char m_tradeMode;\n' + ST + '\tstatic sStall m_stallItem;\n\tstatic std::list<sStall> m_listStallItem;\n\tstatic std::list<sSaleItem> m_maketList;\n',
  '983: m_tradeTitle 0x111f4, m_bHaveHalloweenItem 0x11220, m_replayState 0x11224 (votos): a barraca (2.343 B + 2 listas) saiu'),
 ('sub', H, '\tchar m_fileName[32];\n\tunsigned long m_replayPosition;',
  '\tchar m_fileName[32];\n\tunsigned long m_unk983_11250;\n\tstd::string m_unk983_11254; // 983: string nova (construtor 0064a657)\n'
  '\tunsigned long m_replayPosition; // 983: o construtor zera 0x11270 com fldz/fstp (talvez float)',
  '983: m_replayShotIndex 0x1127c, m_replayVersion 0x11284 (votos)'),
 ('sub', H, '\tunsigned long m_serverTimeTick;\n\tunsigned char m_unused5bdc;\n', '\tunsigned long m_serverTimeTick; // 983: 0x11288\n',
  '983: m_inviteRoomInfo em 0x11298 (construtor de sRoomInfo em 0064a669): 4 bytes a menos depois de m_serverTimeTick'+P),
 ('sub', H, '\tstd::map<std::string, std::list<std::string> > m_visGroupMap;\n\tbool m_goStopMode;\n',
  '\tstd::map<int, int> m_unk983_113e0; // 983: 3 objetos novos de 16 B (construtores 00644280, 00643410 x2; tipo provisório)\n'
  '\tstd::map<int, int> m_unk983_113f0;\n\tstd::map<int, int> m_unk983_11400;\n\tbool m_unk983_11410; // 983: zerado no ClearCommonVars\n'
  '\tbool m_goStopMode; // 983: 0x11411 (construtor 0064ac54)\n\tstd::map<std::string, std::list<std::string> > m_visGroupMap; // 983: 0x11414 (2 votos)\n',
  '983: m_appGiftDownloadState 0x11424 (ClearCommonVars), m_unused5d0c 0x11428, m_cardStackList 0x1142c (5 votos)'),
 ('sub', H, '\tstd::list<sBurnningSpCard> m_burnningSpCardList;\n\tbool m_bNeedFirstLoginAlarm;\n};',
  '\tstd::list<sBurnningSpCard> m_burnningSpCardList;\n\tbool m_bNeedFirstLoginAlarm; // 983: 0x11444\n'
  '\t// 983: cauda nova até 0x11644. Só os tamanhos e os WCrypticValue (construtor 0062bfc0) são medidos.\n'
  '\tunsigned char m_unk983_11445[0x13];\n\tbool m_unk983_11458;\n\tunsigned long m_unk983_1145c[3];\n\tunsigned short m_unk983_11468;\n\tunsigned char m_unk983_1146a;\n'
  '\tunsigned long m_unk983_1146c[4]; // objeto de 16 B (construtor 00643490)\n\tunsigned long m_unk983_1147c[19]; // objeto (construtor 00b3d270) + 4 dwords em 0x114b8\n'
  '\tWCrypticValue<unsigned char> m_unk983_114c8[19];\n\tWCrypticValue<unsigned char> m_unk983_115f8;\n\tunsigned char m_unk983_11608[4];\n'
  '\tstd::string m_unk983_1160c;\n\tunsigned long m_unk983_11628[2]; // objeto (construtor 00589b50)\n\tunsigned long m_unk983_11630;\n\tunsigned long m_unk983_11634;\n'
  '\tunsigned long m_unk983_11638;\n\tunsigned long m_unk983_1163c;\n\tbool m_unk983_11640;\n};',
  '983: sizeof(CSharedDoc) >= 0x11644 (último campo gravado no construtor: 0x11640)'+P),
 ('sub', C, '\tm_bTutorialRedirect = false;\n\tm_unused5bdc = 0;\n', '\tm_bTutorialRedirect = false; // 983: a gravação de m_unused5bdc saiu\n',
  '983: ClearCommonVars grava 0x110ca e logo 0x10708; não há a gravação do m_unused5bdc (confirma que o campo saiu)'),
]
