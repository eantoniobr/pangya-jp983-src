// JP 983: unidade 0064f900–00650540 (CSubGolfRuleBase + a carga da fita de replay). Classe nova do 983; nomes de método meus.
// O `ShotDataLoad` é o CGolfRule::ShotDataLoad do 645 (golfrule.cpp da frente A) com o que o 983 acrescentou: conferência das
// peças do personagem contra a tabela de itens, os três avisos 0x753b ao "Gateway" (0, 0x0d e 0x0b com o arquivo) e o bloco
// "EXTENSION". Deslocamentos do CSharedDoc/CGolfDoc/sPlayerData medidos no exe 983.
#include "subgolfrule.h"
#include "golfdoc.h"
#include "parttidlist.h"
#include "taskmanager.h"
#include "gatewayactor.h"
#include "lobbymain.h"
#include "../shared/localize.h"
#include <list>

// registro de 0x41 bytes da lista de Doc+0x381c (o sSCardAvilityPeriodInfo do 645; campos não levantados)
#pragma pack(push, 1)
struct sCardPeriod983
{
	unsigned long m_00, m_04, m_08, m_0c, m_10, m_14, m_18, m_1c, m_20, m_24, m_28, m_2c, m_30, m_34, m_38, m_3c;
	unsigned char m_40;
};
#pragma pack(pop)

CSubGolfRuleBase::CSubGolfRuleBase()
{
}

CSubGolfRuleBase::~CSubGolfRuleBase()
{
}

void CSubGolfRuleBase::Init()
{
}

void CSubGolfRuleBase::Process(float dt)
{
}

void CSubGolfRuleBase::On3()
{
}

void CSubGolfRuleBase::OnShotEnd()
{
}

bool CSubGolfRuleBase::ShotDataLoad(const char* filename)
{
	size_t len = strlen(filename);
	FILE* fp = fopen(len == 0 ? "D:/work/ProjectG_S4/bin/save/pangya_003.sav" : filename, "rb");
	if (fp == NULL)
	{
		g_bQuit = true;
		return false;
	}
	unsigned long tag = 0;
	unsigned char map = 0;
	CPartTidList parts;
	CGolfRule::sShotData* pShot = RULEJP(m_pRule)->GetShotData983();
	int shotCount = 0;
	unsigned char hole = 0;
	int gameId = 0;
	unsigned long gameTag = 0xffffffff;
	CGolfRule::sShotData data;
	SYSTEMTIME time;
	memset(pShot, 0, sizeof(CGolfRule::sShotData));
	DOC983_SHOTLIST().clear();
	DOC983_U32(0x1127c) = 0;
	fread(&tag, 4, 1, fp);
	fread(&gameTag, 4, 1, fp);
	fread(&map, 1, 1, fp);
	fread(&time, 0x10, 1, fp);
	fread(&gameId, 4, 1, fp);
	DOC983_U32(0x11228) = gameId;
	fread((char*)Doc() + 0x38b0, 0x31c6, 1, fp);
	fread(&parts, 200, 1, fp);
	fread(&hole, 1, 1, fp);
	fread(GOLFDOC()->GetPlayer(0), 0xdb0, 1, fp);
	fread((char*)Doc() + 0x10a99, 4, 1, fp);
	if (gameId == 1)
	{
		fread(pShot, 0x88, 1, fp);
		DOC983_U32(0x1127c) = pShot->holeStroke;
	}
	else if (gameId == 2)
	{
		fread(&shotCount, 4, 1, fp);
		for (int i = 0; i < shotCount; i++)
		{
			fread(&data, 0x88, 1, fp);
			DOC983_SHOTLIST().push_back(data);
			memset(&data, 0, sizeof(data));
		}
	}
	// por personagem (índice = tid & 0x3ffffff): até quatro posições da lista de peças que têm de existir na tabela de itens
	int slots[15][4] = {
		{ 0x12, -1, -1, -1 }, { 0x13, -1, -1, -1 }, { 0x12, -1, -1, -1 }, { 0x13, -1, -1, -1 },
		{ 6, 7, 0x12, 0x13 }, { 8, 9, -1, -1 }, { 0xf, 0x13, 0x14, -1 }, { 9, 0xa, 0xb, 0x16 },
		{ 8, 0x13, -1, -1 }, { 8, 0x15, 0x16, -1 }, { 8, 0x14, 0x15, -1 }, { -1, -1, -1, -1 },
		{ -1, -1, -1, -1 }, { -1, -1, -1, -1 }, { -1, -1, -1, -1 },
	};
	for (int j = 0; j < 4; j++)
	{
		int slot = slots[parts.m_charTid & 0x3ffffff][j];
		if (slot == -1)
			break;
		if (parts.m_tid[slot] != 0 && ((CItemManagerJp2*)((char*)Doc() + 0x20c))->Find983(parts.m_tid[slot]) == NULL)
		{
			parts.m_tid[slot] = 0;
			*(unsigned long*)((char*)Doc() + 0x680e + slot * 4) = 0;
		}
	}
	((CCardManagerJp*)CCardManager::Instance())->Set983(0, (char*)Doc() + 0x6a1c);
	if (IsLocalContent((localContentType_t)0x52))
	{
		int count = 0;
		fread(&count, 4, 1, fp);
		if (count > 0)
		{
			Doc()->m_cardPeriodList.clear();
			for (int i = 0; i < count; i++)
			{
				sCardPeriod983 info;
				fread(&info, 0x41, 1, fp);
				((CSharedDocJp2*)Doc())->AddCardPeriod983(&info);
			}
		}
		memcpy((char*)CCardManager::Instance() + 0x2d, (char*)Doc() + 0x6802, 0x201);
		((CCardManagerJp*)CCardManager::Instance())->CalcCardPeriodAndStatus983();
		((CCardManagerJp*)CCardManager::Instance())->SetPlayerIndex983(0);
	}
	AfxGetTask()->GetActor(s_gatewayActor[1]) << MsgObject(NULL, 0x753b, 0, 0, 0, 0, 0)
		<< MsgObject(NULL, 0x753b, 0xd, 0, 0, 0, 0) << MsgObject(NULL, 0x753b, 0xb, (int)fp, 0, 0, 0);
	ReplayReadExtension983(fp, &time);
	fclose(fp);
	*pShot = DOC983_SHOTLIST().front();
	SetCurMap(map);
	DOC983_U8(0x1051e) = pShot->hole;
	((CSharedDocJp2*)Doc())->SetHoles983(&DOC983_U8(0x1051e), false);
	unsigned char n = 0;
	unsigned int idx;
	do
	{
		idx = n;
		n++;
		if (DOC983_U8(idx + 0x1051e) == pShot->hole)
			goto found;
	} while (n < 0x12);
	n = 0x13;
found:
	DOC983_U8(n + 0x104f9) = hole;
	*((unsigned char*)GOLFDOC() + 0x17c) = pShot->hole;
	GOLFDOC()->SetPartTidList(0, parts.m_charTid, parts.m_hairColor, parts.m_shirtsColor, parts.m_tid, parts.m_uid);
	DOC983_U8(0x10594) = 0;
	strcpy((char*)Doc() + 0x10595, *(char**)((char*)Doc() + 0xc8));
	DOC983_F32(0x11270) = *(float*)((char*)pShot + 0x20);
	DOC983_U32(0x11228) = gameId;
	if (IsLocalContent((localContentType_t)0x58))
		RequestUccInfo(*(sUserInfo*)((char*)Doc() + 0x38b0));
	return true;
}
