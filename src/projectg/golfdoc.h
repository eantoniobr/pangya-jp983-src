#pragma once

#include <bitset>
#include "encrypttypes.h"
#include "parttidlist.h"
#include <map>
#include <list>
#include "objectfactory.h"

class WPolySoup;
class CAutoTarget;
#include "../shared/globalgamedefine.h"
class CSky;

struct sProperty
{
	float bound;
	float roll;
	float min[3];
	float max[3];
	unsigned char pass;
	unsigned char ground;

	sProperty()
	{
		boundSound[0] = 0;
		rollSound[0] = 0;
	}
	~sProperty() { }

	char boundSound[64];
	char rollSound[64];
	char stepSound[64];
};

class CPropertyInfo
{
public:
	CPropertyInfo() { m_defaultIndex = -1; }
	~CPropertyInfo();

	void Init(const TiXmlDocument& doc);
	int GetPropertyIndex(const char* texture);
	const sProperty& GetProperty(int index);

private:
	std::vector<sProperty> m_property;
	std::map<std::string, int> m_textureIndex;
	int m_defaultIndex;
#ifndef REBANG_SEMANTIC_ONLY
public:
	// HACK: never defined; kept for the PCH name-count canaries (EH funclet holder of a former naked Init)
	static void __cdecl RbInitFunclets();
#endif
};

struct sWave
{
	char texture[32];
	float width;
	float freq;
};

class CWaveInfo
{
public:
	CWaveInfo() { }
	~CWaveInfo() { m_wave.clear(); }

	void Load(const char* filename);

	char* GetTexture(int index) { return m_wave[index].texture; }
	float GetWidth(int index) { return m_wave[index].width; }
	float GetFreq(int index) { return m_wave[index].freq; }

private:
	std::map<int, sWave> m_wave;
};

struct sRiver
{
	float scrollVel;
	float tileHead;
	float tileSide;
	float depth;
};

class CRiverInfo
{
public:
	CRiverInfo() { }
	~CRiverInfo() { m_river.clear(); }

	void Load(const char* filename);

	float GetScrollVelocity(int index) { return m_river[index].scrollVel; }
	float GetHeadTile(int index) { return m_river[index].tileHead; }
	float GetSideTile(int index) { return m_river[index].tileSide; }
	float GetDepth(int index) { return m_river[index].depth; }

private:
	std::map<int, sRiver> m_river;
};

class CMapInfo
{
public:
	void Init(const TiXmlDocument& doc, unsigned char index);
	const char* FindItem(const std::string& key);

private:
	std::map<std::string, std::string> m_item;
};

#ifdef REBANG_GOLFRULE_PCH
const float BAR_MIN = 105.0f; // golfrule: emitted before BAR_END
#endif
const float BAR_MIDDLE = 105.0f;
const float BAR_END = 500.0f;
const float BAR_MARGIN = 8.0f;
const float BAR_START = 140.0f;

struct sBar
{
	float power;
	float impact;
	float gauge;
	float gaugeStep;
	int grade;
	bool bFullPower;
	int dir;
	float center;
	float calipers;

	void Reset();
#ifdef REBANG_GOLFRULE_PCH
	float Persent() const;
	float Delta() const;
#endif
};

#pragma pack(push, 1)
struct sWinningPrize
{
	unsigned long holeInOne;
	unsigned long albatross;
	unsigned long eagle;
	unsigned long birdie;
	unsigned long par;
	unsigned long bogey;
	unsigned long unk983_18; // 983: 7 dwords (AddPlayer 006a7470 zera 0x56d..0x589); lugar provisorio
};

struct sPrizeInfo
{
	unsigned long typeId;
	unsigned short unknown;
	unsigned short quantity;
	int type;
	unsigned long unk983_c; // 983: 0x10 por registro (sPlayerData 0xdb0); lugar provisorio
};
#pragma pack(pop)

