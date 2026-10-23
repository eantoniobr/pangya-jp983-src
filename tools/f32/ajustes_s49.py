# F3.5 (sessão 49): unidades que não compilavam com o VS2010 por diferenças VC7.1 -> VC10 (o código gerado não muda) e
# por ramos REBANG_SEMANTIC_ONLY que o rebang não compila. Lido por tools/f32/ajustes.py no fim.
NEW17 = []
# iterador de vector: `_Myptr` é do VC7.1 (C2039); `&*it` dá o mesmo ponteiro
NEW17 += [
 ('todos', 'src/projectg/scoreboard.cpp', 'm_pList->AddItem(it._Myptr);', 'm_pList->AddItem(&*it);', 'VC10: iterador de vector sem _Myptr (C2039)'),
 ('todos', 'src/projectg/lobbymain.cpp', 'm_pRoomGuildRank->AddItem(it._Myptr);', 'm_pRoomGuildRank->AddItem(&*it);', 'VC10: iterador de vector sem _Myptr (C2039)'),
 ('todos', 'src/projectg/scoredlg.cpp', '_ITER_BASE(it)->uid[', 'it->uid[', 'VC10: _ITER_BASE não existe (C2227)'),
]
# std::back_inserter: no VC10 só vem com <iterator> (C2039)
for _f in ('ghostdocument', 'privatetradedlg', 'tradehandler'):
    NEW17.append(('sub', 'src/projectg/%s.cpp' % _f, '#include "minatl.h"\n', '#include "minatl.h"\n#include <iterator> // VC10: std::back_inserter\n',
                  'VC10: std::back_inserter precisa de <iterator> (C2039)'))
