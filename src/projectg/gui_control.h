#pragma once

#include "frform.h"
#include "taskmain.h"
#include "wlist.h"
#include "wflag.h"
class FxInterpreter;

class FrButton;
class FrEdit;
class FrReportDlg;
class WOverlay;
class WFont;
class FrChatFuncDlg;
class Bitmap;
class CShotCountInfo;
class CSimpleUI;
class CWindInfo;
class CFontOverlay;
class CBase;
class CRemainTimeInfo;
class CClubTypeInfo;
class CPowerInfo;
class CAccuracyInfo;
class CMiniScore;
class CAuxMenuUI;
class CPangInfo;
class CHolePoseSkins;
class CExtraHoleInfo;
class CGuildInfo;
class CCalipers;
class WPuppet;
class WTitleFont;
class CHoleInOneScoreInfo;
namespace _gateway { class FrHoleinoneMissionDlg; }
class CHoleEffect;

// JP 983: objetos novos do CScreen (0x250..0x26c) criados pelo OnLoad (007517b0) e apagados pelo OnDestroy (0074d8e0). Sem RTTI
// os nomes sao provisorios (pelo uso), menos os dois efeitos de "recover pangya shot" (vtables 00d209e0/00d209e8).
class CScreenAutoFlag983 // CScreen+0x250, sizeof 2
{
public:
	CScreenAutoFlag983(); // 0074b5e0
	void Reset(); // 0074aa60
	void Process(float dt); // 0074d8a0: copia o byte +0xdc do GOLFDOC enquanto ligado
	bool m_on;
	unsigned char m_value;
};
class CAutoShotButtons983 // CScreen+0x260, sizeof 5: botoes "r_automatic_toma/cobra/spike_button" (Process 00750b90)
{
public:
	CAutoShotButtons983(); // 0074b600
	void Reset(); // 0074aaa0
	void SetOn(bool on); // 0074aab0
	void SetButton(unsigned char kind, bool on); // 0074aac0: 0x10 toma, 0x20 cobra, 0x40 spike (2 = aceso)
	int Process(); // 00750b90: devolve o tipo clicado (0x10/0x20/0x40) ou 0
	void Draw(); // 00753c30
	void DrawToma(); // 00750e30
	void DrawCobra(); // 00750f90
	void DrawSpike(); // 007510f0
	unsigned char m_value;
	bool m_on;
	unsigned char m_state[3];
};
class CCurveArrow983 // CScreen+0x264, sizeof 0x24: setas "CurveArrow_*.png"
{
public:
	CCurveArrow983(); // 0074ab80
	~CCurveArrow983(); // 0074aba0
	void Load(); // 0074b610
	void Reposition(); // 0074b690
	void Process(float dt); // 0074ac00
	void SetType(unsigned int type); // 0074acb0
	void SetState(unsigned int state); // 0074acd0
	void Display(); // 0074e470
	int m_type;
	WOverlay* m_pArrow[3]; // reto, esquerda, direita
	WVector2D m_pos; // centro da tela
	float m_time;
	int m_state; // 0 apagada, 1 acendendo, 2 apagando
	float m_alpha;
};
class CRecoverPangyaShotEffect // CScreen+0x268, sizeof 0x1c
{
public:
	CRecoverPangyaShotEffect(); // 0074b6e0
	virtual ~CRecoverPangyaShotEffect(); // 0074acf0
	void Reset(); // 0074ad00
	void Process(float dt); // 0074b730
	void Display(); // 00751250: quadro "f_footprint_effect_%d"
	float m_interval;
	int m_frameCount;
	bool m_active;
	int m_frame;
	float m_time;
	unsigned long m_unk18;
};
class CRecoverPangyaShotRingEffect // CScreen+0x26c, sizeof 0x20
{
public:
	CRecoverPangyaShotRingEffect(); // 0074b780
	virtual ~CRecoverPangyaShotRingEffect(); // 0074ad20
	void Reset(); // 0074ad30
	void Process(float dt); // 0074b7e0: toca "luck_rainbow_print" no quadro m_soundFrame
	void Display(); // 00751340: quadro "f_rainbowprint_effect_%d"
	float m_interval;
	int m_frameCount;
	int m_soundFrame;
	bool m_active;
	int m_frame;
	float m_time;
	unsigned long m_unk1c;
};

