# F3.5 (sessao 57): CPetFrame no layout do 983 (sizeof 0x358; `push 0x358` em 00743511/0074357d), medido pelo construtor 008b2290 e pelo
# destrutor 008b1aa0. golfplayer.cpp/.h foram adotados (map/adotados.txt): 2a base IPetScriptObject (src/projectg/petscriptobject.h, arquivo
# nosso). Evidencia: out/F3.5/s57/RELATORIO.md. Lido por tools/f32/ajustes.py no fim.
NEW25 = [
 ('sub', 'src/projectg/partsinfo.h',
  'class CPetFrame\n{\n',
  '// 983: dois membros novos do CPetFrame cujo tipo nao foi identificado; so o tamanho e quem os constroi/destroi foram medidos.\n'
  '// 0x28 (0x30 bytes): construtor 00b4f520 (zera 5 dwords, grava 0x20/0xff/0x100, malloc(0x400) em +0x1c; um std::vector em +0x20).\n'
  'struct sPetFrameUnk983_28\n{\n\tsPetFrameUnk983_28();\n\t~sPetFrameUnk983_28();\n\tint m_d[12];\n};\n'
  '// 0x334 (0x24 bytes): construtor 008b1750 (no de arvore de 0x28 bytes em +4, contagem em +8), destrutor 008b1620.\n'
  'struct sPetFrameUnk983_334\n{\n\tsPetFrameUnk983_334();\n\t~sPetFrameUnk983_334();\n\tint m_d[9];\n};\n\n'
  'class CPetFrame\n{\n',
  '983: tipos provisorios dos 2 membros novos do CPetFrame (0x28 e 0x334)'),
 ('sub', 'src/projectg/partsinfo.h',
  '\tWPuppet* m_pCurAniPet;\n\tint m_defPartNum;\n',
  '\tWPuppet* m_pCurAniPet;\n'
  '\t// 983: sizeof 0x358 (645: 0x2f4). +0x40 aqui: m_defPartNum vai para 0x68, m_pPartPet 0x74, m_partTex 0xd4, m_bShirtsClr 0x1f4,\n'
  '\t// m_partList 0x1f8, m_auxPart 0x320 (008acd56); +0x24 no fim.\n'
  '\tsPetFrameUnk983_28 m_unk983_28; // 983: 0x28\n'
  '\tstd::vector<void*> m_vec983_58; // 983: 0x58, vetor de ponteiros (o destrutor 008b1adb o esvazia); tipo do elemento provisorio\n'
  '\tint m_defPartNum;\n',
  '983: CPetFrame +0x40 em 0x28 (objeto de 0x30 bytes + std::vector)'),
 ('sub', 'src/projectg/partsinfo.h',
  '\tunsigned long m_auxPart[5];\n',
  '\tunsigned long m_auxPart[5];\n\tsPetFrameUnk983_334 m_unk983_334; // 983: 0x334..0x358\n',
  '983: CPetFrame +0x24 em 0x334 (sizeof 0x358)'),
]