struct sPlayerData
{
	int state;
	unsigned char index;
	WVector startPos;
	WVector pos;
	WVector unk983_20; // 983: +0xc antes do stroke (stroke em +0x2c)
	WCrypticValue<unsigned char> stroke[18];
	WCrypticValue<unsigned char> putt[18];
	WCrypticValue<int> pang[18];
	WCrypticValue<int> skinsPang[18];
	unsigned long color;
	unsigned long uid;
	unsigned long oid;
	unsigned char itemNum;
	unsigned long item;
	unsigned long unk983_4c0; // 983: zerado junto com item no AddPlayer (006a7553)
	unsigned char teeOrder;
	WCrypticValue<float> gauge;
	unsigned short unusedWord;
	unsigned char bunker;
	unsigned char timeout;
	unsigned char giveUp;
	unsigned long shotFlag;
	// HACK: std::bitset<32> stays instantiated in the PCH (its names keep the PCH name count of the
	// canaries SaveScreenShot/mascotinfodlg); the original field zeroes inline, no bitset COMDATs
	typedef char rb_bitset32[sizeof(std::bitset<32>)];
	WFlags event;
	unsigned char flag;
	unsigned char team;
	unsigned char teammate;
	unsigned long shotTime;
	unsigned char order : 4;
	unsigned char rank : 4;
	unsigned char totalStroke;
	int score;
	WCrypticValue<int> totalPang;
	WCrypticValue<int> bonusPang;
	unsigned long holeNum;
	WCrypticValue<int> power;
	WCrypticValue<int> accuracy;
	WCrypticValue<int> control;
	WCrypticValue<int> spin;
	WCrypticValue<int> curve;
	unsigned char chatBlock;
	sWinningPrize prize;
	unsigned char extPrizeNum;
	sPrizeInfo extPrize[128];
	unsigned char holeInPose;
	unsigned char holeInCollision;
	__int64 skinsTotalPang;
	__int64 skinsSumPang;
	__int64 skinsHolePang;
	unsigned char level;
};

struct sTeamData
{
	int state;
	WCrypticValue<unsigned char> stroke[18];
	WCrypticValue<unsigned char> putt[18];
	WCrypticValue<int> pang[18];
	unsigned char totalStroke;
	int score;
	WCrypticValue<int> totalPang;
	WCrypticValue<int> bonusPang;
	WVector pos;
	unsigned long color;
	WCrypticValue<float> gauge;
	unsigned char bunker;
	unsigned char shooter;
	unsigned char club;
	unsigned char turn;
	unsigned char teeShooter;
	unsigned char holeInPose;
	unsigned char holeInCollision;
};

enum eApproachMissionType
{
};

enum eApproachPrizeType
{
};

enum eApproachWinnerType
{
};

struct sHoleData
{
	WVector tee;
	WVector pin;
	unsigned char par;
	unsigned char playerNum;
	unsigned char rank[4];
	unsigned char result;
	unsigned char carry;
	__int64 pang;
	__int64 basePang;
	unsigned long checkSum;
	unsigned long reserved;
};

struct sCameraData
{
	float distance;
	float height;
	float clearance;
	WVector target;
	float angle;
	float angleOffset;
	WMatrix mat;
	float pitch;
};

#pragma pack(push, 1)
struct sShotResultMsg
{
	unsigned long unused0;
	float pos[3];
	unsigned char unused10;
	unsigned char flag;
	unsigned char unused12[0x14]; // 983: sizeof 0x26 (era 0x25)
};

struct sUnknown46e
{
	unsigned long value;
	unsigned char flag;
};
#pragma pack(pop)

class CTaskDoc : public IObject
{
public:
	CTaskDoc();
	virtual ~CTaskDoc();

#ifdef REBANG_TASKMANAGER_PCH // HACK: taskmanager_pch.h
	CTask* GetTask() const;

#endif
protected:
#ifdef REBANG_TASKMANAGER_PCH // HACK: taskmanager_pch.h
	CTask* m_pTask;

	friend class CTaskManager;
#else
	unsigned long m_unused4;
#endif
};

#if defined(REBANG_GOLFRULE_PCH) || defined(REBANG_GOLFPLAYER_CPP)
enum eTeamName
{
	TEAM_RED,
	TEAM_BLUE
};

#endif
class CPangyaCorrectionObject;
class CPangyaAddCorrectionObj;
class CPangyaCorrectionSetObject;

class CGolfDoc : public CTaskDoc
{
	DECLARE_OBJECT(CGolfDoc)

protected:
	CGolfDoc();

public:
	struct sTarget
	{
		sTarget()
		{
			m_unused0 = 0;
			m_flag = 0;
		}

		unsigned long m_unused0;
		unsigned char m_unused4[0xc];
		unsigned char m_flag;
	};

	virtual ~CGolfDoc();

