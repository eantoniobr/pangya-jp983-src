#pragma once

#include "frform.h"
#include "actor.h"
#include "frcmdtarget.h"
#include "noticeimage.h"

namespace FrGDI
{
	enum eTextAlign;
}

class FrListBox;
class FrStatic;
class FrGaugeBar;
class FrArea;
class FrGraphicInterface;
class Bitmap;
struct sRivalData;

bool RankCompare(const void* a, const void* b);
bool ApproachRankCompare(const void* a, const void* b);

class FrRankForm : public FrForm
{
	friend class CScore;

	DECLARE_OBJECT(FrRankForm)

	FrRankForm();

	void Align();
	// 983 0077ba30: selecao da lista (rival de IA do Grand Prix: id em +0x130, sem oid)
	void SetSel983(unsigned long oid, unsigned short aiId, unsigned char aiType);
	void SortRank();
	void Resize();
	void SetCaptionType(unsigned char type);

protected:
	void OnRankInit(int param);
	void OnRankOwnerDraw(int param);
	void OnRankLBtnDown();
	void OnRankRBtnUp();
	void OnRankDClick();
	void OnCenterBtnUp();
	void OnInfoBtnUp();
	void OnSizeBtnUp();
	void OnBoardInit(int param);
	void OnBar01Init(int param);
	void OnBar02Init(int param);

	virtual void OnProc(const float deltaTime);

private:
protected:
	// 983 (sessao 130): sizeof 0x170 (operator new 007845ea); deslocamentos pelo construtor 00781430 e pelos acessos de OnProc,
	// SetCaptionType, SortRank, OnRankOwnerDraw e CScore::HandleMsg (645 entre parenteses). Os nomes m_unk12d/m_unk12e/m_unk134 sao do 645.
	FrListBox* m_pList;          // 0x110
	FrStatic* m_pBoard;          // 0x114
	unsigned long m_unk118_983;  // 0x118 (novo no 983; nao iniciado no construtor)
	const Bitmap* m_pPcIcon;     // 0x11c (0x118)
	unsigned char m_size;        // 0x120 (0x11c)
	unsigned char m_captionType; // 0x121 (0x11d)
	unsigned long m_tieUid;      // 0x124 (0x120)
	unsigned long m_lastUid;     // 0x128 (0x124)
	unsigned long m_selOid;      // 0x12c (0x128)
	unsigned short m_unk130_983; // 0x130 (novo no 983; zerado no construtor)
	unsigned char m_memberCount; // 0x132 (0x12c)
	unsigned char m_unk12d;      // 0x133: estado da legenda (1..4)
	unsigned char m_unk12e;      // 0x134: buraco do ultimo aviso
	unsigned char m_scrollCount;     // 0x135 (0x12f)
	float m_captionTime;             // 0x138 (0x130)
	unsigned char m_unk134[0x13];    // 0x13c (0x134); [0] = member count copy
	const Bitmap* m_pMedalBmp[4];    // 0x150 (0x148) gold, silver, bronze, noaward
	const Bitmap* m_pTeamRankBmp[2]; // 0x160 (0x158) red, blue
	const Bitmap* m_pRankBgBmp;      // 0x168 (0x160)
	void* m_pContainer983;           // 0x16c (novo no 983): CContentsDoc::GetContainer(0xaa) quando 0x10594 == 0xb, senao NULL

	DECLARE_FRESH_MSGMAP()
};

class FrRankForm2 : public FrForm
{
	DECLARE_OBJECT(FrRankForm2)

	FrRankForm2();

	void SortRank();

protected:
	void OnRankInit(int param);
	void OnRankOwnerDraw(int param);

private:
protected:
	FrListBox* m_pList;              // 0x110
	const Bitmap* m_pMedalBmp[4];    // 0x114 gold, silver, bronze, noaward
	const Bitmap* m_pTeamRankBmp[2]; // 0x124 red, blue
	const Bitmap* m_pRankBgBmp;      // 0x12c
	const Bitmap* m_pPcIcon;         // 0x130
	unsigned long m_unk134;

	DECLARE_FRESH_MSGMAP()
};

