# F3.4 (sessão 35): FrUserInfoForm no layout do 983, lido no construtor 008a7610 (sizeof 0x5d40 = push antes do operator new
# em 008a90c5/008a9190) e nos handlers de Init dos controles de troféu. Lido por tools/f32/ajustes.py no fim.
# Evidência: out/F3.4/s35/classes_983.md.
import re
_UIF = 'src/projectg/userinfoform.h'
NEW7 = [
 # bloco de troféus: no 983 é um sub-objeto de 0x34 em 0x27c (construtor 0089a940 -> Clear 00899940 zera 13 dwords) com
 # SetButton(i, p) 00899970 [+0 + i*4], SetListBox(i, p) 00899980 [+0x10 + i*4], SetEdit(i, p) 008999a0 [+0x20 + i*4],
 # SetNoTrophy(p) 008999c0 [+0x30]; índices: 0 normal, 1 especial, 2 gp normal, 3 gp especial (handlers 0089e0f0..0089e860)
 ('sub', _UIF, '\tint m_reserved270;\n\tFrButton* m_pTrophyBtn[2];\n\tFrListBox* m_pSpecialTrophyBox;\n\tFrListBox* m_pNormalTrophyBox;\n'
  '\tFrStatic* m_pNoTrophy;\n\tFrEdit* m_pNormalTrophyNum;\n\tFrEdit* m_pSpecialTrophyNum;\n',
  '\t// 983: sub-objeto de troféus em 0x27c (13 ponteiros; métodos 00899940..00899a2f). PROVISÓRIO: campos soltos na ordem do 983,\n'
  '\t// sem a classe nem os setters fora de linha (onda 2); m_reserved270 saiu\n'
  '\tFrButton* m_pTrophyBtn[4]; // 983: 0x27c; [2], [3] = "btn_gp_normal", "btn_gp_special"\n'
  '\tFrListBox* m_pNormalTrophyBox; // 983: 0x28c\n\tFrListBox* m_pSpecialTrophyBox; // 983: 0x290\n'
  '\tFrListBox* m_pGpTrophyBox983[2]; // 983: 0x294 "listbox_gp_normal", "listbox_gp_special"; nome meu\n'
  '\tFrEdit* m_pNormalTrophyNum; // 983: 0x29c\n\tFrEdit* m_pSpecialTrophyNum; // 983: 0x2a0\n'
  '\tFrEdit* m_pGpTrophyNum983[2]; // 983: 0x2a4 "edit_gp_normal", "edit_gp_special"; nome meu\n'
  '\tFrStatic* m_pNoTrophy; // 983: 0x2ac\n',
  '983: FrUserInfoForm bloco de troféus de 0x34 em 0x27c (m_pGuildEdit 0x2b0 ... m_pGuildIcon 0x2cc)'),
 ('sub', 'src/projectg/user_info.cpp', '\tm_reserved270 = 0;\n', '', '983: FrUserInfoForm sem m_reserved270'),
 # m_userInfo começa em 0x300 (memset de 0x31c6 em 008a7a09): entre m_pGuildIcon (0x2cc) e ele há 0x30, não 0x34
 ('sub', _UIF, '\tunsigned char m_reserved2b0[0x30];\n',
  '\tunsigned char m_reserved2b0[0x2c]; // 983: 0x2c (PROVISÓRIO: "Btn_rmrvisitor" não existe no mapa do 983; o botão pode ter saído)\n',
  '983: FrUserInfoForm m_userInfo em 0x300'),
 # listas: 0x34c8 (nó 0x14), 0x34d4 (nó 0xc), 0x34e0 (nó 0x14), 0x34ec (nó 0x18); m_oldSeason 0x34f8
 ('sub', _UIF, '\tstd::list<sGuildTrophy> m_guildTrophy;\n\tsSeasonStat m_oldSeason;\n',
  '\tstd::list<sGuildTrophy> m_guildTrophy;\n'
  '\tstd::list<sSpecialTrophy> m_gpSpecialTrophy983; // 983: 0x34e0, nó de 0x14 (tipo pelo tamanho; nome meu)\n'
  '\tstd::list<sGpTrophy983> m_gpTrophy983; // 983: 0x34ec, nó de 0x18 (elemento de 16 B; nome meu)\n'
  '\tsSeasonStat m_oldSeason;\n',
  '983: FrUserInfoForm duas listas novas (m_oldSeason 0x34f8)'),
 # sSeasonStat: construtor 008a5b90 — mapStatistics em +0x109 com 22 elementos, listas em +0x50c (nó 0x14), +0x518 (0xc),
 # +0x524 (0x14); sizeof 0x530 (m_totalSeason 0x3a28 - m_oldSeason 0x34f8)
 ('sub', _UIF, '\tstruct sSeasonStat\n\t{\n\t\tsPangYaUserStatistics statistics;\n\t\tsMapStatistics mapStatistics[20];\n'
  '\t\tsTrophyStatistics trophy;\n\t\tstd::list<sSpecialTrophy> specialTrophy;\n\t\tstd::list<sGuildTrophy> guildTrophy;\n',
  '\tstruct sGpTrophy983 { unsigned long v[4]; }; // 983: elemento de 16 B da lista de 0x34ec (campos não medidos)\n'
  '\tstruct sSeasonStat\n\t{\n\t\tsPangYaUserStatistics statistics;\n\t\tsMapStatistics mapStatistics[22]; // 983: 22 (+0x109)\n'
  '\t\tsTrophyStatistics trophy;\n\t\tstd::list<sSpecialTrophy> specialTrophy;\n\t\tstd::list<sGuildTrophy> guildTrophy;\n'
  '\t\tstd::list<sSpecialTrophy> gpSpecialTrophy983; // 983: +0x524, nó de 0x14; nome meu\n',
  '983: sSeasonStat 0x530 (22 mapas, 3ª lista)'),
 ('sub', _UIF, '\t\t\tfor (int i = 0; i < 20; ++i)\n\t\t\t{\n\t\t\t\tmapStatistics[i].cBestScore = 0x7f;',
  '\t\t\tfor (int i = 0; i < 22; ++i) // 983: 22\n\t\t\t{\n\t\t\t\tmapStatistics[i].cBestScore = 0x7f;', '983: sSeasonStat::Clear com 22 mapas'),
 # vetores de mapas: 0x3fa3, 0x4355, 0x4707 com 22 (laços de 0x16 e memset de 0x3b2 no construtor); m_pBestScoreMap 0x4abc;
 # 0x4ad0..0x4af4 dez dwords zerados; 0x4af8 22 x {dword, byte}; 0x4b66, 0x4f18, 0x52ca, 0x567c mais 4 vetores de 22; m_guildPang 0x5a30
 ('sub', _UIF, '\tsMapStatistics m_classicMapStatistics[20];\n\tsMapStatistics m_oldClassicMapStatistics[20];\n'
  '\tsMapStatistics m_totalClassicMapStatistics[20];\n\tsMapStatistics* m_pBestScoreMap[5];\n',
  '\tsMapStatistics m_classicMapStatistics[22]; // 983: 0x3fa3, 22\n\tsMapStatistics m_oldClassicMapStatistics[22]; // 983: 0x4355\n'
  '\tsMapStatistics m_totalClassicMapStatistics[22]; // 983: 0x4707\n\tsMapStatistics* m_pBestScoreMap[5]; // 983: 0x4abc\n'
  '\tint m_reserved983_4ad0[10]; // 983: dez dwords zerados no construtor (008a7bc6..008a7bfc); não medidos\n'
  '#pragma pack(push, 1)\n\tstruct sMapFlag983 { unsigned long v; unsigned char b; };\n#pragma pack(pop)\n'
  '\tsMapFlag983 m_mapFlag983[22]; // 983: 0x4af8, 22 x 5 B zerados (008a77f0); nome meu\n'
  '\tsMapStatistics m_mapStatistics983[4][22]; // 983: 0x4b66, 0x4f18, 0x52ca, 0x567c (4 vetores de 22; uso não medido)\n',
  '983: FrUserInfoForm vetores de 22 mapas + 4 vetores novos (m_guildPang 0x5a30, m_pFriendBtn 0x5a38)'),
 # cauda: m_pAddFriendDlg 0x5d20, 0x5d24..0x5d2c, byte 0x5d30 zerado no fim do construtor; sizeof 0x5d40
 ('sub', _UIF, '\tunsigned long m_recvSeason;\n\tint m_requestSeason;\n',
  '\tunsigned long m_recvSeason;\n\tint m_requestSeason;\n\tbool m_bReserved983_5d30; // 983: byte zerado em 008a7c74\n'
  '\tint m_reserved983_5d34[3]; // 983: até o sizeof 0x5d40; não medidos\n',
  '983: FrUserInfoForm cauda (sizeof 0x5d40)'),
]

