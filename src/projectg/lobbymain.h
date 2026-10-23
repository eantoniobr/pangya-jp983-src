#pragma once

#include <list>
#include <vector>
#include <memory>

#include "../shared/globalgamedefine.h"
#include "../shared/classdefine.h" // 983: IFF_STRUCT::sHairStyle (m_createHair983)
#include "taskmain.h"
#include "treasure.h"
#include "playerdlg.h"
#include "frcombobox.h"

class FrLoginDlg;
class FrJukeBoxDlg;
class FrAvatarMotionDlg;
struct sRoomListDoc983;
class CLobbyRoomSelector983;
class CGrandPrixGameRoomTimerFont;
class CGrandPrixGameRoomTimerBigFont;
class CGrandPrixGameRoomTicketFont;
class CGrandPrixDiffLevelFont;
class FrInviteDlg;
class FrUserListDlg;
class FrDtRoomDlg;
class FrScoreDlg;
class FrPasswordDlg;
class FrTreasureCourse;
class FrEmoticonDlg;
class FrReportDlg;
class FrMailBoxDlg;
class FrEventPrizeDlg;
class FrNewRecordDlg;
class FrParanNickDlg;
class FrCaddieWarningDlg;
class FrEquipDlg;
class ntHolesEventDlg;
class FrPointEventDlg;
class FrMakeRoomDlg;
class FrWorldTourEventDlg;
class FrFindEbortEventDlg;
class FrHalloweenEventDlg;
class FrHalloweenEventGiftDlg;
class FrChristmasEventDlg;
class FrTicketExchangeDlg;
class FrQuickResultDlg;
class FrValEventDlg;
class FrCreateNickDlg;
class FrUseTikiReportDlg; // 983: jp/usetikireportdlg.h (frente C)
class CGaugeBar983;
class FrMissionEventDlg;
class FrBingoEventDlg;
class FrBirthdayEventDlg;
class FrUniteResultDlg;
class FrTreasureGift;
class FrGuildNoticeDlg;
class CPartTidList;
class FrComboBox;
class FrComboCtlEx;
struct sSlotInfo;
struct sRoomInfo;
enum eTopIconID;

extern Fresh* g_pFresh;
extern WMatrix g_camera;
extern bool g_bQuit;

class CLobbyMain : public CTaskMain
{
	DECLARE_OBJECT(CLobbyMain)

	enum roomSort_t
	{
		ROOM_SORT_NO,
		ROOM_SORT_CATE,
		ROOM_SORT_TITLE,
		ROOM_SORT_GAMETYPE,
		ROOM_SORT_HOLE,
		ROOM_SORT_COURSE,
		ROOM_SORT_STATE
	};
	enum userSort_t
	{
		USER_SORT_GENDER,
		USER_SORT_LEVEL,
		USER_SORT_GUILD,
		USER_SORT_NICK
	};
	enum eBtnDir
	{
	};

