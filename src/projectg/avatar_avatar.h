#pragma once

// A224: deslocamentos do ntAvatar como o avatar_avatar.cpp o define (983 menos a base AvatarBase de 0x68); as visoes parciais
// abaixo usam estes valores e cada uma confere com C_ASSERT (antes ficaram no 645: m_charInfo em 0x3d9 em vez de 0x421)
#define NTAVATAR_OFS_CHARINFO   0x421 // 983 +0x489
#define NTAVATAR_OFS_PARTTIDS   0x624 // 983 +0x68c (007a7364)
#define NTAVATAR_OFS_PETFRAME   0x6ec
#define NTAVATAR_OFS_MOTIONTYPE 0x720

#ifdef REBANG_AVATAR_AVATAR_CPP
// the real classes, as avatar_avatar.cpp defines them

#include <list>
#include "singleton.h"
#include "wboneset.h"
#include "../shared/globalgamedefine.h"
#include "../shared/s5/specialprize/specialprizeitem.h"
#include "parttidlist.h"
#include "fx.h"
#include "wscene.h"
#include <memory>
class FxInterpreter;

class CQuadTree;
class ntBalloonText;
class CPetFrame;
class ntAvatarChatMain;
class Bitmap;
class Waabb;
struct sTexturePart;
struct trace_s;
struct w_motion_data;
enum eSPAVILITYTYPE;

class ntAvatarBurden
{
public:
	ntAvatarBurden()
		: m_pPetFrame(NULL)
	{
	}
	ntAvatarBurden(unsigned long guid, unsigned long face,
		const sCharacterInfo& info, CPetFrame* pPetFrame);
	~ntAvatarBurden();

	bool Load();

	// 983: ctor 007a4710 (+0/+4/+8/+0x20c/+0x2d4); copia 0xb7 dwords = 0x2dc (007b3ec0), nó da lista 0x2e4 (007b4069)
	unsigned long m_guid;
	unsigned long m_face;
	sCharacterInfo m_info;
	CPartTidList m_tids;
	CPetFrame* m_pPetFrame;
	unsigned long m_unk983_2d8; // o ctor do 983 não grava
};
C_ASSERT(sizeof(ntAvatarBurden) == 0x2dc && offsetof(ntAvatarBurden, m_tids) == 0x20c && offsetof(ntAvatarBurden, m_pPetFrame) == 0x2d4);

class ntAvatar
{
	friend class ntAvatarManager;

public:
	~ntAvatar();

	const sCharacterInfo& GetCharacterInfo() const { return m_charInfo; }
	unsigned long GetGuid() const;
	const WVector& GetPosition() const;
	void SetHeadIcon(int icon);
	bool IsTargetPositionChanged(bool bReset);
	void Follow(const char* name);
	void RefreshUccClothes(unsigned long tid, unsigned long uid);
	void SetTradeTitle(const char* title);
	SpecialPrizeItem& GetMySpItem(eSPAVILITYTYPE type);
	bool IsClickable(float x, float y) const;
	ntAvatar* GetFollowingAvatar() const;
	bool GetBoneScreenCoord(const char* name, int* x, int* y) const;
	void SetTargetPosition(const WVector& pos);
	void SetAngle(float angle);
	void SetTargetAngle(float angle);
	void SetPendingTargetAngle(float angle);
	void SetAction(int action);
	void Stop();
	void SetBalloonText(const char* text);
	void UseSPItem(eSPAVILITYTYPE type);
	void SetCharactorInfo(const sCharacterInfo& info);
	void SetPosition(const WVector& pos);
	void SetState(unsigned long state);
	void SetChatFacial(int facial);
	void ChangeMotion(int motion, const char* name, float blendTime);
	bool SendMotion983(const char* name, int type); // 983 007a5000 (PKT, frente C): pacote 0x63 do ChangeMotion
	void Render();
	void RenderOverlay(bool bDetail);
	void Process(float elapsed);

protected:
	ntAvatar(CQuadTree& pvs, const sSlotInfo& slot, const sCharacterInfo& info,
		ntAvatarChatMain* pChatMain);
	CQuadTree& GetPVS();
	void SetLocalPVS(CQuadTree& pvs);

private:
	void SendMove(const WVector& delta, bool bForce);
	void ProcessChangeState();
	void* AttachFx(const Attacher& attacher, const char* name, bool bFlag,
		defines_t* defines);
	void ScriptProcess(const w_motion_data* data, float from, float to,
		bool bAll);
	void ParsePuppetScript(const char* script);
	void ProcessMotion(float elapsed);
	void ParseScript_ShowVis(bool bShow, const char* script);
	void SetPendingTexPart(const char* part, const char* texture);
	sTexturePart* FindTexturePart(const char* part, const char* texture);