class FrRankForm3 : public FrForm
{
	DECLARE_OBJECT(FrRankForm3)

	friend class CScore;

	FrRankForm3();

	void SetScore(int redScore, int blueScore);
	void SetCaptionType(unsigned char type);

protected:
	virtual void OnProc(const float deltaTime);

	void OnRankInit(int param);
	void OnRankOwnerDraw(int param);
	void OnBoardInit(int param);
	void OnScoreGaugeInit(int param);
	void DrawDigit(FrGraphicInterface* gdi, char* text, WPoint pos,
		unsigned long color, FrGDI::eTextAlign align, bool narrow);
	void OnSizeBtnUp();
	void OnScoreInfoInit(int param);
	void OnScoreInfoOwnerDraw();
	void LoadBitmaps();

	FrListBox* m_pList;          // 0x110
	FrStatic* m_pBoard;          // 0x114
	FrGaugeBar* m_pScoreGauge;   // 0x118
	FrArea* m_pScoreInfo;        // 0x11c
	unsigned char m_size;        // 0x120
	unsigned char m_captionType; // 0x121
	unsigned long m_selOid;      // 0x124
	unsigned char m_memberCount; // 0x128
	unsigned char m_unk129;
	unsigned char m_scrollCount; // 0x12a
	float m_captionTime;         // 0x12c
	const Bitmap* m_pRedEmblem;  // 0x130
	const Bitmap* m_pBlueEmblem; // 0x134
	const Bitmap* m_pRankBgBmp;  // 0x138
	const Bitmap* m_pDigit[10];  // 0x13c
	const Bitmap* m_pPlus;       // 0x164
	const Bitmap* m_pMinus;      // 0x168
	unsigned long m_unk16c;      // 0x16c (983: zerado em OnRankInit)
	const Bitmap* m_pPremiumIcon; // 0x170 (golf/premium_score; substitui o icone de PC do 645)
	int m_score[2];              // 0x174 red, blue
	unsigned long m_unk17c;

	DECLARE_FRESH_MSGMAP()
};

class CExhibition;
struct FrListItem;

class CRankExData
{
public:
	CRankExData();
	~CRankExData();

	void InitAreaStage(FrArea* pArea);
	void Clear();
	void OnProc(float deltaTime);
	void CreateLeaderPet(const WRect& rect);
	void SetActive(bool active);
	bool IsMotionFinished();
	void ResetStage();
	void InitRivalData();
	void InitMedalData();
	void DrawRankItem(FrListItem* pItem);
	void DrawStageArea();
	void SetLeader();
	void ShowLeader();
	void ClearRival();
	void SetRivalData();

private:
public:
	sRivalData* m_pRival;            // 0x00
	float m_motionLength;            // 0x04
	float m_time;                    // 0x08
	int m_leader;                    // 0x0c
	int m_showLeader;                // 0x10
	CExhibition* m_pExhibition;      // 0x14
	FrListBox* m_pList;              // 0x18
	FrArea* m_pStage;                // 0x1c
	FrStatic* m_pBoard;              // 0x20
	const Bitmap* m_pMedalBmp[4];    // 0x24 gold, silver, bronze, noaward
	const Bitmap* m_pTeamRankBmp[2]; // 0x34 red, blue
	const Bitmap* m_pRankBgBmp;      // 0x3c
	unsigned long m_unk40;            // 0x40 (983: zerado em InitMedalData)
	const Bitmap* m_pZeroIcon;       // 0x44
	const Bitmap* m_pPremiumIcon;    // 0x48
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbSetleaderFunclets(); // HACK: EH funclets of the naked SetLeader (nakedify)
#endif
};

class FrRankFormEx : public FrForm
{
	friend class CScore;

	DECLARE_OBJECT(FrRankFormEx)

	FrRankFormEx();
	virtual ~FrRankFormEx();

protected:
	void OnStageAreaInit(int param);
	void OnStageAreaOwnerDraw();
	void OnRankInit(int param);

public:
	void SortRank();
	sRivalData* GetRival();

protected:
	void OnRankOwnerDraw(int param);
	void OnBoardInit(int param);

public:
	void Clear();
	void SetActive(bool active);

protected:
	void SetLeader();
	void ShowLeader();

