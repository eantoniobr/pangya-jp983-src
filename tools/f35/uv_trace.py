#!/usr/bin/env python3
"""A183: rastro provisório do AV no Start Game (A182.1; PATCH_PY do wt_build.sh; só na cópia).

No WxTnLBuffer::xFillVertexBufferByMesh: malha cujo FVF pede mais camadas de UV do que (*mesh->uv) tem (ou camada menor
que vtxNum) -> "rastro: uv osso=<nome> vtx=.. camadas FVF=.. malha=.. tam0=.. tam1=.. draw=.. draw2=.. grp=.."; o laço
fica limitado às camadas existentes para a carga seguir e mostrar todas as malhas assim.
"""


def patch(path, pairs):
    s = open(path, 'rb').read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old)
        s = s.replace(old, new)
    open(path, 'wb').write(s)


patch('src/engine/wxtnlbuffer.cpp', [
    (b'\nvoid WxTnLBuffer::xFillVertexBufferByMesh(',
     b'\nextern "C" void __cdecl jp983_rastro(const char* fmt, ...);\nvoid WxTnLBuffer::xFillVertexBufferByMesh('),
    (b'\tconst WMatrix* pMat;\n\tif ((m_xiFlag & 2) == 0)\n',
     b'\t{\n\t\tint nHave = pMesh->uv ? (int)pMesh->uv->size() : 0;\n'
     b'\t\tint nMin = 0x7fffffff;\n'
     b'\t\tfor (int k = 0; k < nHave && k < nLayers; ++k)\n'
     b'\t\t\tif ((int)(*pMesh->uv)[k].size() < nMin) nMin = (int)(*pMesh->uv)[k].size();\n'
     b'\t\tif (nHave < nLayers || (nLayers && nMin < pMesh->vtxNum))\n'
     b'\t\t\tjp983_rastro("uv osso=%s vtx=%d camadas FVF=%d malha=%d tam0=%d tam1=%d draw=%08x draw2=%08x grp=%d rig=%d fvf=%08x",\n'
     b'\t\t\t\tpBatch->xpBone ? pBatch->xpBone->GetBoneName() : "-", pMesh->vtxNum, nLayers, nHave,\n'
     b'\t\t\t\tnHave > 0 ? (int)(*pMesh->uv)[0].size() : -1, nHave > 1 ? (int)(*pMesh->uv)[1].size() : -1,\n'
     b'\t\t\t\tpMesh->drawFlag, pMesh->xiDrawFlag2, pMesh->group, pMesh->rigidNum, dwFVF);\n'
     b'\t\tif (nHave < nLayers) nLayers = nHave;\n'
     b'\t}\n'
     b'\tconst WMatrix* pMat;\n\tif ((m_xiFlag & 2) == 0)\n'),
])
print('uv_trace: ok')
