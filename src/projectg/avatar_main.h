#pragma once

#ifdef REBANG_AVATAR_MAINUI_CPP
// the UI half of ntAvatarChatMain, as avatar_mainui.cpp was written against it

#include "taskmain.h"
#include "scenemanager.h"

class Bitmap;
class FrArea;
class FrButton;
class FrComboBox;
class FrEdit;
class FrForm;
class FrFrame;
class FrWnd;
class FrContextMenuCtrl;
class FrNoteDlg;
class FrTradeDlg;
class FrReportDlg;
class FrEmoticonDlg;
class FrJukeBoxDlg;
class FrAvatarTipDlg;
class FrAvatarChatLogDlg;
class FrAvatarUserListDlg;

// TODO: incomplete (only the UI half, avatar_mainui.cpp, is reconstructed)
class ntAvatarChatMain : public CTaskMain, public CRenderFuncPtr
{
	DECLARE_OBJECT(ntAvatarChatMain)

	ntAvatarChatMain();
	virtual ~ntAvatarChatMain();

	virtual void OnInit();
	virtual void OnPreLoadInit();
	virtual void OnDestroy();
	virtual void Display();
	virtual void DoReLoad();
	// 983 007b0d20 (slot 26, depois do DoReLoad; pedido C58.2): a versao da sala de avatar do
	// CLobbyMain::OnToppage_OneDayQuestDown983 (pacote 0x151); o desktop RF chama por [vtable+0x68] (005fb6d0).
	virtual void OnToppage_OneDayQuestDown983();
	virtual void OnPreserveBack(const char* nextTask);
	virtual void CloseAllDialogs();

public:
	void PlaceUserListBtn983(float w); // D482 (public no 983: QAEXM)
	static void OnContextMenuFreed(void* menu); // D501: zera m_pRightMenu solto (Lounge, d499-1)

protected:
	void InitUI();
	void ResetFrWndPointers();
	void ProcessUI(float deltaTime);
	void ChangePortraitImage(int index);
	void UpdateRightMenu();
	void PopupRightMenu(int x, int y);
	void ToggleJukeBox();
	void ToggleAvatarChatLog();
	void ToggleAvatarUserList();

	void OnAvatarChatMainInit(int param);
	void OnAvatarChatMainFinish();
	void OnPortraitInit(int param);
	void OnPortraitMaskAreaInit(int param);
	void OnPortraitMaskInit(int param);
	void OnPortraitMaskBtnUp();
	void OnPortraitTipButtonInit(int param);
	void OnPortraitTipButtonBtnUp();
	void OnPortraitJukeBoxButtonAreaInit(int param);
	void OnPortraitJukeBoxButtonInit(int param);
	void OnPortraitJukeBoxButtonBtnUp();
	void OnPortraitChatLogButtonInit(int param);
	void OnPortraitChatLogButtonBtnUp();
	void OnAvatarUserListButtonInit(int param);
	void OnMotionBtnInit983(int param);
	void OnAvatarUserListButtonBtnUp();
	void OnChatFrameInit(int param);
	void OnChatViewInit(int param);
	void OnChatTargetInit(int param);
	void OnChatTargetBtnDown(int param);
	bool OnChatTargetEnterKey(int param);
	void OnChatInputInit(int param);
	bool OnChatInputEnterKey(int param);
	void OnEmoticonInit(int param);
	void OnEmoticonBtnUp();
	void OnLanguageInit(int param);
	void OnReportInit(int param);
	void OnReportBtnUp();
	void OnRightMenuInit(int param);
	void OnRightMenuLBtnDown();
	void OnRightMenuRBtnDown();

	bool OnAvatarTipDlgResult(int result, FrForm* pForm);
	bool OnJukeBoxDlgResult(int result, FrForm* pForm);
	bool OnAvatarChatLogDlgResult(int result, FrForm* pForm);
	bool OnAvatarUserListDlgResult(int result, FrForm* pForm);
	bool OnEmoticonResult(int result, FrForm* pForm);
	bool OnReportResult(int result, FrForm* pForm);
	bool OnNoteDlgResult(int result, FrForm* pForm);
	bool OnAddFriendDlgResult(int result, FrForm* pForm);
	bool OnTradeDlgResult(int result, FrForm* pForm);
	bool OnPasswordDlgResult(int result, FrForm* pForm);