	// offsets verified against Ghidra: total size 0xb04
	CQuadTree* m_pPVS;         // 0x0
	char m_idName[0x16];       // 0x4
	char m_nickName[0x16];     // 0x1a
	char m_moveTarget[0x16];   // 0x30
	char m_followName[0x16];   // 0x46
	bool m_bHasGuild;          // 0x5c
	char m_guildName[0x80];    // 0x5d
	unsigned long m_e0;        // 0xe0
	unsigned long m_guid;      // 0xe4
	unsigned char m_e8;        // 0xe8
	unsigned char m_e9;        // 0xe9
	unsigned char m_ea;        // 0xea
	unsigned char m_eb;        // 0xeb
	unsigned long m_ec;        // 0xec
	unsigned long m_state;     // 0xf0
	unsigned long m_prevState; // 0xf4
	int m_action;              // 0xf8
	WVector m_pos;             // 0xfc
	float m_angle;             // 0x108
	float m_targetAngle;       // 0x10c
	bool m_bPendingAngle;      // 0x110
	float m_pendingAngle;      // 0x114
	WVector m_up;              // 0x118
	WVector m_targetPos;       // 0x124
	bool m_bTargetChanged;     // 0x130
	int m_headIcon;            // 0x134
	WVector m_moveAccum;       // 0x138
	ntAvatarBurden m_burden;   // 0x144 (0x2dc no 983)
	bool m_b3d8;                         // 0x420 (983: +0x488, 007a7569; o pad do 645 saiu com o burden de 0x2dc, A224)
	sCharacterInfo m_charInfo;           // 0x421 (983: +0x489, 007a7575)
	CPartTidList m_partTids;             // 0x598
	CPetFrame* m_pPetFrame;              // 0x660
	std::list<sTexturePart*> m_texParts; // 0x664
	float m_alpha;                       // 0x670
	LightSet m_light;                    // 0x674
	w_motion_data* m_pMotion;            // 0x690
	int m_motionType;                    // 0x694
	WBoneSet m_boneSet1;                 // 0x698
	w_motion_data* m_pPrevMotion;        // 0x6c0
	int m_prevMotionType;                // 0x6c4
	WBoneSet m_boneSet2;                 // 0x6c8
	float m_blendTime;                   // 0x6f0
	float m_blendElapsed;                // 0x6f4
	float m_6f8;                         // 0x6f8
	float m_facialTime;                  // 0x6fc
	unsigned long m_motionSendTime;      // 0x700
	ntBalloonText* m_pBalloon;           // 0x704
	float m_balloonRand[3];              // 0x708
	float m_714;                         // 0x714
	float m_718;                         // 0x718
	char m_tradeTitle[0x40];             // 0x71c
	Bitmap* m_pEmblem;                   // 0x75c
	ntAvatarChatMain* m_pChatMain;       // 0x760
	CPvsFxBox m_fxBox;                   // 0x764
	SpecialPrizeItem m_spItems[5];       // 0xac8
	// 983 +0xc80/+0xc84: FxInterpreter(&fxbox, 0) criado no construtor (007a76f9); fx das pecas vestidas (007a4d90)
	std::tr1::shared_ptr<FxInterpreter> m_spFx983;

	void AttachItemFx983(); // 007a4d90
};

class ntAvatarManager : public WSingleton<ntAvatarManager>
{
public:
	using WSingleton<ntAvatarManager>::m_pInstance;

	ntAvatarManager();
	virtual ~ntAvatarManager();

	ntAvatar* FindAvatarByIDName(const char* name) const;
	ntAvatar* FindAvatarByNickName(const char* name) const;
	ntAvatar* FindAvatarByGuid(int guid) const;
	ntAvatar* CheckClick(float x, float y) const;
	void ResetAvatarPositionAngle();
	void Render();
	void RenderOverlay();
	void Process(float elapsed);
	ntAvatar* CreateAvatar(const sSlotInfo& slot, const sCharacterInfo& info,
		ntAvatarChatMain* pChatMain);
	bool DeleteAvatar(const char* name);
	ntAvatar* AvatarByRayIntersect(const WVector& pos,
		const WVector& dir) const;
	void FreeAllAvatars();

