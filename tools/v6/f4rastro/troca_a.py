#!/usr/bin/env python3
"""C102: troca de trecho em unidades da A numa CÓPIA (sem editar o arquivo da A) e compila do jeito do pgbuild.

Uso: python3 tools/v6/f4rastro/troca_a.py TAG_PCH_A TAG_SAIDA
  -> build/TAG_SAIDA/obj/<unidade>.obj; depois make exe ENTREGA=... V6_PG="TAG_SAIDA TAG_PCH_A" [V6_BOBJ=...]
Cada troca: (âncora única no arquivo, texto novo) ou (âncora, texto, 'depois') = inserir depois da âncora.
Opções por unidade: 'head' = compila a versão da revisão REV (não pega trabalho em curso da A) e copia para junto da cópia
os headers de 'heads' na versão do commit (o #include "x.h" acha primeiro a pasta da fonte). Troca atual: fim do caso 0x49 do CLobbyTask::OnPacket (983 00ac112f).
"""
import os, sys, subprocess
ROOT = '/root/jp983src'
sys.path.insert(0, ROOT + '/tools/f32')
import pgbuild as P

# revisão das unidades 'head' (= o que o pg-a172 compilou; HEAD muda quando a A commita e mistura com os .obj velhos)
REV = 'aa0f33dc'

