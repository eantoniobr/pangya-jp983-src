# F3.4 (sessão 32): CSharedDoc — tipos dos objetos novos do 983 tirados dos construtores (tamanho do nó = operator new,
# lugar dos dois bytes de cor/nil). Lido por tools/f32/ajustes.py depois do ajustes_shareddoc2.py.
# Evidência: out/F3.4/s32/objetos_novos.md.
H='src/projectg/shareddoc.h'
NEW3 = [
 ('sub', H, 'class CSharedDoc : public WSingleton<CSharedDoc>\n',
  '// 983: valor opaco de N bytes para os mapas novos (só o tamanho do nó é medido)\n'
  'template <int N> struct sUnk983 { unsigned char b[N]; };\n'
  '// 983: classe nova do Self Design (RTTI .?AVCCommodityList@sd_shop@@, vtable 00d54504, construtor 00b3d270):\n'
  '// vtable, CRITICAL_SECTION em +4, mapa em +0x20 com nó de 0x25c. Corpo fica para a F3.7 (sistemas novos).\n'
  'namespace sd_shop {\nclass CCommodityList\n{\npublic:\n\tCCommodityList();\n\tvirtual ~CCommodityList();\n'
  '\tCRITICAL_SECTION m_cs;\n\tint m_unk1c; // 4 bytes sem gravação no construtor\n\tstd::map<unsigned long, sUnk983<584> > m_map;\n};\n}\n'
  'class CSharedDoc : public WSingleton<CSharedDoc>\n', '983: tipos de apoio dos objetos novos do CSharedDoc'),
 ('sub', H, '\tstd::map<int, int> m_unk983_10a20; // 983: objeto novo de 16 B (construtor 006441a0; tipo provisório)',
  '\tstd::set<unsigned long> m_unk983_10a20; // 983: construtor 006441a0, nó de 0x14 (valor de 4 B)',
  '983: 0x10a20 é árvore com nó de 0x14 (cor/nil em +0x10/+0x11)'),
 ('sub', H, '\tstd::map<int, int> m_unk983_113e0; // 983: 3 objetos novos de 16 B (construtores 00644280, 00643410 x2; tipo provisório)\n'
  '\tstd::map<int, int> m_unk983_113f0;\n\tstd::map<int, int> m_unk983_11400;',
  '\tstd::map<unsigned long, sUnk983<8> > m_unk983_113e0; // 983: construtor 00644280, nó de 0x1c (par de 12 B)\n'
  '\tstd::map<unsigned long, sUnk983<192> > m_unk983_113f0; // 983: construtor 00643410, nó de 0xd4 (par de 196 B)\n'
  '\tstd::map<unsigned long, sUnk983<192> > m_unk983_11400; // 983: idem',
  '983: 0x113e0/0x113f0/0x11400 são árvores com nó de 0x1c e 0xd4'),
 ('sub', H, '\tunsigned long m_unk983_1146c[4]; // objeto de 16 B (construtor 00643490)\n'
  '\tunsigned long m_unk983_1147c[19]; // objeto (construtor 00b3d270) + 4 dwords em 0x114b8',
  '\tstd::map<int, int> m_unk983_1146c; // 983: construtor 00643490, nó de 0x18 (par de 8 B)\n'
  '\tsd_shop::CCommodityList m_unk983_1147c; // 983: construtor 00b3d270 (0x30 bytes)\n'
  '\tunsigned long m_unk983_114ac[7]; // 983: resto até 0x114c8 (4 dwords gravados em 0x114b8)',
  '983: 0x1146c é árvore com nó de 0x18; 0x1147c é sd_shop::CCommodityList (RTTI)'),
]