	virtual bool OnInit();
	virtual void OnProc(const float deltaTime);

public:
	bool IsMotionFinished();
	void ResetStage();

protected:
	CRankExData m_data; // 0x110

	DECLARE_FRESH_MSGMAP()
};

class FrEdit;

class FrAwardForm : public FrForm
{
#ifndef REBANG_SEMANTIC_ONLY
	// HACK: literal hosts of the naked CalcResult / OnUserListOwnerDraw / OnProc (see scoreboard.cpp)
	friend class FrUserInfoForm* USERINFODLG();
	friend class CMessengerInfo* MESSENGER();
	friend class BuddyManager* Buddy();
#endif
	DECLARE_OBJECT(FrAwardForm)

	FrAwardForm();
	virtual ~FrAwardForm();

	virtual bool Close(bool bFade);

protected:
	void OnUserListInit(int param);
	void OnUserListOwnerDraw(int param);
	void OnTab0Init(int param);
	void OnTab1Init(int param);
	void OnExpBar0Init(int param);
	void OnExpBar1Init(int param);
	void OnExpBar2Init(int param);
	void OnExpBar3Init(int param);
	void OnExp0Init(int param);
	void OnExp1Init(int param);
	void OnExp2Init(int param);
	void OnExp3Init(int param);
	void OnExpEnd0Init(int param);
	void OnExpEnd1Init(int param);
	void OnExpEnd2Init(int param);
	void OnExpEnd3Init(int param);
	void OnLevel0Init(int param);
	void OnLevel1Init(int param);
	void OnLevel2Init(int param);
	void OnLevel3Init(int param);
	void OnLevelUp0Init(int param);
	void OnLevelUp1Init(int param);
	void OnLevelUp2Init(int param);
	void OnLevelUp3Init(int param);
	void OnMatchRes0Init(int param);
	void OnMatchRes1Init(int param);
	void OnGainedLadderPoint0Init(int param);
	void OnGainedLadderPoint1Init(int param);
	void OnLadderPoint0Init(int param);
	void OnLadderPoint1Init(int param);
	void OnNextLevelTextInit(int param);

	virtual bool OnInit();
	virtual void OnProc(const float deltaTime);

	void CalcResult();
	void CalcResultMatch();

	const char* m_pSfxName;            // 0x110
	float m_unk114;                    // 0x114
	int m_order[4];                    // 0x118
	FrListBox* m_pUserList;            // 0x128
	FrGaugeBar* m_pExpBar[4];          // 0x12c
	FrStatic* m_pExp[4];               // 0x13c
	FrStatic* m_pExpEnd[4];            // 0x14c
	FrArea* m_pLevel[4];               // 0x15c
	FrArea* m_pLevelUp[4];             // 0x16c
	FrArea* m_pMatchRes[2];            // 0x17c
	unsigned long m_unk184[4];         // 0x184
	unsigned long m_unk194[4];         // 0x194
	unsigned long m_unk1a4[4];         // 0x1a4
	unsigned long m_unk1b4;            // 0x1b4
	int m_unk1b8;                      // 0x1b8
	FrStatic* m_pGainedLadderPoint[2]; // 0x1bc
	FrStatic* m_pLadderPoint[2];       // 0x1c4
	FrEdit* m_pNextLevel;              // 0x1cc
	unsigned long m_unk1d0;
	float m_unk1d4;           // 0x1d4
	const Bitmap* m_pBmp[15]; // 0x1d8 (983: [2]=premium+10, [3..10]=bonus_mascot_*, [11..12]=bonus_ma/2, [13]=zero_vs, [14]=assist_title)
	char unk983_fim[0xc];     // 0x214, sizeof 0x220

	DECLARE_FRESH_MSGMAP()
};

class WOverlay;
class WTitleFont;
class CSimpleUI;
class WVector;

class cAquireItem
{
public:
	struct sPrizeSlot
	{
		std::map<unsigned long, int> m_items;
	};

	cAquireItem();
	~cAquireItem();