	void OnNoteToFriend();
	void OnAddFriend();
	void OnAvatarInfo();
	void OnFollowAvatar();
	void OnKickAvatar();
	void OnAchievementAvatar983(); // 983: 007b1a80 (pacote 0x157; PKT, frente C)
	void OnOpenTradeShop();
	void OnEnterTradeShop();

	virtual void OnUnderBar_ShopUp();
	virtual void OnUnderBar_MyRoomUp();
	virtual void OnUnderBar_CookieUp();
	virtual void OnUnderBar_RankingUp();

	DECLARE_FRESH_MSGMAP()

protected:
	unsigned long m_unknown1e4[18];
	char m_unknown224[2];
	char m_targetNickName[0x16];
	unsigned long m_targetUid;
	unsigned long m_unknown240[26];
	Bitmap* m_pPortraitBmp[15];
	unsigned long m_unknown2d0[98];
	FrArea* m_pPortrait;
	FrButton* m_pPortraitMask;
	FrButton* m_pJukeBoxBtn;
	FrButton* m_pTipBtn;
	FrButton* m_pChatLogBtn;
	FrButton* m_pUserListBtn;
	FrWnd* m_pWnd4c4; // 983: set to NULL in ResetFrWndPointers (last, before m_pRightMenu), no other use found
	FrForm* m_pDlg4c8; // 983: closed in CloseAllDialogs
	FrFrame* m_pChatFrame;
	FrComboBox* m_pChatTarget;
	FrEdit* m_pChatInput;
	FrButton* m_pEmoticonBtn;
	FrArea* m_pLanguage;
	FrButton* m_pReportBtn;
	FrEdit* m_pChatView;
	FrEmoticonDlg* m_pEmoticonDlg;
	FrReportDlg* m_pReportDlg;
	FrNoteDlg* m_pNoteDlg;
	FrForm* m_pAddFriendDlg;
	FrForm* m_pDlg49c;
	FrForm* m_pPasswordDlg;
	FrJukeBoxDlg* m_pJukeBoxDlg;
	FrTradeDlg* m_pTradeDlg;
	FrAvatarTipDlg* m_pAvatarTipDlg;
	FrAvatarChatLogDlg* m_pChatLogDlg;
	FrAvatarUserListDlg* m_pUserListDlg;
	FrContextMenuCtrl* m_pRightMenu;
	int m_chatViewLines;
	int m_uiHideMode;
	unsigned long m_unknown4c4[1];
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbOnchatinputenterFunclets(); // HACK: EH funclets of the naked OnChatInputEnterKey (nakedify)
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbOnemoticonresultFunclets(); // HACK: EH funclets of the naked OnEmoticonResult (nakedify)
#endif
};
#else
#include <list>

#include "singleton.h"
#include "taskmain.h"
#include "scenemanager.h"
#include "golfdoc.h"
#include "avatar_avatar.h"
#include "../shared/s5/specialprize/specialprizeitem.h"

class WResource;
class FrAvatarChatLogDlg;
class FrAvatarUserListDlg;
class CQuadTree;
class WOverlay;
class ntBalloonText;
enum eSPAVILITYTYPE;

#ifdef REBANG_AVATAR_AVATAR_CPP
#include "balloontext.h"
#else
class ntBalloonTextManager : public WSingleton<ntBalloonTextManager>
{
public:
	void Init();
	void Shutdown();
	void Render();
	void Process(float dt);

private:
	std::list<ntBalloonText*> m_balloonList;
	unsigned char m_unknown34[0x44];
};
#endif

class ntAvatarChatMain : public CTaskMain, public CRenderFuncPtr
{
	DECLARE_OBJECT(ntAvatarChatMain)

public:
	ntAvatarChatMain();
	virtual ~ntAvatarChatMain();
#ifdef REBANG_AVATAR_MAIN_CPP
	// HACK: emission order only (same code as the global one), see avatar_main.cpp
	static void operator delete(void* p);
#endif

