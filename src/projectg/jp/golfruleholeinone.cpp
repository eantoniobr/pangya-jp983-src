// JP 983: unidade 00544ce0–005469a0 (CGolfRuleHoleInOne). Regra dos modos de jogo 0x0d/0x0e. O `SetPlayer` é o do
// CGolfRuleApproach (golfruleapproach.cpp da frente A) sem a posição sorteada: todos saem do tee e a lista de rivais é refeita.
// Deslocamentos medidos no exe 983.
#include "minatl.h"
#include "projectg.h"
#include "golfruleholeinone.h"
#include "subgolfrule.h"
#include "golfdocjp.h"
#include "golfdoc.h"
#include "golfrule.h"
#include "golfball.h"
#include "shareddoc.h"
#include "club.h"
#include "packet.h"
#include "networksystem.h"
#include "gatewayactor.h"

// JP 983: campos lidos por deslocamento (o layout do 983 nestas classes ainda não está no fonte da frente A).
#define GOLFDOC983_U8(off) (*(unsigned char*)((char*)GOLFDOC() + (off)))
#define GOLFDOC983_HOLE() GOLFDOC983_U8(0x17c)
#define DOC983_GAMETYPE() DOC983_U8(0x109b8)
// estatística do buraco: Doc + jogador * 0x109 + deslocamento (0xffc8 = m_holeStatistics)
#define DOC983_HOLESTAT(player, off) (*(unsigned long*)((char*)Doc() + (player) * 0x109 + 0xffc8 + (off)))

inline bool IsHoleInOneMode983(int mode) // cópia fora de linha 00544f50
{
	return mode >= 0x0d && mode <= 0x0e;
}

CGolfRuleHoleInOne::CGolfRuleHoleInOne(CGolfRule* pGolfRule)
{
	m_pGolfRule = pGolfRule;
}

CGolfRuleHoleInOne::~CGolfRuleHoleInOne()
{
}

void CGolfRuleHoleInOne::SetGrade()
{
}

void CGolfRuleHoleInOne::SetReady()
{
	RULEJP(m_pGolfRule)->ChangeGameMode983(1);
}

void CGolfRuleHoleInOne::ShowScore(int arg)
{
	ShowScore983();
}

void CGolfRuleHoleInOne::EnableShotReview()
{
	AfxGetTask()->GetActor("ShotReview") << MsgObject(NULL, 0x2fd, (unsigned long)"ENABLE", 1, 0, 0, 0);
}

void CGolfRuleHoleInOne::RequestShotReview(float time)
{
	if (!GOLFDOC983_U8(0x15e))
	{
		GOLFDOC983_U8(0x15e) = true;

		WSendPacket packet((enumClientPacket)0x34);
		packet.Send(TO_GAME);

		SendShotReview983();
	}

	AfxGetTask()->GetActor("ShotReview") << MsgObject(NULL, 0x2fd, (unsigned long)"SET_MAX_HIS", 1, 0, 0, 0);
}

void CGolfRuleHoleInOne::OnHoleIn()
{
	GOLFDOC()->GetPlayer(GOLFDOC()->GetCurrentPlayer())->totalStroke++;

	int holeIn = 0;
	CGolfBall& ball = GolfBall();
	if (g_bUnk983_e47e88)
	{
		DOC983_HOLESTAT(GOLFDOC()->m_currentPlayer, 0x1c)++;
	}
	else if (ball.m_holeIn == 1)
	{
		DOC983_HOLESTAT(GOLFDOC()->m_currentPlayer, 0x3a)++;

		if (GOLFDOC()->GetPlayer(GOLFDOC()->GetCurrentPlayer())->stroke[GOLFDOC983_HOLE() - 1] == (unsigned char)1)
			DOC983_HOLESTAT(GOLFDOC()->m_currentPlayer, 0x2c)++; // de primeira: hole-in-one

		holeIn = 1;
	}

	AfxGetTask()->GetActor(s_gatewayActor[1]) << MsgObject(NULL, 0x7535, 0x0e, holeIn, 0, 0, 0);

	GOLFDOC983_U8(0x7b4) = true;

	AfxGetTask()->GetActor("Score") << MsgObject(NULL, 0x2b, 0, 0, 0, 0, 0);
}

void CGolfRuleHoleInOne::ResetComboGauge()
{
	float limit = Doc()->GetComboGaugeLimit(GOLFDOC()->m_currentPlayer);
	float gauge = limit > 0.0 ? limit : 0.0f;

	GOLFDOC()->GetPlayer(GOLFDOC()->GetCurrentPlayer())->gauge = gauge;

	g_pUnk983_e47e20->SetC(1.0f);
}

void CGolfRuleHoleInOne::ReadyNextShot()
{
	ResetComboGauge();

	DOC983_U8(0x10704) = 0;
	g_pCameraWork983->Fn6db6c0_983(0x1cc); // 983 0xcc (tee-back) = nosso CCameraWork::kTeeBackCamera983 (0xcc nosso = ZOOMOUT)
	GOLFCLUBJP()->Refresh983();
	DOC983_U8(0x10588) = 1;
}

