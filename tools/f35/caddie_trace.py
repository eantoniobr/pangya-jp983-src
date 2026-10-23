#!/usr/bin/env python3
"""A178: rastro provisório do caddie da partida (CGolfCaddie) + o do heap (heap_trace.py). PATCH_PY do wt_build.sh.

Linhas "rastro: caddie ..." no jp983_stubs.log: tid de cada jogador no OnLoad e o item IFF achado no AddCaddie.
"""
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'heap_trace.py')).read())

patch('src/projectg/golfcadie.cpp', [
    ('\nvoid CGolfCaddie::OnLoad()\n{\n',
     '\nextern "C" void __cdecl jp983_rastro(const char* fmt, ...);\nvoid CGolfCaddie::OnLoad()\n{\n'
     '\tjp983_rastro("caddie OnLoad n=%d tut=%d", GOLFDOC()->m_playerNum, GOLFDOC()->m_tutorialMode);\n'),
    ('\n\t\t\tunsigned long tid = Doc()->m_userInfo[i].caddieInfo.tid;\n',
     '\n\t\t\tunsigned long tid = Doc()->m_userInfo[i].caddieInfo.tid;\n'
     '\t\t\tjp983_rastro("caddie i=%d tid=%08x part=%08x", i, tid, Doc()->m_userInfo[i].caddieInfo.tidPart);\n'),
    ('\tIFF_STRUCT::sCaddie* item = ItemManager()->FindCaddie(id);\n',
     '\tIFF_STRUCT::sCaddie* item = ItemManager()->FindCaddie(id);\n'
     '\tjp983_rastro("caddie AddCaddie id=%08x part=%08x item=%p data=%s", id, cadItem, item, item ? item->Data : "-");\n'),
])
print('caddie_trace: ok')
