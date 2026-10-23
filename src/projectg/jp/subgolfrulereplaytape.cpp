// JP 983: unidade 006506e0–00650ab0 (CSubGolfRuleReplayTape). Classe nova do 983: sub-regra da fita de replay. `Init` é o ramo
// "ShotDataLoad" que no 645 estava no CGolfRule; `OnShotEnd` troca o modo da fita (Doc+0x11224) e o modo do jogo ao fim da tacada.
// Deslocamentos medidos no exe 983.
#include "subgolfrule.h"
#include "golfdoc.h"
#include "golfball.h"
#include "polysoup.h"
#include "clientsetting.h"
#include "scenemanager.h"
#include "camerawork.h"
#include "soundmanager.h"
#include "encrypttypes.h"
#include "../shared/localize.h"

CSubGolfRuleReplayTape::CSubGolfRuleReplayTape(CGolfRule* pRule)
{
	m_pRule = pRule;
}

CSubGolfRuleReplayTape::~CSubGolfRuleReplayTape()
{
}

void CSubGolfRuleReplayTape::Process(float dt)
{
	CSubGolfRuleBase::Process(dt);
}

void CSubGolfRuleReplayTape::OnShotEnd()
{
	if (!IsLocalContent((localContentType_t)0x50))
		return;
	CGolfBall& ball = GolfBall();
	if (DOC983_U32(0x11228) == 2)
	{
		if (RULEJP(m_pRule)->IsReplayShotDone983() != true)
			return;
		int n = *(WCrypticValue<int>*)((char*)&ball + 0x2bff4);
		if (DOC983_U32(0x11224) == 7)
		{
			if (n == 1)
				DOC983_U32(0x11224) = 8;
		}
		else if (n == 1 && DOC983_U32(0x11224) != 0xb && DOC983_U32(0x11224) != 1)
			DOC983_U32(0x11224) = 0xd;
		else
			DOC983_U32(0x11224) = 0xa;
	}
	else if (DOC983_U32(0x11228) == 1)
	{
		if (DOC983_U32(0x11224) == 7)
			DOC983_U32(0x11224) = 6;
		if (DOC983_U32(0x11224) == 0xb || DOC983_U32(0x11224) == 0xc)
			DOC983_U32(0x11224) = 0xa;
	}
	WPuppet* pBall = ((CSceneManagerJp*)CSceneManager::Instance())->GetPuppet983("\xb0\xf8");
	if (pBall != NULL && pBall->m_rootbone != NULL)
		pBall->SetAlpha(0xff);
	CCameraWork::Instance()->StopBallSound();
	RULEJP(m_pRule)->SendMsg983("Score", MsgObject(NULL, 0x163, 0, 0, 0, 0, 0));
	g_audio->StopSfx("shot_dist_count");
	if (DOC983_U32(0x11224) == 8 || DOC983_U32(0x11224) == 0xd)
	{
		DOC983_U32(0x11224) = 7;
		RULEJP(m_pRule)->ChangeGameMode983(0x1000);
	}
	else
		RULEJP(m_pRule)->ChangeGameMode983(0x800);
	RULEJP(m_pRule)->SetFlag2c0_983(true);
}

void CSubGolfRuleReplayTape::Init()
{
	DOC983_U32(0x1069c) = 0;
	COption::Instance()->dSetNumPlayers(1);
	GOLFDOC()->MakePlayer(1);
	if (ShotDataLoad((char*)Doc() + 0x11230) == true)
	{
		if (DOC983_U32(0x11228) == 1)
		{
			*(WCrypticValue<int>*)((char*)GOLFDOC()->GetPlayer(0) + 0x508) = 0;
			*(WCrypticValue<int>*)((char*)GOLFDOC()->GetPlayer(0) + 0x4f8) = 0;
		}
		else
			DOC983_U32(0x1127c) = 0;
		GOLFDOC()->m_pPolySoup->LoadMapCheckData(RULEJP(m_pRule)->GetShotData983()->hole);
	}
}