	CLobbyMain();
	virtual ~CLobbyMain();

public:
	virtual void OnLoad();
	virtual void OnDestroy();
	virtual void OnDisplay();
	virtual void OnPreLoadInit();
	virtual void OnInit();
	virtual void OnProcess(float);
	virtual void HandleMsg(const MsgObject&);
	void OpenSingleModeStarter983(); // 00595f60: "single_mode_start" (botao do modo solo do RFLobbyDesktop 005f7540, frente B)

protected:
	void AnimateWebEventButton(float);
	void OnToppage_Destroy();
	void OnToppage_GameUp();
	bool OnValEventDlgResult(int, FrForm*);
	void OnToppage_TreasureIslandLBDown();
	void OnToppage_ServerUp();
	void OnServer_Init(int);
	bool OnNewRecordDlgResult(int, FrForm*);
	void OnBlank_Init(int);
	void OnSecond_Pwd_Init(int);
	void OnSecond_Pwd_Finish();
	bool OnRemoveFriendDlgResult(int, FrForm*);
	bool OnEventDlgResult(int, FrForm*);
	bool OnMailBoxDlgResult(int, FrForm*);
	bool OnScoreDlgResult(int, FrForm*);
	bool OnResultDlg_Report(int, FrForm*);
	bool OnUserListDlgResult(int, FrForm*);
	bool OnNotifyQuitDlgResult(int, FrForm*);
	bool OnCreateInfoResult(int, FrForm*);
	bool OnReportDlgResult(int, FrForm*);
	bool OnUIHackDlgResult(int, FrForm*);
	bool OnMapSelectDlgResult(int, FrForm*);
	bool OnHolesEventDlgResult(int, FrForm*);
	bool OnPointEventDlgResult(int, FrForm*);
	bool OnWorldTourEventDlgResult(int, FrForm*);
	bool OnFindEbortEventDlgResult(int, FrForm*);
	bool OnHalloweenEventDlgResult(int, FrForm*);
	bool OnChristmasEventDlgResult(int, FrForm*);
	bool OnChristmasSockEventDlgResult(int, FrForm*);
	bool OnTicketExchangeDlgResult(int, FrForm*);
	bool OnFirstTutorialDlgResult(int, FrForm*);
	bool OnQuickResultDlgResult(int, FrForm*);
	void ResetControl();
	void RoomList_LoadRoomImages();
	void OnRoomList_Destroy();
	void RoomList_SortRoomList(roomSort_t, int);
	void RoomList_SetCateTabBtn();
	void RoomList_SortUserList(userSort_t);
	void SetControlsRoomListSort(int);
	void OnChatTargetBtnDown(int);
	bool OnChatTargetEnterKey(int);
	void OnGameRoom_Destroy();
	void InitControlsSelectedUserInfo();
	void OnGameRoom_CharSelDown();
	void OnGameRoom_CaddieSelDown();
	void OnGameRoom_ClubSelDown();
	void OnGameRoom_AztecSelDown();
	void OnGameRoom_MascotSelDown();
	void EnableSettingButton(bool);
	void OnGameRoom_UserListInit(int);
	void OnGameRoomExt_Destroy();
	void OnGameRoomExtRes_Destroy();
	void OnCreate_Init(int);
	void OnCreate_Finish();
	void OnCreate_Destroy();
	bool OnCreateNickResult(int, FrForm*);
	bool OnMissionEventResult(int, FrForm*);
	bool OnBingoEventResult(int, FrForm*);
	bool OnKoohBirthdayEventDlg(int, FrForm*);
	void JoinOtherServerRoom();
	float GetTopPageBtnRect();
	void OpenEventPrizeForm(unsigned char);
	void OnToppage_GameInit(int);
	void OnToppage_FamilyInit(int);
	void OnToppage_PangysStudyInit(int);
	void OnToppage_PremiumServiceInit983(int); // 00596290
	void OnToppage_PremiumEndNoticeInit983(int); // 00596180
	void OnToppage_NoticeInit(int);
	void OnToppage_OneDayQuestInit983(int); // 00593900
	void OnToppage_OneDayQuestDown983(); // 00593990
	void OnToppage_RankUpInit983(int); // 005949d0
	void OnToppage_RankUpDown983(); // 00594a90
	void OnToppage_GuildRankInit983(int); // 00594b00
	void OnToppage_GuildRankDown983(); // 00594bb0
	void OnToppage_MotionBtnInit983(int); // 00ab7430
	void OnToppage_JukeboxBtnInit983(int); // 00ab76b0
	void OnToppage_JukeboxBtnUp983(); // 00ab8620 -> 00ab7820
	void OnToppage_MotionBtnUp983(); // 00ab8600
	void SetMotionBtnOnImg983(); // 00ab3620
	void OpenMotionDlg983(); // 00ab8430
	bool OnMotionDlgResult983(int result, FrForm* pForm); // 00ab7610
	bool OnJukeBoxDlgResult983(int result, FrForm* pForm); // 00ab36a0
	void AnchorMotionBtn983(); // 00ab45c0
	void AnchorJukeboxBtn983(); // 00ab4620
	void ReanchorRightIcons983(); // 00ab7780 (OnProcess)
	void OnToppage_NoticeUp();
	void OnToppage_PcbangInit(int);
	void OnToppage_Event1Init(int);
	void OnToppage_Event1Up();
	void OnToppage_NewInit(int);
	void OnToppage_NewOwnerDraw(int);
	void OnToppage_PointEventInit(int);
	void OnToppage_ValEventInit(int);
	void OnToppage_ValEventDown();
	void OnToppage_WorldTourEventInit(int);
	void OnToppage_WorldTourEventDown();
	void OnToppage_FindEbortEventInit(int);
	void OnToppage_FindEbortEventDown();
	void OnToppage_Halloween2007Init(int);
	void OnToppage_Halloween2007EvenDown();
	void OnToppage_Christmas2007EventInit(int);
	void OnToppage_Christmas2007EventDown();
	void OnToppage_TicketExchangeInit(int);
	void OnToppage_TicketExchangeDown();
	void OnToppage_MissionEventInit(int);
	void OnToppage_MissionEventDown();
	void OnToppage_BingoEventInit(int);
	void OnToppage_BingoEventDown();
	void OnToppage_KoohBirthdayEventInit(int);
	void OnToppage_KoohBirthdayEventDown();
	void OnToppage_TreasureIslandInit(int);
	void OnToppage_ServerInit(int);
	void OnServer_Finish();
	bool OnLoginDlgResult(int, FrForm*);
	bool OnVoteDlgResult(int, FrForm*);
	bool OnItemEquipResult(int, FrForm*);
	bool OnEmoticonResult(int, FrForm*);
	bool OnQuickStartDlgResult(int, FrForm*);
	void OpenLayout(const char*);
	void OpenCaddieInfo(const sCaddieInfo&);
	void OnRoomList_RoomListLDown();
	void OnRoomList_RoomSortNoInit(int);
	void OnRoomList_RoomSortNoDown();
	void OnRoomList_RoomSortNoOwnerDraw(int);
	void OnRoomList_RoomSortCateAll_BtnInit(int);
	void OnRoomList_RoomSortCateVS_BtnInit(int);
	void OnRoomList_RoomSortCateMass_BtnInit(int);
	void OnRoomList_RoomSortCateBattle_BtnInit(int);
	void OnRoomList_RoomSortCateChat_BtnInit(int);
	void OnRoomList_RoomSortHoleInit(int);
	void OnRoomList_RoomSortHoleDown();
	void OnRoomList_RoomSortHoleOwnerDraw(int);
	void OnRoomList_RoomSortCourseInit(int);
	void OnRoomList_RoomSortCourseDown();
	void OnRoomList_RoomSortCourseOwnerDraw(int);
	void OnRoomList_RoomSortStateInit(int);
	void OnRoomList_RoomSortStateDown();
	void OnRoomList_RoomSortStateOwnerDraw(int);
	void OnRoomList_RoomSortCateVS_ListInit(int);
	void OnRoomList_RoomSortCateVS_ListOwnerDraw(int);
	void OnRoomList_RoomSortCateMass_ListInit(int);
	void OnRoomList_RoomSortCateMass_ListOwnerDraw(int);
	void OnRoomList_RoomSortCateBattle_ListInit(int);
	void OnRoomList_RoomSortCateBattle_ListOwnerDraw(int);
	void OnRoomList_MakeRoomInit(int);
	void OnRoomList_GuildInfoInit(int);
	void OnRoomList_UserListLBtnUp();
	void OnRoomList_UserListRBtnUp();
	void OnRoomList_UserSortGenderInit(int);
	void OnRoomList_UserSortGenderUp();
	void OnRoomList_UserSortGenderOwnerDraw(int);
	void OnRoomList_UserSortLevelInit(int);
	void OnRoomList_UserSortLevelUp();
	void OnRoomList_UserSortLevelOwnerDraw(int);
	void OnRoomList_UserSortGuildInit(int);
	void OnRoomList_UserSortGuildUp();
	void OnRoomList_UserSortGuildOwnerDraw(int);
	void OnRoomList_UserSortNickInit(int);
	void OnRoomList_UserSortNickUp();
	void OnRoomList_UserSortNickOwnerDraw(int);
	void OnChatBgInit(int);
	void OnChatBgOwnerDraw(int);
	void ToggleChatBtn(bool);
	void OnLanguageInit(int);
	void OnChatInputInit(int);
	void OnReportBtnUp();
	void OnEmoticonInit(int);
	void OnEmoticonBtnUp();
	void OnChannelRoomCloseBtnInit(int);
	void OnGameRoom_BackGroundInit(int);
	void OnGameRoom_Pet0Init(int);
	void OnGameRoom_Pet1Init(int);
	void OnGameRoom_Pet2Init(int);
	void OnGameRoom_Pet3Init(int);
	void Banish();
	void OnGameRoom_RoomUserInit(int);
	void OnGameRoom_MapBgInit(int);
	void SendChangedUserInfo();
	void DrawFrameSelectedUserInfo(WRect);
	void OnGameRoom_CharInit(int);
	void OnGameRoom_CharDown();
	void OnGameRoom_CaddieInit(int);
	void OnGameRoom_CaddieDown();
	void OnGameRoom_ClubInit(int);
	void OnGameRoom_ClubDown();
	void OnGameRoom_AztecInit(int);
	void OnGameRoom_AztecDown();
	void OnGameRoom_MascotInit(int);
	void OnGameRoom_MascotDown();
	void OnGameRoom_EquipItemInit(int);
	void OnGameRoom_EquipItemOwnerDraw(int);
	void OnGameRoom_CharSelInit(int);
	void OnGameRoom_CaddieSelInit(int);
	void OnGameRoom_ClubSelInit(int);
	void OnGameRoom_AztecSelInit(int);
	void OnGameRoom_MascotSelInit(int);
	void OnGameRoom_StartTipInit(int);
	void OnGameRoom_ReadyTipInit(int);
	void OnGameRoom_StartInit(int);
	void OnGameRoom_ReadyInit(int);
	void OnGameRoom_RoomOptionInit(int);
	void OnGameRoom_MapPrevInit(int);
	void OnGameRoom_MapNextInit(int);
	void OnGameRoom_MapLockInit(int);
	void OnGameRoom_ChangeTeamBtnInit(int);
	void OnGameRoom_PowerBarInit(int);
	void OnGameRoom_ControlBarInit(int);
	void OnGameRoom_AccuracyBarInit(int);
	void OnGameRoom_SpinBarInit(int);
	void OnGameRoom_CurveBarInit(int);
	void OnGameRoom_PowerEditInit(int);
	void OnGameRoom_ControlEditInit(int);
	void OnGameRoom_AccuracyEditInit(int);
	void OnGameRoom_SpinEditInit(int);
	void OnGameRoom_CurveEditInit(int);
	void OnGameRoom_ScoreInit(int);
	void OnGameRoomExt_CountdownInit(int);
	void OnGameRoomExt_FrameInit(int);
	void OnGameRoomExt_GuildTab1Init(int);
	void OnGameRoomExt_GuildTab2Init(int);
	void OnGameRoomExt_TeamTab1Init(int);
	void OnGameRoomExt_TeamTab2Init(int);
	void OnGameRoomExt_TeamNumInit(int);
	void OnGameRoomExt_GuildInviteInit(int);
	void OnGameRoomExtRes_RoomUserRankLBtnUp();
	void OnGameRoomExtRes_RoomGuildRankLBtnUp();
	void OnGameRoomExt_UserInfoInit(int);
	void OnCreate_CharInit(int);
	void OnCreate_CharPrevInit(int);
	void OnCreate_CharNextInit(int);
	void OnCreate_HairInit(int);
	void OnCreate_HairPrevInit(int);
	void OnCreate_HairNextInit(int);
	void OnCreate_ShirtsInit(int);
	void OnCreate_ShirtsPrevInit(int);
	void OnCreate_ShirtsNextInit(int);
	void OnCreate_DescInit(int);
	void OnCreate_WarningInit(int);
	void On_PowerBarInit(int);
	void On_ControlBarInit(int);
	void On_AccuracyBarInit(int);
	void On_SpinBarInit(int);
	void On_CurveBarInit(int);
	void OnToppage_TopIcon1Init(int);
	void OnToppage_TopIcon1Up();
	void OnToppage_TopIcon2Init(int);
	void OnToppage_TopIcon2Up();
	void OnToppage_TopIcon3Init(int);
	void OnToppage_TopIcon3Up();
	void OnToppage_TopIcon4Init(int);
	void OnToppage_TopIcon4Up();
	void OnToppage_TopIcon5Init(int);
	void OnToppage_TopIcon5Up();
	void OnToppage_TopIcon6Init(int);
	void OnToppage_TopIcon6Up();
	void ProcessLobbyBgCamera(float);
	void ProcessAdministrator(float);
	void OpenPCBangNoticeForm();
	bool NeedsChangeNick();
	void OpenNoteForm();
	void OnToppage_Init(int);
	void OnToppage_Finish();
	void OnToppage_PangysStudyUp();
	void OnToppage_RentalExpiredAlramInit(int);
	void OnFirstConnectOwnerDraw(int);
	void OnToppage_PointEventDown();
	virtual void CloseAllDialogs();
	void OnLogin_Init(int);
	void OnLogin_Finish();
	void OnLogin_Copyright1Init983(int); // 983: 005934b0 ("LOGIN.copyright1")
	void OnLogin_Copyright2Init983(int); // 983: 005935c0 ("LOGIN.copyright2")
	void OnBlank_Finish();
	bool OnGuildNoticeDlgResult(int, FrForm*);
	bool OnRoomExt30sResQuitDlgResult(int, FrForm*);
	bool OnPCBangDlgResult(int, FrForm*);
	void OpenPremiumService983(); // 00596370: "TOPPAGE.PremiumService" -> notice_popup + premiumservice.ini
	bool OnPremiumServiceDlgResult983(int, FrForm*); // 00ab6860
	bool OnCaddieWarningDlgResult(int, FrForm*);
	void EnableRoomEnterControls(bool);
	void OpenInformation(unsigned long);
	void OpenCreateInfo(unsigned long, const char*);
	bool LatestVersion();
	void OnRoomList_Finish();
	void OnRoomList_RoomListOwnerDraw(int);
	void OnRoomList_RoomListRUp();
	void OnRoomList_GuildInfoLButtonUp();
	void OnRoomList_UserListOwnerDraw(int);
	void OnChatWndBtnInit(int);
	void OnChatWndBtnUp();
	void ReLoadHoleItem();
	bool OnChatInputEnterKey(int);
	void OnChatTargetInit(int);
	void OnGameRoom_Init(int);
	void OnGameRoom_RoomUserDClick();
	void OnGameRoom_TitleInit(int);
	void OnGameRoom_EventOwnerDraw(int);
	void OnGameRoom_MapGaugeInit(int);
	void OpenNewRecordForm();
	void OnGameRoom_EquipItemDown();
	void OnGameRoom_RoomOptionBtnUp();
	void OnGameRoom_MapInit(int);
	void OnGameRoom_MapPrevBtnUp();
	void OnGameRoom_MapNextBtnUp();
	void OnGameRoom_MapHoleComboInit(int);
	void OnGameRoom_MapHoleComboDown();
	void OnGameRoom_UserListBtnUp();
	void OnGameRoomExt_Init(int);
	void OnGameRoomExt_TeamNumOwnerDraw(int);
	void OnGameRoomExtRes_GuildScoreGaugeInit(int);
	void OnGameRoomExt_GuildNumInit(int);
	void OnGameRoomExt_GuildNumOwnerDraw(int);
	void OnGameRoomExtRes_RoomUserRankTabInit(int);
	void OnGameRoomExtRes_Init(int);
	void OnGameRoomExtRes_Finish();
	bool SetFirstChar(CPartTidList*);
	void OnCreate_CreateBtnUp();
	bool OnCreateConfirmResult983(int, FrForm*); // 00ab6fc0: "notify_yesno" do OnCreate_CreateBtnUp; com 1 manda o 0x8
	void OnCreate_CharacterListInit983(int); // 00ab8850: "CREATE.character_list" (lista dos personagens do Character.iff)
	void OnCreate_CharacterListDown983(int); // 00abc0e0: escolhe o personagem da linha
	void OnCreate_CharacterListOwnerDraw983(int); // 00ab70b0: rosto + moldura + cursor
	void OnCreate_DrawAreaInit983(int); // 00ab4330
	void OnCreate_DrawAreaOwnerDraw983(int); // 00ab4380: figura do cabelo e os 5 medidores com o valor
	void OnCreate_CharNameImageInit983(int); // 00ab82a0: "CREATE.char_name_image" na "character_name_pos" do Lua
	void SelectCreateChar983(unsigned char index); // 00abbb90: troca o personagem (0/1/3 -> 11/12/14), boneco e medidores
	bool OnUseTikiReportResult983(int, FrForm*); // 00ab2fa0: resultado da "notify_tiki"
	bool OnSingleModeStartResult983(int, FrForm*); // 00abaa10: resultado da "single_mode_start"; FrYES manda o 0x8 da sala solo
	bool OnRoomListDlgResult983(int, FrForm*); // 00ab6620: resultado da "roomlist"/"grandprix_list"; manda 0x82/0x177
	void OpenGameRoomDlg983(int state); // 00ab6cc0: HandleMsg 0x8b casos 6..0xb; "gameroom_main"/"gameroom_single" pelo estado 3..8
	bool OnGameRoomDlgResult983(int, FrForm*); // 00ab6700: resultado da janela da sala; sai da sala (SendExitRoom983/SendExitGPRoom983)
	bool OnMatchingDlgResult(int, FrForm*);
	void OnToppage_UCCShopBtnUp();
	void OnToppage_CardShopBtnUp();
	void ProcessLobbyPetSync(float);
	void OpenCaddieWarningForm();
	void OnToppage_FamilyUp();
	void OnToppage_PcbangUp();
	bool OnMatchRoomCreateDlgResult(int, FrForm*);
	bool OnMakeRoomDlgResult(int, FrForm*);
	bool OnApproachGiftDlgResult(int, FrForm*);
	bool OnResultDlgResult(int, FrForm*);
	bool OnRoomExtResQuitDlgResult(int, FrForm*);
	bool OnDtRoomDlgResult(int, FrForm*);
	bool OnInviteDlgResult(int, FrForm*);
	bool OnPasswordDlgResult(int, FrForm*);
	bool OnParanNickChangeResult(int, FrForm*);
	void SetStartBtn(bool);
	void SortRank();
	void OnRoomList_RoomListInit(int);
	void OnRoomList_MakeRoomUp();
	void RoomList_FilterRoomList(roomSort_t, int);
	void OnGameRoom_RoomUserLBtnUp();
	void OpenGameExtResQuitForm();
	void OnGameRoom_AztecOwnerDraw(int);
	void OnGameRoom_AztecSelOwnerDraw(int);
	void OnGameRoom_StartBtnUp();
	void OnGameRoom_ReadyBtnUp();
	void OnGameRoom_MapBtnUp();
	void OnGameRoom_ChangeTeamBtnUp();
	void OnGameRoom_ScoreBtnUp();
	void OnGameRoomExt_RoomUserOwnerDraw(int);
	void OnGameRoomExt_ResCloseBtnUp();
	void OnGameRoomExtRes_RoomUserRankInit(int);
	void OnGameRoomExtRes_RoomGuildRankInit(int);
	void OnGameRoomExtRes_RoomGuildRankRBtnUp();
	void ProcessDialogKeyboard(float);
	void ProcessLobbyUI(float);
	void ProcessAutoStart(float);
	void _RefreshUccClothes(sSlotInfo*, unsigned long, const char*);
	void OpenParanNickChange();
	bool OnRoomUseReportDlgResult(int, FrForm*);
	bool OnLevelupFormResult(int, FrForm*);
	void HidePet(unsigned long);
	void SetRoomCharControl(eBtnDir);
	void SetLevelBar();
	void OnRoomList_RoomListDClick();
	void OnRoomList_RoomSortCateAll_BtnDown();
	void OnRoomList_RoomSortCateVS_BtnDown();
	void OnRoomList_RoomSortCateMass_BtnDown();
	void OnRoomList_RoomSortCateBattle_BtnDown();
	void OnRoomList_RoomSortCateChat_BtnDown();
	void OnRoomList_RoomSortCateVS_ListLUp();
	void OnRoomList_RoomSortCateMass_ListLUp();
	void OnRoomList_RoomSortCateBattle_ListLUp();
	void OnRoomList_UserListInit(int);
	void ResetControlsRoomListSort(float);
	void OnGameRoom_RoomUserRBtnUp();
	void OpenUseReportForm();
	void OnGameRoom_CharOwnerDraw(int);
	void OnGameRoom_CaddieOwnerDraw(int);
	void OnGameRoom_ClubOwnerDraw(int);
	void OnGameRoom_MascotOwnerDraw(int);
	void OnGameRoom_CharSelOwnerDraw(int);
	void OnGameRoom_CaddieSelOwnerDraw(int);
	void OnGameRoom_ClubSelOwnerDraw(int);
	void OnGameRoom_MascotSelOwnerDraw(int);
	void OnGameRoomExtRes_RoomUserRankRBtnUp();
	void OnGameRoomExt_UserInfoLBtnUp();
	void RefreshAllUccClothes();
	void OnToppage_RentalExpiredAlramUp();
	void ShowPet(unsigned long);
	void SetRoomCaddieControl(eBtnDir);
	void RemakeTeam(bool);
	void OnRoomList_ChatViewInit(int);
	void OnGameRoom_Finish();
	void GameExtResQuit();
	void SetRoomControls(bool);
	void OnRoomList_Init(int);
	void OnGameRoom_RoomUserOwnerDraw(int);
	void OnGameRoomExt_Finish();
	void OnCreatePetInit(int);
	void OnCreatePetOwnerDraw();
	void OnCreate_CharBtnUp();
	void OnCreate_HairPrevBtnUp();
	void OnCreate_HairNextBtnUp();
	void OnCreate_ShirtsPrevBtnUp();
	void OnCreate_ShirtsNextBtnUp();
	int GetMedalIndex(unsigned long);
	void OnGameRoomExt_GuildInviteLBtnUp();
	void OnGameRoomExtRes_RoomUserRankOwnerDraw(int);
	void OnGameRoomExtRes_RoomGuildRankOwnerDraw(int);
	void MakeRoomUserList();
	void OnGameRoomExt_RoomUserInit(int);

private:
	void CheckTikiReport(const char*);