NEW17 += [
 # strstr const-correto do VC10 (C2440)
 ('sub', 'src/engine/wreg.cpp', '\tchar* pos;\n\tunsigned int i;\n\tfor (i = 0; i < 5; ++i)\n', '\tconst char* pos;\n\tunsigned int i;\n\tfor (i = 0; i < 5; ++i)\n',
  'strstr const-correto do VC10 (C2440)'),
 # truque de ordem de emissão do VC7.1 que o VC10 não aceita (C2440)
 ('sub', 'src/projectg/topiconmanager.cpp', '\tif (0)\n\t\tstd::vector<sTopIcon*>::const_iterator((sTopIcon**)0);\n', '',
  'VC10: const_iterator(ponteiro) não existe (C2440); era só truque de ordem de emissão'),
 # sCards::tid (o ramo REBANG_SEMANTIC_ONLY do rebang usa o nome antigo typeId)
 ('todos', 'src/projectg/ccardbook.cpp', 'info.typeId = pDlg->m_cardTid;', 'info.tid = pDlg->m_cardTid;', 'ramo semântico: sCards::tid (C2039)'),
]
NEW17 += [
 ('todos', 'src/projectg/ccardbook.cpp', 'ItemManager()->FindDesc(m_pItem->typeId);', 'ItemManager()->FindDesc(m_pItem->tid);', 'ramo semântico: sCards::tid (C2039)'),
 ('todos', 'src/projectg/tradedlg.cpp', 'ItemManager()->FindCommonItem((*it).typeId);\n\t\t\tif (common && (common->IsSalable == 1 || common->IsSalable == 3))\n'
  '\t\t\t{\n\t\t\t\titem.dwGuid = (*it).uid;\n\t\t\t\titem.dwTid = (*it).typeId;\n\t\t\t\titem.iNum = (*it).count - ',
  'ItemManager()->FindCommonItem((*it).tid);\n\t\t\tif (common && (common->IsSalable == 1 || common->IsSalable == 3))\n'
  '\t\t\t{\n\t\t\t\titem.dwGuid = (*it).uid;\n\t\t\t\titem.dwTid = (*it).tid;\n\t\t\t\titem.iNum = (*it).cardCount - ',
  'ramo semântico: sCards::tid e cardCount (C2039)'),
 # especializações explícitas de membros da STL do VC7.1 (truques de ordem de emissão/inline): não valem na STL do VC10
 ('corte', 'src/projectg/tradedlg.cpp', 'namespace std\n{\n\ttemplate <>\n\tinline list<sTradeItem>::const_iterator list<sTradeItem>::begin() const\n',
  '} // namespace std\n', '// VC10: sem as especializações de list<sTradeItem>::begin/end do VC7.1\n',
  'VC10: especialização de list::begin/end com _Nextnode/_Myhead do VC7.1 (C2440)'),
 ('corte', 'src/projectg/objectfactory.cpp', '// HACK: explicit specializations (same body as <utility>) fix COMDAT order\n',
  'IObject* const& _Val2)\n\t: first(_Val1), second(_Val2)\n{\n}\n', '// VC10: sem as especializações do construtor de std::pair do VC7.1\n',
  'VC10: pair deriva de _Pair_base; construtor especializado não compila (C2614)'),
 ('corte', 'src/projectg/realmyroomtask.cpp', '// HACK: Keep the original out-of-line pair constructor in OnPacket; both\n',
  'const unsigned int& key, const sItemInfo& value)\n\t: first(key), second(value)\n{\n}\n', '// VC10: sem a especialização do construtor de std::pair do VC7.1\n',
  'VC10: pair deriva de _Pair_base; construtor especializado não compila (C2614)'),
 # conferências de deslocamento do 645 (o CSharedDoc aqui está no layout do 983)
 ('corte', 'src/projectg/realmyroomtask.cpp', 'typedef char\n\trb_chk_sid[offsetof(CSharedDoc, m_myInfo.info.sID) == 0x3e2 ? 1 : -1];\n',
  'rb_chk_uid[offsetof(CSharedDoc, m_myInfo.info.dwUID) == 0x4eb ? 1 : -1];\n', '// 983: sem as conferências de deslocamento do 645 (CSharedDoc no layout do 983)\n',
  '983: conferências de deslocamento do CSharedDoc do 645 (C2118)'),
 # cópia local de WVector2D::Normalize (truque de ordem de emissão): no 983 o corpo está em wmath.h
 ('corte', 'src/projectg/christamseventdlg.cpp', '// HACK\ninline WVector2D& WVector2D::Normalize()\n', '\treturn *this;\n}\n',
  '// 983: WVector2D::Normalize fica em wmath.h\n', 'cópia local de WVector2D::Normalize (C2084)'),
]
# river.cpp: no ramo semântico não existe a classe-sombra CRiverInfo_ (só no ramo de bytes do 645); os 4 leitores já estão
# em linha no CRiverInfo do golfdoc.h
NEW17 += [
 ('corte', 'src/projectg/river.cpp', 'float CRiverInfo_::GetScrollVelocity(int index)\n', '\treturn m_river[index].depth;\n}\n',
  '// ramo semântico: os leitores do CRiverInfo estão em linha no golfdoc.h\n#define RIVERINFO() (GOLFDOC()->m_riverInfo)\n',
  'ramo semântico: CRiverInfo_ e RIVERINFO() só existiam no ramo de bytes do 645 (C2653)'),
]
# CExceptionReport::Init do 983 (009928d0): InitSymFunctions, SetUnhandledExceptionFilter, SetErrorMode(0x8003) — sem a chamada
# _set_security_error_handler (que nem existe na CRT do VC10: C3861)
NEW17 += [
 ('sub', 'src/shared/exceptionreport.cpp', '\t_set_security_error_handler(SecurityErrorHandler);\n', '',
  '983: CExceptionReport::Init não chama _set_security_error_handler (009928d0)'),
]
# Ramo semântico (REBANG_SEMANTIC_ONLY) que ainda usava símbolos do ramo de bytes do 645 (apelidos de linker `rb_*`)
_P = 'src/projectg/'
NEW17 += [
 ('sub', _P + 'ingameguildlobbydlg.cpp', 'WRect(*(volatile float*)&pItem->pos.x + rb_real_42c00000,', 'WRect(pItem->pos.x + 96.0f,',
  'ramo semântico: constante 96.0f no lugar do apelido rb_real_42c00000 (C2065)'),
 ('sub', _P + 'particleparty.cpp', '\t\t\trb_real_41490fdb; // 12.566371f\n', '\t\t\t12.566371f;\n', 'ramo semântico: constante no lugar do apelido rb_real_* (C2065)'),
 ('todos', _P + 'particleparty.cpp', '*(volatile float*)&p->vel.x * rb_real_3f7d70a4; // *= 0.99f', 'p->vel.x * 0.99f;', 'ramo semântico: constante no lugar do apelido rb_real_* (C2065)'),
 ('todos', _P + 'particleparty.cpp', '*(volatile float*)&p->vel.z * rb_real_3f7d70a4; // *= 0.99f', 'p->vel.z * 0.99f;', 'idem'),
 ('todos', _P + 'particleparty.cpp', 'm_alpha -= *(volatile float*)&dt * rb_real_42c00000; // dt * 96.0f', 'm_alpha -= dt * 96.0f;', 'idem'),
 ('sub', _P + 'netresourcemanager.cpp', '\tmemcpy(m_uploadAddress[RESOURCE_BUG_REPORT], rb_bugReportUrl,\n\t\tsizeof(rb_bugReportUrl));\n',
  '\tstrcpy(m_uploadAddress[RESOURCE_BUG_REPORT],\n\t\t"http://qagame.pangya.ntreev.com:50000/post/BugReport.asp"); // texto do 645; conferir no 983\n',
  'ramo semântico: literal no lugar do apelido rb_bugReportUrl (C2065); provisório'),
 ('sub', _P + 'clientsetting.cpp', '\t\trb_ShadowReset(CShadowManager::Instance());\n', '\t\tCShadowManager::Instance()->Reset(); // 645: apelido rb_ShadowReset\n',
  'ramo semântico: chamada direta no lugar do apelido rb_ShadowReset (C3861)'),
 ('sub', _P + 'shotpreview.cpp', '\tif (0)\n\t\tRbOnprocessFunclets();\n\tif (msg.message == -1)\n', '\tif (msg.message == -1)\n',
  'ramo semântico: sem a referência morta a RbOnprocessFunclets (C3861)'),
 ('sub', _P + 'golfrule.cpp', '\trb_ProcessObserver_call(this);\n', '\tProcessObserver();\n', 'ramo semântico: chamada direta no lugar do apelido rb_ProcessObserver_call (C3861)'),
 ('sub', _P + 'golfcadie.cpp', '(const char*)&rb_C_06LLEKBOMH_LE_NO_LI_KO_LB_b_AA))', '"\\xb4\\xde\\xb8\\xae\\xb1\\xe2")) // "correr" (EUC-KR), como no ReadAttribute',
  'ramo semântico: literal no lugar do apelido rb_C_06LLEKBOMH (C2065)'),
]
NEW17 += [
 ('sub', _P + 'console.cpp', 'struct sCausticRb\n{\n', 'extern float causticSpeed; // pool.cpp\nextern int causticAlpha;\n\nstruct sCausticRb\n{\n',
  'ramo semântico: causticSpeed/causticAlpha do pool.cpp no lugar do apelido rb_caustic (C2065)'),
 ('todos', _P + 'console.cpp', '&rb_caustic.speed,', '&causticSpeed,', 'idem'),
 ('todos', _P + 'console.cpp', 'rb_caustic.alpha', 'causticAlpha', 'idem'),
]
NEW17 += [
 ('sub', _P + 'river.cpp', '#define RIVERINFO() (GOLFDOC()->m_riverInfo)\n',
  '#define RIVERINFO() (GOLFDOC()->m_riverInfo)\n#define PVS() (GetPVS()) // CQuadTree::GetLowestGround já está no quadtree.h\n',
  'ramo semântico: PVS() sem a classe-sombra CQuadTree_ (C3861)'),
]
