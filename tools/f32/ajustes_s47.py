# F3.5 (sessão 47): busca de emblema do 983 (NetResourceManager::GetEmblem983, 009ab3e0) nas chamadas que usam sBriefUserInfo,
# sSlotInfo e afins; cada troca foi lida no 983 (out/F3.5/s47/emblema_chamadas_983.tsv). Lido por tools/f32/ajustes.py no fim.
G = 'src/shared/globalgamedefine.h'
NEW15 = [
 # sBriefUserInfo: o campo novo (unk983_32) fica antes do nome do emblema — a troca está em ajustes_shareddoc2.py (entrada reescrita).
 ('sub', 'src/projectg/userlistdlg.cpp', 'GetEmblemByName(user->szEmblemName);', 'GetEmblem983(user->m_GuildId, user->unk983_32);',
  '983: FrUserListDlg::OnUserListOwnerDraw usa GetEmblem983'),
 # FrUserListDlg::OnUserListOwnerDraw (00af98f0): o 983 não tem o ramo de ladder e põe o ícone "gp_host" para dwIdentity & 0x8000
 ('sub', 'src/projectg/userlistdlg.cpp',
  '\tif (Doc()->m_curChannel.Type & 0x80)\n\t\tlevel = g_pFresh->GetManager()->GetBitmap("LEVELS",\n'
  '\t\t\tMakeStr("ladder_%03d", user->dwLadderPoint / 100));\n\telse\n\t{\n'
  '\t\tif (user->dwTitle)\n\t\t{\n\t\t\tIFF_STRUCT::sSkin* skin = ItemManager()->FindSkin(user->dwTitle);\n'
  '\t\t\tif (skin)\n\t\t\t\tlevel = g_pFresh->GetBitmap(skin->c.Icon);\n\t\t\telse\n\t\t\t\tlevel =\n'
  '\t\t\t\t\tg_pFresh->GetBitmap(MakeStr("level_%03d", user->level + 1));\n\t\t}\n\t\telse\n'
  '\t\t\tlevel = g_pFresh->GetBitmap(MakeStr("level_%03d", user->level + 1));\n\t}\n',
  '\tif (user->dwTitle)\n\t{\n\t\tIFF_STRUCT::sSkin* skin = ItemManager()->FindSkin(user->dwTitle);\n'
  '\t\tif (skin)\n\t\t\tlevel = g_pFresh->GetBitmap(skin->c.Icon);\n\t\telse\n'
  '\t\t\tlevel = g_pFresh->GetBitmap(MakeStr("level_%03d", user->level + 1));\n\t}\n\telse\n'
  '\t\tlevel = g_pFresh->GetBitmap(MakeStr("level_%03d", user->level + 1));\n'
  '\tif (user->dwIdentity & 0x8000) // 983\n\t\tlevel = g_pFresh->GetManager()->GetBitmap("LEVELS", "gp_host");\n',
  '983: OnUserListOwnerDraw sem ladder, com gp_host'),
]
# Trocas em bloco GetEmblemByName(nome) -> GetEmblem983(clube, número), por tipo do registro; os pares de campos foram lidos nas
# chamadas do 983 (sRivalData +0x174/+0x178; sSlotInfo +0x58/+0x68; sBriefUserInfo +0x2e/+0x32; sPangYaUserInfo dwGuildId/dwEmblemVer
# = +0x38a/+0x38e em FrUserInfoForm, +0x82a/+0x82e em Doc()->m_myInfo, +0x393a/+0x393e em Doc()->m_userInfo[]; amigo +0x2d/+0x31).
# As chamadas com Doc()->m_roomInfo.GuildInfo (emblema dos 2 times) ficam: sGuildRoomInfo do 983 ainda não foi medido.
_EMB = [
 ('src/projectg/scoreboard.cpp', 'pRival->guildMark', 'pRival->guildUID, pRival->unk983_178'),
 ('src/projectg/scoreboard.cpp', 'Doc()->m_rivalList[p].guildMark', 'Doc()->m_rivalList[p].guildUID, Doc()->m_rivalList[p].unk983_178'),
 ('src/projectg/scoreboard.cpp', 'Doc()->m_rivalList[index].guildMark', 'Doc()->m_rivalList[index].guildUID, Doc()->m_rivalList[index].unk983_178'),
 ('src/projectg/lobbymain.cpp', 'pRival->guildMark', 'pRival->guildUID, pRival->unk983_178'),
 ('src/projectg/lobbymain.cpp', 'pSlot->szEmblemName', 'pSlot->GuildId, pSlot->unk983_68'),
 ('src/projectg/lobbymain.cpp', 'pInfo->szEmblemName', 'pInfo->m_GuildId, pInfo->unk983_32'),
 ('src/projectg/resultdlg.cpp', 'rival.guildMark', 'rival.guildUID, rival.unk983_178'),
 ('src/projectg/resultdlg.cpp', 'pInfo->guildMark', 'pInfo->guildUID, pInfo->unk983_178'),
 ('src/projectg/user_info.cpp', 'm_userInfo.info.szEmblemName', 'm_userInfo.info.dwGuildId, m_userInfo.info.dwEmblemVer'),
 ('src/projectg/headicon.cpp', 'Doc()->m_userInfo[index].info.szEmblemName',
  'Doc()->m_userInfo[index].info.dwGuildId, Doc()->m_userInfo[index].info.dwEmblemVer'),
 ('src/projectg/messengerdlg.cpp', 'Doc()->m_myInfo.info.szEmblemName', 'Doc()->m_myInfo.info.dwGuildId, Doc()->m_myInfo.info.dwEmblemVer'),
 ('src/projectg/messengerdlg.cpp', 'pFriend->szEmblemName', 'pFriend->dwGuildId, pFriend->unk983_31'),
 ('src/projectg/avataruserlistdlg.cpp', 'pSlot->szEmblemName', 'pSlot->GuildId, pSlot->unk983_68'),
 ('src/projectg/avatar_avatar.cpp', 'slot.szEmblemName', 'slot.GuildId, slot.unk983_68'),
 ('src/projectg/detailedroominfodlg.cpp', 'info.szEmblemName', 'info.m_GuildId, info.unk983_32'),
]
for _f, _a, _b in _EMB:
    for _ws in [''] + ['\n' + '\t' * _k for _k in range(1, 9)]:
        NEW15.append(('todos', _f, 'GetEmblemByName(' + _ws + _a + ')', 'GetEmblem983(' + _ws + _b + ')',
                      '983: GetEmblem983 no lugar de GetEmblemByName(%s)' % _a))