	DECLARE_FRESH_MSGMAP()

protected:
	// s112: campos na ordem do 983 (sizeof 0x7a4; out/F3.5/s112/RELATORIO.md). O 983 tirou do CLobbyMain as telas ROOMLIST/GAMEROOM
	// (FrRoomListDlg/FrGameRoomDlg da frente B): os campos do 645 sem lugar no 983 ficam no apêndice depois de 0x7a4.
	int m_topBtnIndex; // 218
	unsigned long m_reserved1e4; // 21c
	FrButton* m_pToppageGame; // 220
	FrButton* m_pToppageFamily;
	FrButton* m_pToppagePangyaStudy;
	FrWnd* m_pToppageReserved;
	FrButton* m_pToppageNotice; // 230
	FrButton* m_pToppageOneDayQuest; // 234: "TOPPAGE.oneday_quest" (00593900); nome meu
	FrButton* m_pToppageServer;
	FrButton* m_pToppagePcbang;
	FrButton* m_pToppageEvent1; // 240
	FrButton* m_pToppagePointEvent;
	FrButton* m_pToppageWorldTourEvent;
	FrButton* m_pToppageFindEbortEvent;
	FrButton* m_pToppageHalloween2007Event; // 250
	FrButton* m_pToppageChristmas2007Event;
	FrButton* m_pToppageTicketExchange;
	FrButton* m_pToppageMissionEvent;
	FrButton* m_pToppageBingoEvent; // 260
	FrButton* m_pToppageKoohBirthdayEvent; // 264: sem uso no 983 (o lugar ficou)
	FrButton* m_pToppageValEvent; // 268: idem
	FrButton* m_pToppageTreasureIsland; // 26c
	FrButton* m_pToppageChristmasSockEvent; // 270: sem uso no 983
	FrButton* m_pToppagePremiumService983; // 274: "TOPPAGE.PremiumService" (Init 00596290)
	FrWnd* m_pToppagePremiumEndNotice983; // 278: "TOPPAGE.premium_service_end_notice" (Init 00596180)
	unsigned long m_unk983_27c; // 27c, 280: zerados no ResetControl 00ab3120 (entre family e pangyastudy); 00ab7a70, 00597160
	unsigned long m_unk983_280;
	unsigned long m_unk983_284[4]; // 284..290: gravados pelo Init 00596180 (premium_service_end_notice)
	FrArea* m_pToppageNew; // 294 ("new_2", 645 0x274)
	Bitmap* m_pLoginBmp[3]; // 298
	Bitmap* m_pNewBmp; // 2a4
	void* m_pGuildNoticeObj; // 2a8
	FrForm* m_pGuildNoticeDlg; // 2ac
	bool m_bCaddieWarning; // 2b0
	sCaddieInfo m_caddieWarning[12]; // 2b1 (memset 0x12c no construtor)
	float m_bgCameraDir; // 3e0
	bool m_bBgCameraPause; // 3e4
	int m_bgCameraStep; // 3e8 (983 00ab5be0)
	float m_bgCameraTime; // 3ec
	float m_bgCameraDuration; // 3f0
	bool m_bLoginBlock; // 3f4
	float m_autoStartTime; // 3f8
	bool m_bAutoStart; // 3fc
	unsigned long m_reserved3b0; // 400
	WRect m_event1Rect; // 404
	float m_event1Dir; // 414
	unsigned long m_reserved3cc; // 418
	FrLoginDlg* m_pLoginDlg; // 41c
	FrInviteDlg* m_pInviteDlg; // 420
	FrUserListDlg* m_pUserListDlg; // 424 (pela ordem do ResetControl; sem outro uso no 983)
	unsigned long m_unk983_428; // 428: zerado no ResetControl (dtroom/score do 645?)
	FrPasswordDlg* m_pPasswordDlg; // 42c
	FrNoticeDlg* m_pPCBangNoticeDlg; // 430
	unsigned long m_reserved418; // 434
	FrForm* m_pPremiumServiceDlg983; // 438: aberta pelo "TOPPAGE.PremiumService" LBUTTONDOWN 00596370
	FrEquipDlg* m_pEquipDlg; // 43c
	FrMailBoxDlg* m_pMailBoxDlg; // 440
	FrEventPrizeDlg* m_pEventPrizeDlg[6]; // 444
	FrNewRecordDlg* m_pNewRecordDlg; // 45c
	FrParanNickDlg* m_pParanNickDlg; // 460
	FrCaddieWarningDlg* m_pCaddieWarningDlg; // 464
	FrUseTikiReportDlg* m_pUseTikiReportDlg983; // 468: "notify_tiki" (HandleMsg 0x8b caso 0xc 00abcc8a; resultado 00ab2fa0)
	ntHolesEventDlg* m_pHolesEventDlg; // 46c (OnToppage_Event1Up 00596480)
	FrPointEventDlg* m_pPointEventDlg; // 470
	unsigned long m_unk983_474; // 474: zerado no construtor
	FrMakeRoomDlg* m_pMakeRoomDlg; // 478
	unsigned long m_reserved46c; // 47c
	FrWorldTourEventDlg* m_pWorldTourEventDlg; // 480
	FrFindEbortEventDlg* m_pFindEbortEventDlg;
	FrHalloweenEventDlg* m_pHalloweenEventDlg;
	FrHalloweenEventGiftDlg* m_pHalloweenEventGiftDlg;
	FrChristmasEventDlg* m_pChristmasEventDlg; // 490
	FrTicketExchangeDlg* m_pTicketExchangeDlg;
	FrForm* m_pQuickStartDlg;
	FrQuickResultDlg* m_pQuickResultDlg;
	FrForm* m_pReservedDlg490; // 4a0
	FrCreateNickDlg* m_pCreateNickDlg; // 4a4
	FrMissionEventDlg* m_pMissionEventDlg; // 4a8
	FrBingoEventDlg* m_pBingoEventDlg; // 4ac
	// 4b0..5d7: sem tipo ainda. Usos no 983: 4b0 ("motion_btn_start" Init 00ab7430, 00ab3620/00ab3660/00ab8430), 4b4, 4b8 (Banish),
	// 4bc (ResetControl), 4c0 (00595280), 4c4 (construtor), 4c8 (byte, construtor), 568 (byte, ProcessLobbyPetSync), 5d0 (byte, 00ab5e00)
	FrButton* m_pMotionBtn983; // 4b0: "TOPPAGE.motion_btn_start" (Init 00ab7430; ancorado a direita por 00ab45c0)
	FrAvatarMotionDlg* m_pMotionDlg983; // 4b4: janela das emocoes (00ab8430 abre, 00ab4500 fecha)
	sRoomListDoc983* m_pRoomListDoc983; // 4b8: CContentsDoc::GetContainer(0xa5) (OnPreLoadInit 00ab9800)
	unsigned char m_unk983_4bc[0x5d8 - 0x4bc];
	FrEdit* m_pCreateChar; // 5d8 (645 0x970)
	FrEdit* m_pCreateDesc;
	unsigned char m_createCharType; // 5e0
	FrEdit* m_pCreateHair;
	unsigned char m_createHairColor; // 5e8
	FrEdit* m_pCreateShirt;
	unsigned char m_createShirtColor; // 5f0
	FrGaugeBar* m_pStatBar[5]; // 5f4: CREATE.powerbar..curvebar (On_PowerBarInit 00ab40b0)
	FrStatic* m_pStatEdit[5]; // 608 (zerados no construtor)
	FrButton* m_pToppageRankUp983; // 61c: "TOPPAGE.rankup" (Init 005949d0)
	FrButton* m_pToppageWebEvent983[2]; // 620, 624: "TOPPAGE.WebEvent1/2" (Init 00597ae0 / 00597c50)
	FrButton* m_pToppageGuildRank983; // 628: "TOPPAGE.guildrank" (Init 00594b00)
	unsigned long m_unk983_62c; // 62c: 00597820 (chamada no construtor)
	// 630: cabelos de cada personagem (HairStyle.iff sem os de cash e com preço < 10000; índice = cCharID), refeitos no
	// OnCreate_Init 00abaf40; m_createHairColor é o índice no vetor do m_createCharType (construtor 00ab78d0, destrutor 00aba1f0)
	std::vector<IFF_STRUCT::sHairStyle> m_createHair983[15];
	FrListBox* m_pCreateCharacterList983; // 720: "CREATE.character_list" (Init 00ab8850)
	FrArea* m_pCreateCharNameImage983; // 724: "CREATE.char_name_image" (Init 00ab82a0)
	WPoint m_hairColorPos983; // 728: "hair_color_pos" do char_select_free.lua (OnCreate_Init 00abaf40; "CREATE.draw_area")
	WPoint m_statusPos983; // 730: "status_pos" (origem dos 5 medidores)
	CGaugeBar983* m_pStatGauge983[5]; // 738..748: medidores "chselect_gauge_%d.tga" (OnCreate_Init 00abaf40, OnCreate_Destroy 00ab9670)
	bool m_motionBtnClicked983; // 74c: "motion_btn_start" LBUTTONUP 00ab8600 e fim da janela 00ab7610
	WRect m_motionBtnRect983; // 750..75c: retangulo do "motion_btn_start" no recurso (base 800 de largura; Init 00ab7430)
	WRect m_jukeboxBtnRect983; // 760..76c: retangulo do "portrait_jukeboxbtn" no recurso (Init 00ab76b0)
	FrButton* m_pToppageJukeboxBtn983; // 770: "TOPPAGE.portrait_jukeboxbtn" Init 00ab76b0
	FrJukeBoxDlg* m_pJukeBoxDlg983; // 774: "jukeboxdlg" (00ab7820 abre; 00ab36a0 zera)
	CLobbyRoomSelector983* m_pRoomSelector983; // 778: zerado no construtor; OnPreLoadInit 00ab9800 (new 0x24, 005a0780)
	unsigned long m_unk983_77c; // 77c: último do ResetControl
	FrForm* m_pGameRoomDlg983; // 780: "gameroom_main"/"gameroom_single" (00ab6cc0; janela da frente B); 00ab2fa0 fecha
	// 784..7a0: fontes do Grand Prix (OnPreLoadInit 00ab9800; titlefontex.h)
	std::tr1::shared_ptr<CGrandPrixGameRoomTimerFont> m_pGPTimerFont983; // 784 (006f5180)
	std::tr1::shared_ptr<CGrandPrixGameRoomTimerBigFont> m_pGPTimerBigFont983; // 78c (006f5240): CGrandPrixClock::m_pFont
	std::tr1::shared_ptr<CGrandPrixGameRoomTicketFont> m_pGPTicketFont983; // 794 (006f5300)
	std::tr1::shared_ptr<CGrandPrixDiffLevelFont> m_pGPDiffLevelFont983; // 79c (006f53c0)
	// 7a4 = sizeof do 983 (push 0x7a4 em 00592fd3)