	ntAvatar* GetMyAvatar() const { return m_pMyAvatar; }

protected:
	CQuadTree& GetPVS();
	void SetLocalPVS(CQuadTree& pvs);

public:
	int m_count;             // 0x28
	ntAvatar* m_avatars[30]; // 0x2c
	ntAvatar* m_pMyAvatar;   // 0xa4
	unsigned long m_a8;      // 0xa8
	unsigned long m_ac;      // 0xac
	bool m_bFlag0;           // 0xb0
	bool m_bFlag1;           // 0xb1
	CQuadTree* m_pPVS;       // 0xb4
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbCreateavatarFunclets(); // HACK: EH funclets of the naked CreateAvatar (nakedify)
#endif
};

#ifdef REBANG_AVATAR_AVATAR_CPP
// emitted out of line by avatar_avatar.obj only, before the inlines of the
// headers that avatar_avatar.cpp includes next (balloontext.h)
unsigned long ntAvatar::GetGuid() const
{
	return m_guid;
}

inline const WVector& ntAvatar::GetPosition() const
{
	return m_pos;
}

void ntAvatar::SetHeadIcon(int icon)
{
	m_headIcon = icon;
}

#endif

// 983: sizeof(ntAvatar) do 645 (0xb04) não vale aqui (bases no layout do 983; tamanho do 983 não medido)
#else
// the partial views the other units were written against

#include "singleton.h"
#include "../shared/globalgamedefine.h"
#include <list>

class CPetFrame;
struct sCharacterInfo;

// Known burden fields and ABI padding used by avatar_task.
class ntAvatarBurden
{
public:
	ntAvatarBurden(unsigned long guid, unsigned long key,
		const sCharacterInfo& info, CPetFrame* pPet);
	~ntAvatarBurden();

	bool Load();
	bool operator<(const ntAvatarBurden& rhs);
	bool operator==(const ntAvatarBurden& rhs);

	// mesma memória do ntAvatarBurden real (983 0x2dc): m_guid aqui é o 2o argumento do ctor (+4), que o operator< do 983 compara (007b36f0)
	unsigned long m_unused0;
	unsigned long m_guid;
	unsigned long m_unused8[(0x2d4 - 8) / 4];
	CPetFrame* m_pPet;
	unsigned long m_unused2d8;
};
C_ASSERT(sizeof(ntAvatarBurden) == 0x2dc && offsetof(ntAvatarBurden, m_pPet) == 0x2d4);

inline bool ntAvatarBurden::operator<(const ntAvatarBurden& rhs)
{
	return m_guid < rhs.m_guid;
}

inline bool ntAvatarBurden::operator==(const ntAvatarBurden& rhs)
{
	return m_guid == rhs.m_guid && m_pPet != (CPetFrame*)-1 &&
		rhs.m_pPet != (CPetFrame*)-1;
}

#ifdef REBANG_AVATAR_MAINUI_CPP
// avatar_mainui.cpp sees the UI-facing fields of the avatar classes.
// TODO: incomplete
class ntAvatar
{
public:
	const sCharacterInfo& GetCharacterInfo() const { return m_charInfo; }
	const char* GetNickName() const { return m_nickName; }
	const WVector& GetPosition() const { return m_position; }
	bool IsMoving() const
	{
		if ((m_position - m_targetPosition).Magnitude() > 0.001f)
			return true;
		return false;
	}

	void Stop();
	void Follow(const char* nickName);
	void SetState(unsigned long state);
	void SetBalloonText(const char* text);
	void SetChatFacial(int face);

	unsigned char m_unknown0[0x1a];
	char m_nickName[0x16];
	unsigned char m_unknown30[0xb0];
	unsigned long m_uid;
	int m_guid;
	bool m_canKick;
	unsigned long m_charTypeId;
	unsigned long m_state;
	unsigned char m_unknownF4[0x8];
	WVector m_position;
	unsigned char m_unknown108[0x1c];
	WVector m_targetPosition;
	unsigned char m_unknown130[NTAVATAR_OFS_CHARINFO - 0x130];
	sCharacterInfo m_charInfo;
};
C_ASSERT(offsetof(ntAvatar, m_state) == 0xf0);
C_ASSERT(offsetof(ntAvatar, m_charInfo) == NTAVATAR_OFS_CHARINFO);

// TODO: incomplete
class ntAvatarManager : public WSingleton<ntAvatarManager>
{
public:
	using WSingleton<ntAvatarManager>::m_pInstance;

	ntAvatar* FindAvatarByGuid(int guid) const;
	ntAvatar* FindAvatarByNickName(const char* nickName) const;

