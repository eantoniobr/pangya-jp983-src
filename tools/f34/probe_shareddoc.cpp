#include "stdafx.h"
#include <stddef.h>
#define CK(m, v) typedef char ck_##m[(offsetof(CSharedDoc, m) == (v)) ? 1 : -1];
CK(m_serverTime, 0x180) CK(m_commandLineID, 0x1d0) CK(m_refreshGuidList, 0x1f4) CK(m_itemManager, 0x20c) CK(m_myInfo, 0x7a0)
CK(m_stringMap, 0x36f4) CK(m_partsList, 0x3734) CK(m_specialTrophyList, 0x37a4) CK(m_cardAbilityList, 0x37ec) CK(m_cardPeriodList, 0x381c) CK(m_questList, 0x3834)
CK(m_cookie, 0x3858) CK(m_cash, 0x3868) CK(m_roomSlotMap, 0x3890) CK(m_userInfo, 0x38b0) CK(m_holeStatistics, 0xffc8)
CK(m_acquireItemList, 0x103ec) CK(m_rivalList, 0x1042c) CK(m_guildMatchupList, 0x10450) CK(m_guildMatchFlagList, 0x10460)
CK(m_gameMode, 0x1048c) CK(m_golfGame, 0x1058c)
#define SZ(t, v) typedef char sz_##t[(sizeof(t) == (v)) ? 1 : -1];
SZ(sMyInfo, 12114) SZ(sUserInfo, 12742) SZ(sCharacterInfo, 513) SZ(sPangYaUserInfo, 301) SZ(sPangYaUserStatistics, 265)
SZ(sItemInfo, 196)
SZ(CItemManager, 1428)
SZ(sUserEquip, 116)
SZ(sMascotInfo, 62)
SZ(sClubInfo, 28)
SZ(sRecordedItemInfo, 252)
static const int szIM = sizeof(CItemManager);
#pragma message("x")
template<int N> struct Show; Show<sizeof(CItemManager)> show1; Show<sizeof(sItemInfo)> show2;