	// ---- apêndice: campos do 645 sem lugar no CLobbyMain do 983 (saem quando o código do 645 que os usa sair) ----
	float m_newBlinkTime;
	int m_newBlinkCount;
	bool m_bNewBlink;
	bool m_bUseReport;
	FrForm* m_pNotifyDlg;
	unsigned long m_myItemSlot[10];
	FrDtRoomDlg* m_pDtRoomDlg;
	FrScoreDlg* m_pScoreDlg;
	FrTreasureCourse* m_pTreasureCourse;
	FrEmoticonDlg* m_pEmoticonDlg;
	FrReportDlg* m_pReportDlg;
	FrForm* m_pReservedDlg428;
	FrForm* m_pExtResQuitDlg;
	FrForm* m_pUseReportDlg;
	FrValEventDlg* m_pValEventDlg;
	FrBirthdayEventDlg* m_pBirthdayEventDlg;
	FrForm* m_pChristmasSockEventDlg;
	FrListBox* m_pRoomList;
	FrViewer* m_pRoomSortNo;
	unsigned long m_reserved4b4;
	FrButton* m_pRoomSortCateAll;
	FrButton* m_pRoomSortCateVS;
	FrButton* m_pRoomSortCateMass;
	FrButton* m_pRoomSortCateBattle;
	FrButton* m_pRoomSortCateChat;
	FrViewer* m_pRoomSortHole;
	FrViewer* m_pRoomSortCourse;
	FrViewer* m_pRoomSortState;
	FrButton* m_pMakeRoom;
	FrButton* m_pGuildInfo;
	FrListBox* m_pUserList;
	FrViewer* m_pUserSortGender;
	FrViewer* m_pUserSortLevel;
	FrViewer* m_pUserSortGuild;
	FrViewer* m_pUserSortNick;
	FrListBox* m_pRoomSortCateVSList;
	FrListBox* m_pRoomSortCateMassList;
	FrListBox* m_pRoomSortCateBattleList;
	Bitmap* m_pRoomListBoxBmp[3][4];
	Bitmap* m_pRoomSortNoBmp[3];
	Bitmap* m_pRoomSortCateBmp[3];
	Bitmap* m_pRoomSortHoleBmp[3];
	Bitmap* m_pRoomSortCourseBmp[3];
	Bitmap* m_pRoomSortStateUpBmp[3];
	Bitmap* m_pRoomSortStateDnBmp[3];
	Bitmap* m_pGenderBmp[10];
	Bitmap* m_pUserSortGenderBmp[3];
	Bitmap* m_pUserSortLevelBmp[3];
	Bitmap* m_pUserSortGuildBmp[3];
	Bitmap* m_pUserSortNickBmp[3];
	unsigned long m_reserved5d0[3];
	Bitmap* m_pInGameBmp;
	Bitmap* m_pUserSortArrowBmp[2];
	Bitmap* m_pRoomEventBmp;
	Bitmap* m_pRoomEvent02Bmp;
	roomSort_t m_roomSort;
	userSort_t m_userSort;
	bool m_bRoomSortRev;
	bool m_bUserSortRev;
	bool m_bRoomSortDown[4];
	bool m_bUserSortDown[4];
	bool m_bCateSelected;
	float m_roomSortDelay;
	float m_userSortDelay;
	float m_cateListTime[3];
	bool m_bInitSlot;
	float m_guildInviteDelay;
	FrArea* m_pChatBg;
	FrButton* m_pChatWndBtn;
	FrArea* m_pLanguage;
	FrEdit* m_pChatInput;
	FrEdit* m_pChatView;
	FrComboBox* m_pChatTarget;
	FrButton* m_pEmoticon;
	FrArea* m_pPet[4];
	FrViewer* m_pBackGround;
	FrViewer* m_pMapBg;
	FrButton* m_pMap;
	FrWnd* m_pReserved658;
	FrWnd* m_pUnused65c;
	FrButton* m_pMapPrev;
	FrButton* m_pMapNext;
	FrComboCtlEx* m_pMapHoleCombo;
	FrGaugeBarImage* m_pMapGauge;
	FrArea* m_pMapLock;
	FrViewer* m_pChar;
	FrViewer* m_pCaddie;
	FrViewer* m_pAztec;
	FrViewer* m_pClub;
	FrViewer* m_pMascot;
	FrViewer* m_pEquipItem;
	FrViewer* m_pCharSel;
	FrViewer* m_pCaddieSel;
	FrViewer* m_pAztecSel;
	FrViewer* m_pClubSel;
	FrViewer* m_pMascotSel;
	FrButton* m_pStart;
	FrButton* m_pReady;
	unsigned long m_reserved6a8;
	FrButton* m_pGuildInvite;
	FrButton* m_pChangeTeam;
	FrWnd* m_pUnused6dc;
	FrButton* m_pScore;
	FrArea* m_pTeamNum;
	FrArea* m_pGuildNum;
	FrWnd* m_pReserved6ec;
	FrWnd* m_pReserved6f0;
	FrFrame* m_pExtFrame;
	FrButton* m_pUnused6f8;
	unsigned long m_reserved6fc[3];
	FrArea* m_pTeamTab[2];
	FrArea* m_pGuildTab[2];
	FrGaugeBar* m_pGuildScoreGauge;
	unsigned long m_reserved71c;
	FrArea* m_pStartTip;
	FrArea* m_pReadyTip;
	FrArea* m_pCurTip;
	FrArea* m_pCountdown;
	FrArea* m_pRoomUserRankTab;
	FrButton* m_pUserInfo;
	FrButton* m_pRoomClose;
	FrEdit* m_pTitle;
	FrButton* m_pRoomOption;
	FrListBox* m_pRoomUser;
	FrListBox* m_pRoomUserRank;
	FrListBox* m_pRoomGuildRank;
	sRoomInfo* m_pSelRoom;
	FrUniteResultDlg* m_pUniteResultDlg;
	FrTreasureGift* m_pTreasureGift;
	FrForm* m_pReservedDlg75c;
	float m_resultDelay;
	std::vector<FrLevelupItemForm*> m_levelupForms;
	Bitmap* m_pTeamBmp[2];
	Bitmap* m_pTeamBaseBmp;
	Bitmap* m_pTeamBase02Bmp;
	Bitmap* m_pInviteBmp;
	Bitmap* m_pMasterSignBmp;
	Bitmap* m_pReadySignBmp;
	Bitmap* m_pSituBmp[7];
	Bitmap* m_pTeamSelectBmp;
	Bitmap* m_pDiveBmp;
	unsigned long m_reserved7b4[2];
	const Bitmap* m_pTeamRankBmp[2];
	const Bitmap* m_pRankBgBmp;
	const Bitmap* m_pRankBmp[4];
	Bitmap* m_pPlayerBaseBmp[4];
	Bitmap* m_pKickBmp;
	Bitmap* m_pReservedBmp7ec[3];
	Bitmap* m_pReservedBmp7f8;
	Bitmap* m_pReservedBmp7fc;
	char m_roomPassword[260];
	bool m_bCreateRoom;
	bool m_bReady;
	bool m_bRoomStateReq;
	bool m_bLockControls;
	bool m_bCanStart;
	unsigned char m_quickStartCate;
	bool m_bIdle;
	std::list<sSlotInfo*> m_redTeam;
	std::list<sSlotInfo*> m_blueTeam;
	unsigned long m_masterOID;
	unsigned long m_selOID;
	unsigned long m_selUID;
	unsigned long m_reserved930;
	unsigned long m_rankViewKind;
};
