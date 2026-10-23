#pragma once

class WPuppet;
class CWeatherType;

enum eObjType
{
	OBJ_BASE,
	OBJ_FUNC,
	OBJ_STATIC,
	OBJ_MODEL,
	OBJ_ACTOR,
	OBJ_CUSTOM,
	OBJ_EFFECT,
	OBJ_NONE
};

class CRenderFuncPtr
{
public:
	CRenderFuncPtr() { }
	~CRenderFuncPtr() { }

	void DisplayAll() { Display(); }

public:
	virtual void DisplayShadow() { }
	virtual void Display() = 0;

protected:
	virtual void DebugDisplay() { }
};

#ifndef REBANG_PCH_SCENEMANAGER
// HACK: the shared PCH keeps this reduced view (IL offsets and name count every other unit depends on);
// the full declarations below are compiled only in the scenemanager PCH (stdafx_scenemanager.h).
struct TransparentElement
{
	TransparentElement(WPuppet* _puppet, Waabb* _aabb, int _texHandle,
		int _polyNum)
	{
		puppet = _puppet;
		aabb = _aabb;
		texHandle = _texHandle;
		polyNum = _polyNum;
	}

	WPuppet* puppet;
	Waabb* aabb;
	int texHandle;
	int polyNum;
};

// TODO: incomplete
class CSceneManager : public CStackableSingleton<CSceneManager>
{
public:
	CSceneManager();

	void RegisterElement(eObjType type, WPuppet* puppet, CRenderFuncPtr* func,
		const char* name, unsigned long flag, Waabb* aabb);
	void DeleteElement(const char* name);
	void SetVisible(const char* name, bool bVisible);
	void Load();
	void SetWeather(unsigned char weather, bool force);
	void SetLobbyWeather(bool enable);
	void UpdateFog(const char* mapName);
#ifdef REBANG_PCH_REALMYROOMDATA // HACK: only in the realmyroomdata PCH, other units keep their name count
	void SetAlpha(const char* name, unsigned char alpha);
#endif
	void SetPuppet(const char* name, WPuppet* puppet);
	void ReleaseElement();
	void UpdateBright();
#ifdef REBANG_PCH_POOL // HACK: only in the pool PCH, other units keep their IL and name count
	void Render(WView* view, unsigned long flag);

	using WSingleton<CSceneManager>::m_pInstance;
#endif

	unsigned char m_unused28[0x88];
	CWeatherType* m_pWeather;
	void UpdateFog(bool bForce);
#ifdef REBANG_CLIENTSETTING_PCH
	void SetReflection(bool bEnable);
	void SetLOD(bool bEnable, bool bForce);
#endif

	void ShowTag() { m_bShowTag = !m_bShowTag; }
	bool ToggleTransparent() { return m_bTransparent = !m_bTransparent; }

private:
	unsigned char m_unusedb4[0x55]; // 983: uma lista a menos (m_bShowTag 0x109)
	bool m_bShowTag;
	unsigned char m_unused116[0x12];
	bool m_bTransparent;
	unsigned char m_unused129[0x7];
};
#else
class WTextureView;

struct SceneElement
{
	SceneElement()
	{
		type = OBJ_STATIC;
		puppet = NULL;
		func = NULL;
		name[0] = '\0';
		texView = NULL;
		aabb = NULL;
		flag = 0;
		alpha = 0xff;
		visible = true;
	}
	~SceneElement() { }

	bool operator==(const char* n) const
	{
		if (name[0] == '\0' || n == NULL)
			return false;
		return strcmpi(name, n) == 0;
	}

	eObjType type;
	WPuppet* puppet;
	CRenderFuncPtr* func;
	char name[128];
	unsigned long flag;
	unsigned char alpha;
	bool visible;
	WTextureView* texView;
	Waabb* aabb;
};

struct SceneElemRegister
{
	eObjType type;
	WPuppet* puppet;
	CRenderFuncPtr* func;
	const char* name;
	unsigned long flag;
	Waabb* aabb;
};

struct CustomElement
{
	CustomElement(eObjType _type, CRenderFuncPtr* _func)
	{
		type = _type;
		func = _func;
	}

	eObjType type;
	CRenderFuncPtr* func;
};

struct TransparentElement
{
	TransparentElement(WPuppet* _puppet, Waabb* _aabb, int _texHandle,
		int _polyNum)
	{
		puppet = _puppet;
		aabb = _aabb;
		texHandle = _texHandle;
		polyNum = _polyNum;
	}

	WPuppet* puppet;
	Waabb* aabb;
	int texHandle;
	int polyNum;
};

typedef std::list<SceneElement>::iterator SceneElementIter;
typedef std::list<CustomElement>::iterator CustomElementIter;
typedef std::list<TransparentElement>::iterator TransparentElementIter;

class WView;
class WFont;
class CSea;
class CMarker;
class CWeatherType;
class CBeach;
class CWavelet;
class CPool;
class ntRiver;