# vetor de edits "especiais": 19 no 983, com "es0_4".."es0_6" nos índices 3..5 (0x19c..0x1a4; es0_3 0x198, es1 0x1a8 — sessão 34).
# Os índices do 645 de 3 para cima andam +3; os laços de 11 e os 16 viram 14 e 19 (PROVISÓRIO: contagens não lidas no 983)
def _renum_special(m):
    t = m.group(1).strip()
    mm = re.fullmatch(r'(\d+)( \+ i)?', t)
    if not mm: return m.group(0)
    n = int(mm.group(1)); n += 3 if n >= 3 else 0
    return 'm_pSpecialEdit[%d%s]' % (n, mm.group(2) or '')
NEW7 += [
 ('renum', 'src/projectg/user_info.cpp', _UIF, 'FrEdit* m_pSpecialEdit[19];', r'm_pSpecialEdit\[([^\]]*)\]', _renum_special,
  '983: FrUserInfoForm índices do m_pSpecialEdit renumerados (3.. -> 6..)'),
 ('renum', 'src/projectg/user_info.cpp', _UIF, 'FrEdit* m_pSpecialEdit[19];', r'SetVisible\(\(FrWnd\*\*\)m_pSpecialEdit, 16, ',
  lambda m: 'SetVisible((FrWnd**)m_pSpecialEdit, 19, ', '983: FrUserInfoForm SetVisible dos 19 edits'),
 ('renum', 'src/projectg/user_info.cpp', _UIF, 'FrEdit* m_pSpecialEdit[19];', r'for \(int i = 0; i < 11; \+\+i\)(\s*\{?\s*)m_pSpecialEdit\[i\]->SetVisible\(false\)',
  lambda m: 'for (int i = 0; i < 14; ++i)' + m.group(1) + 'm_pSpecialEdit[i]->SetVisible(false)', '983: FrUserInfoForm laço dos 14 primeiros edits'),
 ('sub', _UIF, '\tFrEdit* m_pSpecialEdit[16];\n\tFrEdit* m_pSpecialEdit983[3]; // 983: o vetor tem 19; os 3 novos ("es0_4".."es0_6") s\xe3o os \xedndices 3..5 DO MEIO.\n'
  '\t// PROVIS\xd3RIO: postos no fim para acertar o que vem depois (+12) sem renumerar os ~70 usos; es1..mh5 seguem 12 B atr\xe1s (onda 2)\n',
  '\tFrEdit* m_pSpecialEdit[19]; // 983: 19; "es0_4".."es0_6" nos \xedndices 3..5 (handlers de Init ainda n\xe3o escritos)\n',
  '983: FrUserInfoForm m_pSpecialEdit[19] com os índices do 983'),
]