	void Reset();
	void OnProc(float delta);
	void DisplayPrizeList(int index);
#ifndef REBANG_SEMANTIC_ONLY
	// HACK: body of DisplayPrizeList under another name (see scoreboard.cpp)
	void RbDisplayPrizeListImpl(int index);
#endif

protected:
	WVector GetPlayer2DPos(int index);

	const Bitmap* m_pFrame[3];                    // 0x0
	sPrizeSlot m_slot[4];                         // 0xc
	const Bitmap* m_pBubble[3];                   // 0x3c
	std::map<unsigned long, WOverlay*> m_icon[4]; // 0x48
	WTitleFont* m_pFont;                          // 0x78
	CSimpleUI* m_pNumberUI;                       // 0x7c
	float m_time;                                 // 0x80
	float m_maxTime;                              // 0x84, sizeof 0x88
};

class FrButton;

class FrScoreForm : public FrForm
{
#ifndef REBANG_SEMANTIC_ONLY
	// HACK: literal hosts of the naked OnHoleListOwnerDraw / OnGolferListOwnerDraw / OnDraw (see scoreboard.cpp)
	friend int IsPcBang();
	friend class FrRankingDlg* RANKINGDLG();
	friend bool IsWebLogin();
#endif
	friend class CScore;

	DECLARE_OBJECT(FrScoreForm)

	enum eState
	{
		STATE_NORMAL,
		STATE_HIDE,
		STATE_RESULT,
		STATE_FINAL,
	};

	FrScoreForm();

	void SetState(eState state);
	void Resize();
	void SortLists(bool force);
	void ChangeTurn();
	void UpdatePang();
	void UpdatePang983(); // 00788d70 (983)
	void SetTypeBtn();
	void SetPPL(const char* name);
	void SetDesc();

protected:
	void LoadBitmaps();

	void OnBar2Init(int param);
	void OnBar3Init(int param);
	void OnFront9BtnInit(int param);
	void OnFront9BtnUp();
	void OnBack9BtnInit(int param);
	void OnBack9BtnUp();
	void OnShotBtnUp();
	void OnGraphBtnUp();
	void OnVersusBtnUp();
	void OnPuttBtnUp();
	void OnPangBtnUp();
	void OnShotBtnInit(int param);
	void OnGraphBtnInit(int param);
	void OnPuttBtnInit(int param);
	void OnPangBtnInit(int param);
	void OnVersusBtnInit(int param);
	void OnHoleListInit(int param);
	void OnHoleListOwnerDraw(int param);
	void OnParListInit(int param);
	void OnParListOwnerDraw(int param);
	void OnPangListInit(int param);
	void OnPangListOwnerDraw(int param);
	void OnBlankPanel01Init(int param);
	void OnBlankPanel01OwnerDraw(int param);
	void OnBlankPanel02Init(int param);
	void OnBlankPanel02OwnerDraw(int param);
	void OnBlankPanel03Init(int param);
	void OnBlankPanel03OwnerDraw(int param);
	void OnGolferListInit(int param);
	void OnGolferListOwnerDraw(int param);
	void OnRecordListInit(int param);
	void OnRecordListOwnerDraw(int param);
	void OnTotalListInit(int param);
	void OnTotalListOwnerDraw(int param);

	virtual bool OnInit();
	virtual void OnProc(const float deltaTime);
	virtual void OnDraw();

	void SetFrontBackBtn();
	void DrawShot(FrListItem* item);
	void DrawVersus(FrListItem* item);
	void DrawGraph(FrListItem* item);
	void DrawPutt(FrListItem* item);
	void DrawPang(FrListItem* item);
	void DrawSkins(FrListItem* item);
	void DrawDigit(FrGraphicInterface* gdi, char* text, WPoint pos,
		unsigned long color, FrGDI::eTextAlign align, bool narrow);
	unsigned long GetScoreColor(int score);
	void OnTotalInit(int param);
	void OnPPLInit(int param);
	void OnBoard1Init(int param);
	void OnBoard2Init(int param);
	void OnDrawLinesInit(int param);
	void OnDrawLinesOwnerDraw(int param);
	void OnCancelBtnInit(int param);
	void OnCancelBtnUp();
	void OnCloseBtnInit(int param);
	void OnCloseBtnUp();
	void ConditionalStrCat(char* dest, const char* src);

