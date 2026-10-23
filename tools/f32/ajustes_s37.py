# F3.4 (sessão 37): WPolySoup e WPuppet no layout do 983, medidos no construtor. Lido por tools/f32/ajustes.py no fim.
# Evidência: out/F3.4/s37/classes_983.md.
NEW9 = [
 # WPolySoup: construtor 00948fb0 (new de 0x49c0 em 0066d240). sHeader ganhou construtor (0092af50 → 00926cd0 → 00926c90)
 # e um int em +0x28 (m_modelNum 0xa8, m_rmrModelNum 0xac, m_texture 0xb0 … m_point 0xc4); ponteiro novo em 0xc8
 # (zerado na lista de inicialização entre m_point e m_model); m_model 0xcc; m_baseModel 0xdc; Waabb novo em 0xe0 (zerado
 # no construtor e de novo no corpo, logo depois de m_modelNum = 0); m_texIndex 0xf8; m_fadeNear 0x108; m_fadeFar 0x10c;
 # m_extraHoleStartArea 0x110; m_pDoc 0x128; um só byte em 0x12c (m_bBuildTnL; m_bUnused saiu); m_staticPetGrp 0x130;
 # m_bgFx 0x13c; m_bgFxNum 0x493c; m_lightList 0x4944; m_npcList 0x4950; m_unusedList 0x4960; m_soundBox 0x4970;
 # m_cullDistance 0x4980; 0x4984 = 0xfffe0000 (novo); dois vetores em 0x4988 e 0x4998 (shadowmap refeito: 00945db0,
 # 00947eb0, EnableShadowmap 0094ad70); m_bSmapLoadFailed 0x49a8; m_holecupTex 0x49ac; m_triList 0x49b0 (nó 0x3c no 983:
 # o tipo do mapa mudou, o objeto segue com 0x10); sizeof 0x49c0.
 ('sub', 'src/projectg/polysoup.h', '\t\tint textureNum;\n\t\tint nodeNum;\n\t};\n',
  '\t\tint textureNum;\n\t\tint nodeNum;\n\t\tint unk28_983; // 983: +0x28 (zerado em 00926cd0); nome meu\n\t};\n',
  '983: WPolySoup::sHeader 0x2c (m_modelNum 0xa8)'),
 ('sub', 'src/projectg/polysoup.h', '\tsPoint* m_point;\n\tstd::vector<sModel*> m_model;\n\tsModel* m_baseModel;\n',
  '\tsPoint* m_point;\n\tvoid* m_unk_c8_983; // 983: 0xc8 (NULL na lista de inicialização); nome meu\n'
  '\tstd::vector<sModel*> m_model;\n\tsModel* m_baseModel;\n\tWaabb m_aabb_e0_983; // 983: 0xe0 (zerado no construtor); nome meu\n',
  '983: WPolySoup ponteiro novo em 0xc8 (m_model 0xcc, m_baseModel 0xdc) e Waabb novo em 0xe0 (m_texIndex 0xf8)'),
 ('sub', 'src/projectg/polysoup.h', '\tCGolfDoc* m_pDoc;\n\tbool m_bUnused;\n\tbool m_bBuildTnL;\n',
  '\tCGolfDoc* m_pDoc;\n\tbool m_bBuildTnL; // 983: 0x12c (m_bUnused não existe mais)\n',
  '983: WPolySoup sem m_bUnused (m_pDoc 0x128, m_staticPetGrp 0x130, m_bgFx 0x13c)'),
 ('sub', 'src/projectg/polysoup.h', '\tfloat m_cullDistance;\n\tint m_smapMeshNum;\n\tint* m_smapTexHandle;\n\tw_mesh* m_smapMesh;\n',
  '\tfloat m_cullDistance;\n\tunsigned long m_unk4984_983; // 983: 0x4984 = 0xfffe0000 no construtor; nome meu\n'
  '\tstd::vector<int> m_smapVec4988_983; // 983: 0x4988; tipo do elemento não medido\n'
  '\tstd::vector<w_mesh*> m_smapVec4998_983; // 983: 0x4998; tipo do elemento não medido\n'
  '\t// 983: os três abaixo não existem mais (PROVISÓRIO: static para o .cpp do 645 compilar)\n'
  '\tstatic int m_smapMeshNum;\n\tstatic int* m_smapTexHandle;\n\tstatic w_mesh* m_smapMesh;\n',
  '983: WPolySoup cauda do shadowmap (m_bSmapLoadFailed 0x49a8, m_holecupTex 0x49ac, m_triList 0x49b0, sizeof 0x49c0)'),
 ('sub', 'src/projectg/polysoup.cpp', '\t  m_baseModel(NULL),\n\t  m_bUnused(false),\n\t  m_bBuildTnL(false),\n\t  m_smapMeshNum(0),\n\t  m_smapTexHandle(NULL),\n\t  m_smapMesh(NULL),\n',
  '\t  m_unk_c8_983(NULL),\n\t  m_baseModel(NULL),\n\t  m_bBuildTnL(false),\n\t  m_unk4984_983(0xfffe0000),\n',
  '983: lista de inicialização do WPolySoup'),
 ('sub', 'src/projectg/polysoup.cpp', 'WPolySoup::WPolySoup(CGolfDoc* pDoc)\n',
  '// 983: não existem mais (PROVISÓRIO)\nint WPolySoup::m_smapMeshNum;\nint* WPolySoup::m_smapTexHandle;\nw_mesh* WPolySoup::m_smapMesh;\n\n'
  'WPolySoup::WPolySoup(CGolfDoc* pDoc)\n', '983: definição dos static provisórios do shadowmap'),
 # WPuppet (cópia do exe): construtor 00b8f7e0 (new de 0x220 em 00b5b6a5 e 00b92718), destrutor 00b8fc10. Ordem nova:
 # m_petName 0x2c (memset de 0x40), m_rootbone 0x6c, m_lightmode 0x70, m_phybone 0x74, m_mat 0x94, m_addedMotionList 0xc4,
 # m_rendMode 0xe4, ponteiro para o próprio/original em 0xe8 (o construtor grava this; o destrutor testa [0xe8] == this
 # onde o 645 testava !m_bClone), m_frame 0xf0, m_framenum 0xf4, m_faceNum 0xf8, m_bound 0xfc, m_boundSphere 0x114,
 # m_BBox 0x124, m_storeTexList 0x12c, m_use_tex_piece 0x130, m_bbList 0x150, m_mdList 0x170, m_fanimList 0x174,
 # m_boneList 0x194 (construtor fora de linha 00b733d0), 0x24 B não medidos, m_aniLen 0x1d8, mapa 0x1e0 (nó 0x18), lista
 # 0x1f0 (nó 0x38), vetor 0x1fc (o destrutor mede o tamanho: m_xTransfMatPtrList), 0x20c = 0xfffe0000, mapa 0x210 (nó 0x30).
 ('sub', 'include/engine/wpuppet.h',
  '\tint m_lightmode;\n\tWList<WBone*> m_phybone;\n\tWMatrix m_mat;\n\tWList<w_motion_addition*> m_addedMotionList;\n\tint m_rendMode;\n'
  '\tbool m_bClone;\n\tbool m_bHaveCenter;\n\tw_share_pet_data::w_frame* m_frame;\n\tint m_framenum;\n\tchar m_petName[0x40];\n\tint m_faceNum;\n',
  '\tchar m_petName[0x40]; // 983: 0x2c\n\tWBone* m_rootbone; // 983: 0x6c\n\tint m_lightmode; // 983: 0x70\n'
  '\tWList<WBone*> m_phybone; // 983: 0x74\n\tWMatrix m_mat; // 983: 0x94\n\tWList<w_motion_addition*> m_addedMotionList; // 983: 0xc4\n'
  '\tint m_rendMode; // 983: 0xe4\n\tWPuppet* m_pOrigin983; // 983: 0xe8 (this no construtor; clone = != this); nome meu\n'
  '\tstatic bool m_bClone; // 983: não existe (PROVISÓRIO: static para o .cpp do 645 compilar)\n'
  '\tbool m_bHaveCenter; // 983: lugar não medido (0xec livre)\n'
  '\tw_share_pet_data::w_frame* m_frame; // 983: 0xf0\n\tint m_framenum;\n\tint m_faceNum; // 983: 0xf8\n',
  '983: WPuppet ordem nova dos campos até m_faceNum'),
 ('sub', 'include/engine/wpuppet.h',
  '\tWList<WBone*> m_boneList;\n\tfloat m_aniLen;\n\tint m_iPetType;\n\tWBone* m_rootbone;\n\tWMatrixPtrList m_xTransfMatPtrList;\n',
  '\tWList<WBone*> m_boneList; // 983: 0x194\n\tunsigned char m_unk1b4_983[0x24]; // 983: não medido\n\tfloat m_aniLen; // 983: 0x1d8\n'
  '\tint m_iPetType; // 983: lugar não medido (0x1dc livre)\n\tunsigned char m_map1e0_983[0x10]; // 983: mapa (nó 0x18)\n'
  '\tunsigned char m_list1f0_983[0xc]; // 983: lista (nó 0x38)\n\tWMatrixPtrList m_xTransfMatPtrList; // 983: 0x1fc\n'
  '\tunsigned long m_unk20c_983; // 983: 0xfffe0000 no construtor\n\tunsigned char m_map210_983[0x10]; // 983: mapa (nó 0x30)\n',
  '983: WPuppet cauda (sizeof 0x220)'),
 ('sub', 'src/engine/wpuppet.cpp', 'WPuppet::WPuppet()\n', 'bool WPuppet::m_bClone; // 983: não existe (PROVISÓRIO)\n\nWPuppet::WPuppet()\n',
  '983: definição do static provisório m_bClone'),
]