	int m_avatarCount;
	ntAvatar* m_avatars[30];
	ntAvatar* m_pMyAvatar;
	ntAvatar* m_pLitAvatar;
	ntAvatar* m_pHighlightAvatar;
	bool m_active;
	bool m_overlayDetail;
};
#elif !defined(REBANG_AVATAR_MAIN_CPP)
enum eSPAVILITYTYPE
{
};

class SpecialPrizeItem
{
public:
	unsigned char m_unused0[8];
	unsigned long m_value;
};

// TODO: incomplete
class ntAvatar
{
public:
	const sCharacterInfo& GetCharacterInfo() const { return m_charInfo; }
	bool GetBoneScreenCoord(const char* bone, int* x, int* y) const;

	SpecialPrizeItem& GetMySpItem(eSPAVILITYTYPE type);
	void SetBalloonText(const char* text);
	void SetState(unsigned long state); // 983 007a4820 (s111: resultados da AlchemyDlg/card_compose do CTaskMain)

#ifdef REBANG_AVATAR_TASK_CPP
	unsigned char m_unused0[0xe0];
	unsigned long m_guid;
	unsigned long m_key;
	unsigned char m_unusede8[0xfc - 0xe8];
	WVector m_pos;
	unsigned char m_unused108[0x144 - 0x108];
	ntAvatarBurden m_burden;
	bool m_bBurdenLoaded;
	sCharacterInfo m_charInfo;
	unsigned char m_unused622[NTAVATAR_OFS_PETFRAME - NTAVATAR_OFS_CHARINFO - sizeof(sCharacterInfo)];
	CPetFrame* m_pPetFrame;
#else
	unsigned char m_unknown0[0xe4];
	int m_guid;
	unsigned char m_unknownE8[0xf0 - 0xe8];
	// A224: o nosso ntAvatar nao tem a base AvatarBase (0x68): o estado do 983 em +0x158 e o m_state (+0xf0) do avatar_avatar.cpp,
	// que o SetState grava; em +0x158 o bongdari/ranking/taskmain liam lixo do burden e o mandavam no pacote 0x63
	unsigned long m_state983;
	unsigned char m_unknownF4[NTAVATAR_OFS_CHARINFO - 0xf4];
	sCharacterInfo m_charInfo;
#endif
};
#ifdef REBANG_AVATAR_TASK_CPP
C_ASSERT(offsetof(ntAvatar, m_burden) == 0x144);
C_ASSERT(offsetof(ntAvatar, m_bBurdenLoaded) == 0x420);
C_ASSERT(offsetof(ntAvatar, m_charInfo) == NTAVATAR_OFS_CHARINFO);
C_ASSERT(offsetof(ntAvatar, m_pPetFrame) == NTAVATAR_OFS_PETFRAME);
#else
C_ASSERT(offsetof(ntAvatar, m_state983) == 0xf0);
C_ASSERT(offsetof(ntAvatar, m_charInfo) == NTAVATAR_OFS_CHARINFO);
#endif

// TODO: incomplete
#ifdef REBANG_AVATAR_TASK_CPP
// HACK: instantiate the burden list before the manager singleton, as in the original.
typedef char RbAvatarBurdenListSize[sizeof(std::list<ntAvatarBurden>)];
#endif

class ntAvatarManager : public WSingleton<ntAvatarManager>
{
public:
	using WSingleton<ntAvatarManager>::m_pInstance;

	ntAvatar* FindAvatarByGuid(int guid) const;
	ntAvatarManager();
	virtual ~ntAvatarManager();

	ntAvatar* FindAvatarByNickName(const char* name) const;
#ifdef REBANG_TASKMAIN_PCH // other includers keep their IL
	void SetActive(bool bActive) { m_bActive = bActive; }
#endif

	unsigned char m_unused4[0xa4 - sizeof(WSingleton<ntAvatarManager>)];
	ntAvatar* m_pMyAvatar;
	unsigned char m_unuseda8[0xb0 - 0xa8];
	bool m_bActive; // 0xb0
	unsigned char m_unusedb1[0xb8 - 0xb1];
};
#else
// avatar_main.cpp sees the real SpecialPrizeItem (specialprizeitem.h) and a wider view of the avatar classes.
class CPartTidList;
class ntAvatarChatMain;
class SpecialPrizeItem;
enum eSPAVILITYTYPE;

// TODO: incomplete
class ntAvatar
{
public:
	const sCharacterInfo& GetCharacterInfo() const { return m_charInfo; }