	eState m_state;          // 0x110
	FrButton* m_pFront9Btn;  // 0x114
	FrButton* m_pBack9Btn;   // 0x118
	FrButton* m_pTypeBtn[6]; // 0x11c shot, graph, putt, pang, skins, versus
	FrListBox* m_pHoleList;  // 0x134
	FrListBox* m_pParList;   // 0x138
	FrListBox* m_pPangList;  // 0x13c
	FrListBox* m_pList[3];   // 0x140 golfer, record, total
	FrButton* m_pCancelBtn;  // 0x14c
	FrButton* m_pCloseBtn;   // 0x150
	FrArea* m_pBar2;         // 0x154
	FrArea* m_pBar3;         // 0x158
	FrArea* m_pPPL;          // 0x15c
	bool m_bPPL;             // 0x160
	int m_order[4];          // 0x164
	bool m_bFront9;          // 0x174
	int m_type;              // 0x178
	float m_aniTime;         // 0x17c
	__int64 m_pang;          // 0x180
	__int64 m_bonusPang;     // 0x188
	int m_playerCount;       // 0x190
	std::map<unsigned long, const Bitmap*> m_bitmap; // 0x194
	const Bitmap* m_pDigit[10];                      // 0x1a0
	const Bitmap* m_pPlus;                           // 0x1c8
	const Bitmap* m_pMinus;                          // 0x1cc
	const Bitmap* m_pPoint;                          // 0x1d0
	const Bitmap* m_pWin;                            // 0x1d4
	const Bitmap* m_pLose;                           // 0x1d8
	const Bitmap* m_pDraw;                           // 0x1dc
	const Bitmap* m_pNoResult;                       // 0x1e0
	const Bitmap* m_pQuestion;                       // 0x1e4
	const Bitmap* m_pArrow;                          // 0x1e8
	const Bitmap* m_pUnused1f0_983;                  // 0x1f0 (983 zera em LoadBitmaps 78b1c9; era o icone de PC do 645)
	const Bitmap* m_pPCIcon;                         // 0x1f4 (983: bitmap golf/premium_score)
	bool m_bShowBlankPanel;                          // 0x1f8
	FrArea* m_pBlankPanel[3];                        // 0x1fc, 0x200, 0x204

	DECLARE_FRESH_MSGMAP()
};

class FrMatchItems : public FrForm
{
	DECLARE_OBJECT(FrMatchItems)

public:
	FrMatchItems();
	virtual ~FrMatchItems();

	void Reset()
	{
		m_bAnimate = true;
		m_bPlaySound = true;
	}

protected:
	virtual bool OnInit();
	void OnViewInit(int param);
	void OnViewOwnerDraw(int param);

protected:
	std::map<unsigned long, WOverlay*> m_icon; // 0x110
	unsigned long m_unk11c;                    // 0x11c
	float m_x;                                 // 0x120
	float m_y;                                 // 0x124
	unsigned long m_unk128[6];                 // 0x128
	FrArea* m_pView;                           // 0x140
	CSimpleUI* m_pNumberUI;                    // 0x144
	bool m_bAnimate;                           // 0x148
	bool m_bPlaySound;                         // 0x149
	int m_count;                               // 0x14c
	int m_unk150;                              // 0x150
	float m_aniTime;                           // 0x154, sizeof 0x158

	DECLARE_FRESH_MSGMAP()
};

class FrScoreDlg;
class FrLevelupItemForm;
class FrTreasureGauge;
class FrNextHole;
class cAquireItem;

// 983: quadro de avisos do placar do Grand Prix ("grandprix_issueboard.lua"; 0x30, em FrGrandPrixRankForm+0x3cc). Nao existe no
// 645. Layout pelo construtor 00796600, destrutor 00796620 e o destrutor do elemento 0078b5e0; nomes e tipos dos elementos meus.
struct sGrandPrixIssue983
{
	std::string text;        // +0x00: "issue_string" (formato do MakeStr)
	int type;                // +0x1c: "issue_string_type" (1..6, escolhido pelo SelectType983)
	std::vector<int> values; // +0x20: "argment_type" (0 = apelido, 1 = placar total, 2 = pang do buraco)
};