	sPlayerData* GetPlayer(unsigned char index);
	sTeamData* GetTeam(unsigned char index);
	bool IsCurrentPlayerEvent983(unsigned long flag); // JP 983: 00663870
	void MakePlayer(unsigned char num);
	void MakeTeam();
	void ResetTeamVars();
	void LoadXml(const char* filename, unsigned char index, bool reload);
	void RefreshPlayerNum();
	void SetPlayerLevel(unsigned char index);
	CPartTidList& GetPartTidList(unsigned char index);
	void SetPartTidList(unsigned char index, unsigned long charTid,
		unsigned char hairColor, unsigned char shirtColor,
		unsigned long* partTid, unsigned long* partId);
	void SetApproachCurHoleResult(sApproachResultData& result);
	void SetApproachGameResult(sApproachResultData& result);
	void ApproachDataAllClear();
	void ClearApproachCurHoleResult();
	void ClearApproachGameResult();
	sApproachResultData* GetAppMyCurHoleResult();
	sApproachResultData* GetAppMyGameResult();
	void MakeHoleData();
	void ClearShotResultMsg();
	void InitShotResultMsg();
	void LogStrokeScore();
	void UpdateBright(float bright);
	void SendReport();
	WMatrix MakeTopViewCameraMatrix(bool check);
	WMatrix GetDefaultCamera();
	void MakeDefaultCamera(bool apply);
	sCameraData& GetCameraData() { return m_cameraData; }
	void SetApproachMissionDesc(const char* desc);
	char* GetApproachMissionDesc();
	void SetApproachMissionType(eApproachMissionType type);
	void SetApproachPrizeType(eApproachPrizeType type);
	void SetApproachWinnerType(eApproachWinnerType type);
	eApproachMissionType GetApproachMissionType() const;
	eApproachPrizeType GetApproachPrizeType() const;
	eApproachWinnerType GetApproachWinnerType() const;
	std::list<sApproachResultData*>& GetApproachCurHoleResult();
	std::list<sApproachResultData*>& GetApproachGameResult();
	void AddApproachTotalPrize(unsigned long prize);
	unsigned long GetApproachTotalPrize() const;
	WMatrix* MakeTopViewCameraMatrix(WMatrix& out, bool bTop);

	unsigned char GetCurrentPlayer() { return m_currentPlayer; }
#ifdef REBANG_GOLFRULE_PCH
	unsigned char& GetUIAlpha();
	sBar& GetBar();
	unsigned long& GameMode();
	void NetGameEnd();
	bool IsNetGameEnd();
	void SetTeeShotReady(bool);
	bool IsTeeShotReady();
	void SetTeamGameWinner(eTeamName);
	void SetStatUpdated(bool);
	bool GetStatUpdated() const;
	bool GetApproachReloaded();
	void SetApproachReloaded(bool);
#endif
#ifdef REBANG_GOLFPLAYER_CPP // golfplayer.cpp defines it (emission order); other includers keep their names
	eTeamName GetTeamGameWinner();
#endif
	unsigned char GetCurrentPlayerNum();
	void SetCurrentPlayerNum(int num);
	unsigned char GetPlayerNum() { return m_playerNum; }
	bool IsPause();
	void SetPause(bool bPause);
	bool GetDay();
	void SetDay(bool bDay) { m_bDay = bDay; }
	bool IsReported();
	void SetReport(bool bReport);
	bool IsShowChat();
	void ShowChat(bool bShow);
	int GetSaveChatNum();
	void SetSaveChatNum(int num);
	sHoleData& GetHoleData() { return m_pHoleData[m_currentHole - 1]; }
	void SetHoleRange983(unsigned char hole, float range); // JP 983: 00661eb0 (tee e pin do buraco pelo alcance; modo 0xb)
	void SetHoleTees983(unsigned char hole, std::vector<WVector2D>* pTees); // JP 983: 00661f30 (pin + todos os tees; o 1o vira o tee)
#ifdef REBANG_GOLFRULE_PCH // golfrule.cpp: body in golfrule_pch_inl.h / at the original PCH position (emission order)
	sHoleData& GetHoleData(unsigned char hole);
#else
	sHoleData& GetHoleData(unsigned char hole) { return m_pHoleData[hole - 1]; }
#endif