void CGolfRuleHoleInOne::OnShotEnd()
{
	ResetComboGauge();

	IActor* pGateway = AfxGetTask()->GetActor(s_gatewayActor[1]);

	int bHoleIn = GolfBall().m_holeIn == 1;
	bool bMission = false;
	AfxGetTask()->GetActor(s_gatewayActor[1])
		<< MsgObject(NULL, 0x7535, 0x14, (unsigned long)&bMission, 0, 0, 0);

	bool bSkip = false;
	if (IsHoleInOneMode983(DOC983_GAMETYPE()))
	{
		switch (DOC983_GAMETYPE())
		{
		case 0x0c:
		case 0x0e:
		case 0x13:
			if (bHoleIn && bMission)
				bSkip = true;
			break;
		}
	}

	if (!bSkip)
	{
		int index = 0;
		pGateway << MsgObject(NULL, 0x7535, 0x12, (unsigned long)&index, 0, 0, 0);

		if (index >= 0 && index < 4)
			RULEJP(m_pGolfRule)->SendMsg983("Player", MsgObject((IActor*)m_pGolfRule, 0x14e, index, 0, 0, 0, 0));
	}

	if (bHoleIn == 1)
		AfxGetTask()->GetActor("ShotReview") << MsgObject(NULL, 0x2fd, (unsigned long)"RESET_REVIEW", 0, 0, 0, 0);

	IActor* pScreen = AfxGetTask()->GetActor("Screen");
	pScreen << MsgObject(NULL, 0x245, 0, 0, 0, 0, 0);

	float value = 0.0f;
	if (!IsHoleInOneMode983(DOC983_GAMETYPE()))
	{
		pGateway << MsgObject(NULL, 0x7535, 6, (unsigned long)&value, 0, 0, 0);
		pScreen << MsgObject(NULL, 0xbd, (unsigned long)&value, 0, 0, 0, 0);
	}
	else if (!bHoleIn || !bMission)
	{
		pGateway << MsgObject(NULL, 0x7535, 6, (unsigned long)&value, 0, 0, 0);
		pScreen << MsgObject(NULL, 0xbd, (unsigned long)&value, 0, 0, 0, 0);
	}

	GOLFDOC()->GetPlayer(GOLFDOC()->GetCurrentPlayer())->itemNum = 0;
	GOLFDOC()->GetPlayer(GOLFDOC()->GetCurrentPlayer())->item = 0;
	GOLFDOCJP()->DisablePlayerEvent(6, GOLFDOC()->m_currentPlayer);
}

void CGolfRuleHoleInOne::SetPlayer()
{
	if (m_pGolfRule == NULL)
		return;

	if (WNetworkSystem::Instance()->IsConnected(WNetworkSystem::NET_GAME))
	{
		GOLFDOC()->MakePlayer(1);

		std::list<sSlotInfo>& slotList = Doc()->m_slotList;
		Doc()->m_rivalList.clear();
		Doc()->m_rivalList.reserve(slotList.size());

		for (std::list<sSlotInfo>::iterator it = slotList.begin();
			it != slotList.end(); ++it)
		{
			if ((*it).dwGuid == -1)
			{
				GOLFDOC()->GetPlayer(0)->state = 3;
				continue;
			}

			Doc()->SetIndex((*it).dwGuid);
			sRivalData rival;
			rival.Clear983();
			rival.hole = Doc()->m_holeOrder[0];
			rival.uid = (*it).dwUserUID;
			rival.oid = (*it).dwGuid;
			rival.ballPos = GOLFDOC()->GetHoleData(GOLFDOC983_HOLE()).tee;

			rival.flag = (*it).gender;
			memset(rival.holeStroke, 0, sizeof(rival.holeStroke));
			rival.titleTypeId = (*it).dwTitle;
			rival.team = (*it).bTeam;
			rival.rank = 1;
			rival.state = 0;
			rival.totalStroke = 0;
			rival.totalScore = 0;
			rival.totalPang = 0;
			rival.totalBonusPang = 0;
			rival.observerState = 1;
			rival.observerRank = 1;
			rival.unk983_138 = 0;
			rival.unk983_140 = 0;
			rival.unk983_148 = 0;
			memset(rival.holeScore, 0, sizeof(rival.holeScore));
			memset(rival.holePang, 0, sizeof(rival.holePang));
			rival.order = (*it).connectionRank;
			rival.quitOrder = slotList.size();
			rival.finishOrder = slotList.size();
			rival.level = (*it).level;
			strcpy(rival.nickname, (*it).sNick);
			strcpy(rival.guildName, (*it).sGuild);
			rival.unk983_178 = (*it).unk983_68;
			rival.guildUID = (*it).GuildId;
			strcpy(rival.guildMark, (*it).szEmblemName);
			rival.mascotTypeId = (*it).tidMascot;
			rival.capability = (*it).dwIdentity;
			rival.pangMastery = (*it).pangma[0];
			rival.pangNitro = (*it).pangma[1];
			rival.guildPoint = 0;
			Doc()->m_rivalList.push_back(rival);

			if ((*it).dwGuid == MyGuid(true))
			{
				sPlayerData* pPlayer = GOLFDOC()->GetPlayer(0);
				pPlayer->team = (*it).bTeam;
				m_pGolfRule->AddPlayer(0, (*it).sNick, (*it).dwUserUID,
					(*it).dwGuid, Doc()->m_userInfo[0].caddieInfo.tid);
			}

			Doc()->ClearUserInfoTimeMap((*it).dwUserUID);
			GOLFDOC()->RefreshPlayerNum();
		}
	}

	if (IsHoleInOneMode983(DOC983_GAMETYPE()))
	{
		if (OnlinePlay())
			AfxGetTask()->GetActor(s_gatewayActor[1]) << MsgObject(NULL, 0x7535, 3, 0, 0, 0, 0);
		else
			GOLFDOC()->SetHoleRange983(GOLFDOC983_HOLE(), GOLFCLUBJP()->Fn6add30_983(0));
	}
	else
	{
		GOLFDOC()->SetHoleRange983(GOLFDOC983_HOLE(), GOLFCLUBJP()->Fn6add30_983(0));
	}

	if (WNetworkSystem::Instance()->IsConnected(WNetworkSystem::NET_GAME))
		m_pGolfRule->SendHoleData();
}
