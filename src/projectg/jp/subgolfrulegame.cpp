// JP 983: unidade 00650540–006506e0 (CSubGolfRuleGame). Classe nova do 983; o `Init` é o laço de carga dos buracos que no 645
// estava no CGolfRule (golfrule.cpp da frente A, "LoadMapCheckData"). Deslocamentos medidos no exe 983.
#include "subgolfrule.h"
#include "golfdoc.h"
#include "polysoup.h"
#include "networksystem.h"
#include "lobbymain.h"

CSubGolfRuleGame::CSubGolfRuleGame(CGolfRule* pRule)
{
	m_pRule = pRule;
}

CSubGolfRuleGame::~CSubGolfRuleGame()
{
}

void CSubGolfRuleGame::Init()
{
	DOC983_SHOTLIST().clear();
	for (unsigned char i = 0; i < DOC983_U8(0x10699); i++)
	{
		*(unsigned char*)(*(int*)((char*)GOLFDOC() + 0xd8) - 0x1f + DOC983_U8(i + 0x1051e) * 0x38) = 0;
		*(unsigned char*)(*(int*)((char*)GOLFDOC() + 0xd8) - 0x1a + DOC983_U8(i + 0x1051e) * 0x38) = 3;
		if (DOC983_U8(0x109b8) == 0x12 || DOC983_U8(0x109b8) == 0x14)
			SetCurMap(DOC983_U8(i + 0x1050c));
		if (!GOLFDOC()->m_pPolySoup->LoadMapCheckData(DOC983_U8(i + 0x1051e)) &&
			WNetworkSystem::Instance()->IsConnected(WNetworkSystem::NET_GAME) != 0)
		{
			g_bQuit = true;
			return;
		}
		GetCurMap();
	}
	switch (DOC983_U8(0x109b8))
	{
	case 0x14:
	case 0x15:
		SetCurMap(DOC983_U8(0x1050c));
		break;
	}
}
