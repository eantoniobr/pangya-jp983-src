# F3.5 (sessão 53): classes centrais com sizeof diferente do 983 (lista da s52, out/F3.5/s52/mkinst/mkinst.tsv). Aqui os membros novos
# entram no LUGAR medido (construtor/destrutor do 983 + votos de out/F3.5/s53/raw), não no fim. Nomes `*983*` são provisórios.
# Lido por tools/f32/ajustes.py no fim.
_T = 'src/projectg/taskmanager.h'
_G = 'src/projectg/golfrule.h'
_GC = 'src/projectg/golfrule.cpp'
NEW21 = [
 # ---- CTask: 0x1fc -> 0x208 (push 0x208 em 00abf4f3/00b1c4d0/0082c760; construtor 009bf340, destrutor 009bc170) ----
 ('sub', _T, '\tFrGaugeBar* m_pProgressGauge;\n\tCAnotherHand m_anotherHand;\n',
  '\tFrGaugeBar* m_pProgressGauge;\n'
  '\tvoid* m_pUnk983_68; // 983: ponteiro novo (zerado em 009bf433; o destrutor chama 009b74d0 e operator delete: objeto sem vtable). Tipo provisório\n'
  '\tCAnotherHand m_anotherHand; // 983: 0x6c\n',
  '983: CTask tem um ponteiro novo em +0x68; m_anotherHand vai para +0x6c (009bf400, 009bc28a)'),
 ('sub', _T, '\tunsigned long m_taskFlag;\n\tbool m_bRecieveWhisper;\n\tbool m_bPause;\n\tfloat m_netSyncTime;\n',  # s56: sem o '};' (o rebang 34f62e0 pos um bloco #ifdef antes dele)
  '\tunsigned long m_taskFlag; // 983: 0x1f4\n\tbool m_bRecieveWhisper; // 983: 0x1f8 (= 1 em 009bf420)\n'
  '\tIActor* m_pDummyActor983; // 983: 0x1fc = cópia do ms_pDummyActor (00f006f8) gravada no fim do construtor (009bf52a). Nome provisório\n'
  '\tbool m_bPause; // 983: 0x200 (SetPause fora de linha em 0066f810)\n\tfloat m_netSyncTime; // 983: 0x204\n',
  '983: sizeof(CTask) = 0x208: m_taskFlag 0x1f4, m_bRecieveWhisper 0x1f8, ponteiro novo 0x1fc, m_bPause 0x200, m_netSyncTime 0x204'),
 # ---- CGolfRule: 0x600 -> 0x650 (push 0x650 em 0068b443; construtor 0068aea0) ----
 ('sub', _G, '\tunsigned char m_unused1ec[0x1f8 - 0x1ec];\n',
  '\tstd::deque<void*> m_unk983_224; // 983: 2º contêiner tipo deque (0x18 bytes no VS2010) construído em 0068aee3, antes do m_backUpStack. Tipo do elemento provisório\n'
  '\tunsigned char m_unk983_23c[0xc]; // 983: +0xc até m_modeTime (0x260); posição dentro de 0x23c..0x260 não medida\n'
  '\tunsigned char m_unused1ec[0x1f8 - 0x1ec];\n',
  '983: CGolfRule +0x24 antes de m_modeTime (votos 0x23c -> 0x260, 0x284 -> 0x2a8; m_backUpStack 0x2b4 -> 0x2d8)'),
 ('sub', _G, '\tunsigned char m_unused388[0x3a8 - 0x388];\n',
  '\tunsigned char m_unused388[0x3a8 - 0x388 - 0xc]; // 983: 12 bytes a menos entre m_shotData (WCrypticValue em 0x3cc) e m_bgPosList (0x3fc)\n',
  '983: m_bgPosList 0x3e8 -> 0x3fc (+0x14) depois de m_shotData +0x20'),
 ('sub', _G, '\tunsigned char m_unused42d[0x444 - 0x42d];\n',
  '\tunsigned char m_unused42d[0x444 - 0x42d + 4]; // 983: +4 (m_unk444 0x484 -> 0x49c; m_pApproachEndDlg 0x468 -> 0x47c)\n',
  '983: +4 entre m_unk42c e m_unk444'),
 ('sub', _G, '\tunsigned long m_unk448; // 0x448\n',
  '\tfloat m_unk448; // 0x448; 983: float (fldz/fstp [esi+0x4a0] em 0068af83)\n',
  '983: m_unk448 é float (construtor 0068af83)'),
 ('sub', _G, '\tFrButton* m_pOnelineBtn;                 // 0x4c0\n\tbool m_unk4c4; ',
  '\tFrButton* m_pOnelineBtn;                 // 0x4c0\n'
  '\tvoid* m_pUnk983_51c; // 983: 3 dwords novos (0x51c zerado no fim do construtor, 0068b217; 0x520/0x524 não vistos). Tipos provisórios\n'
  '\tunsigned long m_unk983_520;\n\tunsigned long m_unk983_524;\n\tbool m_unk4c4; ',
  '983: m_unk4c4 0x504 -> 0x528 (+0x24), m_pOnelineBtn 0x500 -> 0x518 (+0x18)'),
 ('sub', _G, '\tunsigned char m_unused529[0x538 - 0x529];\n',
  '\tunsigned char m_unused529[0x538 - 0x529 + 0x20]; // 983: +0x20 (m_unk4c5 0x529; m_pRadioPredictNormalShot 0x578 -> 0x5bc)\n',
  '983: +0x20 entre m_unk4c5 e os botões de previsão'),
 ('sub', _G, '\tCGolfRuleBase* m_pRuleBase; // 0x5b4\n\tbool m_unk5b8;              // 0x5b8\n\tbool m_bWaitForStart;       // 0x5b9\n\tint m_unk5bc;               // 0x5bc\n',
  '\tCGolfRuleBase* m_pRuleBase; // 0x5b4; 983: 0x638\n'
  '\tvoid* m_pUnk983_63c;        // 983: ponteiro novo, zerado junto com m_pRuleBase (0068b036) e usado como objeto (mov ecx, [esi+0x63c]). Tipo provisório\n'
  '\tbool m_unk5b8;              // 0x5b8; 983: 0x640\n\tbool m_bWaitForStart;       // 0x5b9; 983: 0x641\n\tint m_unk5bc;               // 0x5bc; 983: 0x644\n'
  '\tunsigned long m_unk983_648; // 983: zerado no fim do construtor (0068b21d)\n\tunsigned long m_unk983_64c; // 983: sizeof 0x650\n',
  '983: fim do CGolfRule (m_pRuleBase 0x638, novo 0x63c, m_unk5bc 0x644, novo 0x648)'),
 # construtor do 983 (0068aea0): ordem das gravações, m_unk448 float, id 0x18000031, 2 zeros novos, 3 no fim
 ('corte', _GC, 'CGolfRule::CGolfRule()\n{\n\tm_dispPriority = DISP_PRIORITY_0;\n', '\tm_unk5bc = 0;\n}\n',
  'CGolfRule::CGolfRule()\n{\n\t// 983 (0068aea0): mesma lista do 645 em outra ordem, mais os campos novos\n'
  '\tm_unk448 = 0.0f;\n\tm_dispPriority = DISP_PRIORITY_0;\n\tm_pChatView = NULL;\n\tm_pEmoticonBtn = NULL;\n\tm_pLanguage = NULL;\n'
  '\tm_pReportBtn = NULL;\n\tm_pChatTarget = NULL;\n\tm_pChatEdit = NULL;\n\tm_pEmoticonDlg = NULL;\n\tm_pReportDlg = NULL;\n'
  '\tm_pMyInfoBtn = NULL;\n\tm_pOptionBtn = NULL;\n\tm_pCaddieBookBtn = NULL;\n\tm_pUnplayableBtn = NULL;\n\tm_pPauseBtn = NULL;\n'
  '\tm_pChatRecordBtn = NULL;\n\tm_pOnelineView = NULL;\n\tm_pOnelineBtn = NULL;\n\tm_pUnk490 = NULL;\n\tm_unk444 = false;\n'
  '\tm_cancelItemSlot = 0x18000031; // 983 (era 0x1800002d)\n\tm_unk420 = 0;\n\tm_pOnelineReqDlg = NULL;\n\tm_pApproachResultDlg = NULL;\n'
  '\tm_pApproachEndDlg = NULL;\n\tm_unk4c4 = false;\n\tmemset(m_unk4c5, 0, sizeof(m_unk4c5));\n\tm_pRuleBase = NULL;\n\tm_pUnk983_63c = NULL;\n'
  '\n\tif (IsLocalContent(S4_SPECIALSHOT_RESTRICTION_MODIFY))\n\t{\n\t\tm_unk1e4 = 0;\n\t\tm_unk1e0 = 0;\n\t\tm_unk1e8 = 0;\n\t}\n'
  '\n\tif (IsLocalContent(S4_REPLAY_SYSTEM))\n\t{\n\t\tm_pReplayControlDlg = NULL;\n\t\tm_pRecordAviDlg = NULL;\n'
  '\t\tCReplayControlManager::Instance()->Init();\n\t\tm_unk59c = 0;\n\t\tm_unk5a0 = 0;\n\t}\n'
  '\n\tDoc()->m_goStopMode = false; // 983: aqui há `call 00b3b1e0` (devolve o endereço de um objeto estático, 00f03b10) e nenhuma gravação; não reproduzido\n'
  '\n\tm_pPredictShotUI = new CSimpleUI("[impact.png");\n'
  '\tm_pPredictShotUI->Add("Pangya", WRect(0.0f, 18.0f, 128.0f, 18.0f), false);\n'
  '\tm_pPredictShotUI->Add("Tomahawk", WRect(0.0f, 72.0f, 128.0f, 18.0f), false);\n'
  '\tm_pPredictShotUI->Add("Cobra", WRect(0.0f, 126.0f, 128.0f, 18.0f), false);\n'
  '\tm_pPredictShotUI->Add("Spike", WRect(0.0f, 144.0f, 128.0f, 18.0f), false);\n'
  '\n\tm_pRadioPredictNormalShot = NULL;\n\tm_pRadioPredictCobraShot = NULL;\n\tm_pRadioPredictSpikeShot = NULL;\n'
  '\tm_pRadioPredictTomahwakShot = NULL;\n\tm_unk5bc = 0;\n\tm_pUnk983_51c = NULL;\n\tm_unk983_648 = 0;\n}\n',
  '983: construtor do CGolfRule (0068aea0)'),
 # ---- CScreen: 0x444 -> 0x528 (push em 00753cb0; construtor 00751400; votos de out/F3.5/s53/raw) ----
 ('sub', 'src/projectg/gui_control.h', '\tCGuildInfo* m_pGuildInfo;\n\tCSimpleUI* m_pCammodeUI;\n\tCSimpleUI* m_pClubLineUI;\n\tCSimpleUI* m_pIconUI;\n\tCSimpleUI* m_pTutoTextUI;\n\tCSimpleUI* m_pCommandArrowUI;\n\tCSimpleUI* m_pTutoEscUI;\n',
  '\tCGuildInfo* m_pGuildInfo;\n'
  '\tvoid* m_pUnk983_250[7]; // 983: 8 ponteiros novos em 0x250..0x26c, zerados no construtor (00751400). Tipos provisórios\n'
  '\tCSimpleUI* m_pCommandArrowUI; // 983: saiu do lugar antigo (m_pTutoTextUI 0x27c e m_pTutoEscUI 0x280 são vizinhos); posto no 8º ponteiro novo (0x26c) só para o fonte compilar; NÃO medido\n'
  '\tCSimpleUI* m_pCammodeUI; // 983: 0x270\n\tCSimpleUI* m_pClubLineUI;\n\tCSimpleUI* m_pIconUI;\n\tCSimpleUI* m_pTutoTextUI;\n\tCSimpleUI* m_pTutoEscUI; // 983: 0x280\n',
  '983: CScreen +0x20 em m_pCammodeUI (0x250 -> 0x270) e +0x1c de m_pTutoEscUI (0x264 -> 0x280) a m_pFont (0x2cc -> 0x2e8)'),
 ('sub', 'src/projectg/gui_control.h', '\tunsigned long m_remainTimeColor;\n\tbool m_hudVisible;\n',
  '\tunsigned long m_remainTimeColor;\n'
  '\tunsigned char m_unk983_2f8[0x14]; // 983: +0x1c entre m_pFont (0x2e8) e m_hudVisible (0x314); lugar exato dentro do vão não medido\n'
  '\tfloat m_unk983_30c; // 983: 0.0f no construtor\n\tunsigned long m_unk983_310; // 983: 0 no construtor\n\tbool m_hudVisible; // 983: 0x314\n',
  '983: CScreen m_hudVisible 0x2dc -> 0x314 (+0x38)'),
 ('sub', 'src/projectg/gui_control.h', '\tsHitMark m_hitMarks[21];\n',
  '\tsHitMark m_hitMarks[21 + 10]; // 983: +0x50 entre m_hitBarTime (0x334) e m_blinkTime (0x434) = 10 marcas a mais (hipótese: o vetor cresceu; não conferi o limite do laço)\n',
  '983: CScreen m_blinkTime 0x3ac -> 0x434 (+0x88)'),
 ('sub', 'src/projectg/gui_control.h', '\tunsigned char m_playerCount;\n\tunsigned char m_unused409[0x3];\n',
  '\tunsigned char m_playerCount; // 983: 0x4c8\n\tunsigned char m_unused409[0x3];\n'
  '\tvoid* m_pUnk983_4cc; // 983: zerado no construtor\n'
  '\tvoid* m_pUnk983_4d0; // 983: objeto de 0x1e0 bytes criado no construtor (operator new + 0088e520(0, 0))\n'
  '\tunsigned long m_unk983_4d4;\n\tstd::string m_unk983_4d8; // 983: 2 std::string construídas vazias (0x4d8, 0x4f4)\n\tstd::string m_unk983_4f4;\n'
  '\tunsigned char m_unk983_510[0x18]; // 983: sizeof 0x528\n',
  '983: fim do CScreen (m_playerCount 0x4c8; ponteiros 0x4cc/0x4d0; strings 0x4d8/0x4f4)'),
 # ---- CGolfDoc: 0x860 -> 0x8c0 (push em 0066dcc0) ----
 ('sub', 'src/projectg/golfdoc.h', '\tunsigned long m_approachTotalPrize;\n\tstatic std::stack<CGolfDoc*, std::list<CGolfDoc*> > m_GolfDocInstanceStack;\n',
  '\tunsigned long m_approachTotalPrize;\n'
  '\tunsigned char m_unk983_860[0x60]; // 983: sizeof 0x8c0. Os votos dão delta 0 até 0x85c, então o espaço novo fica no fim; o construtor (0066d240) não o toca e não achei quem o usa\n'
  '\tstatic std::stack<CGolfDoc*, std::list<CGolfDoc*> > m_GolfDocInstanceStack;\n',
  '983: sizeof(CGolfDoc) = 0x8c0 (MakeInstance 0066dcc0; era 0x860)'),
 # ---- CGrid: 0x3240 -> 0x6b20 (push em 00749ae0) ----
 ('sub', 'src/projectg/grid.h', '\t\tMAX_GRID = 21\n',
  '\t\tMAX_GRID = 31 // 983 (era 21): m_grid 0x303c -> 0x691c = 31 * 31 * 0x1c (voto m_angle 0x3064 -> 0x6944; cauda igual, 0x1dc)\n',
  '983: sizeof(CGrid) = 0x6b20 = grade de 31 x 31 blocos'),
 # ---- CGolfCaddie: 0xa8 -> 0xd8 (construtor 0073a5d0) ----
 ('sub', 'src/projectg/golfcadie.h', '\tint m_fxScript;                 // +0x70\n\tCRing* m_pRing;                 // +0x74\n',
  '\tint m_fxScript;                 // +0x70\n'
  '\tvoid* m_pUnk983_74;             // 983: ponteiro novo = objeto de 0x1e0 bytes criado no construtor (operator new + 0088e520(0, 0); a mesma classe do CScreen +0x4d0). Classe não identificada; o nosso construtor NÃO o cria\n'
  '\tCRing* m_pRing;                 // +0x74; 983: 0x78\n',
  '983: CGolfCaddie tem um ponteiro novo em +0x74 (m_pRing 0x78, m_pCaddieTalk 0xa8)'),
 ('sub', 'src/projectg/golfcadie.h', '\tCCaddieTalk* m_pCaddieTalk;     // +0xa4\n',
  '\tCCaddieTalk* m_pCaddieTalk;     // +0xa4; 983: 0xa8\n'
  '\tstd::map<int, std::string> m_unk983_ac; // 983: árvore com nó de 0x30 bytes (cabeça em +0xb0, tamanho em +0xb4; 0x10 bytes no VS2010); chave/valor são hipótese pelo tamanho do nó\n'
  '\tstd::string m_unk983_bc;       // 983: std::string vazia (0xbc..0xd8); sizeof 0xd8\n',
  '983: fim do CGolfCaddie (map em 0xac, string em 0xbc)'),
]
# ---- localContentType_t no 983 (src/shared/localize.h) ----
# Medido com tools/f35/lcids.py (out/F3.5/s53/lc/lcids.tsv: id nosso -> id do 983 em cada chamada pareada de IsLocalContent) e pelo
# limite do bitset em IsLocalContent do 983 (cmp esi, 0xa7 em 00a7a8d3; o nosso era 0xa4).
#   medido: +1 em 0x15 0x17 0x1e 0x29 0x31 0x38 0x3a 0x3e 0x4b 0x4f 0x50 0x51 0x53 0x54 0x56 0x57 0x59 0x60; 0 até 0x14 e em 0x6a 0x6d;
#           -1 em 0x71 (e 0x72, sem nome); -3 em 0x7d 0x7f 0x81 0x83 0x85 0x87.
#   interpolado (sem chamada pareada; segue o vizinho medido): os demais de 0x15 a 0x68 (+1), 0x76 (-1), 0x80 0x82 0x84 (-3).
#   não mexidos: 0x6b 0x6c 0x6e 0x6f (entre 0 e -1) e os ids usados como número no fonte (0x70, 0x8c, 0x9a...).
def _lc():
    import re, os
    p = '/root/jp983src/src/shared/localize.h'
    med = {0x15, 0x17, 0x1e, 0x29, 0x31, 0x38, 0x3a, 0x3e, 0x4b, 0x4f, 0x50, 0x51, 0x53, 0x54, 0x56, 0x57, 0x59, 0x60, 0x71, 0x7d, 0x7f, 0x81, 0x83, 0x85, 0x87}
    out = []
    for m in re.finditer(r'^\t(\w+) = (0x[0-9a-f]+),\n', open(p, encoding='latin-1').read(), re.M):
        n, v = m.group(1), int(m.group(2), 16)
        d = 1 if 0x15 <= v <= 0x68 else -1 if v in (0x71, 0x76) else -3 if 0x7d <= v <= 0x87 else 0
        if d:
            out.append(('sub', 'src/shared/localize.h', '\t%s = 0x%02x,\n' % (n, v),
                        '\t%s = 0x%02x, // 983 (645: 0x%02x; %s)\n' % (n, v + d, v, 'medido' if v in med else 'interpolado'),
                        '983: localContentType_t %s 0x%02x -> 0x%02x' % (n, v, v + d)))
    return out
