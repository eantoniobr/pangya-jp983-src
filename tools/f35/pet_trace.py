#!/usr/bin/env python3
"""A181: rastro provisório do caddie da partida (PATCH_PY do wt_build.sh; só na cópia).

Linhas "rastro: pet ..." no jp983_stubs.log: cada CPetBody::LoadPuppet (nome e puppet achado ou nulo) e, no
CGolfCaddie::Display, as 5 primeiras chamadas e 1 a cada 600 (m_bVisible, m_pCaddie, distância à câmera, ShouldDisplay).
"""


def patch(path, pairs):
    s = open(path, 'rb').read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old)
        s = s.replace(old, new)
    open(path, 'wb').write(s)


DECL = b'extern "C" void __cdecl jp983_rastro(const char* fmt, ...);\n'
patch('src/projectg/petbody.cpp', [
    (b'\nvoid CPetBody::LoadPuppet(const char* name, bool bOptimizeBone, bool bOption)\n{\n'
     b'\tm_pPet = g_resrcmng->GetPuppet(name, false, true, bOption);\n',
     b'\n' + DECL + b'void CPetBody::LoadPuppet(const char* name, bool bOptimizeBone, bool bOption)\n{\n'
     b'\tm_pPet = g_resrcmng->GetPuppet(name, false, true, bOption);\n'
     b'\tjp983_rastro("pet LoadPuppet %s -> %p", name, m_pPet);\n'),
])
patch('src/projectg/golfcadie.cpp', [
    (b'\nvoid CGolfCaddie::Display()\n{\n',
     b'\n' + DECL + b'void CGolfCaddie::Display()\n{\n'
     b'\tstatic int n = 0;\n'
     b'\tif (n++ < 5 || n % 600 == 0)\n'
     b'\t\tjp983_rastro("pet caddie Display n=%d vis=%d caddie=%p dist=%d show=%d", n, m_bVisible, m_pCaddie,\n'
     b'\t\t\t(int)(g_camera.pivot - m_pos).Magnitude(), ShouldDisplay());\n'),
])
print('pet_trace: ok')