class CScreen : public CTaskMain
{
	DECLARE_OBJECT(CScreen)

public:
	struct sOverlay
	{
		sOverlay() { m_pOverlay = NULL; }

		~sOverlay()
		{
			if (g_resrcmng && m_pOverlay)
			{
				g_resrcmng->Release(m_pOverlay);
				m_pOverlay = NULL;
			}
		}

		char m_name[0x20];
		WOverlay* m_pOverlay;
	};

	struct sHitMark
	{
		float y;
		unsigned long color;
	};

	virtual ~CScreen() { }

	virtual void OnDestroy();
	virtual void OnPreLoadInit();
	virtual void OnInit();
	virtual void OnLoad();
	virtual void OnProcess(float dt);
	virtual void OnDisplay();

protected:
	CScreen();

	virtual void HandleMsg(const MsgObject& msg);

	void AddOverlay(const char* name, const char* file, int flags);
	void DrawOverlay(const char* name, const WRect& rect, unsigned char alpha,
		int flags);
	void DrawOverlay2(const char* name, const WRect& rect, int color,
		int flags);

private:
	void DrawCammodeInfo();
	void DrawWindInfo();
	void DrawMatchBand983(); // 983: 0074d160
	void DrawMatchTime983(); // 983: 0074d530
	void DrawGrandPrixTimer983(); // 983: 0074cd20 (thunk 0074e160)
	void DrawRemainTime();
	void DrawSpecialShotDesc983(); // 00750a50
	void DrawCommandArrow();
	void DrawClubInfo();
	void DrawApproachInfo();
	void DrawTutorialUI();
	void DrawHitBarInfo(); // 983: 00758290
	void DrawDriverThumb983(int width, int hitX, unsigned char alpha); // 983: 00754650
	void DrawPutterThumb983(); // 983: 00754bc0
	void LoadTreasureOverlays983(); // 983: 0074c960
	void LoadGrandPrixOverlays983(); // 983: 007500a0
	bool LoadGrandPrixUi983(); // 983: 0074ff30 (grandprix_ingame_ui.lua)
	void DrawClubBallUI();
	bool OnTrainingOptionDlgResult(int result, FrForm* pForm);