class sGrandPrixIssueBoard983
{
public:
	sGrandPrixIssueBoard983();  // 00796600
	~sGrandPrixIssueBoard983(); // 00796620

	bool IsFirst983(int index);                              // 00781b50: rival `index` em 1o
	bool IsBestHolePang983(int index, unsigned char hole);   // 00781b90: ninguem fez mais pang no buraco
	bool IsHoleScore983(int index, unsigned char hole, int score); // 00781c50 (sem chamador no 983)
	void GetArgText983(int index, int argType, std::string& text); // 007895c0
	int SelectType983(int index, unsigned char hole, sGrandPrixIssue983& issue); // 00789f10 (o 3o argumento nao e lido)
	void FindIssue983(int type, sGrandPrixIssue983& issue); // 0078b750
	void MakeText(int index, unsigned char hole);          // 00796a90
	bool Load(std::string filename);                       // 00799400
	const std::string& GetText();                          // 0077bd90
	void SetCaption983(FrStatic* pText);                   // 00781b20: SetCaption(K2L_Compatibility(m_text))

	std::vector<sGrandPrixIssue983> m_list; // +0x00
	int m_unk10;                            // +0x10 (o construtor nao zera)
	std::string m_text;                     // +0x14
};

// 983: efeito do placar do Grand Prix (em FrGrandPrixRankForm+0x424, 0xcc). Layout pelo construtor 00796200, destrutor 00796290 e
// Init 0077bda0; nomes meus.
class FrGrandPrixRankEffect983
{
public:
	FrGrandPrixRankEffect983();  // 00796200
	~FrGrandPrixRankEffect983(); // 00796290

	void Init();                         // 0077bda0
	void Load();                         // 00799890: LoadLua983("grandprix_ingame_ui.lua") + LoadBitmaps983
	bool LoadLua983(std::string filename); // 00796ec0: tabela "grandprix_scoreborad_notice_table"
	void LoadBitmaps983();               // 0078a220
	void Draw(FrGraphicInterface* pGDI); // 0077def0
	void Start(const WRect& rect);       // 0077e130

	int m_mode;                           // +0x00: 2 no Init (nada a desenhar), 0 no Show, 1 no 0078eb00
	std::string m_name[3];                // +0x04: "text_bg_start_img", "text_bg2_middle_img", "text_bg3_end_img"
	const Bitmap* m_bmp58[3];             // +0x58: GetBitmap dos tres nomes
	std::vector<std::string> m_names64[2]; // +0x64: "hole_out_waiting_img1/2_file_name" / "next_hole_waiting_img1_file_name"
	std::vector<const Bitmap*> m_bmps84[2]; // +0x84
	WPoint m_textPos983;                  // +0xa4: "notice_text_img_pos_x/y" (so o y e usado)
	WRect m_rectAC;                 // +0xac
	WRect m_rectBC;                 // +0xbc
};

// 983: placar do Grand Prix ("grandprix_scoreboard"; RTTI .?AVFrGrandPrixRankForm@@, vtables 00d24c34 / 00d24c28 / 00d24c20;
// sizeof 0x4f0 pelo `operator new` do CreateForm 007968f0). Nao existe no 645. Layout pelo construtor 00796650, destrutor 00796770 e
// Init983 0077e310 (sessao 132); nomes dos metodos e campos sao meus (o 983 so tem a RTTI da classe).
class FrGrandPrixRankForm : public FrForm
{
	DECLARE_OBJECT(FrGrandPrixRankForm)

public:
	FrGrandPrixRankForm(); // 00796650
	virtual ~FrGrandPrixRankForm(); // 00796770

	virtual bool OnInit();                  // 007998d0 (slot 32)
	virtual void OnDraw();                  // 0077e440 (slot 8)
	virtual void OnProc(const float deltaTime); // 00788c10 (slot 9)