	bool IsFollowing() const { return m_followName[0] ? true : false; }
	bool IsHoldState() const { return (m_state & 0x7e) ? true : false; }
	unsigned long GetUID() const { return m_uid; }
	const char* GetIDName() const { return m_idName; }
	const char* GetNickName() const { return m_nickName; }
	const WVector& GetTargetPosition() const { return m_targetPos; }
	int GetMotion() const { return m_motion; }
	unsigned long GetState() const { return m_state; }
	unsigned long GetAction() const { return m_action; }
	void AddState(unsigned long state) { SetState(m_state | state); }
	void SubState(unsigned long state) { SetState(m_state & ~state); }
	CPartTidList& GetPartTidList()
	{
		return *(CPartTidList*)((char*)this + NTAVATAR_OFS_PARTTIDS); // A421: era 0x598 (645)
	}

	void SetState(unsigned long state);
	void SetPosition(const WVector& pos);
	void SetAngle(float angle);
	void SetPendingTargetAngle(float angle);
	void ChangeMotion(int type, const char* name, float blend);
	void SetCharactorInfo(const sCharacterInfo* info);
	void SetTradeTitle(const char* title);
	void SetChatFacial(int facial);
	void Stop();
	void SetTargetPosition(const WVector& pos);
	void SetAction(unsigned long action);
	void Follow(const char* name);
	bool IsTargetPositionChanged(bool bReset);
	ntAvatar* GetFollowingAvatar();
	void UseSPItem(eSPAVILITYTYPE type);
	SpecialPrizeItem& GetMySpItem(eSPAVILITYTYPE type);
	void RefreshUccClothes(unsigned long typeId, unsigned long id);

	unsigned char m_unknown0[4];
	char m_idName[0x16];
	char m_nickName[0x2c];
	char m_followName[0x9a];
	unsigned long m_uid;
	int m_guid;
	unsigned char m_unknownE8[8];
	unsigned long m_state;
	unsigned char m_unknownF4[4];
	unsigned long m_action;
	WVector m_pos;
	unsigned char m_unknown108[0x1c];
	WVector m_targetPos;
	unsigned char m_unknown130[NTAVATAR_OFS_CHARINFO - 0x130];
	sCharacterInfo m_charInfo;
	unsigned char m_unknown622[NTAVATAR_OFS_PARTTIDS + 8 - NTAVATAR_OFS_CHARINFO - sizeof(sCharacterInfo)];
	unsigned long m_uccRef[24]; // m_partTids.m_tid
	unsigned long m_uccClothesId[24];
	unsigned char m_unknown6ec[NTAVATAR_OFS_MOTIONTYPE - (NTAVATAR_OFS_PARTTIDS + 8 + 0xc0)];
	int m_motion;
};
C_ASSERT(offsetof(ntAvatar, m_state) == 0xf0);
C_ASSERT(offsetof(ntAvatar, m_charInfo) == NTAVATAR_OFS_CHARINFO);
C_ASSERT(offsetof(ntAvatar, m_uccRef) == NTAVATAR_OFS_PARTTIDS + 8);
C_ASSERT(offsetof(ntAvatar, m_motion) == NTAVATAR_OFS_MOTIONTYPE);

// TODO: incomplete
class ntAvatarManager : public WSingleton<ntAvatarManager>
{
public:
	using WSingleton<ntAvatarManager>::m_pInstance;

	ntAvatar* FindAvatarByGuid(int guid) const;
	ntAvatar* FindAvatarByNickName(const char* nick) const;
	ntAvatar* FindAvatarByIDName(const char* name) const;
	void DeleteAvatar(const char* nick);
	void Render();
	void Process(float dt);
	ntAvatar* AvatarByRayIntersect(WVector& origin, WVector& dir);
	ntAvatar* CheckClick(float x, float y);
	void RenderOverlay();
	void ResetAvatarPositionAngle();
	void FreeAllAvatars();
	ntAvatar* CreateAvatar(sSlotInfo* slot, sCharacterInfo* charInfo,
		ntAvatarChatMain* main);

	int m_count;
	ntAvatar* m_avatars[30];
	ntAvatar* m_pMyAvatar;
	ntAvatar* m_pHoverAvatar;
	ntAvatar* m_pClickAvatar;
	bool m_bRestored;
#ifdef REBANG_TASKMANAGER_PCH // HACK: taskmanager_pch.h
	void SetActive(bool bActive);
#endif
};
#endif
#endif