	CFontOverlay* m_pFontOverlay;
	CBase* m_pGroundInfo;
	CWindInfo* m_pWindInfo;
	CRemainTimeInfo* m_pRemainTimeInfo;
	CClubTypeInfo* m_pClubTypeInfo;
	CPowerInfo* m_pPowerInfo;
	CAccuracyInfo* m_pAccuracyInfo;
	WPuppet* m_pWindPuppet;
	CMiniScore* m_pMiniScore;
	CAuxMenuUI* m_pAuxMenuUI;
	CPangInfo* m_pPangInfo;
	CHolePoseSkins* m_pHolePoseSkins;
	CExtraHoleInfo* m_pExtraHoleInfo;
	CGuildInfo* m_pGuildInfo;
	CScreenAutoFlag983* m_pAutoFlag983; // 983: 0x250
	CHoleInOneScoreInfo* m_pHoleInOneScoreInfo983; // 983: 0x254 (tipo de jogo 0xb)
	_gateway::FrHoleinoneMissionDlg* m_pUnk983_258; // 983: janela "holeinone_mission" (tipo de jogo 0xb, criada no OnInit), fechada primeiro no OnDestroy
	CHoleEffect* m_pHoleEffect983; // 983: 0x25c (tipo de jogo 0xb)
	CAutoShotButtons983* m_pAutoShotButtons983; // 983: 0x260
	CCurveArrow983* m_pCurveArrow983; // 983: 0x264
	CRecoverPangyaShotEffect* m_pRecoverPangyaShotEffect983; // 983: 0x268
	CRecoverPangyaShotRingEffect* m_pRecoverPangyaShotRingEffect983; // 983: 0x26c
	CSimpleUI* m_pCammodeUI; // 983: 0x270
	CSimpleUI* m_pClubLineUI;
	CSimpleUI* m_pIconUI;
	CSimpleUI* m_pTutoTextUI;
	CSimpleUI* m_pTutoEscUI; // 983: 0x280
	CSimpleUI* m_pQuestMsgUI[12];
	WTitleFont* m_pTitleFont;
	CSimpleUI* m_pMissionUI;
	float m_tutoScale;
	float m_accumValue;
	float m_fadeValue;
	WList<sOverlay*> m_overlays;
	WFont* m_pFont;
	union
	{
		float m_remainTimeArcShown;
		WTitleFont* m_pTitleFont2983; // 983 (0074be40): +0x2ec, fonte "[font_wind_x2.jpg" 32x32
	};
	union
	{
		float m_remainTimeArc;
		float m_gpTextOffsetX983; // 983 (0074ff30): "hole_limited_time_text_offset_x" do grandprix_ingame_ui.lua em +0x2f0
	};
	union
	{
		unsigned long m_remainTimeColor;
		float m_gpTextOffsetY983; // +0x2f4
	};
	float m_gpColonOffsetX983; // +0x2f8 "remain_time_sign_colon_str_offset_x"
	float m_gpSecondOffsetX983; // +0x2fc "remain_time_second_str_offset_x"
	unsigned char m_unk983_300[0xc]; // 983: +0x1c entre m_pFont (0x2e8) e m_hudVisible (0x314); lugar exato dentro do vão não medido
	float m_unk983_30c; // 983: 0.0f no construtor
	unsigned long m_unk983_310; // 983: 0 no construtor
	bool m_hudVisible; // 983: 0x314
	unsigned char m_unused2a5[0x3];
	unsigned long m_hitBarBaseColor;
	int m_msgColorTime;
	unsigned long m_msgColor;
	unsigned char m_unused2b4[0x4];
	int m_hitBarFrom;
	int m_hitBarCount;
	unsigned long m_hitBarColor;
	float m_hitBarTime;
	float m_remainTimeY;
	sHitMark m_hitMarks[21 + 10]; // 983: +0x50 entre m_hitBarTime (0x334) e m_blinkTime (0x434) = 10 marcas a mais (hipótese: o vetor cresceu; não conferi o limite do laço)
	float m_blinkTime;
	WFlags m_drawFlags;
	float m_cammodeAlpha;
	float m_ballStateFade;
	bool m_bHoleShown[15];
	unsigned char m_unused393;
	unsigned char m_unknown394;
	unsigned char m_unknown395;
	unsigned char m_unused396[0x2];
	float m_unknown398;
	float m_unknown39C;
	unsigned char m_unknown3A0;
	unsigned char m_unused3a1[0x3];
	float m_unknown3A4;
	float m_unknown3A8;
	int m_selectedIndex;
	float m_bannerTime;
	int m_unknown3B4;
	unsigned char m_tutoTextAlpha;
	unsigned char m_unused3b9[0x3];
	float m_tutoTextX;
	float m_tutoTextY;
	float m_unknown3C4;
	int m_unknown3C8;
	float m_tutoX;
	float m_tutoY;
	float m_tutoTime;
	int m_tutoStep;
	float m_unknown3DC;
	bool m_turnStarted;
	bool m_unknown3E1;
	bool m_unknown3E2;
	bool m_unknown3E3;
	int m_turnTime;
	float m_unknown3E8[3];
	float m_clubAngle;
	int m_clubSpinDir;
	float m_clubSwing;
	CCalipers* m_pCalipers;
	int m_clubBoundingBox;
	unsigned char m_playerCount; // 983: 0x4c8
	unsigned char m_unused409[0x3];
	void* m_pUnk983_4cc; // 983: zerado no construtor
	FxInterpreter* m_pFxInterpreter983; // 983: 0x4d0 = new FxInterpreter(NULL, 0) no construtor (00751670)
	bool m_grandPrix983; // 983: 0x4d4 (liga o relogio do Grand Prix no OnLoad)
	unsigned char m_unk983_4d5[3];
	std::string m_unk983_4d8; // 983: 2 std::string construídas vazias (0x4d8, 0x4f4)
	std::string m_unk983_4f4;
	float m_gpUiOffsetX983; // 983: 0x510 "hole_limited_time_ui_offset_x"
	float m_gpUiOffsetY983; // 983: 0x514
	unsigned char m_unk983_518;
	bool m_unk983_519; // 983: false no OnLoad
	unsigned char m_unk983_51a[2];
	float m_unk983_51c; // 983: 0.5f no OnLoad
	float m_unk983_520; // 983: 0.0f no OnLoad
	unsigned char m_unk983_524[4]; // 983: sizeof 0x528
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbDrawapproachinfoFunclets(); // HACK: EH funclets of the naked DrawApproachInfo (nakedify)
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbOndisplayFunclets(); // HACK: EH funclets of the naked OnDisplay (nakedify)
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbOnprocessFunclets(); // HACK: EH funclets of the naked OnProcess (nakedify)
#endif
};

