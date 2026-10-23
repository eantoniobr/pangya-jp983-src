#pragma once

#include <string>
#include <list>
#include <map>
#include "frform.h"
#include "frlistbox.h"
#include "frcontextmenuctrl.h"
class FrMessengerDlg;
class FrMessengerChatDlg;
class FrNoteDlg;
class FrAddFriendDlg;
class FrOptionDlg;
class FrMemoDlg;
class FrGuildNoticeDlg;
class NewsReader;

namespace MSN
{
	enum eStatusType
	{
		STATUS_ACTIVE,
		STATUS_PLAYING,
		STATUS_AWAY,
		STATUS_BUSY,
		STATUS_ONLINE,
		STATUS_OFFLINE
	};
}

enum eConnectStatus
{
	CONNECT_STATUS_ACCEPTED = 2,
	CONNECT_STATUS_POSITION_SENT = 3,
	CONNECT_STATUS_COMPLETE = 4
};

struct sMsnChat
{
	std::string nick;
	std::string msg;
	unsigned long reserved;

	sMsnChat()
	{
		nick = "";
		msg = "";
		reserved = 0;
	}
};

#include "frbutton.h"
#include "frarea.h"

struct sChatSlot
{
	FrMessengerChatDlg* pDlg;
	unsigned long uid;
	bool bAlarm;
	std::list<sMsnChat> chatList;
	WRect rect;
	std::string tempChat;

	sChatSlot()
	{
		pDlg = NULL;
		uid = 0;
		bAlarm = false;

		tempChat = "";
		memset(&rect, 0, sizeof(rect));
		chatList.clear();
	}
};

class FrMessengerDlg : public FrForm
{
public:
	static const WRTTI m_RTTI;
	virtual const WRTTI* GetRTTI() const { return &m_RTTI; }
	friend IObject* FrMessengerDlgMakeInstance();

	FrMessengerDlg();

	virtual bool Close(bool bResult);

	void UpdateFriendList();
	void SetAddFriendNick(const char* nick, unsigned long uid);
	void SetTargetNick(const char* nick);
	void OpenAddFriendNickDlg();

	void EnableInvite(bool bEnable) { m_bEnableInvite = bEnable; }

protected:
	virtual bool OnLButtonDown(const WPoint& pt);

	void OnMessenger_FriendListInit(int param);
	void OnMessenger_FriendListOwnerDraw(int param);
	void OnMessenger_FriendListLBtnDown();
	void OnMessenger_FriendListRBtnDown();
	void OnMessenger_FriendListDBtnDown();
	void OnMessenger_GuildListInit(int param);
	void OnMessenger_GuildListOwnerDraw(int param);
	void OnMessenger_GuildListLBtnDown();
	void OnMessenger_GuildListRBtnDown();
	void OnMessenger_GuildListDBtnDown();
	void OnMessenger_CloseLBtnDown();
	void OnMessenger_MyInfoInit(int param);
	void OnMessenger_MyInfoOwnerDraw(int param);
	void OnMessenger_FriendBtnInit(int param);
	void OnMessenger_FriendLBtnDown();
	void OnMessenger_GuildBtnInit(int param);
	void OnMessenger_GuildLBtnDown();
	void OnMessenger_GuildNoticeBtnInit(int param);
	void OnMessenger_GuildNoticeLBtnDown();
	void OnMessenger_FindLBtnDown();
	void OnMessenger_RightMenuInit(int param);
	void OnMessenger_RightMenuLBtnDown();
	void OnMessenger_StateBtnInit(int param);
	void OnMessenger_StateLBtnDown();
	void OnMessenger_StateMenuInit(int param);
	void OnMessenger_StateMenuLBtnDown();

	void OnChatToFriend();
	void OnNoteToFriend();
	void OnInfoFriend();
	void OnAchievementFriend983(); // 983: 00900c50 (pacote 0x157)
	void OnAcceptFriend();
	void OnRemoveFriend();
	void OnBlockFriend();
	void OnBlockCancelFriend();
	void OnAliasToFriend();
	void OnInviteFriend();
	void OnGoWithFriend();

	bool OnAddFriendDlgResult(int result, FrForm* pForm);
	bool OnNoteDlgResult(int result, FrForm* pForm);
	bool OnMemoDlgResult(int result, FrForm* pForm);
	bool OnRemoveFriendDlgResult(int result, FrForm* pForm);
	bool OnBlockFriendDlgResult(int result, FrForm* pForm);
	bool OnBlockCancelFriendDlgResult(int result, FrForm* pForm);
	bool OnGuildNoticeDlgResult(int result, FrForm* pForm);

	void DrawFriendGroup(int param);
	void DrawGuildGroup(int param);
	void SetCount();
	void RestoreOther(unsigned long uid);
	MSN::eStatusType GetBuddyStatus(sFriend* pFriend);