# lista fixa (gerada uma vez por _lc() sobre o cabeçalho do rebang b43864b), para o ajuste não depender do estado do arquivo
NEW21 += [
 ('sub', 'src/shared/localize.h', '\tS3_EVENT_FLAG = 0x22,\n', '\tS3_EVENT_FLAG = 0x23, // 983 (645: 0x22; interpolado)\n', '983: localContentType_t S3_EVENT_FLAG 0x22 -> 0x23'),
 ('sub', 'src/shared/localize.h', '\tS3_ICE_SPA = 0x26,\n', '\tS3_ICE_SPA = 0x27, // 983 (645: 0x26; interpolado)\n', '983: localContentType_t S3_ICE_SPA 0x26 -> 0x27'),
 ('sub', 'src/shared/localize.h', '\tS3_DISCONNECT_CODE = 0x27,\n', '\tS3_DISCONNECT_CODE = 0x28, // 983 (645: 0x27; interpolado)\n', '983: localContentType_t S3_DISCONNECT_CODE 0x27 -> 0x28'),
 ('sub', 'src/shared/localize.h', '\tS3_MATCH_HISTORY = 0x28,\n', '\tS3_MATCH_HISTORY = 0x29, // 983 (645: 0x28; interpolado)\n', '983: localContentType_t S3_MATCH_HISTORY 0x28 -> 0x29'),
 ('sub', 'src/shared/localize.h', '\tS3_LEVELUP_ITEM = 0x29,\n', '\tS3_LEVELUP_ITEM = 0x2a, // 983 (645: 0x29; medido)\n', '983: localContentType_t S3_LEVELUP_ITEM 0x29 -> 0x2a'),
 ('sub', 'src/shared/localize.h', '\tS3_HUNDRED_MODE = 0x2b,\n', '\tS3_HUNDRED_MODE = 0x2c, // 983 (645: 0x2b; interpolado)\n', '983: localContentType_t S3_HUNDRED_MODE 0x2b -> 0x2c'),
 ('sub', 'src/shared/localize.h', '\tS3_CHECK_SESSION = 0x2c,\n', '\tS3_CHECK_SESSION = 0x2d, // 983 (645: 0x2c; interpolado)\n', '983: localContentType_t S3_CHECK_SESSION 0x2c -> 0x2d'),
 ('sub', 'src/shared/localize.h', '\tS3_SHOTRESULT_ENCRYPT = 0x2d,\n', '\tS3_SHOTRESULT_ENCRYPT = 0x2e, // 983 (645: 0x2d; interpolado)\n', '983: localContentType_t S3_SHOTRESULT_ENCRYPT 0x2d -> 0x2e'),
 ('sub', 'src/shared/localize.h', '\tS3_INTRUSION = 0x2e,\n', '\tS3_INTRUSION = 0x2f, // 983 (645: 0x2e; interpolado)\n', '983: localContentType_t S3_INTRUSION 0x2e -> 0x2f'),
 ('sub', 'src/shared/localize.h', '\tS3_SAFETEE_ITEM = 0x2f,\n', '\tS3_SAFETEE_ITEM = 0x30, // 983 (645: 0x2f; interpolado)\n', '983: localContentType_t S3_SAFETEE_ITEM 0x2f -> 0x30'),
 ('sub', 'src/shared/localize.h', '\tS3_AUTOCALIPERS_ITEM = 0x30,\n', '\tS3_AUTOCALIPERS_ITEM = 0x31, // 983 (645: 0x30; interpolado)\n', '983: localContentType_t S3_AUTOCALIPERS_ITEM 0x30 -> 0x31'),
 ('sub', 'src/shared/localize.h', '\tS3_STRENGTH = 0x31,\n', '\tS3_STRENGTH = 0x32, // 983 (645: 0x31; medido)\n', '983: localContentType_t S3_STRENGTH 0x31 -> 0x32'),
 ('sub', 'src/shared/localize.h', '\tS3_CADDIEBONUS = 0x32,\n', '\tS3_CADDIEBONUS = 0x33, // 983 (645: 0x32; interpolado)\n', '983: localContentType_t S3_CADDIEBONUS 0x32 -> 0x33'),
 ('sub', 'src/shared/localize.h', '\tS3_ELFEAR = 0x33,\n', '\tS3_ELFEAR = 0x34, // 983 (645: 0x33; interpolado)\n', '983: localContentType_t S3_ELFEAR 0x33 -> 0x34'),
 ('sub', 'src/shared/localize.h', '\tS3_INSERTGIFT_CHANGE = 0x34,\n', '\tS3_INSERTGIFT_CHANGE = 0x35, // 983 (645: 0x34; interpolado)\n', '983: localContentType_t S3_INSERTGIFT_CHANGE 0x34 -> 0x35'),
 ('sub', 'src/shared/localize.h', '\tS3_PASSWORD_MD5 = 0x35,\n', '\tS3_PASSWORD_MD5 = 0x36, // 983 (645: 0x35; interpolado)\n', '983: localContentType_t S3_PASSWORD_MD5 0x35 -> 0x36'),
 ('sub', 'src/shared/localize.h', '\tS3_TUTORIAL_RENEWAL = 0x38,\n', '\tS3_TUTORIAL_RENEWAL = 0x39, // 983 (645: 0x38; medido)\n', '983: localContentType_t S3_TUTORIAL_RENEWAL 0x38 -> 0x39'),
 ('sub', 'src/shared/localize.h', '\tS3_MAP_EVENT = 0x39,\n', '\tS3_MAP_EVENT = 0x3a, // 983 (645: 0x39; interpolado)\n', '983: localContentType_t S3_MAP_EVENT 0x39 -> 0x3a'),
 ('sub', 'src/shared/localize.h', '\tS3_ROOKIE_CHANNEL = 0x3a,\n', '\tS3_ROOKIE_CHANNEL = 0x3b, // 983 (645: 0x3a; medido)\n', '983: localContentType_t S3_ROOKIE_CHANNEL 0x3a -> 0x3b'),
 ('sub', 'src/shared/localize.h', '\tS3_TIKI_REPORT = 0x3d,\n', '\tS3_TIKI_REPORT = 0x3e, // 983 (645: 0x3d; interpolado)\n', '983: localContentType_t S3_TIKI_REPORT 0x3d -> 0x3e'),
 ('sub', 'src/shared/localize.h', '\tS3_ROOKIE_RESTRICT = 0x3e,\n', '\tS3_ROOKIE_RESTRICT = 0x3f, // 983 (645: 0x3e; medido)\n', '983: localContentType_t S3_ROOKIE_RESTRICT 0x3e -> 0x3f'),
 ('sub', 'src/shared/localize.h', '\tS3_NEWYEAR_MONEY = 0x40,\n', '\tS3_NEWYEAR_MONEY = 0x41, // 983 (645: 0x40; interpolado)\n', '983: localContentType_t S3_NEWYEAR_MONEY 0x40 -> 0x41'),
 ('sub', 'src/shared/localize.h', '\tS3_ITEMDROP_LOG = 0x44,\n', '\tS3_ITEMDROP_LOG = 0x45, // 983 (645: 0x44; interpolado)\n', '983: localContentType_t S3_ITEMDROP_LOG 0x44 -> 0x45'),
 ('sub', 'src/shared/localize.h', '\tS3_ADD_USER_ACTION_LOG = 0x45,\n', '\tS3_ADD_USER_ACTION_LOG = 0x46, // 983 (645: 0x45; interpolado)\n', '983: localContentType_t S3_ADD_USER_ACTION_LOG 0x45 -> 0x46'),
 ('sub', 'src/shared/localize.h', '\tS3_TUTORIAL_SECOND_GRADE = 0x46,\n', '\tS3_TUTORIAL_SECOND_GRADE = 0x47, // 983 (645: 0x46; interpolado)\n', '983: localContentType_t S3_TUTORIAL_SECOND_GRADE 0x46 -> 0x47'),
 ('sub', 'src/shared/localize.h', '\tS3_OPEN_LUCKY_POUCH = 0x4a,\n', '\tS3_OPEN_LUCKY_POUCH = 0x4b, // 983 (645: 0x4a; interpolado)\n', '983: localContentType_t S3_OPEN_LUCKY_POUCH 0x4a -> 0x4b'),
 ('sub', 'src/shared/localize.h', '\tS3_MYSTIC_RING = 0x4b,\n', '\tS3_MYSTIC_RING = 0x4c, // 983 (645: 0x4b; medido)\n', '983: localContentType_t S3_MYSTIC_RING 0x4b -> 0x4c'),
 ('sub', 'src/shared/localize.h', '\tS3_EVENT_ADDTIONAL_GIVEAWAY = 0x4d,\n', '\tS3_EVENT_ADDTIONAL_GIVEAWAY = 0x4e, // 983 (645: 0x4d; interpolado)\n', '983: localContentType_t S3_EVENT_ADDTIONAL_GIVEAWAY 0x4d -> 0x4e'),
 ('sub', 'src/shared/localize.h', '\tS4_PACKET_COMPRESS = 0x4e,\n', '\tS4_PACKET_COMPRESS = 0x4f, // 983 (645: 0x4e; interpolado)\n', '983: localContentType_t S4_PACKET_COMPRESS 0x4e -> 0x4f'),
 ('sub', 'src/shared/localize.h', '\tS4_REPLAY_SYSTEM = 0x4f,\n', '\tS4_REPLAY_SYSTEM = 0x50, // 983 (645: 0x4f; medido)\n', '983: localContentType_t S4_REPLAY_SYSTEM 0x4f -> 0x50'),
 ('sub', 'src/shared/localize.h', '\tS4_SPECIALSHOT_RESTRICTION_MODIFY = 0x50,\n', '\tS4_SPECIALSHOT_RESTRICTION_MODIFY = 0x51, // 983 (645: 0x50; medido)\n', '983: localContentType_t S4_SPECIALSHOT_RESTRICTION_MODIFY 0x50 -> 0x51'),
 ('sub', 'src/shared/localize.h', '\tS4_CARD_SYSTEM = 0x51,\n', '\tS4_CARD_SYSTEM = 0x52, // 983 (645: 0x51; medido)\n', '983: localContentType_t S4_CARD_SYSTEM 0x51 -> 0x52'),
 ('sub', 'src/shared/localize.h', '\tS4_GOWITH_FRIEND = 0x53,\n', '\tS4_GOWITH_FRIEND = 0x54, // 983 (645: 0x53; medido)\n', '983: localContentType_t S4_GOWITH_FRIEND 0x53 -> 0x54'),
 ('sub', 'src/shared/localize.h', '\tS4_INVITE_FRIEND = 0x54,\n', '\tS4_INVITE_FRIEND = 0x55, // 983 (645: 0x54; medido)\n', '983: localContentType_t S4_INVITE_FRIEND 0x54 -> 0x55'),
 ('sub', 'src/shared/localize.h', '\tS4_REAL_MYROOM = 0x56,\n', '\tS4_REAL_MYROOM = 0x57, // 983 (645: 0x56; medido)\n', '983: localContentType_t S4_REAL_MYROOM 0x56 -> 0x57'),
 ('sub', 'src/shared/localize.h', '\tS4_UCC = 0x57,\n', '\tS4_UCC = 0x58, // 983 (645: 0x57; medido)\n', '983: localContentType_t S4_UCC 0x57 -> 0x58'),
 ('sub', 'src/shared/localize.h', '\tS4_TREASURE_HUNTER = 0x58,\n', '\tS4_TREASURE_HUNTER = 0x59, // 983 (645: 0x58; interpolado)\n', '983: localContentType_t S4_TREASURE_HUNTER 0x58 -> 0x59'),
 ('sub', 'src/shared/localize.h', '\tS4_MATCHING_SYSTEM = 0x59,\n', '\tS4_MATCHING_SYSTEM = 0x5a, // 983 (645: 0x59; medido)\n', '983: localContentType_t S4_MATCHING_SYSTEM 0x59 -> 0x5a'),
 ('sub', 'src/shared/localize.h', '\tS4_GHOST = 0x5d,\n', '\tS4_GHOST = 0x5e, // 983 (645: 0x5d; interpolado)\n', '983: localContentType_t S4_GHOST 0x5d -> 0x5e'),
 ('sub', 'src/shared/localize.h', '\tS4_GUID_BASE = 0x5f,\n', '\tS4_GUID_BASE = 0x60, // 983 (645: 0x5f; interpolado)\n', '983: localContentType_t S4_GUID_BASE 0x5f -> 0x60'),
 ('sub', 'src/shared/localize.h', '\tS4_MAILBOX_FOR_REAL_MYROOM = 0x60,\n', '\tS4_MAILBOX_FOR_REAL_MYROOM = 0x61, // 983 (645: 0x60; medido)\n', '983: localContentType_t S4_MAILBOX_FOR_REAL_MYROOM 0x60 -> 0x61'),
 ('sub', 'src/shared/localize.h', '\tS4_REAL_MYROOM_TEST_ENABLE = 0x61,\n', '\tS4_REAL_MYROOM_TEST_ENABLE = 0x62, // 983 (645: 0x61; interpolado)\n', '983: localContentType_t S4_REAL_MYROOM_TEST_ENABLE 0x61 -> 0x62'),
 ('sub', 'src/shared/localize.h', '\tS4_OPEN_RECYCLE_SPECIAL_TAB = 0x63,\n', '\tS4_OPEN_RECYCLE_SPECIAL_TAB = 0x64, // 983 (645: 0x63; interpolado)\n', '983: localContentType_t S4_OPEN_RECYCLE_SPECIAL_TAB 0x63 -> 0x64'),
 ('sub', 'src/shared/localize.h', '\tS4_APPLY_CARD_FAMILYMODE = 0x64,\n', '\tS4_APPLY_CARD_FAMILYMODE = 0x65, // 983 (645: 0x64; interpolado)\n', '983: localContentType_t S4_APPLY_CARD_FAMILYMODE 0x64 -> 0x65'),
 ('sub', 'src/shared/localize.h', '\tS4_OFFLINE_SHOP = 0x66,\n', '\tS4_OFFLINE_SHOP = 0x67, // 983 (645: 0x66; interpolado)\n', '983: localContentType_t S4_OFFLINE_SHOP 0x66 -> 0x67'),
 ('sub', 'src/shared/localize.h', '\tS4_TREASURE_HUNTER_AD = 0x67,\n', '\tS4_TREASURE_HUNTER_AD = 0x68, // 983 (645: 0x67; interpolado)\n', '983: localContentType_t S4_TREASURE_HUNTER_AD 0x67 -> 0x68'),
 ('sub', 'src/shared/localize.h', '\tS4_NEW_GUILD_POINT = 0x68,\n', '\tS4_NEW_GUILD_POINT = 0x69, // 983 (645: 0x68; interpolado)\n', '983: localContentType_t S4_NEW_GUILD_POINT 0x68 -> 0x69'),
 ('sub', 'src/shared/localize.h', '\tS4_ITEM_STORAGE = 0x71,\n', '\tS4_ITEM_STORAGE = 0x70, // 983 (645: 0x71; medido)\n', '983: localContentType_t S4_ITEM_STORAGE 0x71 -> 0x70'),
 ('sub', 'src/shared/localize.h', '\tS4_FURNITURE_ABILITY = 0x76,\n', '\tS4_FURNITURE_ABILITY = 0x75, // 983 (645: 0x76; interpolado)\n', '983: localContentType_t S4_FURNITURE_ABILITY 0x76 -> 0x75'),
 ('sub', 'src/shared/localize.h', '\tS4NT_VIEW_OFFLINE_GUILD = 0x7d,\n', '\tS4NT_VIEW_OFFLINE_GUILD = 0x7a, // 983 (645: 0x7d; medido)\n', '983: localContentType_t S4NT_VIEW_OFFLINE_GUILD 0x7d -> 0x7a'),
 ('sub', 'src/shared/localize.h', '\tS4_FIX_ENCHANT = 0x7f,\n', '\tS4_FIX_ENCHANT = 0x7c, // 983 (645: 0x7f; medido)\n', '983: localContentType_t S4_FIX_ENCHANT 0x7f -> 0x7c'),
 ('sub', 'src/shared/localize.h', '\tNT_FURNITURESAVE2 = 0x80,\n', '\tNT_FURNITURESAVE2 = 0x7d, // 983 (645: 0x80; interpolado)\n', '983: localContentType_t NT_FURNITURESAVE2 0x80 -> 0x7d'),
 ('sub', 'src/shared/localize.h', '\tS4_NT_NICKNAME_CHANGE = 0x81,\n', '\tS4_NT_NICKNAME_CHANGE = 0x7e, // 983 (645: 0x81; medido)\n', '983: localContentType_t S4_NT_NICKNAME_CHANGE 0x81 -> 0x7e'),
 ('sub', 'src/shared/localize.h', '\tS4_NT_NICKNAME_CHANGE_2ND = 0x82,\n', '\tS4_NT_NICKNAME_CHANGE_2ND = 0x7f, // 983 (645: 0x82; interpolado)\n', '983: localContentType_t S4_NT_NICKNAME_CHANGE_2ND 0x82 -> 0x7f'),
 ('sub', 'src/shared/localize.h', '\tS4_NT_EVENT_MISSION = 0x83,\n', '\tS4_NT_EVENT_MISSION = 0x80, // 983 (645: 0x83; medido)\n', '983: localContentType_t S4_NT_EVENT_MISSION 0x83 -> 0x80'),
 ('sub', 'src/shared/localize.h', '\tS4_NT_SC_ITEMSLOT = 0x84,\n', '\tS4_NT_SC_ITEMSLOT = 0x81, // 983 (645: 0x84; interpolado)\n', '983: localContentType_t S4_NT_SC_ITEMSLOT 0x84 -> 0x81'),
 ('sub', 'src/shared/localize.h', '\tS4_NT_EVENT_BINGO = 0x85,\n', '\tS4_NT_EVENT_BINGO = 0x82, // 983 (645: 0x85; medido)\n', '983: localContentType_t S4_NT_EVENT_BINGO 0x85 -> 0x82'),
 ('sub', 'src/shared/localize.h', '\tS4_HACKINGTOOL = 0x87,\n', '\tS4_HACKINGTOOL = 0x84, // 983 (645: 0x87; medido)\n', '983: localContentType_t S4_HACKINGTOOL 0x87 -> 0x84'),
 ('sub', 'src/shared/localize.h', '\tMAX_LOCAL_CONTENTS = 0xa4\n', '\tMAX_LOCAL_CONTENTS = 0xa7 // 983: cmp esi, 0xa7 em IsLocalContent (00a7a8d3); era 0xa4\n', '983: MAX_LOCAL_CONTENTS 0xa4 -> 0xa7'),
 # ids passados como número: IsLocalContent((localContentType_t)N). O texto novo leva o comentário /*983*/ e por isso não casa de novo (idempotente).
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x15)', 'IsLocalContent((localContentType_t)0x16 /*983: era 0x15; medido*/)', '983: id de IsLocalContent 0x15 -> 0x16 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x16)', 'IsLocalContent((localContentType_t)0x17 /*983: era 0x16; interpolado*/)', '983: id de IsLocalContent 0x16 -> 0x17 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x17)', 'IsLocalContent((localContentType_t)0x18 /*983: era 0x17; medido*/)', '983: id de IsLocalContent 0x17 -> 0x18 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x18)', 'IsLocalContent((localContentType_t)0x19 /*983: era 0x18; interpolado*/)', '983: id de IsLocalContent 0x18 -> 0x19 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x1e)', 'IsLocalContent((localContentType_t)0x1f /*983: era 0x1e; medido*/)', '983: id de IsLocalContent 0x1e -> 0x1f (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x20)', 'IsLocalContent((localContentType_t)0x21 /*983: era 0x20; interpolado*/)', '983: id de IsLocalContent 0x20 -> 0x21 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x21)', 'IsLocalContent((localContentType_t)0x22 /*983: era 0x21; interpolado*/)', '983: id de IsLocalContent 0x21 -> 0x22 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x24)', 'IsLocalContent((localContentType_t)0x25 /*983: era 0x24; interpolado*/)', '983: id de IsLocalContent 0x24 -> 0x25 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x26)', 'IsLocalContent((localContentType_t)0x27 /*983: era 0x26; interpolado*/)', '983: id de IsLocalContent 0x26 -> 0x27 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x28)', 'IsLocalContent((localContentType_t)0x29 /*983: era 0x28; interpolado*/)', '983: id de IsLocalContent 0x28 -> 0x29 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x29)', 'IsLocalContent((localContentType_t)0x2a /*983: era 0x29; medido*/)', '983: id de IsLocalContent 0x29 -> 0x2a (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x2a)', 'IsLocalContent((localContentType_t)0x2b /*983: era 0x2a; interpolado*/)', '983: id de IsLocalContent 0x2a -> 0x2b (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x2b)', 'IsLocalContent((localContentType_t)0x2c /*983: era 0x2b; interpolado*/)', '983: id de IsLocalContent 0x2b -> 0x2c (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)43)', 'IsLocalContent((localContentType_t)44 /*983: era 43; interpolado*/)', '983: id de IsLocalContent 43 -> 44 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x2d)', 'IsLocalContent((localContentType_t)0x2e /*983: era 0x2d; interpolado*/)', '983: id de IsLocalContent 0x2d -> 0x2e (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)46)', 'IsLocalContent((localContentType_t)47 /*983: era 46; interpolado*/)', '983: id de IsLocalContent 46 -> 47 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x2e)', 'IsLocalContent((localContentType_t)0x2f /*983: era 0x2e; interpolado*/)', '983: id de IsLocalContent 0x2e -> 0x2f (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x2f)', 'IsLocalContent((localContentType_t)0x30 /*983: era 0x2f; interpolado*/)', '983: id de IsLocalContent 0x2f -> 0x30 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x30)', 'IsLocalContent((localContentType_t)0x31 /*983: era 0x30; interpolado*/)', '983: id de IsLocalContent 0x30 -> 0x31 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x31)', 'IsLocalContent((localContentType_t)0x32 /*983: era 0x31; medido*/)', '983: id de IsLocalContent 0x31 -> 0x32 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x32)', 'IsLocalContent((localContentType_t)0x33 /*983: era 0x32; interpolado*/)', '983: id de IsLocalContent 0x32 -> 0x33 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x38)', 'IsLocalContent((localContentType_t)0x39 /*983: era 0x38; medido*/)', '983: id de IsLocalContent 0x38 -> 0x39 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x39)', 'IsLocalContent((localContentType_t)0x3a /*983: era 0x39; interpolado*/)', '983: id de IsLocalContent 0x39 -> 0x3a (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x3a)', 'IsLocalContent((localContentType_t)0x3b /*983: era 0x3a; medido*/)', '983: id de IsLocalContent 0x3a -> 0x3b (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x3f)', 'IsLocalContent((localContentType_t)0x40 /*983: era 0x3f; interpolado*/)', '983: id de IsLocalContent 0x3f -> 0x40 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x48)', 'IsLocalContent((localContentType_t)0x49 /*983: era 0x48; interpolado*/)', '983: id de IsLocalContent 0x48 -> 0x49 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x4b)', 'IsLocalContent((localContentType_t)0x4c /*983: era 0x4b; medido*/)', '983: id de IsLocalContent 0x4b -> 0x4c (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x4c)', 'IsLocalContent((localContentType_t)0x4d /*983: era 0x4c; interpolado*/)', '983: id de IsLocalContent 0x4c -> 0x4d (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x4f)', 'IsLocalContent((localContentType_t)0x50 /*983: era 0x4f; medido*/)', '983: id de IsLocalContent 0x4f -> 0x50 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)79)', 'IsLocalContent((localContentType_t)80 /*983: era 79; medido*/)', '983: id de IsLocalContent 79 -> 80 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x50)', 'IsLocalContent((localContentType_t)0x51 /*983: era 0x50; medido*/)', '983: id de IsLocalContent 0x50 -> 0x51 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x51)', 'IsLocalContent((localContentType_t)0x52 /*983: era 0x51; medido*/)', '983: id de IsLocalContent 0x51 -> 0x52 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)81)', 'IsLocalContent((localContentType_t)82 /*983: era 81; medido*/)', '983: id de IsLocalContent 81 -> 82 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x54)', 'IsLocalContent((localContentType_t)0x55 /*983: era 0x54; medido*/)', '983: id de IsLocalContent 0x54 -> 0x55 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)84)', 'IsLocalContent((localContentType_t)85 /*983: era 84; medido*/)', '983: id de IsLocalContent 84 -> 85 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)85)', 'IsLocalContent((localContentType_t)86 /*983: era 85; interpolado*/)', '983: id de IsLocalContent 85 -> 86 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x55)', 'IsLocalContent((localContentType_t)0x56 /*983: era 0x55; interpolado*/)', '983: id de IsLocalContent 0x55 -> 0x56 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x56)', 'IsLocalContent((localContentType_t)0x57 /*983: era 0x56; medido*/)', '983: id de IsLocalContent 0x56 -> 0x57 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x57)', 'IsLocalContent((localContentType_t)0x58 /*983: era 0x57; medido*/)', '983: id de IsLocalContent 0x57 -> 0x58 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)88)', 'IsLocalContent((localContentType_t)89 /*983: era 88; interpolado*/)', '983: id de IsLocalContent 88 -> 89 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x58)', 'IsLocalContent((localContentType_t)0x59 /*983: era 0x58; interpolado*/)', '983: id de IsLocalContent 0x58 -> 0x59 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x59)', 'IsLocalContent((localContentType_t)0x5a /*983: era 0x59; medido*/)', '983: id de IsLocalContent 0x59 -> 0x5a (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x5a)', 'IsLocalContent((localContentType_t)0x5b /*983: era 0x5a; interpolado*/)', '983: id de IsLocalContent 0x5a -> 0x5b (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)90)', 'IsLocalContent((localContentType_t)91 /*983: era 90; interpolado*/)', '983: id de IsLocalContent 90 -> 91 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x5b)', 'IsLocalContent((localContentType_t)0x5c /*983: era 0x5b; interpolado*/)', '983: id de IsLocalContent 0x5b -> 0x5c (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x5f)', 'IsLocalContent((localContentType_t)0x60 /*983: era 0x5f; interpolado*/)', '983: id de IsLocalContent 0x5f -> 0x60 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x60)', 'IsLocalContent((localContentType_t)0x61 /*983: era 0x60; medido*/)', '983: id de IsLocalContent 0x60 -> 0x61 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x61)', 'IsLocalContent((localContentType_t)0x62 /*983: era 0x61; interpolado*/)', '983: id de IsLocalContent 0x61 -> 0x62 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x63)', 'IsLocalContent((localContentType_t)0x64 /*983: era 0x63; interpolado*/)', '983: id de IsLocalContent 0x63 -> 0x64 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x64)', 'IsLocalContent((localContentType_t)0x65 /*983: era 0x64; interpolado*/)', '983: id de IsLocalContent 0x64 -> 0x65 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x65)', 'IsLocalContent((localContentType_t)0x66 /*983: era 0x65; interpolado*/)', '983: id de IsLocalContent 0x65 -> 0x66 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x66)', 'IsLocalContent((localContentType_t)0x67 /*983: era 0x66; interpolado*/)', '983: id de IsLocalContent 0x66 -> 0x67 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x71)', 'IsLocalContent((localContentType_t)0x70 /*983: era 0x71; medido*/)', '983: id de IsLocalContent 0x71 -> 0x70 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x72)', 'IsLocalContent((localContentType_t)0x71 /*983: era 0x72; medido*/)', '983: id de IsLocalContent 0x72 -> 0x71 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x76)', 'IsLocalContent((localContentType_t)0x75 /*983: era 0x76; interpolado*/)', '983: id de IsLocalContent 0x76 -> 0x75 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x7e)', 'IsLocalContent((localContentType_t)0x7b /*983: era 0x7e; medido*/)', '983: id de IsLocalContent 0x7e -> 0x7b (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x80)', 'IsLocalContent((localContentType_t)0x7d /*983: era 0x80; interpolado*/)', '983: id de IsLocalContent 0x80 -> 0x7d (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x81)', 'IsLocalContent((localContentType_t)0x7e /*983: era 0x81; medido*/)', '983: id de IsLocalContent 0x81 -> 0x7e (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)129)', 'IsLocalContent((localContentType_t)126 /*983: era 129; medido*/)', '983: id de IsLocalContent 129 -> 126 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x82)', 'IsLocalContent((localContentType_t)0x7f /*983: era 0x82; interpolado*/)', '983: id de IsLocalContent 0x82 -> 0x7f (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x83)', 'IsLocalContent((localContentType_t)0x80 /*983: era 0x83; medido*/)', '983: id de IsLocalContent 0x83 -> 0x80 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x84)', 'IsLocalContent((localContentType_t)0x81 /*983: era 0x84; interpolado*/)', '983: id de IsLocalContent 0x84 -> 0x81 (interpolado)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x85)', 'IsLocalContent((localContentType_t)0x82 /*983: era 0x85; medido*/)', '983: id de IsLocalContent 0x85 -> 0x82 (medido)'),
 ('todos', 'src/projectg/*.cpp', 'IsLocalContent((localContentType_t)0x87)', 'IsLocalContent((localContentType_t)0x84 /*983: era 0x87; medido*/)', '983: id de IsLocalContent 0x87 -> 0x84 (medido)'),
]
