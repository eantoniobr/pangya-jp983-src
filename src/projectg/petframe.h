#pragma once

class CPartTidList;
class WPuppet;
class WBoneSet;
class WScene;
class WView;
struct LightSet;
struct w_motion_data;

// TODO: incomplete
class CPartList
{
public:
	bool FindPart(unsigned long tid) const;

	unsigned char m_unused0[0x13c];
};

// TODO: incomplete
class CPetFrame
{
public:
	CPetFrame();
	~CPetFrame();

	// 983 008b23f0: 6 argumentos (ret 0x18); o 6o e o IDummyPlayer dono (NULL aqui; ver partsinfo.h)
	bool Build(const CPartTidList* tids, unsigned long* uids, bool bUnk1,
		bool bUnk2, int option, class IDummyPlayer* pOwner = NULL);
	bool Refresh(CPartTidList* tids);
	WPuppet* GetBonePet();
	WPuppet* GetCurAniPet();
	void ApplyBoneSet983(WBoneSet* set); // 983 008acc90
	void Animate983(WBoneSet* set, const char* name, float time); // 983 008acdf0 (GetBones + ApplyBones do 645 juntos)
	void UpdateLightSource(LightSet* light, bool addLight, WScene* scene);
	void SetAlpha(unsigned char alpha);
	void Render(WView* view, bool bTransform, float scale, bool bFlag0,
		bool bFlag1, bool bFlag2);
	bool FindAuxPart(unsigned long tid);
	bool SetMakeup();
	bool HasMPet(char* name);
	void SetInvisible(bool bInvisible);
	w_motion_data* FindMotionData(const char* name, bool bFlag,
		WPuppet** ppPuppet);

	// visao parcial do CPetFrame de partsinfo.h, com os deslocamentos do 983 (m_partList +0x1f8; 645: +0x1b8)
	unsigned long m_tid;
	WPuppet* m_pBonePet; // +0x04
	unsigned char m_unused8[0x8];
	int m_skinTexture; // +0x10
	unsigned char m_unused14[0x1e4];
	CPartList m_partList; // +0x1f8
	// 983: o resto ate sizeof 0x358 (o `new CPetFrame` do 983 faz `push 0x358`, 00876dc9; o partsinfo.h tem m_unk983_334 aqui).
	// Sem isto a visao media 0x334 e quem faz `new CPetFrame` por ela alocava 0x24 bytes a menos do que o construtor escreve.
	unsigned char m_unused334[0x24]; // +0x334
};
