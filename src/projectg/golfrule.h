#pragma once

#ifdef REBANG_GOLFRULE_PCH
#include "taskmain.h"
#include <stack>
#else
#include "actor.h"
#endif

#ifdef REBANG_GOLFRULE_PCH
class FrReplayControlDlg;
class FrEmoticonDlg;
class FrApproachResultDlg;
class FrApproachEndDlg;
class FrOnelineReqDlg;
class CGolfRuleBase;
class CSubGolfRuleBase; // 983: include/jp/subgolfrule.h (frente B)
class FrComboBox;
class CSimpleUI;

class CGolfRule : public CTaskMain
#else
class CGolfRule : public IActor
#endif
{
#ifdef REBANG_GOLFRULE_PCH
	DECLARE_OBJECT(CGolfRule)

#endif
public:
	friend class CGolfRuleBase;
	friend class CGolfRuleQuickrace;
	friend class CGolfRuleTimeattack;
	friend class CGolfRuleTutorial;
	friend class CGolfRuleGuildMatch; // 983: RequestShotReview (CheckNetMsgWait_Send)
	friend class CGolfRule30Battle;   // 983: RequestShotReview (CheckNetMsgWait_Send)
	friend class CGolfRuleNewApproach; // 983: [10] 006a9790 (SendShotResult, ApproachTimeOut983)
#ifdef REBANG_GOLFRULE_PCH

	struct sBackUp
	{
		WVector pos;         // 0x00
		float unk0c;         // 0x0c
		unsigned char unk10; // 0x10
		unsigned char unk11; // 0x11
		float unk14;         // 0x14
		__int64 unk18;       // 0x18
		__int64 unk20;       // 0x20
		__int64 unk28;       // 0x28
		unsigned long unk30[(0x58 - 0x30) / 4];
		char club[4];        // 0x58
		unsigned char unk5c; // 0x5c
		unsigned char unk5d; // 0x5d
	};
#endif

	struct sShotData
	{
		unsigned char hole;
		WVector wind;
		unsigned char weather;
		unsigned char stroke;
		sBar bar;
		WVector pos;
		float angle;
		float curve;
		float spin;
		int pvsFrame;
		unsigned long special;
		unsigned long clubPower;
		char club[4];
		unsigned char bunker;
		unsigned long item;
		float deviation;
		unsigned char holeStroke;
		int pang;
		int bonusPang;
		WCrypticValue<float> gauge;
	};

	void AddPlayer(unsigned char index, const char* name, unsigned long uid,
		unsigned long oid, unsigned long caddie);
	void SendHoleData();
	void LoadShot(const char* filename);

#ifdef REBANG_GOLFRULE_PCH
	CGolfRule();
	virtual ~CGolfRule();

#endif
	sShotData* GetShotData() { return &m_shotData; }
	void SendMsg983(const char* target, const MsgObject& msg); // JP 983: 00671330
	bool IsModeTimeOver983(); // JP 983: 0066e8c0 (m_modeTime >= 3.0f)
	bool IsNetWaiting983();   // JP 983: 0066e8a0 (m_bContinueDlg || m_bNetMsgWait)
	void SetUnk26c_983(float time); // 983: a base grava +0x2c8 direto (006a8817); aqui ela so ve a parte comum
protected:
	void ReturnLobby(bool); // 0067cc70 (visivel fora do pch para o CGolfRule30Battle)
public:
#ifdef REBANG_GOLFRULE_PCH
	unsigned char GetCurTeam() { return m_curTeam; }
	virtual void OnLoad();
	void SetFlagCutin(bool);
	bool GetFlagCutin();
	virtual void OnInit();
	virtual void OnDisplay();
	void SetCurrentGolfRule();
	virtual void OnDestroy();
	virtual void OnReload();
	void SaveShot(char const*);
	virtual void OnPreLoadInit();
	virtual void HandleMsg(MsgObject const&);
	virtual void OnProcess(float);
#endif

protected:
	unsigned char GetFirstTurn();
	void ResetData(const WVector& pos);
	void ChangeGameMode(unsigned long mode);
	void SetNetMsgWait(bool, int, char*, float);
	void CheckNetMsgWait_Send(char*);
	void SendShotResult();       // fora do bloco PCH: a CGolfRuleNewApproach [10] chama
	void ApproachTimeOut983(); // 00695270
#ifdef REBANG_GOLFRULE_PCH
	void OnChatTargetBtnDown(int);
	void OnSpecialCardBtnUp();
	void OnCaddieBookBtnUp();
	void OnChatRecordBtnUp();
	void SetGrade();
	void SetVisibleUpperBtns(bool);
	bool CheckGiveUp();
	void ToggleCommandBtns(bool);
	void CheckNetMsgWait_Recv(char*);
	void SetAngle(float);
	bool OnPlayerInfoDlgResult(int, FrForm*);
	void OnEmoticonInit(int);
	void OnLanguageInit(int);
	void OnReportInit(int);
	bool OnChatTargetEnterKey(int);
	void OnChatInputInit(int);
	void OnSpecialCardInit(int);
	void OnMyInfoInit(int);
	void OnOptionInit(int);
	void OnOptionBtnUp();
	void OnUnplayableInit(int);
	void OnPauseInit(int);
	void OnChatRecordInit(int);
	void OnOnelineViewInit(int);
	void OnOnelineViewOwnerDraw(int);
	void OnOnelineBtnInit(int);
	bool OnOnelineReqChkOutDlgResult(int, FrForm*);
	void OnRadioPredictNormalShotInit(int);
	void OnRadioPredictTomahwakShotInit(int);
	void OnRadioPredictCobraShotInit(int);
	void OnRadioPredictSpikeShotInit(int);
	void OnRadioPredictNormalShotDown();
	void OnRadioPredictNormalShotDraw(int);
	void SetPlayer();
	void IntergrateFile(char const*);
	void SendReportError(unsigned char);
	void ResetUiPos_Board();
	void OnMessengerBtnUp();
	void OnMessengerBubbleEditInit(int);
	void OnMessenger_AlarmBtnUp();
	void OnMessenger_GiftAlarmBtnInit(int);
	void OnReplayStatusInit(int);
	void OnMoveTeeInit(int);
	void OnMoveTeeBtnUp();
	void OnShotReviewPreInit(int);
	void OnShotReviewNextInit(int);
	void OnShotReviewPreBtnUp();
	void OnShotReviewNextBtnUp();
	void OnMainFinish();
	void OnPremiumServiceEndNoticeInit(int);
	void OnPremiumServiceEndNoticeOwnerDraw(int);
	void OnChatViewInit(int);
	void OnChatTargetInit(int);
	bool OnChatInputEnterKey(int);
	void OnCaddieBookInit(int);
	void OnUnplayableBtnUp();
	void OnPauseBtnUp();
	bool OnOnelineReqDlgResult(int, FrForm*);
	void OnOnelineBtnUp();
	void OnTopBarHoverOn(int);
	void OnTopBarHoverOff(int);
	void OnRadioPredictTomahwakShotDown();
	void OnRadioPredictCobraShotDown();
	void OnRadioPredictSpikeShotDown();
	void OnRadioPredictTomahwakShotDraw(int);
	void OnRadioPredictCobraShotDraw(int);
	void OnRadioPredictSpikeShotDraw(int);
	unsigned long GetHolePang(unsigned char);
	void DoDebugCamera(float);
	bool GetBarCondition();
	void SetSpecialShot();
	void CheckSpecialShotSpinAndCurve();
	WMatrix BankCamera(float);
	void ReactionForShot();
	bool PauseDlgResult(int, FrForm*);
	bool CancelDropDlgResult(int, FrForm*);
	bool GoStopDlgResult(int, FrForm*);
	bool OnEmoticonResult(int, FrForm*);
	bool OnReportResult(int, FrForm*);
	bool CanCancelShot();
	void OnMessengerBtnInit(int);
	void OnMessenger_AlarmBtnInit(int);
	void OnMessenger_GiftAlarmBtnUp();
	bool IsMaxWithHGParts(unsigned char);
	void OnEmoticonBtnUp();
	void OnReportBtnUp();
	void OnMyInfoBtnUp();
	void RecordPlayerList();
	bool CheckDropOut();
	bool HaveTeeShots();
	void RecordPlayerData(unsigned char);
	void RecordTeamData(unsigned char);
	void RecordGiveUp(unsigned char);
	void DispatchMatchItems();
	void SetHoleInPose(bool);
	__int64 CalcWinnersPang(unsigned long);
	void DoFlyBall_Flying(float);
	void CaptureProcess();
	void DoApproachNextHole(float);
	void UpdateShotResultStat();
	void CorrectShotResult();
	void SetEnvironmentVariableA();
	void ForcedMoveBall(WVector const&);
	unsigned char GetNextTurn();
	void AddPrize(int);
	bool CheckAllHoleOut();
	bool ContinueDlgResult(int, FrForm*);
	bool OnReturnLobbyResult(int, FrForm*);
	bool OnGPAwardNotifyResult983(int, FrForm*); // 00671310 (B72): retorno do "notify_ok2" da premiacao do Grand Prix
	void DoGameOver(float);
	void CalcInputCommand();
	bool SetTurnChangeEvent();
	void Replay(bool);
	void AddExtPrize();
	void CancelShot();
	bool OnForgetDlgResult(int, FrForm*);
	void PlayBGM();
	void CommandBox();
	void ChangeTurn();
	void GetWinningPrize(int);
	bool SetHoleInPose_Skins();
	void SendHoleStat();
	bool ReturnToLobbyDlgResult(int, FrForm*);
	void CheckUserBGM(char const*);
	void EncodePacket(enumClientPacket, WSendPacket&);
	void ResetRank();
	bool CanMoveToNextHole();
	void RecordScoreByPlayer(unsigned char);
	void RecordScoreByTeam(unsigned char);
	bool SetHoleInPose_Match();
	bool SetHoleInPose_Team();
	void CalcSkinsHolePang();
	void DoFlyBall_Stopped(float);
	void DoCoursePreview(float);
	void DoGetReadyToCaptureBG(float);
	void DoNavigateCamera(float);
	void DoTopViewCamera(float);
	void Skip();
	void HitShot();
	bool OnApproachEndDlgResult(int, FrForm*);
	bool OnApproachDlgResult(int, FrForm*);
	void SetReady();
	void DoFixedCamera(float);
	void DoSpotCamera(float);
	void DoDespairPose(float);
	void DoScoreBoard(float);
	void DoHoleInPose(float);
	void DoWaitForStart(float);
	void DoCloseupCaddie(float);
	void ReadyForNextTurn();
	void DoDrive(float);
	void DoFlyBall(float);
	void DoStand(float);
	void DriveGauge(float, bool);
	void PuttingGauge(float, bool);
	void DoToDefaultCamera(float);
	void DoToDefaultCameraNext983();
	void Drop(WVector const&);
	void Cancel();
	void Warp(WVector const&);
	void DoTimeOut(float);
	void DoPlayerPreview(float);
	bool IsWaiting983(); // JP 983: 0066e870
	void DoPowerGauge(float);

private:
	void SetRadioPredictShotPress(FrButton*);
	void UpdateRadioPredictShotButtonStatus();
	bool StandViewClick();
	int HoleReplay2();
	void ReplayBoxClose();
	bool IsLastShotRelplay();
	void InitRadioPredictShotButton(FrButton**, int, float);
	void ToggleGameUI();
	void _ImeReset();
	char* GetPangyaInstallDic();
	void HoleReplay();
	void SwingReplay();
	void AutoReplay();
	bool OnReplayModeDlgResult(int, FrForm*);
	bool OnRecordAviResult(int, FrForm*);
	bool GetShotCntData();
	void SaveGame(int);
	void LoadGame(int);
	void QuickSave(char const*);
	void ReplayBoxOpen();
	void OnRecordAviBtnUp();
	void AddSomeInfo(WSendPacket&);
	void HoleComboGaugeSetting();
	bool TopViewClick();
	void FlyBy(float);
	void AllReplay();
	bool ShotDataLoad(char const*);
	int ShotDataSave(char const*); // 983: sem o modo anonimo (006884f0)
	void SaveErrorFile();
	void ReplayTapeCheckAndUse();
	void CollectBallStopData();
	void QuickLoad(char*);
	void ProcessObserver();

	DECLARE_FRESH_MSGMAP()
#endif

public:
#ifdef REBANG_GOLFRULE_PCH
	// TODO: incomplete; offsets from the ghidra dump, CTaskMain ends at 0x1e0 (dsize, members reuse tail padding)
	unsigned long m_unk1e0; // 0x1e0
	unsigned long m_unk1e4; // 0x1e4
	unsigned long m_unk1e8; // 0x1e8
	std::deque<void*> m_unk983_224; // 983: 2º contêiner tipo deque (0x18 bytes no VS2010) construído em 0068aee3, antes do m_backUpStack. Tipo do elemento provisório
	unsigned char m_unk983_23c[0xc]; // 983: +0xc até m_modeTime (0x260); posição dentro de 0x23c..0x260 não medida
	unsigned char m_unused1ec[0x1f8 - 0x1ec];
	WVector m_camPivot; // 0x1f8
	float m_modeTime;   // 0x204
	unsigned char m_unused208[0x24c - 0x208];
	WVector m_targetPos; // 0x24c
	unsigned char m_unused258[0x265 - 0x258];
	bool m_unk265; // 0x265
	unsigned char m_unused266[0x26c - 0x266];
	float m_unk26c; // 0x26c
	unsigned char m_unused270[0x27c - 0x270];
	std::stack<sBackUp> m_backUpStack; // 0x27c
	sBackUp m_backUp;                  // 0x290
	unsigned long m_unk2f0;            // 0x2f0
	sShotData m_shotData;              // 0x2f4
	char m_sfxName[0x20]; // 983 0x3dc (645: m_wind 0x37c + 0x388 nome do som); o 983 não tem m_wind: LoadGame 0067c5a5 lê o vento numa
	                      // local; o nome do som do voo fica em +0x3dc (ChangeGameMode 0068fc2e/0068fc4d, DoFlyBall_Flying 0067f7ad); s96
	std::vector<WVector> m_bgPosList; // 0x3a8
	unsigned char m_curTeam;          // 0x3b8
	unsigned char m_unused3b9[0x3ca - 0x3b9];
	bool m_bContinueDlg;            // 0x3ca
	bool m_bNetMsgWait;             // 0x3cb
	int m_netMsgWaitType;           // 0x3cc
	char* m_pNetMsgWait;            // 0x3d0
	char* m_pNetMsgRecv;            // 0x3d4
	unsigned long m_netMsgSendTick; // 0x3d8
	unsigned long m_netMsgRecvTick; // 0x3dc
	float m_netMsgWaitTime;         // 0x3e0
	unsigned char m_unused3e4[0x3f4 - 0x3e4];
	unsigned long m_unk3f4;   // 0x3f4
	unsigned char m_bgmIndex; // 0x3f8
	unsigned char m_unused3f9[0x3fc - 0x3f9];
	unsigned long m_cmdTick; // 0x3fc
	unsigned char m_unused400[0x408 - 0x400];
	bool m_unk408; // 0x408
	unsigned char m_unused409[0x414 - 0x409];
	FrForm* m_pPauseDlg;                       // 0x414
	FrForm* m_pGoStopDlg;                      // 0x418
	FrForm* m_pCancelDropDlg;                  // 0x41c
	unsigned long m_unk420;                    // 0x420
	FrApproachResultDlg* m_pApproachResultDlg; // 0x424
	FrApproachEndDlg* m_pApproachEndDlg;       // 0x428
	bool m_unk42c;                             // 0x42c
	unsigned char m_unused42d[3];
	float m_dbgCam[2];    // 983 0x484/0x488 (645 0x430/0x434): câmera de depuração (DoDebugCamera; OnPreLoadInit -1.0f/100.0f); s96
	float m_unk983_48c;   // 983: novo (OnPreLoadInit 0068bf86..: fst [esi+0x48c])
	WVector m_dbgCamPos;  // 983 0x490 (645 0x438..0x440; DoDebugCamera: 490 494 498 = 438 43c 440); s96
	bool m_unk444;          // 0x444
	float m_unk448; // 0x448; 983: float (fldz/fstp [esi+0x4a0] em 0068af83)
	int m_cancelItemSlot;   // 0x44c
	unsigned char m_unused450[0x460 - 0x450];
	std::vector<std::string> m_bgmList;      // 0x460
	FrComboBox* m_pChatTarget;               // 0x470
	FrEdit* m_pChatEdit;                     // 0x474
	FrButton* m_pEmoticonBtn;                // 0x478
	FrArea* m_pLanguage;                     // 0x47c
	FrButton* m_pReportBtn;                  // 0x480
	FrEdit* m_pChatView;                     // 0x484
	FrEmoticonDlg* m_pEmoticonDlg;           // 0x488
	FrForm* m_pReportDlg;                    // 0x48c
	FrWnd* m_pUnk490;                        // 0x490
	FrOnelineReqDlg* m_pOnelineReqDlg;       // 0x494
	FrReplayControlDlg* m_pReplayControlDlg; // 0x498
	FrForm* m_pRecordAviDlg;                 // 0x49c
	FrButton* m_pReplayBox;                  // 0x4a0; 983 +0x4f8: FrButton (00671190)
	FrButton* m_pMyInfoBtn;                  // 0x4a4
	FrButton* m_pOptionBtn;                  // 0x4a8
	FrButton* m_pCaddieBookBtn;              // 0x4ac
	FrButton* m_pUnplayableBtn;              // 0x4b0
	FrButton* m_pPauseBtn;                   // 0x4b4
	FrButton* m_pChatRecordBtn;              // 0x4b8
	FrArea* m_pOnelineView;                  // 0x4bc
	FrButton* m_pOnelineBtn;                 // 0x4c0
	FrButton* m_pMoveTeeBtn;        // 983 +0x51c: MAIN.move_tee (006770d0)
	FrButton* m_pShotReviewNextBtn; // 983 +0x520: MAIN.shot_review_button_next (00670830)
	FrButton* m_pShotReviewPreBtn;  // 983 +0x524: MAIN.shot_review_button_pre (006707c0)
	bool m_unk4c4;                           // 0x4c4
	char m_unk4c5[100];                      // 0x4c5
	FrArea* m_pPremiumNotice;  // 983 +0x590: MAIN.premium_service_end_notice (00672e10)
	float m_unk983_594;         // 983: OnPreLoadInit/OnProcess 0069cc0a
	float m_unk983_598;
	bool m_b983_59c;            // 983: ligado no DoPlayerPreview (00696021) quando CSharedDoc+0x1160a != 0
	const Bitmap* m_pPremiumBmp[4]; // 983 +0x5a0: "Premium service_close_00/01/02", "Premium service_base"
	unsigned long m_pvsFrame[3]; // 983 0x5b0 (645 0x52c): quadros do PVS no tiro (ChangeGameMode 0068d911..0068d943); s96
	FrButton* m_pRadioPredictNormalShot;   // 0x538
	FrButton* m_pRadioPredictTomahwakShot; // 0x53c
	FrButton* m_pRadioPredictCobraShot;    // 0x540
	FrButton* m_pRadioPredictSpikeShot;    // 0x544
	CSimpleUI* m_pPredictShotUI;           // 0x548
	int m_captureTiles;                    // 0x54c
	int m_captureIndex;                    // 0x550
	int m_captureMode;                     // 0x554
	bool m_bGameUI;                        // 0x558
	char m_saveFileName[0x59c - 0x559];    // 0x559
	unsigned long m_unk59c;                // 0x59c
	unsigned long m_unk5a0;                // 0x5a0
	unsigned long m_unk5a4;                // 0x5a4
	unsigned long m_replayFlags;           // 0x5a8
	int m_replayState;                     // 0x5ac
	unsigned char m_unused5b0[0x5b2 - 0x5b0];
	bool m_bFlagCutin; // 0x5b2
	unsigned char m_unused5b3[0x5b4 - 0x5b3];
	CGolfRuleBase* m_pRuleBase; // 0x5b4; 983: 0x638
	CSubGolfRuleBase* m_pSubRule983; // 983 +0x63c: sub-regra da frente B (include/jp/subgolfrule.h): CSubGolfRuleGame (m_playingMode 1) ou CSubGolfRuleReplayTape (2), criada no SetCurrentGolfRule 00677290 (s101)
	bool m_unk5b8;              // 0x5b8; 983: 0x640
	bool m_bWaitForStart;       // 0x5b9; 983: 0x641
	int m_unk5bc;               // 0x5bc; 983: 0x644
	unsigned long m_unk983_648; // 983: zerado no fim do construtor (0068b21d)
	unsigned long m_unk983_64c; // 983: sizeof 0x650
#else
	// TODO: incomplete
	unsigned char m_unused1c[0x354 - sizeof(IActor)]; // D192: m_shotData em 0x354 no 983 (LoadShot 0067c240); era 0x2f4 (645) fora do pch
	sShotData m_shotData;
#endif
};

#ifdef REBANG_GOLFRULE_PCH
#ifdef REBANG_GOLFRULE_PCH // golfrule.cpp: inline bodies the original PCH has here (emission order)
inline void CGolfRule::SetFlagCutin(bool flag)
{
	m_bFlagCutin = flag;
}

inline bool CGolfRule::GetFlagCutin()
{
	return m_bFlagCutin;
}
#endif

#endif