	void ClearRankList();             // 0077be20: m_pRankList->ClearItem()
	void UpdateBlink983(float dt);    // 0077be30: +0x198/+0x19c/+0x1a0
	bool UpdateTimer983(float dt);    // 0077be80: +0x404 (0.05 s)
	float GetWaitTime();              // 0077bee0: +0x180
	void Fn0077bef0_983();            // +0x3fc = 1
	void Fn0077bf00_983();            // +0x3fc = 0
	bool Fn0077bf10_983();            // devolve +0x3fc
	void Fn0077bf20_983();            // +0x3fd = 1
	void ReleaseTitleFont983();       // 0077bf30
	void ResetSounds983();            // 0077bf90: +0x41c..+0x422 = 0
	void Init983();                   // 0077e310
	void ScrollByKey983(float dt);    // 0077e460
	void ResetPoints983();            // 0077e4e0: +0x138..+0x17c
	void CreateTitleFont983();        // 0077e5d0
	void Fn0077e660_983();
	void Fn0077ea00_983();
	void UpdateHole983();             // 00781c80: +0x3fe/+0x400 pelo buraco atual
	bool LoadBitmaps983();            // 00781cd0: GetBitmap dos nomes lidos pelo LoadUi983
	void SetWaitTime(float t);        // 00781dc0: +0x180 (golfdoc +0x195 == 1 troca pelo valor fixo)
	void Fn00782070_983();            // guarda o rank de cada jogador (+0x152 -> +0x1a8)
	void PlaySound983(int index, bool bPlay); // 007820f0: m_soundList[index] (0 = BGM)
	const char* GetSoundName983(unsigned int index); // 00782180
	void PlayCountSound983(int count); // 007821d0: +0x41c..+0x41f
	void PlayRankSound983(int type);  // 00782260: +0x420..+0x422
	int GetRankType983(unsigned char hole, const sRivalData* pRival); // 007822d0
	void Fn00782330_983(bool b);      // +0x423
	void Show(bool bShow);            // 007858e0: SetActive/SetVisible + 007820f0 (+0x408, +0x424)
	void UpdateWait983(float dt);     // 00785940: conta +0x180 e avisa o GolfRule (0x33b)
	void Align983();                  // 00788c50
	void RefreshRank();               // 00788cf0: lista dos jogadores (CSharedDoc +0x1042c, flag +0x36) quando golfdoc +0x158 & 0x2000
	void Fn007896d0_983(unsigned short v); // ... e RefreshRank
	bool LoadUi983(std::string filename); // 00797230: "grandprix_ingame_ui.lua" (posicoes, espera, nomes das imagens, sons)
	void Fn00797980_983(unsigned short v); // texto por K2L_Compatibility
	void SetIssueText983(int);         // 00782050 (sem chamador no 983): m_issueBoard.SetCaption983(m_pIssueText)
	void Fn0078eb00_983();            // +0x408 = 1, GetIndex, 007822d0/00782260

	FrListBox* m_pRankList;           // +0x110 (ClearItem/AddItem)
	FrWnd* m_pWnd114;                 // +0x114
	FrStatic* m_pIssueText;           // +0x118 (SetCaption no 00797980)
	FrWnd* m_pUnk11c;                 // +0x11c: o 983 copia o retangulo dele (+0x34) na mensagem 0x178
	FrWnd* m_pWnd983[6];              // +0x120..+0x134 (SetVisible pelo +0x423)
	WPoint m_point983[9];             // +0x138..+0x17c
	float m_waitTime;                 // +0x180
	WTitleFont* m_pTitleFont;         // +0x184
	WPoint m_offset983;               // +0x188
	WPoint m_pos983;                  // +0x190
	float m_blinkTime983;             // +0x198
	float m_blinkElapsed983;          // +0x19c
	bool m_bBlink983;                 // +0x1a0
	std::string m_name1a4[3];         // +0x1a4
	const Bitmap* m_p1f8[3];          // +0x1f8 (GetBitmap dos nomes +0x1a4, no 00781cd0)
	std::string m_name204[11];        // +0x204
	const Bitmap* m_p338[11];         // +0x338 (nomes +0x204)
	std::string m_name364[3];         // +0x364
	const Bitmap* m_p3b8[3];          // +0x3b8 (nomes +0x364)
	WPoint m_point3c4;                // +0x3c4
	sGrandPrixIssueBoard983 m_issueBoard; // +0x3cc
	bool m_unk3fc;                    // +0x3fc
	bool m_unk3fd;                    // +0x3fd
	unsigned char m_curHole983;       // +0x3fe
	int m_holeIndex983;               // +0x400
	float m_timer983;                 // +0x404
	bool m_unk408;                    // +0x408: zerado pelo CScore na mensagem 0x172
	std::vector<std::string> m_soundList; // +0x40c
	bool m_bSoundPlayed983[7];        // +0x41c
	bool m_bShowWnd983;               // +0x423
	FrGrandPrixRankEffect983 m_effect; // +0x424, sizeof 0x4f0