	virtual void OnPreLoadInit();
	virtual void OnLoad();
	virtual void OnInit();
	virtual void OnProcess(float);
	virtual void OnDisplay();
	void PlaceUserListBtn983(float w); // D482 (avatar_mainui.cpp)
	virtual void OnDestroy();
	virtual void OnPreserveBack(char const*);
	virtual void OnRestorePreserved();
	virtual void HandleMsg(const MsgObject&);
	virtual void Display();
	virtual void DoReLoad();
	// 983 007b0d20 (slot 26, depois do DoReLoad; pedido C58.2): a versao da sala de avatar do
	// CLobbyMain::OnToppage_OneDayQuestDown983 (pacote 0x151); o desktop RF chama por [vtable+0x68] (005fb6d0).
	virtual void OnToppage_OneDayQuestDown983();
	virtual void CloseAllDialogs();

protected:
	virtual void OnUnderBar_ShopUp();
	virtual void OnUnderBar_MyRoomUp();
	virtual void OnUnderBar_CookieUp();
	virtual void OnUnderBar_RankingUp();
	CQuadTree& GetPVS() { return *m_pPVS; }
	void SetLocalPVS(CQuadTree& pvs) { m_pPVS = &pvs; }
	void CheckUIPosition();
	void PrintText(float, float, char const*, float, int, float, unsigned long);
	void RefreshAllUccClothes();
	void LoadBg(char const*, int);
	void ProcessCamera(float);
	void ToggleTopViewMode();
	void InitUI();
	void ResetFrWndPointers();
	void ProcessUI(float);
	void PopupRightMenu(int, int);
	void OnOpenTradeShop();
	void OnEnterTradeShop();

private:
	DECLARE_FRESH_MSGMAP()

private:
	friend class ntAvatar;

	void StartSpEffect(ntAvatar*, eSPAVILITYTYPE);
	bool CanUseSPItem(eSPAVILITYTYPE);
	bool SpCommand(char const*);
	void ChangePortraitImage(unsigned long);

	unsigned char m_unknown1e4[8];
	CWaveInfo m_waveInfo;
	CRiverInfo m_riverInfo;
	float m_time;
	bool m_b208;
	int m_glowBallTex;
	unsigned char m_b210;
	unsigned char m_unknown211[0x15];
	char m_szPickNick[0x16];
	int m_i23c;
	WTL::CString m_str240;
	WVector m_v244;
	WVector m_v250;
	WVector m_v25c;
	float m_f268;
	float m_f26c;
	float m_f270;
	float m_f274;
	float m_f278;
	WVector m_v27c;
	bool m_bTopView;
	float m_f28c;
	unsigned char m_unknown290[4];
	WVector m_topViewPos;
	bool m_b2a0;
	WTitleFont* m_pTitleFont;
	Bitmap* m_pBitmap[10];
	WOverlay* m_genderIcons[6];
	WOverlay* m_mannerIcons[2];
	WOverlay* m_angelIcons[2];
	WOverlay* m_stateIcons[11];
	WOverlay* m_stateBars[9];
	WOverlay* m_emotiObject;
	int m_shadowTexture;
	unsigned char m_unknown350[0x104 + 0x14]; // D464: +0x14 = m_b454 em 0x4a8 como no 983 (HandleMsg 0x16/0x17)
	bool m_b454;
	unsigned char m_unknown455[11];
	FrButton* m_pBtn460;
	unsigned char m_unknown464[8];
	FrWnd* m_pWnd46c;
	unsigned char m_unknown470[0x48]; // D464: ChatLogDlg em 0x50c ... m_pPVS em 0x544 (983, size 0x548); antes 0x4f0.. sobrepunha os ponteiros de UI do avatar_mainui
	FrAvatarChatLogDlg* m_pChatLogDlg;
	FrAvatarUserListDlg* m_pUserListDlg;
	FrForm* m_pForm4b8;
	int m_i4bc;
	int m_viewMode;
	unsigned long m_ul4c4;
	unsigned char m_curMap;
	unsigned char m_u4c9;
	bool m_b4ca;
	LightSet m_lightset;
	CQuadTree* m_pPVS;
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbNtavatarchatmainFunclets(); // HACK: EH funclets of the naked ~ntAvatarChatMain (nakedify)
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbLoadbgFunclets(); // HACK: EH funclets of the naked LoadBg (nakedify)
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbOnrestorepreservFunclets(); // HACK: EH funclets of the naked OnRestorePreserved (nakedify)
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbSpcommandFunclets(); // HACK: EH funclets of the naked SpCommand (nakedify)
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbOnloadFunclets(); // HACK: EH funclets of the naked OnLoad (nakedify)
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbHandlemsgFunclets(); // HACK: EH funclets of the naked HandleMsg (nakedify)
#endif
};
#endif
