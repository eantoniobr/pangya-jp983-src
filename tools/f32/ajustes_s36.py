# F3.4 (sessão 36): classes sem tela, medidas no construtor do 983. Lido por tools/f32/ajustes.py no fim.
# Evidência: out/F3.4/s36/classes_983.md.
NEW8 = [
 # CWind: construtor 006cb590 (vtable 00d1a3dc). WCrypticValue<float> em 0x14, 0x24, 0x34 (novo), 0x44 (novo); byte 0x54
 # (novo; 006c9300 grava !arg); m_roll 0x58; m_mat 0x5c; m_light 0x8c; dword 0xa8 (novo); m_pitch 0xac; min 0xb0 (1.0),
 # max 0xb4 (9.0); m_bEnable 0xb8; m_areas 0xc8; dois vetores cifrados de 0x3c (3 WCrypticValue<float> + WVector de cache;
 # 006c7e00 decifra para o cache e devolve o ponteiro) em 0xd8 e 0x114; m_specialIntensity 0x150; m_specialDirection 0x160;
 # m_bSpecial 0x170; m_fxMat 0x174; m_fxPos 0x1a4; m_pFxSeq 0x1b0; sizeof 0x1b4. SetSpecialWind do 983 (006c7e40) passa
 # 0x114 quando especial e 0xd8 quando não: 0x114 = m_specialWind, 0xd8 = m_globalWind; m_netWind não existe mais.
 ('sub', 'src/projectg/wind.h', 'class CWind\n{\npublic:\n',
  '// 983: vetor cifrado (0x3c): 3 WCrypticValue<float> + cache em claro; 006c7e00 = Get(). Nome meu.\n'
  'struct WCrypticVector983\n{\n\tWCrypticValue<float> x;\n\tWCrypticValue<float> y;\n\tWCrypticValue<float> z;\n\tWVector plain;\n\n'
  '\tconst WVector& Get()\n\t{\n\t\tplain.x = x;\n\t\tplain.y = y;\n\t\tplain.z = z;\n\t\treturn plain;\n\t}\n'
  '\tWCrypticVector983& operator=(const WVector& v)\n\t{\n\t\tx = v.x;\n\t\ty = v.y;\n\t\tz = v.z;\n\t\treturn *this;\n\t}\n'
  '\toperator WVector() { return Get(); }\n};\n\n'
  'class CWind\n{\npublic:\n', '983: tipo do vetor cifrado do CWind (0x3c)'),
 ('sub', 'src/projectg/wind.h', '\tWCrypticValue<float> m_direction;\n\tfloat m_roll;\n',
  '\tWCrypticValue<float> m_direction;\n\tWCrypticValue<float> m_cryptic34_983; // 983: 0x34 (zerado em 006c9300); nome meu\n'
  '\tWCrypticValue<float> m_cryptic44_983; // 983: 0x44 (setter 006c9290); nome meu\n'
  '\tbool m_b54_983; // 983: 0x54 (006c9300 grava !arg2); nome meu\n\tfloat m_roll;\n',
  '983: CWind 2 WCrypticValue<float> + byte novos (m_roll 0x58, m_mat 0x5c, m_light 0x8c)'),
 ('sub', 'src/projectg/wind.h', '\tLightSet m_light;\n\tfloat m_pitch;\n',
  '\tLightSet m_light;\n\tunsigned long m_unk_a8_983; // 983: 0xa8, não medido\n\tfloat m_pitch;\n',
  '983: CWind dword novo em 0xa8 (m_pitch 0xac, m_minIntensity 0xb0, m_maxIntensity 0xb4, m_bEnable 0xb8, m_areas 0xc8)'),
 ('sub', 'src/projectg/wind.h', '\tWVector m_netWind;\n\tWVector m_globalWind;\n\tWVector m_specialWind;\n',
  '\tstatic WVector m_netWind; // 983: não existe (PROVISÓRIO: static para o .cpp do 645 compilar)\n'
  '\tWCrypticVector983 m_globalWind; // 983: 0xd8\n\tWCrypticVector983 m_specialWind; // 983: 0x114\n',
  '983: CWind vetores cifrados em 0xd8 e 0x114, sem m_netWind (m_specialIntensity 0x150 ... m_pFxSeq 0x1b0, sizeof 0x1b4)'),
 ('sub', 'src/projectg/wind.cpp', 'CWind::CWind()\n{\n', 'WVector CWind::m_netWind; // 983: não existe (PROVISÓRIO)\n\nCWind::CWind()\n{\n',
  '983: definição do static provisório m_netWind'),
 # CFxBox: construtor 009735a0 (vtable 00d3d290). Mapas (cabeça/tamanho): 0x128 (nó 0x30, novo), 0x138 (nó 0x30 =
 # m_sequenceCache), m_pResMng 0x148 (Init 0096c7b0), 0x14c (nó 0x30), 0x15c (nó 0x18 = m_spray), 0x16c (nó 0x18), lista
 # 0x408 (nó 0x10), m_groundHeightMax 0x418, m_groundHeightMin 0x41c, sizeof 0x420 (CPvsFxBox: mapas em 0x420 e 0x430,
 # sizeof 0x440 — construtor 0048e9b0). A classe é opaca no fonte (blocos m_unused*): só os tamanhos dos blocos mudam.
 # (s47) os 3 ajustes do fxbox.h saíram: o rebang e6a6c6e abriu a classe (REBANG_FXBOX_CPP) e o arquivo passou a ser
 # mantido pela mescla de 3 vias, com o layout do 983 resolvido à mão (out/F3.5/s47/RELATORIO.md).
 # CBase: construtor 006e46d0. m_texLine 0x78; em 0x7c um CGroundMaxPowerInfo (RTTI da vtable 00d08b38, base CFontInfo;
 # construtor 00527220 carrega "[font_condition.jpg"/"[font_condition_x2.jpg"; 0x2c bytes) no lugar de m_texFont;
 # m_segments 0xa8 (= 12), m_penalty 0xac, m_spin 0xb0, m_matrix 0xb8, m_angle 0xe8, m_fx 0xec, m_vl 0x52c, m_vtx 0x540.
 ('sub', 'src/projectg/ground_info.h', '#include "fx.h"\n', '#include "fx.h"\n#include "fontinfo.h"\n', '983: CBase usa CFontInfo'),
 ('sub', 'src/projectg/ground_info.h', 'class CBase\n{\npublic:\n',
  '// 983: classe nova (RTTI CGroundMaxPowerInfo : CFontInfo, vtable 00d08b38, construtor 00527220, 0x2c bytes).\n'
  '// Só o tamanho está medido; corpo na F3.7.\nclass CGroundMaxPowerInfo : public CFontInfo\n{\npublic:\n\tCGroundMaxPowerInfo();\n'
  '\tvirtual ~CGroundMaxPowerInfo();\n\nprivate:\n\tunsigned char m_unk983[0x2c - sizeof(CFontInfo)];\n};\n\n'
  'class CBase\n{\npublic:\n', '983: CGroundMaxPowerInfo (só tamanho)'),
 ('sub', 'src/projectg/ground_info.h', '\tint m_texLine;\n\tint m_texFont;\n',
  '\tint m_texLine;\n\tstatic int m_texFont; // 983: não existe (PROVISÓRIO: static para o .cpp do 645 compilar)\n'
  '\tCGroundMaxPowerInfo m_maxPowerInfo; // 983: 0x7c; nome meu\n',
  '983: CBase objeto de 0x2c em 0x7c no lugar de m_texFont (m_segments 0xa8 ... m_fx 0xec, m_vl 0x52c, m_vtx 0x540)'),
 ('sub', 'src/projectg/ground_info.cpp', '\t: m_pCurBall(NULL), m_texLine(0), m_texFont(0)\n', '\t: m_pCurBall(NULL), m_texLine(0)\n',
  '983: m_texFont saiu da lista de inicialização'),
 ('sub', 'src/projectg/ground_info.cpp', 'CBase::CBase()\n', 'int CBase::m_texFont; // 983: não existe (PROVISÓRIO)\n\nCBase::CBase()\n',
  '983: definição do static provisório m_texFont'),
 # WResourceManager (cópia do exe): construtor 00b5cd40. 0x14 = std::map<std::string, std::string> (nó 0x48; o
 # AddMissingTexture 00b5c0c0 faz find + insert(pair(nome, nome))) no lugar da WList<char*> de 0x20; m_matchList 0x24
 # (1024), texList 0x44 (64), puppetList 0x64, soundList 0xa4, fontList 0xe4, voiceList 0x124, originList 0x144,
 # m_lock[4] em 0x164 (vetor de 4 x 0x20 no construtor; Lock 00b55aa0 = this + tipo*0x20 + 0x164), WList nova (16, 16) em
 # 0x1e4, sizeof 0x204. Pelos votos, LoadBitmapA usa o lock 2 (0x1a4) e GetPuppet o lock 3 (0x1c4): o tipo novo é o 1.
 ('sub', 'include/engine/wresrcmng.h', '\tRML_TEXTURE_LOADING = 0,\n\tRML_BITMAP_LOADING = 1,\n\tRML_PUPPET_LOADING = 2\n',
  '\tRML_TEXTURE_LOADING = 0,\n\tRML_UNK1_983 = 1, // 983: lock novo (0x184); uso não medido\n\tRML_BITMAP_LOADING = 2,\n\tRML_PUPPET_LOADING = 3,\n\tRML_COUNT = 4\n',
  '983: 4 locks no WResourceManager (o novo é o índice 1)'),
 ('sub', 'include/engine/wresrcmng.h', '#include "wresrccache.h"\n', '#include "wresrccache.h"\n#include <map>\n#include <string>\n', '983: std::map no WResourceManager'),
 ('sub', 'include/engine/wresrcmng.h', '\tWList<char*>& MissingTextureList() { return m_missingTextureList; }\n',
  '\tstd::map<std::string, std::string>& MissingTextureList() { return m_missingTextureList; }\n', '983: tipo de m_missingTextureList'),
 ('sub', 'include/engine/wresrcmng.h', '\tWList<char*> m_missingTextureList;\n',
  '\tstd::map<std::string, std::string> m_missingTextureList; // 983: 0x14, 0x10 bytes (era WList<char*>)\n', '983: m_missingTextureList é std::map (m_matchList 0x24 ... originList 0x144)'),
 ('sub', 'include/engine/wresrcmng.h', '\tWLock m_lock[3];\n',
  '\tWLock m_lock[RML_COUNT]; // 983: 0x164, 4 locks\n\tWList<void*> m_list1e4_983; // 983: 0x1e4, WList(16, 16); tipo do elemento não medido\n',
  '983: m_lock[4] em 0x164 + WList nova em 0x1e4 (sizeof 0x204)'),
 ('sub', 'src/engine/wresrcmng.cpp', '\t: m_missingTextureList(8, 8), m_matchList(1024, 1024), texList(64, 64)\n',
  '\t: m_matchList(1024, 1024), texList(64, 64), m_list1e4_983(16, 16)\n', '983: construtor 00b5cd40'),
 ('sub', 'src/engine/wresrcmng.cpp',
  '\tfor (char* text = m_missingTextureList.Start(); text;\n\t\ttext = m_missingTextureList.Next())\n\t{\n\t\tif (text)\n\t\t\tdelete[] text;\n\t}\n\tm_missingTextureList.Reset();\n',
  '\tm_missingTextureList.clear(); // 983: std::map (destrutor do 983 não lido)\n', '983: m_missingTextureList é std::map'),
 ('sub', 'src/engine/wresrcmng.cpp',
  '\tif (!m_missingTextureList.Find(filename))\n\t{\n\t\tchar* text = new char[strlen(filename) + 1];\n\t\tstrcpy(text, filename);\n\t\tm_missingTextureList.AddItem(text, text, false);\n\t}\n',
  '\t// 983 (00b5c0c0)\n\tstd::string name(filename);\n\tif (m_missingTextureList.find(name) == m_missingTextureList.end())\n\t\tm_missingTextureList.insert(std::make_pair(name, name));\n',
  '983: AddMissingTexture com std::map'),
 ('sub', 'src/engine/wresrcmng.cpp', '\tfor (int i = 0; i < 3; i++)\n\t\tm_lock[i].UnlockInThread(threadID);\n',
  '\tfor (int i = 0; i < RML_COUNT; i++) // 983: 4 (00b55ae0)\n\t\tm_lock[i].UnlockInThread(threadID);\n', '983: UnlockAllByThread percorre 4 locks'),
 # CSceneManager: construtor 009b42a0 (vtable 00d3f704). Listas (cabeça, tamanho; nó): 0xbc (0xa4), 0xc8 (0x94),
 # 0xd4 (0x94), 0xe0 (0x18), 0xec (0x18); byte 0xf8 (SetType grava 1 = m_bDirty); lista 0xfc (0x18 = m_drops); byte 0x109;
 # m_pFont 0x10c; névoa 0x110..0x118; word 0x11c; 0x120. São 5 listas antes de m_bDirty (no 645 eram 6) e as de 0xc8/0xd4
 # têm elemento de 0x8c (não o CustomElement de 8): o desenho por listas foi refeito (onda 2). Aqui só o deslocamento do
 # que vem depois: sai uma lista de 12 bytes.
 ('sub', 'src/projectg/scenemanager.h', '\tunsigned char m_unusedb4[0x61];\n', '\tunsigned char m_unusedb4[0x55]; // 983: uma lista a menos (m_bShowTag 0x109)\n',
  '983: CSceneManager (definição opaca) -12 antes de m_bShowTag; sizeof 0x124'),
 ('sub', 'src/projectg/scenemanager.h', '\tstd::list<TransparentElement> m_transparent3;\n',
  '\tstatic std::list<TransparentElement> m_transparent3; // 983: só 5 listas (PROVISÓRIO: qual saiu não foi medido; static para o .cpp do 645 compilar)\n',
  '983: CSceneManager -12 antes de m_bDirty (0xf8), m_drops 0xfc, m_pFont 0x10c, sizeof 0x124'),
 ('sub', 'src/projectg/scenemanager.cpp', 'CSceneManager::CSceneManager()\n',
  'std::list<TransparentElement> CSceneManager::m_transparent3; // 983: não existe como membro (PROVISÓRIO)\n\nCSceneManager::CSceneManager()\n',
  '983: definição do static provisório m_transparent3'),
 # CGolfDoc: construtor 0066d240, lado a lado com o nosso (cmpfunc --diff). No 983: nada grava 0x174 e um float 0.0 vai
 # para 0x178 (onde o nosso zera o dword 0x174); m_currentHole 0x17c, m_shotPhase 0x188, m_bright 0x18c, dword 0x190,
 # word 0x194 (m_bNoStat + byte novo 0x195), floats 0x198/0x19c, -1 em 0x1a0/0x1a4, word 0x1a8, __int64 em 0x1b0..0x1d4
 # (+8 pelo alinhamento), memset(0x340, 0x84), sShotResultMsg[4] em 0x3c4 com 0x26 cada (laço do construtor: -1 no
 # 1º dword, zeros até 0x25; memset de 0x98), memset(0x45c, 0x32), 0x48e/0x492, m_partTidList 0x494, listas 0x844/0x850.
 ('sub', 'src/projectg/golfdoc.h', '\tunsigned long m_unknown164;\n',
  '\tunsigned long m_unk174_983; // 983: 0x174, o construtor não grava; nome meu\n'
  '\tfloat m_unknown164; // 983: 0x178, float 0.0 no construtor (PROVISÓRIO: pode ser campo novo e o m_unknown164 antigo ser o de 0x174)\n',
  '983: CGolfDoc +4 em 0x174 (m_currentHole 0x17c ... m_bright 0x18c)'),
 ('sub', 'src/projectg/golfdoc.h', '\tunsigned char m_unused181[3];\n',
  '\tbool m_b195_983; // 983: 0x195, zerado junto com m_bNoStat (word); nome meu\n\tunsigned char m_unused181[2];\n',
  '983: CGolfDoc byte novo em 0x195'),
 ('sub', 'src/projectg/golfdoc.cpp', '\tm_bNoStat = false;\n\tm_bShowChat = true;\n', '\tm_bNoStat = false;\n\tm_b195_983 = false;\n\tm_bShowChat = true;\n',
  '983: construtor do CGolfDoc zera 0x195'),
 ('sub', 'src/projectg/golfdoc.h', '\tunsigned char flag;\n\tunsigned char unused12[0x13];\n};\n',
  '\tunsigned char flag;\n\tunsigned char unused12[0x14]; // 983: sizeof 0x26 (era 0x25)\n};\n', '983: sShotResultMsg 0x26 (m_shotResultMsg 0x3c4..0x45c)'),
 ('sub', 'src/projectg/golfdoc.h', '\tunsigned char m_unknown440[0x2e];\n', '\tunsigned char m_unknown440[0x32]; // 983: memset de 0x32 em 0x45c\n',
  '983: CGolfDoc bloco de 0x32 em 0x45c (m_unknown46e 0x48e, m_partTidList 0x494, tudo depois +16)'),
]