	WPolySoup* m_pPolySoup;
	CSky* m_pSky;
	CAutoTarget* m_pAutoTarget;
	CPropertyInfo m_propertyInfo;
	CMapInfo m_mapInfo;
	CWaveInfo m_waveInfo;
	CRiverInfo m_riverInfo;
	WList<char*> m_modelNameList;
	int m_tutorialMode;
	std::list<unsigned long> m_list7c;
	unsigned long m_unknown88;
	unsigned char m_unused8c[0xc];
	unsigned char m_unknown98;
	unsigned char m_unused99[3];
	std::string m_xmlFile;
	sPlayerData* m_pPlayer;
	sTeamData* m_pTeam;
	int m_teamNum;
	unsigned char m_currentPlayerNum;
	unsigned char m_playerNum;
	unsigned char m_unusedc6[2];
	sHoleData* m_pHoleData;
	unsigned char m_unknowncc;
	unsigned char m_unusedcd[3];
	sBar m_bar; // 983: +0xe0 (Bar() 004ae160: [[0xe47e2c]+0x11024] + 0xe0; o 645 tinha a barra em +0xd0); pedido C23
	sCameraData m_cameraData;
	unsigned long m_gameMode;
	unsigned char m_unknown14c;
	bool m_bPause;
	unsigned char m_unknown14e;
	bool m_bReport;
	bool m_bDay;
	bool m_bShowChat;
	unsigned char m_unused152[2];
	int m_saveChatNum;
	unsigned char m_unknown158;
	unsigned char m_unknown159;
	unsigned char m_unknown15a;
	unsigned char m_unused15b[5];
	unsigned char m_unknown160;
	unsigned char m_unused161[3];
	unsigned long m_unk174_983; // 983: 0x174, o construtor não grava; nome meu
	float m_unknown164; // 983: 0x178, float 0.0 no construtor (PROVISÓRIO: pode ser campo novo e o m_unknown164 antigo ser o de 0x174)
	unsigned char m_currentHole;
	unsigned char m_unused169[3];
	unsigned long m_remainTime;
	unsigned long m_shotTime;
	unsigned char m_shotPhase;
	unsigned char m_currentPlayer;
	unsigned char m_unused176[2];
	float m_bright;
	bool m_bDropRequest;
	bool m_bStopRequest;
	unsigned char m_maxGrade;
	bool m_bStopDlg;
	bool m_bNoStat;
	bool m_b195_983; // 983: 0x195, zerado junto com m_bNoStat (word); nome meu
	unsigned char m_unused181[2];
	float m_unknown184;
	float m_unknown188;
	int m_unknown18c;
	int m_unknown190;
	unsigned short m_unknown194;
	unsigned char m_unused196[2];
	__int64 m_unknown198;
	__int64 m_unknown1a0;
	unsigned long m_unknown1a8;
	unsigned char m_unknown1ac;
	unsigned char m_unused1ad[3];
	__int64 m_unknown1b0;
	__int64 m_unknown1b8;
	unsigned char m_unused1c0[0x168];
	unsigned long m_unknown328[0x21];
	sShotResultMsg m_shotResultMsg[4];
	unsigned char m_unknown440[0x32]; // 983: memset de 0x32 em 0x45c
	sUnknown46e m_unknown46e;
	unsigned char m_unused473;
	CPartTidList m_partTidList[4];
	bool m_bApproach794;
	bool m_bApproach795;
	char m_approachMissionDesc[0x82];
	eApproachMissionType m_approachMissionType;
	eApproachPrizeType m_approachPrizeType;
	eApproachWinnerType m_approachWinnerType;
	std::list<sApproachResultData*> m_approachCurHoleResult;
	std::list<sApproachResultData*> m_approachGameResult;
	unsigned long m_approachTotalPrize;
	// 983 (pedido C26): objetos de correcao do PangYa por jogador (indice = m_currentPlayer); o construtor (0066d240) nao os toca
	CPangyaCorrectionObject* m_pPangyaCorrection983[4];       // +0x860: 0065fe70 (habilidade 0x0a)
	CPangyaAddCorrectionObj* m_pPangyaAddCorrection983[4];    // +0x870: 0065fec0 (0x16)
	CPangyaCorrectionSetObject* m_pPangyaCorrectionSet983[4]; // +0x880: 0065fef0; 0065fed0 zera, 00662200 refaz (conteudo 0xad, 0x23)
	unsigned char m_unk983_890[0x30];                         // 983: sizeof 0x8c0; nao achei quem usa
	static std::stack<CGolfDoc*, std::list<CGolfDoc*> > m_GolfDocInstanceStack;
	// HACK: instantiates stack<CGolfDoc*> (and its list) in the PCH (COMDAT order); reuses the name (PCH name-count canaries)
	typedef char
		rb_bitset32[sizeof(std::stack<CGolfDoc*, std::list<CGolfDoc*> >)];
};

