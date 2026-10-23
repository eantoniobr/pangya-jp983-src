# F3.5 (sessao 55): CParticleEffect do 983 (sizeof 0x80: shared_ptr<FxInterpreter> em 0x78), CLightColumn 0x1d8, metodo do FxInterpreter
# chamado pelo HandleMsg do 983 (0088aa60). src/projectg/particle.cpp foi adotado (map/adotados.txt): HandleMsg (00778d70) e
# CheckExtShotEffect (007783e0) reescritos a mao pelo 983. Evidencia: out/F3.5/s55/RELATORIO.md. Lido por tools/f32/ajustes.py no fim.
_PH = 'src/projectg/particle.h'
_YH = 'src/projectg/particleparty.h'
_YC = 'src/projectg/particleparty.cpp'
_FH = 'src/projectg/fxinterpreter.h'
NEW23 = [
 ('sub', _PH, '#include <vector>\n', '#include <vector>\n#include <memory>\n', '983: std::tr1::shared_ptr no CParticleEffect'),
 ('sub', _PH, '#include "wlist.h"\n', '#include "wlist.h"\n#include "fxinterpreter.h"\n', '983: o construtor do CParticleEffect cria o FxInterpreter'),
 ('sub', _PH, '\tbool CheckExtShotEffect(const char* spray, const char* sound);\n',
  '\tbool CheckExtShotEffect(int message); // 983: 007783e0, 1 argumento (a mensagem)\n', '983: CheckExtShotEffect(int)'),
 ('sub', _PH, '\tCLightColumn* m_pLight;\n#ifndef REBANG_SEMANTIC_ONLY\n',
  '\tCLightColumn* m_pLight;\n\tstd::tr1::shared_ptr<FxInterpreter> m_spFxInterpreter983; // 983: 0x78 (construtor 00779c87..00779d05); sizeof 0x80\n#ifndef REBANG_SEMANTIC_ONLY\n',
  '983: CParticleEffect +0x78 = shared_ptr<FxInterpreter> (_Ref_count<FxInterpreter> em 007799a0)'),
 ('sub', _YH, '\tvoid FadeIn() { m_fadeState = 1; }\n\tvoid FadeOut() { m_fadeState = 2; }\n\nprivate:\n',
  '\tvoid FadeIn() { m_fadeState = 1; }\n\tvoid FadeOut() { m_fadeState = 2; }\n'
  '\tvoid SetMode983(int mode) { m_mode983 = mode; } // 983: usado por CParticleEffect::HandleMsg (mensagem 0x1ef); nome meu\n\nprivate:\n',
  '983: CLightColumn +0x1d4 gravado pela mensagem 0x1ef (00779384)'),
 ('sub', _YH, '\tint m_texScreen;\n\tfloat m_scroll;\n};',
  '\tint m_texScreen;\n\tfloat m_scroll;\n\tint m_unk983_1d0; // 983: zerado no construtor (006eb8d4); nome meu\n'
  '\tint m_mode983; // 983: 0x1d4, zerado no construtor; 3 ou 4 pela mensagem 0x1ef; sizeof 0x1d8 (push em 00778cf9)\n};',
  '983: CLightColumn 0x1d0 -> 0x1d8'),
 ('sub', _YC, '\tfor (int i = 0; i < 5; i++)\n\t{\n\t\tm_tex[i] = 0;\n\t}\n}\n\nCLightColumn::~CLightColumn()',
  '\tfor (int i = 0; i < 5; i++)\n\t{\n\t\tm_tex[i] = 0;\n\t}\n\tm_unk983_1d0 = 0;\n\tm_mode983 = 0;\n}\n\nCLightColumn::~CLightColumn()',
  '983: construtor do CLightColumn zera 0x1d0 e 0x1d4 (006eb8d4)'),
 ('sub', _FH, '\tvoid SetUnk983_1cc(int v); // 983: 0088c460 (corpo nao escrito)\n',
  '\tvoid SetUnk983_1cc(int v); // 983: 0088c460 (corpo nao escrito)\n'
  '\tvoid PlayFx983(const char* file, const WVector* pos); // 983: 0088aa60 (.seq/.spr numa posicao; corpo nao escrito; nome meu)\n',
  '983: FxInterpreter 0088aa60, chamado pelo CParticleEffect::HandleMsg'),
 # GetHoleCupPos: no 983 (005298c0, 44 chamadas) devolve referencia ao pino do buraco, nao uma copia
 ('sub', 'src/projectg/shareddoc.inl', 'inline WVector GetHoleCupPos()\n{', 'inline const WVector& GetHoleCupPos() // 983: 005298c0 devolve referencia\n{',
  '983: GetHoleCupPos devolve const WVector& (005298c0: lea eax, [pino]; ret)'),
 ('todos', 'src/projectg/*.cpp', '\nWVector GetHoleCupPos();\n', '\nconst WVector& GetHoleCupPos(); // 983: devolve referencia\n', '983: declaracao local de GetHoleCupPos'),
]
