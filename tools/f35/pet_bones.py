#!/usr/bin/env python3
"""A181: experimento (só na cópia; PATCH_PY do wt_build.sh) — matrizes dos ossos do caddie da partida.

Roda o pet_trace.py e, no CGolfCaddie::Display, nos quadros 300 e 1500: "rastro: osso <nome> t=x,y,z s=|X|,|Y|,|Z|"
para cada osso do puppet (m_matrix depois do Render; escala x100). Osso com escala/translação absurda = faixa diagonal.
"""
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pet_trace.py')).read())

patch('src/projectg/golfcadie.cpp', [
    (b'\nvoid CGolfCaddie::Display()\n{\n',
     b'\nstatic void DumpBones983(WBone* b)\n{\n'
     b'\tfor (; b; b = b->GetNext())\n\t{\n\t\tconst WMatrix& m = b->GetMatrix();\n'
     b'\t\tjp983_rastro("osso %s t=%d,%d,%d s=%d,%d,%d", b->GetBoneName(), (int)m.xm, (int)m.ym, (int)m.zm,\n'
     b'\t\t\t(int)(100 * sqrtf(m.xx * m.xx + m.yx * m.yx + m.zx * m.zx)), (int)(100 * sqrtf(m.xy * m.xy + m.yy * m.yy + m.zy * m.zy)),\n'
     b'\t\t\t(int)(100 * sqrtf(m.xz * m.xz + m.yz * m.yz + m.zz * m.zz)));\n'
     b'\t\tDumpBones983(b->GetChild());\n\t}\n}\n\n'
     b'void CGolfCaddie::Display()\n{\n'),
    (b'\tm_pCaddie->m_pBody->Display();\n\tif (m_pRing && m_pCaddie->m_bRing)\n',
     b'\tm_pCaddie->m_pBody->Display();\n'
     b'\tif (n == 300 || n == 1500)\n\t\tDumpBones983(m_pCaddie->m_pBody->GetPet()->GetRootBone());\n'
     b'\tif (m_pRing && m_pCaddie->m_bRing)\n'),
])
print('pet_bones: ok')