TROCAS = [
    ('src/projectg/lobbytask.cpp', [
        # 983 00ac13f9..00ac14ff: sem a mensagem 0 com o layout "GAMEROOM"/"GAMEROOM_EXT" do 645 (ela troca a página e
        # destrói o RFLobbyDesktop); manda 0x8b com o estado da janela da sala (CLobbyMain::OpenGameRoomDlg983) e,
        # nas salas de realGameType 0xc/0xe/0x13 (00500200), a 0x2f do 983 (= M983(0x2e)).
        ('\t\t\t\tGetActor("Lobby") << MsgObject(NULL, M983(0x2e), 0, 0, 0, 0, 0);\n\t\t\t\tlayout = "GAMEROOM_EXT";',
         '\t\t\t\tlayout = "GAMEROOM_EXT";'),
        ('\t\t\tGetActor("Lobby") << MsgObject(NULL, 0, (int)layout, 0, 0, 0, 0);\n',
         '\t\t\t(void)layout;\n'
         '\t\t\tint roomState983 = 6;\n'
         '\t\t\tbool single983 = false;\n'
         '\t\t\tif (IsMassGame(Doc()->m_roomInfo.gameType))\n'
         '\t\t\t{\n'
         '\t\t\t\tunsigned char rt = (unsigned char)Doc()->m_roomInfo.realGameType;\n'
         '\t\t\t\tif (rt == 0xc || rt == 0xe || rt == 0x13)\n'
         '\t\t\t\t{\n'
         '\t\t\t\t\troomState983 = 0xb;\n'
         '\t\t\t\t\tsingle983 = true;\n'
         '\t\t\t\t}\n'
         '\t\t\t\telse\n'
         '\t\t\t\t\troomState983 = IsGrandPrixGameType983(rt) ? 0xa : 7;\n'
         '\t\t\t}\n'
         '\t\t\tGetActor("Lobby") << MsgObject(NULL, 0x8b, roomState983, 0, 0, 0, 0);\n'
         '\t\t\tif (single983)\n'
         '\t\t\t\tGetActor("Lobby") << MsgObject(NULL, M983(0x2e), 0, 0, 0, 0, 0);\n'),
    ], {'head': True}),
    # rastro: quem libera a lista de salas (CLobbyMain+0x77c) sem zerar o ponteiro (c102-1: AV no OpenGameRoomDlg983)
    ('src/projectg/lobbymain.cpp', [
        ('#include "exhibition.h"\n', 'extern "C" void __cdecl jp983_rastro(const char* fmt, ...);\nextern "C" void* _ReturnAddress(void);\n#pragma intrinsic(_ReturnAddress)\n', 'depois'),
        ('void CLobbyMain::HandleMsg(const MsgObject& msg)\n{\n',
         '\tif (msg.message == 0x8b) jp983_rastro("C102 Lobby 0x8b p1=%d p2=%d 77c=%08x 780=%p", msg.param1, msg.param2, m_unk983_77c, m_pGameRoomDlg983);\n', 'depois'),
        ('\t\t\tFrRoomListDlg* pRoomListDlg = (FrRoomListDlg*)m_unk983_77c;\n',
         '\t\t\tjp983_rastro("C102 0x8b4 abriu lista 77c=%08x", m_unk983_77c);\n', 'depois'),
        ('bool CLobbyMain::OnRoomListDlgResult983(int result, FrForm* form)\n{\n',
         '\tjp983_rastro("C102 OnRoomListDlgResult983 r=%d form=%p 77c=%08x", result, form, m_unk983_77c);\n', 'depois'),
        ('void CLobbyMain::OpenGameRoomDlg983(int state)\n{\n',
         '\tjp983_rastro("C102 OpenGameRoomDlg983 %d 77c=%08x vt=%08x 780=%p", state, m_unk983_77c, m_unk983_77c ? *(unsigned long*)m_unk983_77c : 0, m_pGameRoomDlg983);\n', 'depois'),
        ('void CLobbyMain::OpenSingleModeStarter983()\n{\n',
         '\tjp983_rastro("C102 OpenSingleModeStarter983 77c=%08x", m_unk983_77c);\n', 'depois'),
        ('bool CLobbyMain::OnSingleModeStartResult983(int result, FrForm* form)\n{\n',
         '\tjp983_rastro("C102 OnSingleModeStartResult983 r=%d 77c=%08x", result, m_unk983_77c);\n', 'depois'),
        ('void CLobbyMain::CloseAllDialogs()\n{\n',
         '\tjp983_rastro("C102 CloseAllDialogs 77c=%08x ret=%p", m_unk983_77c, _ReturnAddress());\n', 'depois'),
        # 983 0059fa80: LatestVersion983 (era stub, devolvia 0 e o Start Game do dono não mandava o 0x0E)
        ('bool CLobbyMain::LatestVersion()\n{\n',
        'bool LatestVersion983()\n{\n'
         '\tjp983_rastro("C102 LatestVersion983 [%s]", Doc()->m_packetNickname.c_str());\n'
         '\tif (Doc()->m_packetNickname > "JP.R7.983.00")\n\t{\n'
         '\t\tAfxGetTask()->SendMsgToMainActor(MsgObject(NULL, 0x23, (int)K2L_Compatibility("\\xc3\\xd6\\xbd\\xc5 \\xb9\\xf6\\xc1\\xaf\\xc0\\xb8\\xb7\\xce '
         '\\xbe\\xf7\\xb5\\xa5\\xc0\\xcc\\xc6\\xae\\xb0\\xa1 \\xc7\\xca\\xbf\\xe4\\xc7\\xd5\\xb4\\xcf\\xb4\\xd9."), 0, 0, 0, 0));\n'
         '\t\treturn false;\n\t}\n\treturn true;\n}\n\nbool CLobbyMain::LatestVersion()\n{\n'),
        # 983 00abc724/00abc747 (HandleMsg 0xe/0xf): repassa à janela da sala (+0x780) em vez da página GAMEROOM do 645
        ('#include "exhibition.h"\n',
         '#include "jp/singletypedlg.h"\nstruct GRAccess983 : public FrGameRoomDlg\n{\n'
         '\tstatic void List(FrForm* f) { ((GRAccess983*)(FrGameRoomDlg*)f)->MakeRoomUserList(); }\n'
         '\tstatic void Master(FrForm* f) { ((GRAccess983*)(FrGameRoomDlg*)f)->UpdateMaster983(); }\n};\n', 'depois'),
        ('\tcase M983(0xe):\n\t{\n',
         '\t\tjp983_rastro("C102 Lobby 0xe dlg=%p", m_pGameRoomDlg983);\n'
         '\t\tif (m_pGameRoomDlg983)\n\t\t{\n\t\t\tGRAccess983::List(m_pGameRoomDlg983);\n'
         '\t\t\tGRAccess983::Master(m_pGameRoomDlg983);\n\t\t\tbreak;\n\t\t}\n', 'depois'),
        ('\tcase M983(0xf):\n\t{\n',
         '\t\tif (m_pGameRoomDlg983)\n\t\t{\n\t\t\tGRAccess983::Master(m_pGameRoomDlg983);\n\t\t\tbreak;\n\t\t}\n', 'depois'),
        # 983 00aba697..00aba6bb: o construtor zera +0x4b0/4b4, 738..748, 770/774, 274, 77c e 780 (o nosso não: lixo no 77c/780)
        ('CLobbyMain::CLobbyMain()\n{\n',
         '\tmemset(m_unk983_4b0, 0, 8);\n'
         '\tfor (int i983 = 0; i983 < 5; i983++)\n\t\tm_pStatGauge983[i983] = NULL;\n'
         '\tm_pToppageJukeboxBtn983 = NULL;\n\tm_unk983_774 = 0;\n\tm_pToppagePremiumService983 = NULL;\n'
         '\tm_unk983_77c = 0;\n\tm_pGameRoomDlg983 = NULL;\n', 'depois'),
    ], {'head': True, 'heads': ['src/projectg/lobbymain.h', 'src/projectg/lobbybg.h']}),
    # 0xa5 CLobbyContainer do 983 (0x1c; vtable 00d3c600: dtor 00912380, Initialize 00907aa0 = Reset, Release 00907ab0,
    # Reset 00907ac0). Sem ele o GetContainer(0xa5) devolve NULL e a FrGameRoomDlg (m_pDoc +0x14c) dá AV no ResetRoom983.
    ('src/projectg/icontentsdoc.cpp', [
        ('#include "packets/aiplayerinfocontainer.h"\n',
         'struct CLobbyContainer983 : public IContentsDataContainer\n{\n'
         '\tvirtual bool Initialize() { Reset(); return true; } // 00907aa0\n'
         '\tvirtual bool Release() { return true; } // 00907ab0\n'
         '\tvirtual bool Reset() // 00907ac0\n\t{\n'
         '\t\tm_gameType = -1; m_selOID = 0xffffffff; m_selUID = 0xffffffff; m_14 = 0xffffffff; m_cate = 4; m_18 = 0;\n'
         '\t\treturn true;\n\t}\n'
         '\tint m_gameType; // +4\n\tint m_cate; // +8\n\tunsigned long m_selOID; // +0xc\n\tunsigned long m_selUID; // +0x10\n'
         '\tunsigned long m_14; // +0x14\n\tunsigned char m_18; // +0x18\n};\n', 'depois'),
        ('\t// PENDENTE: 0xa5 CLobbyContainer (0x1c, s\xf3 a vtable 00d3c600 no construtor), bForce = false.\n',
         '\tInsertContainer((localContentType_t)0xa5, new CLobbyContainer983, false);\n'),
    ], {'head': True}),
    # 983 00a6990e..00a69931: o CProjectG cria o CUiFrameSetManager (0xa8, "uiframeset.xml") logo depois do CRankingInfo; o
    # nosso não cria e o COption::UpdatePowerGaugeLayout983 dá AV ao entrar na partida (c102-10)
    ('src/projectg/projectg.cpp', [
        ('\tnew CRankingInfo;\n', '\tnew CUiFrameSetManager;\n', 'depois'),
        ('#include "clientsetting.h"\n', '#include "jp/uiframesetmanager.h"\nextern "C" void __cdecl jp983_rastro(const char* fmt, ...);\n', 'depois'),
        ('\tif (m_pDxDiagInfo && !m_pDxDiagInfo->IsGathered())\n\t\tm_pDxDiagInfo->GatherInfo();\n\tif (g_bQuit)\n',
         '\t\tjp983_rastro("C103 CProjectG::Quit task=%p", CTaskManager::Instance()->GetCurrentTask()),\n', 'depois'),
    ], {'head': True}),
    # C103: quem fecha o jogo na carga da partida (c102-11: ~CProjectG com a thread do CAnotherHand ainda no OnLoad)
    ('src/projectg/golfbg.cpp', [
        ('#include "minatl.h"\n', 'extern "C" void __cdecl jp983_rastro(const char* fmt, ...);\n', 'depois'),
        ('g_bQuit = true;', 'jp983_rastro("C103 golfbg quit linha %d curso=%s", __LINE__, GetCourseName()); g_bQuit = true;', 'todas'),
    ], {'head': True}),
    ('src/projectg/mainframe.cpp', [
        ('#include "minatl.h"\n', 'extern "C" void __cdecl jp983_rastro(const char* fmt, ...);\n', 'depois'),
        ('\t\tg_bQuit = _GGC_CheckGameMon() == 0;\n', '\t\tif (g_bQuit) jp983_rastro("C103 GGC quit");\n', 'depois'),
    ], {'head': True}),
]


