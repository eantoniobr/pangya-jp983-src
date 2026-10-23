#!/usr/bin/env python3
"""A181: experimento (só na cópia; PATCH_PY do wt_build.sh) — a "faixa diagonal" (PRIORIDADE 01) é a malha do caddie?

Roda o pet_trace.py e, por cima: o CGolfCaddie::Display (partida) e o IDummyPet::Display (lobby) NÃO desenham o pet e gravam
a esfera de contorno do puppet ("rastro: pet esfera ...": centro e raio; raio enorme = vértices esticados).
"""
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pet_trace.py')).read())

SPH = (b'\t\t{\n\t\t\tconst WSphere& s = %s->GetBoundSphere();\n'
       b'\t\t\tjp983_rastro("pet esfera %s %%d %%d %%d r=%%d", (int)s.pos.x, (int)s.pos.y, (int)s.pos.z, (int)s.radius);\n\t\t}\n')
patch('src/projectg/golfcadie.cpp', [
    (b'\t\t\t(int)(g_camera.pivot - m_pos).Magnitude(), ShouldDisplay());\n',
     b'\t\t\t(int)(g_camera.pivot - m_pos).Magnitude(), ShouldDisplay());\n'
     b'\tif (ShouldDisplay() && (n < 5 || n % 600 == 0))\n\t{\n\t\tm_pCaddie->m_pBody->Display();\n' +
     SPH % (b'm_pCaddie->m_pBody->GetPet()', b'caddie') + b'\t}\n\treturn;\n'),
])
patch('src/projectg/jp/dummypet.cpp', [
    (b'\nvoid IDummyPet::Display()\n{\n', b'\n' + DECL + b'void IDummyPet::Display()\n{\n'),
    (b'\tm_pPuppet->UpdateBSphere();\n\tif (g_view->InFrustum(m_pPuppet->GetBoundSphere()))\n',
     b'\tm_pPuppet->UpdateBSphere();\n\tstatic int n = 0;\n\tif (n++ < 5 || n % 600 == 0)\n' + SPH % (b'm_pPuppet', b'dummypet') +
     b'\tif (n > 0)\n\t\treturn;\n\tif (g_view->InFrustum(m_pPuppet->GetBoundSphere()))\n'),
])
print('pet_hide: ok')
