#pragma once

#include "frform.h"

class FrEdit;
class FrContextMenuCtrl;
class Bitmap;
struct FrListItem;
struct GUILD_USER_LIST;

namespace _guild
{
	class CGuildInfo;

	class CGuildMainForm : public FrForm
	{
	public:
		static const WRTTI m_RTTI;

		struct sMemberItem
		{
			const GUILD_USER_LIST* pInfo;
			bool bEmpty;
		};

		CGuildMainForm();

		void SetLinkGuildInfo(CGuildInfo* pInfo) { m_pLinkGuildInfo = pInfo; }

		void DisableJoinButton();
		void InitSearchMode();
		void RequestMember_Page(int page);
		void UnLockScrollMemberList();
		void RefreshMyGuildHistory();
		void RequestChangeClass(GUILD_CLASS_IDX classIdx);
		void ClearForm();
		void RefreshGuildMember();
		void RefreshGuildSearch();
		void Refresh();

		// TODO: this class definition is incomplete
		unsigned char m_unused110[0x58];
		FrEdit* m_pIntroduceEdit;
		FrEdit* m_pNoticeEdit;
		unsigned char m_unused170[0x1c];
		FrContextMenuCtrl* m_pCommandMenu;
		FrListItem* m_pSelectedMember;
		unsigned char m_unused194[0x3c];
		const Bitmap* m_pTalkIcon;
		unsigned char m_unused1d4[0x14];
		CGuildInfo* m_pLinkGuildInfo;
		int m_guildActorParam;
		unsigned char m_unused1f0[0xcc];
		float m_talkTextOffset;
		float m_talkIconOffset;
		unsigned char m_unused2c4[0x10];
		const GUILD_USER_LIST* m_pCommandUserInfo;
		unsigned char m_unused2d8[0x38];
	};
}
