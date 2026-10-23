# F3.5 (sessao 58): WBone no layout do 983 (sizeof 0x1dc; 645: 0x1b4), medido pelo construtor 00ba47d0 e pelos pares de instrucoes da
# unidade wbone (out/F3.5/s58/wbone/votos.txt). Evidencia: out/F3.5/s58/RELATORIO.md. Lido por tools/f32/ajustes.py no fim.
NEW26 = [
 ('sub', 'include/engine/wbone.h', '#include <map>\n#include <vector>\n', '#include <map>\n#include <list>\n#include <vector>\n', '983: WBone usa std::list'),
 ('sub', 'include/engine/wbone.h',
  '\tWBone::w_bone_physic_link* m_physic;\n\tw_mesh* m_mesh;\n\tchar m_name[64];\n\tunsigned int m_hashCode;\n\tchar* m_motion_bone_name;\n'
  '\tWQuat m_basicQuat;\n\tWMatrix m_basicMat;\n\tWSphere m_bound_sphere;\n\tWaabb m_bound_aabb;\n'
  '\tw_keyframe_pos* m_keyPos;\n\tint m_keyPosNum;\n\tw_keyframe_rot* m_keyRot;\n\tint m_keyRotNum;\n\tint m_keyFlag;\n'
  '\tWBone* m_parent;\n\tWBone* m_child;\n\tWBone* m_next;\n\tfloat m_lightLine;\n\tint m_rendMode;\n\tint m_id;\n'
  '\tunsigned int m_selfillumColor;\n',
  '\t// 983: ordem nova (construtor 00ba47d0, SetID 00b96f50). O nome abre a classe e a arvore sobe para o topo; m_motion_bone_name\n'
  '\t// saiu (ApplyBoneSetList 00ba1180 passa o proprio osso/nome ao FindBoneKey). Novos: escala basica, um float, 2 pares de chaves\n'
  '\t// (tipos e nomes provisorios) e uma lista no fim.\n'
  '\tchar m_name[64]; // 0x00\n\tint m_id; // 0x40\n\tWBone* m_child; // 0x44\n\tWBone* m_next; // 0x48\n\tw_mesh* m_mesh; // 0x4c\n'
  '\tWBone* m_parent; // 0x50\n\tWBone::w_bone_physic_link* m_physic; // 0x54\n\tunsigned int m_hashCode; // 0x58\n'
  '\tWQuat m_basicQuat; // 0x5c\n\tWVector m_basicScale983; // 0x6c, construtor: (1, 1, 1)\n\tWMatrix m_basicMat; // 0x78\n'
  '\tfloat m_unk983_a8; // 0xa8, construtor: -1.0f\n\tWSphere m_bound_sphere; // 0xac\n\tWaabb m_bound_aabb; // 0xbc\n'
  '\tw_keyframe_pos* m_keyPos; // 0xd4\n\tint m_keyPosNum;\n\tw_keyframe_rot* m_keyRot; // 0xdc\n\tint m_keyRotNum;\n'
  '\tvoid* m_key983_e4; // 0xe4, construtor: 0 (par ponteiro/contagem, como m_keyPos)\n\tint m_key983_e8;\n'
  '\tvoid* m_key983_ec; // 0xec\n\tint m_key983_f0;\n\tint m_keyFlag; // 0xf4\n'
  '\tfloat m_lightLine; // 0xf8\n\tint m_rendMode; // 0xfc\n'
  '\tunsigned int m_selfillumColor; // 0x100\n',
  '983: WBone reordenado (nome em 0, arvore no topo, m_motion_bone_name removido, +0x1c ate m_bonescale)'),
 ('sub', 'include/engine/wbone.h',
  '\tunsigned int m_vtxColor;\n\tfloat m_bonescale;\n',
  '\tunsigned int m_vtxColor; // 0x1c8\n\tfloat m_bonescale; // 0x1cc\n'
  '\tstd::list<void*> m_list983_1d0; // 983: 0x1d0 (no de 0xc bytes: elemento de 4); sizeof 0x1dc\n',
  '983: WBone ganha uma std::list no fim (sizeof 0x1dc)'),
 ('sub', 'src/engine/wbone.cpp',
  '\tm_motion_bone_name = GetNameSubBip();\n',
  '\t// 983: m_motion_bone_name nao existe mais\n',
  '983: WBone sem m_motion_bone_name'),
 ('sub', 'src/engine/wbone.cpp', 'set->AddBoneKey(m_motion_bone_name, ', 'set->AddBoneKey(m_name, ', '983: WBone sem m_motion_bone_name (nome inteiro)'),
 ('sub', 'src/engine/wbone.cpp', 'set->FindBoneKey(m_motion_bone_name)', 'set->FindBoneKey(m_name)', '983: WBone sem m_motion_bone_name (nome inteiro)'),
 ('sub', 'src/engine/wbone.cpp',
  '\tm_keyFlag = 0;\n\tm_bound_sphere = WSphere(WVector::ZERO, 0.0f);\n',
  '\tm_basicScale983 = WVector(1.0f, 1.0f, 1.0f); // 983\n\tm_unk983_a8 = -1.0f; // 983\n\tm_keyFlag = 0;\n'
  '\tm_key983_e4 = 0; // 983\n\tm_key983_e8 = 0;\n\tm_key983_ec = 0;\n\tm_key983_f0 = 0;\n'
  '\tm_bound_sphere = WSphere(WVector::ZERO, 0.0f);\n',
  '983: construtor do WBone inicia os membros novos (00ba47d0)'),
 ('sub', 'include/engine/wbone.h', 'char* GetBoneMotionName() { return m_motion_bone_name; }', 'char* GetBoneMotionName() { return m_name; } // 983: sem m_motion_bone_name', '983: WBone sem m_motion_bone_name'),
]
