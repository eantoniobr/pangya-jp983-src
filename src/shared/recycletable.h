#pragma once

struct sRecycleItem
{
	unsigned long dwTid;
	unsigned long dwItemid;
	unsigned short iNum;
	unsigned char byLevel;
	unsigned char byFlag983; // 983: +0x0b, byte baixo de sCadieMagicBox+0x14 (00a22d80)
	short iChar;
	short iIndex;
	unsigned char byItemType;
	unsigned short wTime;
	_SYSTEMTIME date;
	unsigned long dwRandSeq;
	char szRandName[40];
	_SYSTEMTIME dateStart983; // 983: +0x50 e +0x60 (sizeof 0x70), periodo da receita no CadieMagicBox.iff
	_SYSTEMTIME dateEnd983;

	sRecycleItem() // 983: o new[] do leitor 00a22d80 zera cada elemento
	{
		memset(this, 0, sizeof(*this));
	}
};
C_ASSERT(sizeof(sRecycleItem) == 0x70);
C_ASSERT(offsetof(sRecycleItem, szRandName) == 0x28);

extern int g_NumIndexRecycleItem;
extern int g_NumLowRecycleItem;
extern int g_NumMidRecycleItem;
extern int g_NumHighRecycleItem;
extern int g_NumSpecialRecycleItem;
extern int g_NumEventRecycleItem;
extern sRecycleItem** g_ArrayTidMixItem;
extern sRecycleItem* g_ArrayRecycleItem;

void InitIndexRecycleItem()
{
	for (short i = 0; i < g_NumIndexRecycleItem; i++)
	{
		g_ArrayRecycleItem[i].iIndex = i;
	}
}

unsigned long GetTidMixItem(short index, int mix)
{
	if (index < 0)
		return 0;
	if (index >= g_NumIndexRecycleItem)
		return 0;
	if (mix < 0)
		return 0;
	if (mix >= 4)
		return 0;

	return g_ArrayTidMixItem[index][mix].dwTid;
}

unsigned short GetNumMixItem(short index, int mix)
{
	if (index < 0)
		return 0;
	if (index >= g_NumIndexRecycleItem)
		return 0;
	if (mix < 0)
		return 0;
	if (mix >= 4)
		return 0;

	return g_ArrayTidMixItem[index][mix].iNum;
}

unsigned long GetTidRecycleItem(short index)
{
	if (index < 0)
		return 0;
	if (index >= g_NumIndexRecycleItem)
		return 0;

	return g_ArrayRecycleItem[index].dwTid;
}

unsigned short GetNumRecycleItem(short index)
{
	if (index < 0)
		return 0;
	if (index >= g_NumIndexRecycleItem)
		return 0;

	return g_ArrayRecycleItem[index].iNum;
}

const sRecycleItem* GetRecycleItem(short index)
{
	if (index < 0)
		return 0;
	if (index >= g_NumIndexRecycleItem)
		return 0;

	return &g_ArrayRecycleItem[index];
}
