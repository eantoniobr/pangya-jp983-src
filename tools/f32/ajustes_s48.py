# F3.5 (sessão 48): emblema dos 2 times pelo sGuildRoomInfo do 983 (layout em ajustes_shareddoc2.py, entrada reescrita):
# GetEmblemByName(GuildInfo.szEmblemName[i]) -> GetEmblem983(GuildInfo.nGuildID[i], GuildInfo.unk983_20[i]).
# Lido no 983: lobbymain 005122a8/005123cf, 0051419d/005141c2; scoreboard 00781798/007817bd, 00785360/00785385;
# resultdlg 00ae86f5, 00ae88c5, 00aefc7d/00aefd25 (todos `movsx reg, word [doc + 0x1097f|0x10981]`). Lido por tools/f32/ajustes.py no fim.
NEW16 = []
for _f in ('src/projectg/lobbymain.cpp', 'src/projectg/scoreboard.cpp', 'src/projectg/resultdlg.cpp'):
    for _i in ('0', '1'):
        for _ws in [''] + ['\n' + '\t' * _k for _k in range(1, 9)]:
            _a = 'Doc()->m_roomInfo.GuildInfo.szEmblemName[%s]' % _i
            _b = 'Doc()->m_roomInfo.GuildInfo.nGuildID[%s], Doc()->m_roomInfo.GuildInfo.unk983_20[%s]' % (_i, _i)
            NEW16.append(('todos', _f, 'GetEmblemByName(' + _ws + _a + ')', 'GetEmblem983(' + _ws + _b + ')',
                          '983: GetEmblem983 no lugar de GetEmblemByName(%s)' % _a))
