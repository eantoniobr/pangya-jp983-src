# F3.5 (sessão 45): sSlotInfo no layout do 983, medido no construtor 00500360 (sizeof 0x15c = push em 00856d1b) e em
# CGolfRuleApproach::SetPlayer 006a98e0 (sGuild +0x1a, connectionRank +0x2e, pangma +0xce). Lido por tools/f32/ajustes.py no fim.
G = 'src/shared/globalgamedefine.h'
NEW13 = [
 ('sub', G, '\tchar sNick[22];\n\tchar sGuild[21];\n\tunsigned char connectionRank;',
  '\tchar sNick[22];\n\tchar sGuild[20]; // 983: 21 -> 20 (connectionRank em +0x2e)\n\tunsigned char connectionRank;',
  '983: sSlotInfo::sGuild tem 20 bytes'),
 ('sub', G, '\tchar szEmblemName[12];\n\tunsigned long dwUserUID;\n\tunsigned long state;',
  '\tchar szEmblemName[12];\n\tunsigned long unk983_68; // 983: 4 bytes novos (dwUserUID em +0x6c)\n\tunsigned long dwUserUID;\n\tunsigned long state;',
  '983: sSlotInfo ganha 4 bytes antes de dwUserUID'),
 ('sub', G, '\t\tmemset(tidSkin, 0, sizeof(tidSkin));\n\t}\n\n\tbool operator==(const unsigned long& id) const { return dwGuid == id; }',
  '\t\tmemset(tidSkin, 0, sizeof(tidSkin));\n\n\t\tunk983_155 = 0.0f; // 983\n\t\tunk983_159 = 0;\n\t\tunk983_15a = 0;\n\t}\n\n\tbool operator==(const unsigned long& id) const { return dwGuid == id; }',
  '983: o construtor do sSlotInfo zera a cauda nova'),
]
