#!/usr/bin/env python3
"""A179: guard_trace.py + correção provisória do CClubRangeInfo do fallingspot (só no worktree; a unidade é da D).

O fallingspot.h declarava um CClubRangeInfo próprio de 0x24 com o mesmo nome do de fontinfo.h (CFontInfo + m_pos, 0x38):
o CSpot::OnLoad aloca 0x24 e o construtor do fontinfo (único no link) escreve até +0x38 -> estouro de heap (a179-1, GUARDA
em CSpot::OnLoad+0x34). O 983 faz new(0x38) + construtor 005281c0 (00729fab).
"""
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'guard_trace.py')).read())

h = open('src/projectg/fallingspot.h', encoding='latin-1').read()
i = h.index('class CClubRangeInfo\n{')
j = h.index('};\n', i) + 3
open('src/projectg/fallingspot.h', 'w', encoding='latin-1').write(h[:i] + 'class CClubRangeInfo;\n' + h[j:])
patch('src/projectg/fallingspot.cpp', [
    ('#include "scenemanager.h"\n', '#include "scenemanager.h"\n#include "fontinfo.h"\n'),
    ('void CClubRangeInfo::SetPos(const WVector& pos)\n{\n\tm_pos = pos;\n}\n', ''),
    ('\t\t\tm_pRangeInfo->m_color = m_color2;\n\t\t\tm_pRangeInfo->SetPos(m_pos);\n',
     '\t\t\tm_pRangeInfo->SetColor(m_color2);\n\t\t\tm_pRangeInfo->m_pos = m_pos;\n'),
])
print('clubrange_trace: ok')