# FrResultTeamDlg::OnRedInit/OnBlueInit (00ae8680, 00ae8850): fora do modo 6, o 983 escolhe o fundo pelo Doc()->m_eventFlag
# (doc+0x10499): o time marcado fica com a imagem normal e o outro com a "_dark".
NEW16 += [
 ('sub', 'src/projectg/resultdlg.cpp', '\t\telse\n\t\t\tm_pRed->SetBgImg("30in_team_redteam_dark");\n',
  '\t\telse if (Doc()->m_eventFlag != 1) // 983\n\t\t\tm_pRed->SetBgImg("30in_team_redteam");\n'
  '\t\telse\n\t\t\tm_pRed->SetBgImg("30in_team_redteam_dark");\n', '983: OnRedInit escolhe o fundo pelo m_eventFlag'),
]
NEW16 += [
 ('sub', 'src/projectg/resultdlg.cpp', '\t\telse\n\t\t\tm_pBlue->SetBgImg("30in_team_blueteam_dark");\n',
  '\t\telse if (Doc()->m_eventFlag != 0) // 983\n\t\t\tm_pBlue->SetBgImg("30in_team_blueteam");\n'
  '\t\telse\n\t\t\tm_pBlue->SetBgImg("30in_team_blueteam_dark");\n', '983: OnBlueInit escolhe o fundo pelo m_eventFlag'),
]
# FrResultDlg/FrResultTeamDlg::OnIdOwnerDraw (00aecd30, 00aed680): no 983 o retângulo do emblema soma `offset` (ainda 0) a x e y,
# as constantes 6 e 27 são double e o y do texto soma 0.0 (double) — lido em 00aecda9..00aece61.
_R = 'src/projectg/resultdlg.cpp'
NEW16 += [
 ('todos', _R, 'WRect(m_pId->GetRect().x, m_pId->GetRect().y - 6.0f,', 'WRect(m_pId->GetRect().x + offset, m_pId->GetRect().y + offset - 6.0,',
  '983: OnIdOwnerDraw, retângulo do emblema com offset e 6.0 double'),
 ('todos', _R, '\t\t\t\toffset = 27.0f;\n', '\t\t\t\toffset = offset + 27.0;\n', '983: OnIdOwnerDraw, offset + 27.0 (double)'),
 ('todos', _R, 'WPoint(m_pId->GetRect().x + offset, m_pId->GetRect().y), 0,', 'WPoint(m_pId->GetRect().x + offset, m_pId->GetRect().y + 0.0), 0,',
  '983: OnIdOwnerDraw, y do texto + 0.0 (double)'),
]
NEW16 += [
 ('todos', _R, 'WRect(m_pTeamId->GetRect().x, m_pTeamId->GetRect().y - 6.0f,', 'WRect(m_pTeamId->GetRect().x + offset, m_pTeamId->GetRect().y + offset - 6.0,',
  '983: FrResultTeamDlg::OnIdOwnerDraw, retângulo do emblema com offset e 6.0 double'),
 ('todos', _R, 'WPoint(m_pTeamId->GetRect().x + offset, m_pTeamId->GetRect().y),', 'WPoint(m_pTeamId->GetRect().x + offset, m_pTeamId->GetRect().y + 0.0),',
  '983: FrResultTeamDlg::OnIdOwnerDraw, y do texto + 0.0 (double)'),
 # FrResultTeamDlg::OnRedOwnerDraw/OnBlueOwnerDraw (00ae8750, 00ae8920): constantes 10, 1 e 30 em double no 983 (fadd qword)
 ('todos', _R, 'WRect(pos.x + 10.0f, pos.y + 1.0f,', 'WRect(pos.x + 10.0, pos.y + 1.0,', '983: OnRed/BlueOwnerDraw com constantes double'),
 ('todos', _R, 'WPoint(pos.x, pos.y + 30.0f), 0,', 'WPoint(pos.x, pos.y + 30.0), 0,', '983: OnRed/BlueOwnerDraw com constantes double'),
]
# sky.cpp: o strrchr do VC10 devolve const char* para argumento const (C2440); o código gerado não muda
NEW16 += [
 ('sub', 'src/projectg/sky.cpp', "\t\tchar* ext = strrchr(obj->option.c_str(), '.');", "\t\tconst char* ext = strrchr(obj->option.c_str(), '.');",
  'strrchr const-correto do VC10 (C2440)'),
]
# CSky no layout do 983 (construtor 00705330: m_color em 0x8e4, m_pLensFlare/m_pStars/m_pMoons em 0x8e8..0x8f0, m_upRot/m_nearRot
# em 0x8f4/0x8f8; não inicia m_heightOffset, m_turn, m_farNum, m_nearNum). Os 6 campos que o 983 não tem vão para o fim da classe,
# provisórios, enquanto LoadSky/Render/RenderUpAndBottom (que ainda os usam) não forem reescritos pelo 983.
_S = 'src/projectg/sky.h'
NEW16 += [
 ('sub', _S, '\tfloat m_cloudTimer;\n\tfloat m_heightOffset;\n\tunsigned long m_color;\n\tfloat m_turn;\n\tint m_farNum;\n\tint m_nearNum;\n'
  '\tunsigned char m_unused8e8[0xc0];\n\tWVector m_camPos;\n',
  '\tfloat m_cloudTimer;\n\tunsigned long m_color; // 983: 0x8e4\n', '983: CSky sem os 6 campos entre m_cloudTimer e m_pLensFlare'),
 ('sub', _S, '\tfloat m_upRot;\n\tfloat m_nearRot;\n};',
  '\tfloat m_upRot;\n\tfloat m_nearRot;\n\t// 983: a classe acaba aqui (0x8fc); os campos abaixo n\xe3o existem no 983 (provis\xf3rios, no fim para n\xe3o deslocar os outros)\n'
  '\tfloat m_heightOffset;\n\tfloat m_turn;\n\tint m_farNum;\n\tint m_nearNum;\n\tWVector m_camPos;\n};',
  '983: campos do CSky que o 983 não tem, no fim (provisório)'),
]
_K = 'src/projectg/sky.cpp'
NEW16 += [
 # CSky::Clear (00704fc0): `sar eax, 0xd; and eax, 0x1ff` — o índice do buffer de índices tem 9 bits a partir do bit 13 no 983
 ('sub', _K, '\t\t\t\t(m_batch[i].xiFlag1 >> 14) & 0xff);', '\t\t\t\t(m_batch[i].xiFlag1 >> 13) & 0x1ff);', '983: CSky::Clear lê o índice em >>13 & 0x1ff'),
 # CSky::CalcScaleByView (007052d0): fdiv qword 500.0
 ('sub', _K, 'return (view->GetScale() + view->GetScale()) * 0.002f;', 'return (view->GetScale() + view->GetScale()) / 500.0;',
  '983: CalcScaleByView divide por 500.0 (double)'),
 # CSky::RenderFlatCloud (007066d0): flags de desenho do 983
 ('sub', _K, 'view->DrawPolygonFan(pVtx, (m_cloudTex & 0x7ff) | 0x20300000, 0x400,', 'view->DrawPolygonFan(pVtx, (m_cloudTex & 0x7ff) | 0x400000, 0x200,',
  '983: RenderFlatCloud com os flags do 983 (0x400000, 0x200)'),
 # Render* (00706120, 00706320, 00706910): o 983 não guarda m_camPos; usa view->GetCamera().pivot direto ([view+0x50])
 ('todos', _K, '\t\tm.pivot = m_camPos;\n', '\t\tm.pivot = view->GetCamera().pivot;\n', '983: CSky::Render* usam a posição da câmera direto'),
 ('sub', _K, '\tm_camPos = view->GetCamera().pivot;\n\tm_camPos.y += m_heightOffset;\n\n', '', '983: CSky::Render não guarda m_camPos'),
]
# CSky::Render (00706aa0): no 983 o Flush depois das estrelas/luas leva 1 no 2º argumento (push 1; push 0) e o bloco das nuvens
# (RenderFlatCloud/RenderBillboardCloud) não é chamado daqui; `pivot + m_offset` com os operandos na ordem do 983.
NEW16 += [
 ('todos', _K, '\t\t\tm_pStars->Display(g_view);\n\t\t\tg_view->Flush(0);\n', '\t\t\tm_pStars->Display(g_view);\n\t\t\tg_view->Flush(0, true);\n',
  '983: CSky::Render, Flush(0, true) depois das estrelas'),
 ('todos', _K, '\t\t\tm_pMoons->Display(g_view);\n\t\t\tg_view->Flush(0);\n', '\t\t\tm_pMoons->Display(g_view);\n\t\t\tg_view->Flush(0, true);\n',
  '983: CSky::Render, Flush(0, true) depois das luas'),
 ('sub', _K, '\t\tRenderNearCylinder(view);\n\n\t\tint mode = GOLFDOC()->m_gameMode;\n\t\tif (mode != 0x200000)\n\t\t{\n\t\t\tif (mode & 0x200)\n'
  '\t\t\t\tRenderFlatCloud(view);\n\t\t\telse\n\t\t\t\tRenderBillboardCloud(view);\n\t\t}\n\t}\n',
  '\t\tRenderNearCylinder(view);\n\t\t// 983: as nuvens n\xe3o s\xe3o desenhadas daqui\n\t}\n', '983: CSky::Render sem o bloco das nuvens'),
]
NEW16 += [
 ('sub', _K, 'spray->Pos() = g_view->GetCamera().pivot + spray->m_offset;', 'spray->Pos() = spray->m_offset + g_view->GetCamera().pivot;',
  '983: CSky::Render, ordem dos operandos na posição das luas'),
 ('sub', _K, '\tfloat clip[2] = { view->GetClipNearValue(), view->GetClipFarValue() };\n\n\tview->SetClip(1.0f, CalcClipFarByView(view), false);',
  '\tfloat clipNear = view->GetClipNearValue();\n\tfloat clipFar = view->GetClipFarValue();\n\n\tview->SetClip(1.0f, CalcClipFarByView(view), false);',
  '983: CSky::Render guarda os dois planos em variáveis soltas'),
 ('sub', _K, '\tview->SetClip(clip[0], clip[1], false);\n\tview->UpdateCamera();\n}\n\nvoid CSky::RenderUpAndBottom',
  '\tview->SetClip(clipNear, clipFar, false);\n\tview->UpdateCamera();\n}\n\nvoid CSky::RenderUpAndBottom', '983: CSky::Render guarda os dois planos em variáveis soltas'),
]
NEW16 += [
 # construtor (00705330): sem m_heightOffset, m_turn, m_farNum, m_nearNum; os dois zeros em float (0x8dc, 0x8e0) são gravados
 # depois de raio/distância/altura/cor
 ('sub', _K, '\tm_cloudInterval = 0.0f;\n\tm_cloudTimer = 0.0f;\n\tm_heightOffset = 0.0f;\n\tm_turn = 0.0f;\n\tm_cloudRadius = 1120.0f;\n'
  '\tm_cloudFar = 1600.0f;\n\tm_cloudHeight = 416.0f;\n\tm_color = 0xffffffff;\n\tm_farNum = 2;\n\tm_nearNum = 2;\n',
  '\tm_cloudRadius = 1120.0f;\n\tm_cloudFar = 1600.0f;\n\tm_cloudHeight = 416.0f;\n\tm_color = 0xffffffff;\n\tm_cloudInterval = 0.0f;\n\tm_cloudTimer = 0.0f;\n',
  '983: construtor do CSky sem os 4 campos que o 983 não tem e na ordem do 983'),
]