	FrListBox* m_pFriendList;
	FrListBox* m_pGuildList;
	FrContextMenuCtrl* m_pRightMenu;
	FrContextMenuCtrl* m_pStateMenu;
	const Bitmap* m_pStatusIcon[5];
	const Bitmap* m_pSexIcon[3][2];
	const Bitmap* m_pGroupIcon[2];
	unsigned long m_selectUID;
	FrButton* m_pTabBtn[3]; // 983: +0x158 aba amigos, +0x15c campo novo (nao lido), +0x160 aba guilda (indices 0 e 2)
	FrButton* m_pStateBtn;
	unsigned long m_unknown168;
	FrArea* m_pMyInfo;
	int m_friendCount;
	int m_friendOnCount;
	int m_guildCount;
	int m_guildOnCount;
	FrNoteDlg* m_pNoteDlg;
	FrAddFriendDlg* m_pAddFriendDlg;
	FrButton* m_pNoticeBtn; // 983: +0x188
	FrOptionDlg* m_pOptionDlg; // 983: +0x18c
	unsigned long m_unknown18c;
	unsigned long m_unk983_194[12]; // 983: +0x194..+0x1c3 (ctor 00902780 inicia +0x194,+0x1ac,+0x1b0,+0x1b4,+0x1bc)
	FrMemoDlg* m_pMemoDlg; // 983: +0x1c4
	sFriend m_groupRow[3];
	std::list<sFriend*> m_friendOnList;
	std::list<sFriend*> m_friendOffList;
	std::list<sFriend*> m_guildList;
	std::list<sFriend*> m_guildOnList;
	std::list<sFriend*> m_guildOffList;
	bool m_bEnableInvite;

private:
	static sFRESH_ENTRY _MsgEntries[];

protected:
	static sFRESH_MSGMAP _MsgMap;
	virtual const sFRESH_MSGMAP* GetMessageMap() const;
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbOnmessengerguildFunclets(); // HACK: EH funclets of the naked OnMessenger_GuildNoticeLBtnDown (nakedify)
#endif
public:
};

struct MSNServerInfo : public sGameServerInfo
{
	MSNServerInfo() { bInvalid = false; }

	bool bInvalid;
};

class CMessengerInfo : public WSingleton<CMessengerInfo>, public FrCmdTarget
{
	friend class MSNUnit;
	friend class FrMessengerChatDlg;
	friend class CLobbyTask;
#ifdef REBANG_GOLFRULE_PCH
	friend class CGolfRule;
#endif
	friend class FrMessengerDlg;

public:
	CMessengerInfo();

	FrMessengerDlg* GetMessengerDlg() { return m_pMessengerDlg; }

	void Process(float delta);
	void Open(bool bForce);
	bool Close(bool bForce);
	void Toggle();
	void CloseWindow();
	void Refresh();
	bool IsVisible();

	void Notify1(const char* msg);
	void Notify2(const char* msg);
	void Notify3();
	void Notify4(bool bAlarm);
	void AlarmBtnUp(unsigned long uid);
	void RecvChat(sFriend* pFriend, std::string msg);
	void RepositionPopupDlg(FrMessengerChatDlg* pDlg, int index);

	void SetOfflineUserNick(const char* nick, unsigned long uid);
	void SetTargetNick(const char* nick);
	void SetMyStatus(MSN::eStatusType status);
	void SetGameFocus(bool bFocus);
	void InvalidateCurrentServer();

	MSN::eStatusType GetMyStatus() { return m_myStatus; }

	bool IsGameFocus() { return m_bGameFocus; }

	void SetComplete(eConnectStatus status) { m_complete = status; }
	eConnectStatus GetComplete() { return m_complete; }

	bool IsWaitingForServerList() { return m_bWaitServerList; }
	void SetServerListWaitingState(bool bWait) { m_bWaitServerList = bWait; }

	void SetCurrentServerIndex(int index) { m_curServerIndex = index; }

	void EnableInvite(bool bEnable) { m_bEnableInvite = bEnable; }

	// 983: convite de guilda pelo mensageiro (pacote 0xa8; pedido C30) - so declaracao, corpos com a C
	void AskGuildInvite983(std::string name, unsigned long key, bool bApply); // 009048b0 (ret 0x24)

protected:
	bool OnMessengerDlgResult(int result, FrForm* pForm);
	bool OnMessengerChatDlgResult(int result, FrForm* pForm);
	bool OnGuildInviteDlgResult983(int result, FrForm* pForm); // 983: 00901b60 (pacote 0xa8; pedido C30)
	void SaveCurrentFocus();
	void ApplySavedFocus();

	std::string m_str983_2c; // 983: +0x2c, montada vazia no construtor 00906bf0 (uso nao lido)
	unsigned long m_unk983_48; // 983: +0x48, o construtor nao toca
	std::list<sChatSlot> m_chatSlotList; // 983: +0x4c

public:
	WRect m_dlgRect;
	WRect m_alarmRect;

protected:
	std::map<unsigned long, sUserInfoTime> m_userInfoTimeMap;
	std::list<MSNServerInfo> m_serverList;
	FrMessengerDlg* m_pMessengerDlg;
	float m_notifyTime;
	float m_checkTime;
	bool m_bNotify;
	bool m_bGameFocus;
	bool m_bAutoAway;
	eConnectStatus m_complete;
	bool m_bWaitServerList;
	int m_curServerIndex;
	MSN::eStatusType m_myStatus;
	int m_popupIndex;
	bool m_bFriendOnExpand;
	bool m_bFriendOffExpand;
	bool m_bUnknown96;
	std::list<unsigned long> m_focusList;
	NewsReader* m_pNewsReader;
	FrGuildNoticeDlg* m_pGuildNoticeDlg;
	unsigned long m_unknownAC;
	unsigned long m_unknownB0;
	bool m_bEnableInvite;
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbSavecurrentfocusFunclets(); // HACK: EH funclets of the naked SaveCurrentFocus (nakedify)
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbRecvChatImpl(); // HACK: naked body of RecvChat (aliased; by-value std::string parameter)
	static void __cdecl
	RbRecvchatFunclets(); // HACK: EH funclets of the naked RecvChat (nakedify)
#endif
};

inline CMessengerInfo* MESSENGER()
{
	return CMessengerInfo::Instance();
}
