# F3.5 (sessao 56): import do rebang 34f62e0 (golfplayer.cpp, taskmanager.cpp). CGolfPlayer no layout do 983 (sizeof 0x29c), medido pelo
# construtor 00740ca0 e pelos votos de deslocamento (out/F3.5/s56/votos). src/projectg/taskmanager.cpp foi adotado (map/adotados.txt):
# 23 linhas da versao C que nao compilavam corrigidas a mao. Evidencia: out/F3.5/s56/RELATORIO.md. Lido por tools/f32/ajustes.py no fim.
NEW24 = [
 ('sub', 'src/projectg/golfplayer.h',
  '#include "extendedeffect.h"\n',
  '#include "extendedeffect.h"\n#include "fxinterpreter.h"\n',
  '983: CGolfPlayer cria um FxInterpreter no construtor'),
 ('sub', 'src/projectg/golfplayer.h',
  '\tstd::vector<sCondBBSpray> m_condSpray[4];   // 0x18\n\tstd::vector<sCondBBSequence> m_condSeq[4];  // 0x58\n\tstd::vector<unsigned long> m_condIds[4];    // 0x98\n\tstd::vector<CFxSpray*> m_sprays;            // 0xd8\n\tstd::vector<CFxSequence*> m_sequences;      // 0xe8\n',
  '\t// 983: sizeof 0x29c (push em 007417c0). Medido pelo construtor 00740ca0 e pelos votos (out/F3.5/s56/votos): de 0x38 a 0x84 tudo\n\t// -0xc4; de 0x90 em diante -0xbc. Os comentarios de deslocamento a direita, daqui para baixo, sao os do 645.\n\tvoid* m_vptrPetScript983; // 983: 0x18 = vtable 00d20540 da 2a base IPetScriptObject (14 slots); a base NAO foi escrita (provisorio)\n\tint m_unk983_1c; // 983: 0x1c, uso nao achado\n\tFxInterpreter* m_pFxInterpreter983; // 983: 0x20 = new FxInterpreter(NULL, 0) em 00740dd5; substitui os 5 vetores de fx do 645\n\tint m_unk983_24[4]; // 983: 0x24..0x30 zerados no corpo do construtor; tipo provisorio\n',
  '983: CGolfPlayer 0x18..0x34 (2a vtable, FxInterpreter em 0x20, 4 dwords); os 5 vetores de fx do 645 sairam'),
 ('sub', 'src/projectg/golfplayer.h',
  '\tfloat m_ballDist;                           // 0x14c\n',
  '\tint m_unk983_88; // 983: zerado no fim do construtor (00740de1)\n\tint m_unk983_8c; // 983: idem\n\tfloat m_ballDist;                           // 0x14c\n',
  '983: CGolfPlayer +8 bytes em 0x88/0x8c (zerados em 00740de1)'),
 ('sub', 'src/projectg/golfplayer.h',
  '\tstd::vector<std::pair<unsigned long, unsigned long> >\n\t\tm_abilityParts;          // 0x334\n\tCExtendedEffect m_extEffect; // 0x344\n',
  '\tCExtendedEffect m_extEffect; // 983: 0x278 (o vetor m_abilityParts que vinha antes saiu daqui)\n\tint m_unk983_298; // 983: 4 bytes ate 0x29c, uso nao achado\n\t// ---- 645: membros que o 983 nao tem neste lugar; ficam DEPOIS do fim do objeto do 983 so para a versao C das funcoes ainda nao\n\t// reescritas compilar (HandleMsg, ParseBoundingBoxScript, ...). Com eles o sizeof nosso e maior que 0x29c: provisorio.\n\tstd::vector<sCondBBSpray> m_condSpray[4];   // 0x18\n\tstd::vector<sCondBBSequence> m_condSeq[4];  // 0x58\n\tstd::vector<unsigned long> m_condIds[4];    // 0x98\n\tstd::vector<CFxSpray*> m_sprays;            // 0xd8\n\tstd::vector<CFxSequence*> m_sequences;      // 0xe8\n\tstd::vector<std::pair<unsigned long, unsigned long> >\n\t\tm_abilityParts; // 645: 0x334\n',
  '983: CGolfPlayer m_extEffect em 0x278, sizeof 0x29c; membros do 645 sem lugar no 983 vao para depois do fim (provisorio)'),
 ('sub', 'src/projectg/golfplayer.cpp',
  '\tm_bCombo = false;\n\tm_comboTime = 0;\n\tm_val320 = 0;\n\tm_powerShotKeyTime = 0;\n\tm_bPowerShot = false;\n\tm_bFlag329 = false;\n\tm_powerShotKeyState = 0;\n\tm_pHeadBone = NULL;\n\tm_valF8 = 0;\n\tm_bFlag330 = false;\n}',
  '\tResetComboState(); // 983: chamada a 0073daa0 no lugar das duas atribuicoes\n\tm_powerShotKeyTime = 0;\n\tm_val320 = 0;\n\tm_bPowerShot = false;\n\tm_bFlag329 = false;\n\tm_powerShotKeyState = 0;\n\tm_pHeadBone = NULL;\n\tm_valF8 = 0;\n\tm_bFlag330 = false;\n\tm_unk983_24[0] = 0;\n\tm_unk983_24[1] = 0;\n\tm_unk983_24[2] = 0;\n\tm_unk983_24[3] = 0;\n\tm_pFxInterpreter983 = new FxInterpreter(NULL, 0); // 983: 00740dad..00740dde\n\tm_unk983_88 = 0;\n\tm_unk983_8c = 0;\n}',
  '983: corpo do construtor do CGolfPlayer na ordem de 00740d78..00740de7'),
 ('sub', 'src/projectg/golfplayer.cpp', '\t\tif (m_headAngle < 1.0471976f)\n', '\t\tif (m_headAngle < 1.0471975430846214) // 983: compara com double (00d1a498 = 60 * (double)0.017453292f)\n',
  '983: InputProcess compara m_headAngle com constante double (0073e2c0)'),
 ('sub', 'src/projectg/golfplayer.cpp', '\t\tif (m_headAngle > -1.0471976f)\n', '\t\tif (m_headAngle > -1.0471975430846214) // 983: double (00d1ca90)\n',
  '983: InputProcess, limite negativo em double'),
]