// Members come from the offsets used by scenemanager.cpp (m_unk_* not named yet)
class CSceneManager : public CStackableSingleton<CSceneManager>
{
public:
	struct sDrop
	{
		WVector pos;
		unsigned long color;
	};

	CSceneManager();
	virtual ~CSceneManager();

	void RegisterElement(eObjType type, WPuppet* puppet, CRenderFuncPtr* func,
		const char* name, unsigned long flag, Waabb* aabb);
	void RegisterElement(SceneElemRegister& reg);
	void ReleaseElement();
	void DeleteElement(const char* name);
	void SetVisible(const char* name, bool bVisible);
	void Load();
	void SetWeather(unsigned char weather, bool force);
	void SetLobbyWeather(bool enable);
	void UpdateFog(const char* mapName);
	void UpdateFog(bool bLoad);
	void UpdateBright();
	WPuppet* GetPuppet(const char* name);
	eObjType GetType(const char* name);
	void SetAlpha(const char* name, unsigned char alpha);
	void SetPuppet(const char* name, WPuppet* puppet);
	void SetType(const char* name, eObjType type);
	void UpdateSea();
	void UpdateWind();
	void Process(float dt);
	void Prerender(WView* view);
	void Clear();
	void SetReflection(bool enable);
	void SetLOD(bool bLod, bool bUpdate);
	void Render(WView* view, unsigned long mask);
	void DropTest();
	void DrawDebugLine(WView* view);

protected:
	void Render_RenderSky(WView* view);
	void Render_RenderWaterStuff(WView* view);
	void Render_RenderWeather(WView* view);
	void Render_RenderWeatherFullScreenOverlay(WView* view);
	void Render_BuildImposter(WView* view);
	void Render_RenderEffect(WView* view);
	void Render_RenderBillboardGroup(WView* view);
	void Render_RenderCustom(WView* view);
	unsigned char OverlapCamera(WView* view, const SceneElement& elem);
	void DrawImposter(WView* view, const TransparentElement& elem);
	void RenderShadow(WView* view, unsigned long mask);
	void DrawPuppet(WView* view, WPuppet* puppet, Waabb* aabb);
	void Render_RenderOBMarker(WView* view);
	void Render_BaseAndShadow(WView* view, unsigned long mask);
	int Render_RenderElement(WView* view, unsigned long mask);
	void Render_RenderBlendGroup(WView* view,
		std::list<TransparentElement>& elements, int blend, int count);
	void Render_RenderNearGroup(WView* view);
	void Render_RenderDropPosition(WView* view);
	void Render_RenderSea(WView* view);

	WList<CBeach*> m_beachList;
	WList<CWavelet*> m_waveletList;
	WList<CPool*> m_poolList;
	WList<ntRiver*> m_riverList;
	CSea* m_pSea;
	CMarker* m_pMarker;
	CWeatherType* m_pWeather;
	CWeatherType* m_pCloud;
	bool m_bFog;
	bool m_bLod;
	bool m_unk_ba;
	std::list<SceneElement> m_elements;
	std::list<CustomElement> m_custom1;
	std::list<CustomElement> m_custom2;
	std::list<TransparentElement> m_transparent1;
	std::list<TransparentElement> m_transparent2;
	static std::list<TransparentElement> m_transparent3; // 983: só 5 listas (PROVISÓRIO: qual saiu não foi medido; static para o .cpp do 645 compilar)
	bool m_bDirty;
	std::list<sDrop> m_drops;
	char m_unk_114;
	bool m_unk_115;
	char m_unk_116[2];
	WFont* m_pFont;
	float m_fogStart;
	float m_fogEnd;
	unsigned long m_fogColor;
	bool m_unk_128;
	bool m_unk_129;
	char m_unk_12a[2];
	struct sDebugDraw
	{
		unsigned long bits;
	};
	sDebugDraw m_debugDraw;

private:
	static WTVertex vtr[4];
	static WTVertex* vtx[5];
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbRenderrenderblenFunclets(); // HACK: EH funclets of the naked Render_RenderBlendGroup (nakedify)
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbLoadFunclets(); // HACK: EH funclets of the naked Load (nakedify)
#endif
};
#endif

class CWavelet
{
public:
	struct sWavelet
	{
		WVector pos[2];
		WVector dir;
		float u[2];
	};

	struct sLayer
	{
		float pos;
		float delay;
		float alpha;
		float time;
		float speed;
		int state;
	};

	CWavelet();
	virtual ~CWavelet();

	virtual void Process(float dt);
	virtual void Render();

	void SetWavelet(const std::vector<WVector>& points, const char* name,
		int layerNum);

protected:
	virtual void ReadAttribute(const char* name);
	virtual void SetLayer(int num);

	std::vector<sWavelet> m_wavelet;
	int m_texHandle;
	float m_width;
	float m_frequency;
	float m_deceleration;
	float m_fadeInTime;
	float m_fadeOutTime;
	float m_delay;
	std::vector<sLayer> m_layer;

	static WTVertex vtr[4];
	static WTVertex* vtx[5];
};