#ifdef REBANG_STDAFX_STATICS
// HACK: header statics that the original emitted only in the units that compiled stdafx.h without the
// PCH (stdafx.cpp itself and videoin.cpp). /Yu units never emit unreferenced header statics, so they are
// kept behind this macro (defined by videoin.cpp) and the PCH stays unchanged.
// golfdoc.h:282-283 in the original line table.
static float BAR_LEN = BAR_END - BAR_START;
static float BAR_MIDPOINT = (BAR_END + BAR_START) * 0.5f;
// The original header of these is unknown; only their .data bytes are known.
static const char* s_taskName[5] = { "CLobbyTask", "CShopTask",
	"CRealMyRoomTask", "ntAvatarChatTask", "CGolfTask" };
static int rb_unknownInt = 0xff;
static char rb_unknownChar = (char)0xff;
// s_courseOrder comes after BAR_END/BAR_START in the original .rdata.
#include "courseorder.h"
#endif

#ifdef REBANG_GOLFRULE_PCH
#ifdef REBANG_GOLFRULE_PCH // golfrule.cpp: inline bodies the original PCH has here (emission order)
#ifndef REBANG_STDAFX_STATICS
static float BAR_LEN =
	BAR_END - BAR_START; // golfdoc.h:282 in the original line table
#endif
inline void CTask::SetPause(bool bPause)
{
	m_bPause = bPause;
}
inline float sBar::Persent() const
{
	return (power - BAR_START) / BAR_LEN;
}

inline float sBar::Delta() const
{
	return impact - center;
}

inline sHoleData& CGolfDoc::GetHoleData(unsigned char hole)
{
	return m_pHoleData[hole - 1];
}
inline unsigned char& CGolfDoc::GetUIAlpha()
{
	return m_unknowncc; // 983: +0xdc (005298f0); o 645 lia +0xcc cru
}
inline sBar& CGolfDoc::GetBar()
{
	return m_bar; // 983: +0xe0 (004ae160); o 645 lia +0xd0 cru
}
inline unsigned long& CGolfDoc::GameMode()
{
	return m_gameMode;
}
inline void CGolfDoc::NetGameEnd()
{
	m_unknown14c = 1; // 983 +0x15c (era o +0x14c cru do 645)
}
inline bool CGolfDoc::IsNetGameEnd()
{
	return m_unknown14c != 0;
}
inline void CGolfDoc::SetTeeShotReady(bool b)
{
	m_unknown14e = b; // 983 +0x15e (era o +0x14e cru do 645)
}
inline bool CGolfDoc::IsTeeShotReady()
{
	return m_unknown14e != 0;
}
inline void CGolfDoc::SetPause(bool b)
{
	m_bPause = b;
}
inline bool CGolfDoc::IsPause()
{
	return m_bPause;
}
inline void CGolfDoc::SetTeamGameWinner(eTeamName t)
{
	*(eTeamName*)&m_teamNum = t; // 983 +0xd0 (era o +0xc0 cru do 645)
}
inline void CGolfDoc::SetReport(bool b)
{
	m_bReport = b; // 983 +0x15f (era o +0x14f cru do 645)
}
inline void CGolfDoc::ShowChat(bool b)
{
	m_bShowChat = b;
}
inline bool CGolfDoc::IsShowChat()
{
	return m_bShowChat;
}
inline void CGolfDoc::SetStatUpdated(bool b)
{
	*((unsigned char*)this + 0x794) = b;
}
inline bool CGolfDoc::GetStatUpdated() const
{
	return *(bool*)((unsigned char*)this + 0x794);
}
inline bool CGolfDoc::GetApproachReloaded()
{
	return *(bool*)((unsigned char*)this + 0x795);
}
inline void CGolfDoc::SetApproachReloaded(bool b)
{
	*((unsigned char*)this + 0x795) = b;
}
#endif

#endif

#ifdef REBANG_GOLFTASK_PCH // golftask.cpp: golfdoc.h:546 in the original (PCH inline, emission order)
inline bool CGolfDoc::IsReported()
{
	return m_bReport;
}
#endif
