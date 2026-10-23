# F3.5 (sessão 46): sRivalData no layout do 983 (sizeof 0x190 -> 0x1b8), medido no construtor do 983 00544f90 (fora de linha, 5
# chamadores; zera campo a campo), em CIntrusion::PlayersUpdate 008567d0 (monta o registro na pilha) e em
# CIntrusion::RivalDataUpdate 00856370 (holeScore +0x38, holeStroke +0x80, holePang +0x98, totalPang +0x128, totalScore +0x14c,
# totalStroke +0x150, hole +0x151). Lido por tools/f32/ajustes.py no fim.
S = 'src/projectg/shareddoc.h'
NEW14 = [
 ('sub', S, '\tchar nickname[22];\n\tchar guildName[21];\n\tunsigned char team;',
  '\tchar nickname[22];\n\tchar guildName[20]; // 983: 21 -> 20 (team em +0x32)\n\tunsigned char team;',
  '983: sRivalData::guildName tem 20 bytes'),
 ('sub', S, '\t__int64 totalBonusPang;\n\tint totalScore;',
  '\t__int64 totalBonusPang;\n\t__int64 unk983_138; // 983: 0x14 bytes novos (totalScore em +0x14c); tipos supostos\n'
  '\t__int64 unk983_140;\n\tint unk983_148;\n\tint totalScore;',
  '983: sRivalData ganha 0x14 bytes antes de totalScore'),
 ('sub', S, '\tunsigned long guildUID;\n\tchar guildMark[12];\n\tunsigned long guildPoint;',
  '\tunsigned long guildUID;\n\tunsigned long unk983_178; // 983: recebe sSlotInfo::unk983_68 (guildMark em +0x17c)\n\tchar guildMark[12];\n\tunsigned long guildPoint;',
  '983: sRivalData ganha 4 bytes antes de guildMark'),
 ('sub', S, '\tunsigned char pangMastery;\n\tunsigned char pangNitro;\n};',
  '\tunsigned char pangMastery;\n\tunsigned char pangNitro;\n'
  '\tunsigned long unk983_1a4; // 983: cauda nova (sizeof 0x1b8)\n\tunsigned char unk983_1a8;\n\tunsigned long unk983_1ac;\n'
  '\tfloat unk983_1b0;\n\tunsigned char unk983_1b4;\n\tunsigned short unk983_1b6;\n\n'
  '\t// 983: função 00544f90 (fora de linha, sem valor de retorno: não é construtor; uid e oid ficam como estão). Nome meu.\n\tvoid Clear983()\n\t{\n'
  '\t\tmemset(nickname, 0, sizeof(nickname));\n\t\tmemset(guildName, 0, sizeof(guildName));\n'
  '\t\tteam = 0;\n\t\tlevel = 0;\n\t\tstate = 0;\n'
  '\t\tmemset(holeScore, 0, sizeof(holeScore));\n\t\tmemset(holeStroke, 0, sizeof(holeStroke));\n'
  '\t\tmemset(holePang, 0, sizeof(holePang));\n'
  '\t\ttotalPang = 0;\n\t\ttotalBonusPang = 0;\n\t\tunk983_138 = 0;\n\t\tunk983_140 = 0;\n\t\tunk983_148 = 0;\n'
  '\t\ttotalScore = 0;\n\t\ttotalStroke = 0;\n\t\thole = 0;\n\t\trank = 0;\n\t\torder = 0;\n\t\tquitOrder = 0;\n\t\tfinishOrder = 0;\n'
  '\t\tballPos = WVector::ZERO;\n\t\tobserverState = 0;\n\t\tobserverRank = 0;\n\t\ttitleTypeId = 0;\n\t\tflag = 0;\n'
  '\t\tguildUID = 0;\n\t\tunk983_178 = 0;\n\t\tmemset(guildMark, 0, sizeof(guildMark));\n'
  '\t\tguildPoint = 0;\n\t\tmemset(&approachDistance, 0, 8); // 983: os dois campos de distância num memset só\n\t\tapproachTime = 0;\n'
  '\t\tcapability = 0;\n\t\tmascotTypeId = 0;\n\t\tmemset(&pangMastery, 0, 2);\n'
  '\t\tunk983_1b0 = 0.0f;\n\t\tunk983_1a4 = 0;\n\t\tunk983_1a8 = 0;\n\t\tunk983_1ac = 0;\n\t\tunk983_1b4 = 0;\n\t\tmemset(&unk983_1b6, 0, sizeof(unk983_1b6));\n\t}\n};',
  '983: sRivalData com cauda nova de 0x16 bytes e função que zera'),
 ('sub', 'src/projectg/netresourcemanager.h', '\tconst Bitmap* GetEmblemByName(const char* name);\n',
  '\tconst Bitmap* GetEmblemByName(const char* name);\n'
  '\t// 983: 009ab3e0, 59 chamadas; toma o lugar do GetEmblemByName(guildMark) nas telas (nome meu)\n'
  '\tconst Bitmap* GetEmblem983(unsigned long guildUID, unsigned long emblem);\n',
  '983: NetResourceManager ganha a busca de emblema por (guildUID, número)'),
]
