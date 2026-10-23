#pragma once

#include <map>
#include <string>
#include "fxsequence.h"

class CFxSpray;
class CFxSequence;
class CFxKeeper;
class WResourceManager;

struct defines_t;
#ifdef REBANG_FX_CPP
struct sFxKeeper;
#endif

// HACK: the full layout is only visible to fxbox.cpp (see fxsequence.h): every other unit keeps
// the partial view so its code and name count stay as in the original.
#ifdef REBANG_FXBOX_CPP
#include <list>

class W3dAniSpr;
struct sFxKeeper;
typedef std::list<sFxKeeper>::iterator FxKeeperIt;
#endif

// TODO: incomplete
class CFxBox
{
	friend class CFxSequence;
#ifdef REBANG_FXSPRAY_CPP
	friend class CFxSpray;
#endif

public:
	CFxBox();
	virtual ~CFxBox();

	virtual void ProcessAttacher(float elapsed) { }

	void Init(WResourceManager* pResMng);
	void SetCamera(const WMatrix* camera);
	CFxSpray* LoadSpray(const char* filename, defines_t* defines);
	CFxSequence* LoadSequence(const char* filename, bool bDelete,
		defines_t* defines);
	void AddSpray(CFxSpray* spray);
	void AddSequence(CFxSequence* sequence);
	void DeleteSequence(CFxSequence* sequence, bool bDeleteChild);
	bool Process(float elapsed);
	void Display(WView* view);
	void Clear();
	void ClearAll(bool bFree);
	void DeleteSpray(CFxSpray* spray);
	void SetScreenCenter(float x, float y);
	std::map<CFxSpray*, CFxSpray*>& GetSprayList();
// HACK: see fxsequence.h (the members only fx.cpp uses are only visible to it)
#ifdef REBANG_FX_CPP
	void AddFxKeeper(sFxKeeper& keeper);
	void ClearFxKeeper();
	std::map<CFxSequence*, CFxSequence*>& GetSequenceList();
	CFxSpray* GetSpray(int index);
	bool FindSequence(CFxSequence* sequence);
	bool FindSpray(CFxSpray* spray);
	bool GetOutput(WVector& pos, unsigned char& alpha);
#endif
	void EraseFxKeeper(CFxKeeper* keeper);
	bool PreprocessDefines(defines_t& defines, const char* line);
	void ProcessDefines(defines_t& defines, char* str);

	void ClearSpray(bool bFree); // 983: CFxSequence "clear"
#ifdef REBANG_FXBOX_CPP
	void ClearSequence(bool bFree);
	void ClearSprite();
	void ClearOriginalSpray();
	void ClearOriginalSequence();
	bool Finished();
	void ClearDefines(defines_t& defines, defines_t* parent);
	const CFxSequence::sLine& GetLastError();
	void CallFxKeeperCallBack(void* param);
	void AddFxKeeper(sFxKeeper& keeper);
	void ClearFxKeeper();
#endif

	void SetGroundHeightArea(float maxHeight, float minHeight)
	{
		m_groundHeightMax = maxHeight;
		m_groundHeightMin = minHeight;
	}

protected:
	virtual bool CheckGroundCollision(const WVector& from, const WVector& to,
		float& height, float radius);
	virtual void OnSequenceCreated(CFxSequence* sequence);
	virtual void OnSequenceDeleted(CFxSequence* sequence);
	virtual void OnSprayCreated(CFxSpray* spray);
	virtual void OnSprayDeleted(CFxSpray* spray);

	float ParseNumber(const char* str);
#ifdef REBANG_FXSPRAY_CPP // HACK: see fxspray.h
	W3dAniSpr* LoadSprite(const char* filename, int type, int frames);
	float Random(float minimum, float maximum);
	WVector Random(const WVector& minimum, const WVector& maximum);
	WVector Random(const WVector& center, float minimum, float maximum,
		float angle);
#endif
#ifdef REBANG_FXBOX_CPP
	W3dAniSpr* LoadSprite(const char* filename, int width, int height);
#endif

public:
	float m_frameTime;
#ifdef REBANG_FXBOX_CPP
	float m_timeScale;
	bool m_bPause;
	unsigned long m_unused10[0x40];
	bool m_bStop;
	int m_unk114;
	bool m_bLimitElapsed;
	int m_displayCount;
	int m_displayCount2;
	bool m_bUnk124;
	std::map<std::string, CFxSpray*> m_sprayCache; // 983: 0x128
#else
	unsigned char m_unused8[0x120]; // 983
	unsigned char m_map128_983[0x10]; // 983: m_sprayCache
#endif
	std::map<std::string, CFxSequence*> m_sequenceCache;
	WResourceManager* m_pResMng;
#ifdef REBANG_FXBOX_CPP
	std::map<std::string, W3dAniSpr*> m_sprite; // 983: 0x14c
#else
	unsigned char m_unused144[0x10]; // 983: m_sprite em 0x14c
#endif
	std::map<CFxSpray*, CFxSpray*> m_spray;
#ifdef REBANG_FX_CPP
	std::map<CFxSequence*, CFxSequence*> m_sequence;
	unsigned char m_unused168[0x2ac - sizeof(std::map<CFxSequence*, CFxSequence*>)];
#elif defined(REBANG_FXBOX_CPP)
	std::map<CFxSequence*, CFxSequence*> m_sequence; // 983: 0x16c
	const WMatrix* m_pCamera;
	WTVertex* m_pVertex[4];
	int m_numVertex;
	WTVertex m_vertex[4];
	CFxSequence::sLine m_lastError;
	unsigned long m_unused334;
	// 983: m_fxKeeper em 0x408 (construtor 009735a0) -- os tipos do 983 ja dao esse deslocamento sem enchimento (s47)
	std::list<sFxKeeper> m_fxKeeper;
#else
	unsigned char m_unused15c[0x2ac]; // 983: 0x16c..0x418
#endif

protected:
	float m_groundHeightMax;
	float m_groundHeightMin;

#ifdef REBANG_FXBOX_CPP
private:
	void DeleteSpray(std::map<CFxSpray*, CFxSpray*>::iterator& it);
	void DeleteSequence(std::map<CFxSequence*, CFxSequence*>::iterator& it,
		bool bDeleteChild);
#endif
};

#ifdef REBANG_FXBOX_CPP
// HACK: instantiates the iterator before the ones fxbox.cpp uses first (COMDAT emission order).
typedef char FxSequenceIteratorSize[sizeof(
	std::map<CFxSequence*, CFxSequence*>::iterator)];
#endif

class CFxKeeper
{
public:
	CFxKeeper()
		: m_pFxBox(NULL)
	{
	}
	virtual ~CFxKeeper()
	{
		if (m_pFxBox)
			m_pFxBox->EraseFxKeeper(this);
	}

	virtual void EmptyFx(void* fx) = 0;

#ifdef REBANG_FXBOX_CPP
	void SetFxManager(CFxBox* pFxBox) { m_pFxBox = pFxBox; }
#endif

	CFxBox* m_pFxBox;
};

struct sFxKeeper
{
	CFxKeeper* keeper;
	void (CFxKeeper::*func)(void*);
};

#include "fxbox.inl"