def main():
    tag_pch, tag_out = sys.argv[1], sys.argv[2]
    units = {u[0]: u for u in P.units()}
    class A: pass
    a = A(); a.flags = None; a.B = ROOT + '/build/' + tag_pch
    ok = True
    for src, trocas, opt in TROCAS:
        if opt.get('head'):
            txt = subprocess.check_output(['git', '-C', ROOT, 'show', REV + ':' + src]).decode('latin-1')
        else:
            txt = open(ROOT + '/' + src, encoding='latin-1').read()
        for e in trocas:
            anc, novo = e[0], e[1]
            n = txt.count(anc)
            if n != 1 and not (n > 1 and len(e) > 2 and e[2] == 'todas'):
                sys.exit('FALHA âncora (%d ocorrências) em %s: %r' % (n, src, anc[:60]))
            txt = txt.replace(anc, anc + novo if len(e) > 2 and e[2] == 'depois' else novo)  # 'todas' = todas as ocorrências
        cp = '%s/build/%s/troca_src/%s' % (ROOT, tag_out, src)
        os.makedirs(os.path.dirname(cp), exist_ok=True)
        for h in opt.get('heads', []):
            open(os.path.dirname(cp) + '/' + os.path.basename(h), 'wb').write(
                subprocess.check_output(['git', '-C', ROOT, 'show', REV + ':' + h]))
        open(cp, 'w', encoding='latin-1').write(txt)
        _, _, pch, fi, einc = units[src]
        args = P.base_args(a, einc, src) + fi + ['/I' + ROOT + '/' + os.path.dirname(src)]
        if pch: args += ['/Yu' + os.path.basename(pch)[:-4] + '.h', '/Fp' + P.pch_file(a, pch)]
        obj = '%s/build/%s/obj/%s.obj' % (ROOT, tag_out, src[:-4])
        os.makedirs(os.path.dirname(obj), exist_ok=True)
        rc = P.cl(args + ['/Fo' + obj, cp], obj[:-4] + '.log')
        print(src, 'rc=%d' % rc, '' if rc == 0 else open(obj[:-4] + '.log', errors='replace').read()[-800:])
        ok = ok and rc == 0
    sys.exit(0 if ok else 1)

main()