class CMiniScore
{
public:
	CMiniScore();
	~CMiniScore();

	void ChangeCharacter();
	WRect GetIconRect(int flags);
	void Flicker();
	void ResetUiPosition();
	void Show();
	void Hide();
	void StartFloating();
	void Process(float dt);
	void Display();

private:
	CShotCountInfo* m_pShotCountInfo;
	WOverlay* m_pInfo;
	const Bitmap* m_pCharBitmap[4];
	const Bitmap* m_pVsIcon;
	WOverlay* m_pHp;
	WOverlay* m_pNPlayer;
	WOverlay* m_pBestRecordL;
	WOverlay* m_pBestRecordR;
	CSimpleUI* m_pHoleOutUI;
	WFont* m_pFont;
	WRect m_iconUV;
	int m_unk983_44; // 983: +4 antes de m_iconRect (GetIconRect 0074b120 le w/h em +0x50/+0x54; Show/Hide em +0x68..+0x78)
	WRect m_iconRect;
	WRect m_charRect;
	float m_offsetY;
	float m_posX;
	int m_state;
	float m_stateTime;
	unsigned char m_alpha;
	unsigned char m_unused75[3];
	unsigned long m_gameMode;
};

class CAuxMenuUI : public FrCmdTarget
{
public:
	CAuxMenuUI();
	virtual ~CAuxMenuUI();

	void Display();
	void SetActive(bool active, int index);
	void ChangeTurn();
	void SetPause();
	void OpenChatRecord();
	void SetUnplayable();
	void Process(float dt);
	void ResetSelected() { m_selected = -1; }
	FrChatFuncDlg* GetChatFuncDlg() { return m_pChatFuncDlg; }

private:
	bool OnChatFuncDlgResult(int result, FrForm* pForm);
	bool OnDropDlgResult(int result, FrForm* pForm);
	bool OnDropFailDlgResult(int result, FrForm* pForm);

	WOverlay* m_pBase;
	WOverlay* m_pBlack;
	WOverlay* m_pWhite;
	int m_hover;
	int m_active;
	int m_selected;
	float m_slide;
	FrForm* m_dropDlg;
	FrForm* m_dropFailDlg;
	unsigned char m_pauseCount;
	unsigned char m_unused29[3];
	FrChatFuncDlg* m_pChatFuncDlg;
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbSetpauseFunclets(); // HACK: EH funclets of the naked SetPause (nakedify)
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbOndropdlgresultFunclets(); // HACK: EH funclets of the naked OnDropDlgResult (nakedify)
#endif
};

class CDrivingDistInfo
{
public:
	CDrivingDistInfo();
	~CDrivingDistInfo();

	void OnChangeTurn();
	void Process(float dt);
	void Display(WFont* font);

private:
	WOverlay* m_pNPlayer;
	WOverlay* m_pTopDrv;
	bool m_bShow;
	bool m_bBlink;
	unsigned char m_topIdx;
	unsigned char m_prevIdx;
	unsigned long m_topColor;
	unsigned long m_myColor;
	float m_baseDist;
	float m_topDist;
	float m_myDist;
};

class FrChatFuncDlg : public FrForm
{
public:
	DECLARE_OBJECT(FrChatFuncDlg)

	FrChatFuncDlg();
	virtual ~FrChatFuncDlg();

	void AddChatMsg(const char* msg, int color);

protected:
	void OnChatViewInit(int param);
	void OnShowChatInit(int param);
	void OnHideChatInit(int param);
	void OnBtnShowChatUp();
	void OnBtnHideChatUp();
	void OnBtnSaveChatUp();
	void OnBtnAccuseUp();
	void OnBtnCloseDlgUp();
	bool OnReportDlgResult(int result, FrForm* pForm);

	DECLARE_FRESH_MSGMAP()

private:
	unsigned long m_unused110;
	FrButton* m_pBtnShowChat;
	FrButton* m_pBtnHideChat;
	unsigned long m_unused11c;
	unsigned long m_unused120;
	FrEdit* m_pChatView;
	FrReportDlg* m_pReportDlg;
	unsigned long m_unused12c;
};