	DECLARE_FRESH_MSGMAP()
};

class CScore : public IActor, public FrCmdTarget
{
	class CScoreBg
	{
	public:
		CScoreBg();
		~CScoreBg();

		void ScoreBgCommand(int command);

	protected:
		void SetDesktopWallPaper(bool bShow, bool bDefault);

		Bitmap* m_pBitmap; // 0x0
		bool m_bCaptured;  // 0x4
#ifndef REBANG_SEMANTIC_ONLY
	public:
		static void __cdecl
		RbScorebgcommandFunclets(); // HACK: EH funclets of the naked ScoreBgCommand (nakedify)
#endif
	};

protected:
	CScore();

public:
	DECLARE_OBJECT(CScore)

	virtual ~CScore() { }

	virtual void OnLoad();
	virtual void OnReload();
	virtual void OnProcess(float delta);
	virtual void OnDisplay();
	virtual void OnDestroy();
	virtual void HandleMsg(const MsgObject& msg);

protected:
	void OnCloseBtnUp();
	bool OnRankFormExResult(int result, FrForm* pForm);
	bool UpdateRivals();
	bool OnGuildScoreFormResult(int result, FrForm* pForm);
	bool OnGrandPrixRankFormResult(int result, FrForm* pForm); // 0077c540 (983)

private:
	void ImageSortByCharacterIndex(std::vector<sNoticeImage>& images);
	void CheckOpenedDlg();

protected:
	int m_state;                               // 0x1c
	float m_unk20;                             // 0x20
	int m_unk24;                               // 0x24
	int m_unk28;                               // 0x28
	int m_unk2c;                               // 0x2c
	int m_unk30;                               // 0x30
	FrScoreForm* m_pScore;                     // 0x34
	FrRankForm* m_pRank;                       // 0x38
	FrRankForm2* m_pRank2;                     // 0x3c
	FrRankForm3* m_pRank3;                     // 0x40
	FrRankFormEx* m_pRankEx;                   // 0x44
	FrGrandPrixRankForm* m_pGrandPrix;         // 0x48 (983; zerado no construtor 00799f10): placar do Grand Prix; os membros seguintes andam +4
	FrForm* m_pAward;                          // 0x48
	FrMatchItems* m_pItems;                    // 0x4c
	FrScoreDlg* m_pGuildScore;                 // 0x50
	std::vector<FrLevelupItemForm*> m_levelup; // 0x54
	FrTreasureGauge* m_pTreasureGauge;         // 0x64
	FrNextHole* m_pNextHole;                   // 0x68
	FrForm* m_unk6c;                           // 0x6c
	FrForm* m_unk70;                           // 0x70
	float m_unk74;                             // 0x74
	WPoint m_rankPos;                          // 0x78
	cAquireItem* m_pAquire;                    // 0x80
	std::vector<sNoticeImage> m_images;        // 0x84
	CScoreBg m_bg;                             // 0x94, sizeof 0x9c

	DECLARE_FRESH_MSGMAP()
#ifndef REBANG_SEMANTIC_ONLY
public:
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbOnprocessFunclets(); // HACK: EH funclets of the naked OnProcess (nakedify)
#endif
};
