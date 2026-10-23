#pragma once

#include <vector>
#include "polysoup.h"
#ifndef REBANG_QUADTREE_CPP
#include "golfball.h"
#endif

enum enumPolyBlend
{
	W_POLY_BLEND_NORMAL,
	W_POLY_BLEND_ADD = 0x800000,
	W_POLY_BLEND_MULTIPLY = 0x1000000,
	W_POLY_BLEND_INVMULTIPLY = 0x1800000,
	W_POLY_BLEND_FORCE_DWORD = 0x7fffffff
};

#ifdef REBANG_QUADTREE_CPP
// HACK: only quadtree.cpp sees these classes (the original has user-written constructors here, line table, and
// includes golfball.h after them); the IL of the other includers (emission order) is unchanged.
class CAniObj
{
public:
	CAniObj()
	{
		m_value = 100.0f;
		m_sound[0] = 0;
	}
	~CAniObj() { }

	unsigned char m_type;
	unsigned long m_rand;
	short m_id;
	float m_time;
	char m_sound[0x20];
	float m_value;
};

class CRotObj : public CAniObj
{
public:
	CRotObj() { }

	float m_angle;
	float m_invSize;
};

class CMoveObj : public CAniObj
{
public:
	CMoveObj() { }

	WVector m_startPos;
	WVector m_endPos;
	float m_standTime;
	float m_moveTime;
};

class CVtxObj : public CAniObj
{
public:
	CVtxObj() { }
};

class CTranObj : public CAniObj
{
public:
	CTranObj() { }
};

#include "golfball.h"
#else
class CAniObj;
class CRotObj;
class CMoveObj;
class CVtxObj;
class CTranObj;
#endif

class WPuppet;

struct fragmentsCache_s
{
	bool bUsed;
	WVector box[4];
	WVector normal;
	int numVertices;
	WVector vertices[1024];
	int numIndices;
	unsigned short indices[1536];
};

struct trace_s
{
	WVector m_endPos;
	float m_fraction;
	WVector m_normal;
	float m_planeDist;
	bool m_flag;
};

typedef WPolySoup::sModel sQuadPuppetHolder;

// TODO: incomplete
class CQuadTree
{
public:
	struct sWater
	{
		Waabb aabb;
		int type;
	};

	struct sColData
	{
		unsigned char groundType;
		short objIndex;
		int triIndex;
		int frame;
		WVector pos;
		WVector normal;
	};

	struct sColResponse
	{
		struct GolfBallClone
		{
			GolfBallClone(const CGolfBall& ball);

#ifdef REBANG_QUADTREE_CPP // HACK: other includers keep their IL (emission order)
			float GetRadius() const { return m_pBall->m_radius; }
			unsigned long GetSpecial() const { return m_pBall->m_special; }
			float GetInitSpin() const { return m_pBall->m_initSpin; }
			int GetRenderNum() const { return m_pBall->m_renderNum; }
			int GetTopFrame() const { return m_pBall->m_topFrame; }
			int GetAttrIndex() const { return m_pBall->m_attrIndex; }
#else
			float GetRadius() const;
			unsigned long GetSpecial() const;
			float GetInitSpin() const;
			int GetRenderNum() const;
			int GetTopFrame() const;
			int GetAttrIndex() const;
#endif

			WVector m_pos;
			WVector m_vel;
			short m_colObjIndex;
			int m_colTriIndex;
			CGolfBall::eBallState m_state;
			CGolfBall* m_pBall;
		};

		sColResponse(const CGolfBall& ball, const WVector& colPos,
			const WVector& colNormal);

		GolfBallClone m_ball;
		unsigned char m_unused28[0x20];
		char m_sound[0x44];
		WVector m_normal;
		unsigned char m_unused98[0x4];
		WVector m_colPos;
		WVector m_colNormal;
		bool m_bBounced;
		bool m_bRolled;
	};

	float GetObbPos(Wobb& obb, bool bMax, int axis);
	void OBBToAABB(Wobb obb, Waabb& aabb, WVector& pos);
	void TraceOBB_Avatar_genPosition(const WVector& start, const WVector& end,
		trace_s* pTrace, WPolySoup::sModel* pModel);
	void TraceOBB_WallSliding(const WVector& start, const WVector& end,
		trace_s* pTrace, WPolySoup::sModel* pModel, int axis, bool bForce);
	int Get_WallSlidingAngle(const WVector& pos, WPolySoup::sModel* pModel,
		WVector& out);
	void TraceOBB_Wall(const WVector& start, const WVector& end,
		trace_s* pTrace, WPolySoup::sModel* pModel, int axis, bool bForce);
	bool TraceOBB_Object(const WVector& start, const WVector& end,
		const Waabb& box, trace_s* pTrace, WPolySoup::sModel* pModel,
		bool bAll);
	void TraceAABB(const WVector& start, const WVector& end, const Waabb& box,
		trace_s* pTrace);
	void TraceOBB(const WVector& start, const WVector& end, const Waabb& box,
		trace_s* pTrace);
	void TraceOBB_New(const WVector& start, const WVector& end,
		const Waabb& box, trace_s* pTrace);
	void DrawDebugTraceOBB(const WVector& start, const WVector& end,
		const Waabb& box);
	void DrawDebugTraceAABB(const WVector& start, const WVector& end,
		const Waabb& box);

private:
	unsigned long MakeRand(unsigned long limit);
	unsigned char GetObjQuad(const WVector& a, const WVector& b);
	float GetRollCoeff(int propIndex) const;
	float GetBounceCoeff(int propIndex) const;
	bool IsPenetrable(int propIndex) const;
	float GetWeatherRollCoeff(int propIndex) const;
	float GetWeatherBounceCoeff(int propIndex) const;
	bool PointInTriangle(const WVector& p, const WVector& a, const WVector& b,
		const WVector& c) const;
	bool SameSide(const WVector& p1, const WVector& p2, const WVector& a,
		const WVector& b) const;

protected:
	float IntersectPlane(const WVector& pos, const WVector& vel,
		const WPlane& plane, bool bBothSides);
	bool IsValid(const WVector& pos);
	void BounceResponse(const WVector& normal);
	void RollProcess(float dt);
	void BounceProcess(float dt);
	void SpinProcess(float dt);
	void ScriptProcess(int index, float from, float to);
	void ParsePuppetScript(int index, const char* script);
	void RollingBallGroundResponse(CGolfBall& ball, float dt,
		const WVector& dir, int triIndex, const WVector& normal);
	void CommitResponse(CGolfBall& ball, const sColResponse& response,
		int index);
	WVector ColTest(const WVector& pos, bool bKeepPos, int* pIndex, bool bAll);
	bool ObjColTest(const WVector& dir, short objIndex, WPlane* pPlane,
		float& t, int& triIndex);
	void ObjResponse(const WVector& dir, float t, const WVector& normal,
		sColResponse& response);
	float IntersectObj(const WVector& pos, const WVector& dir, WPlane* pPlane);
	float CheckCollision(const WVector& pos, const WVector& dir, int* pIndex,
		bool bFlag);

private:
	WVector closestPointOnTriangle(const WVector& p, const WVector& a,
		const WVector& b, const WVector& c) const;
	WVector closestPointOnLine(const WVector& a, const WVector& b,
		const WVector& p) const;
	WVector DistanceBetweenRayNSegment(const WVector& rayPos,
		const WVector& rayDir, const WVector& segPos, const WVector& segDir);
	float IntersectRayTriangle(const WVector& orig, const WVector& dir,
		const WVector* tri);
	float intersectPolygon(const WVector& pos, const WVector& center,
		const WVector& vel) const;
	WVector GetCollisionPoint(const WVector& dir);

private:
	WVector ApplyForce();
	void SetPenaltyPos(const Waabb& water);
	void HoleProcess(float dt);
	float IntersectPoint(WVector dir);
	WVector GetFriction();
	bool StuckInBunker(const WVector& normal);
	void MakeCollisionData(short objIndex);
	void CalcObjMeshData(short objIndex, int triIndex);
	void MakeAfterBurner();
	void MakeVectorSlide(float scale, float limit, float boost, int count);
	const char* FindTexture(int texHandle);
	void ClipDecalPolygon(WVector* pVerts, int num, int plane);
	void ClipDecalTriangle(const WPolySoup::sTriangle* pTri, WVector normal);

public:
	float IntersectRollingBallGround(const WVector& pos, const WVector& vel,
		const float& dist, int& outIndex, WVector& outNormal, bool bFlag1,
		bool bFlag2, bool bBothSides);
	const char* GetBounceSound(int propIndex) const;
	const char* GetRollSound(int propIndex) const;
	const char* GetStepSound(int propIndex) const;
	void SetBaseVtxColor(unsigned long color);
	void SetCondition();
	void SetObjVtxColor(unsigned long color);
	bool SimpleColTest(const WVector& start, const WVector& ray);
	void GetObjList(WVector start, const WVector& ray);
	void GetObjList(Waabb aabb);
	float GetGravity();
	void HoleIn();
	WVector ColObject(const WVector& pos, bool bKeepPos, int* pIndex,
		bool bAll);
	void GravityModifier(float gravity);

	void GetMeshList(WVector pos);
	void GetMeshList(WVector pos, const WVector& dir);
	void GetMeshList(Waabb aabb);
	void SetAvatarPosition(const WVector& pos, float radius);
	float GetHighestGround(WVector pos, int* pIndex);
	float GetLowestGround(WVector pos);
	float GetBasePosY(WVector pos, float offset);
	bool CheckPickRoom(WVector pos);

	void ResetHoleData();
	void UpdateVtxColor(float dt);
	int GetMeshIndex(const WVector& pos, bool bObject);
	float GetGroundSlope(int meshIndex);
	void UpdateProperty();
	void PreProcess(float dt, bool bOneFrame);
	int CheckCamera();
	void DecalFragments(const WVector* box, const WVector& normal,
		WVector* pVerts, int* pVertNum, int maxVerts, unsigned short* pIndices,
		int* pIndexNum, int maxIndices, bool bAll);
	void AddWater(Waabb aabb, int type);
	unsigned char GetGroundType(WVector pos, bool bCheckTee,
		CGolfBall::eWater* water);
	WVector GetGroundPoint(WVector pos, bool bObject, int* index, bool bWater);
	float GetGreenPos(const WVector& pos);
	WVector GetRayIntersection(WVector start, WVector ray);
	WVector GetRayIntersectionObj(WVector start, WVector ray);
	float GetShadowIntensity(const WVector& pos);
	WVector GetRayIntersectionWall(WVector start, WVector ray);
	void BallProcess(float dt, bool bCupCapture = true);
	void DrawDecal(int texHandle, const WVector& pos, const WVector& dirX,
		const WVector& dirZ, float width, float height, enumPolyBlend blend,
		bool bFlag);
	void Reserve(short num);
	bool IsOBArea(const WVector& pos);
	void MakeBaseStructure(WPolySoup::sModel* model, bool bRebuild);
	void MakeObjStructure(short index, int modelIndex, bool bRebuild);

	void SetPolySoup(WPolySoup* pPolySoup) { m_pPolySoup = pPolySoup; }
	float GetMinPowerOnGround(const WVector& pos);
	float GetMinPowerOnGround();
	WVector GetMeshNormal(int index);
	WVector GetMeshNormal(const WVector& pos);
	float GetMaxPowerOnGround(const WVector& pos);
	float RayIntersectAll(const WVector& start, const WVector& ray,
		bool bObject);

#ifdef REBANG_CONSOLE_CPP
	// HACK: only console.cpp sees these inline bodies: they occupy IL in every unit that includes this
	// header (fontinfo's pow(float,int) moves)
	void SetBounceFactor(float f) { m_bounceFactor = f; }
	void SetRollFactor(float f) { m_rollFactor = f; }
	void SetCondition(float f) { m_condition = f; }
	float GetGreenFactor() const { return m_greenFactor; }
	void SetGreenFactor(float f) { m_greenFactor = f; }
	void PaintIndex(int i) { m_paintIndex = i; }
#else
	void SetBounceFactor(float f);
	void SetRollFactor(float f);
	void SetCondition(float f);
	float GetGreenFactor() const;
	void SetGreenFactor(float f);
	void PaintIndex(int i);
	// HACK: never defined; name-count canary (polysoup WPolySoup::MakeStatistics counts the bodies above)
	void RbQuadTreePad0();
	void RbQuadTreePad1();
	void RbQuadTreePad2();
	void RbQuadTreePad3();
	void RbQuadTreePad4();
	void RbQuadTreePad5();
#endif
	void CalcGreenPlane();

	CQuadTree();
	~CQuadTree();
	WVector TestCameraCollision(const WVector& pos);
	int GetBounceCount();
	int GetTextureHandle(const WVector& pos);
	void ResetWater();
	const char* GetStepSound(const WVector& pos);
	WVector GetMeshObjcet(const WVector& pos);
	int GetObjIndex(const WVector& pos, bool bFlag);
	bool OverlappedWithObject(WVector pos, float radius);
	void GetAABB(Waabb& aabb);
	bool IsFallenIntoWater(WVector pos, Waabb* pAabb, bool bKeepWater);
	bool IsOverWater(WVector pos);
	const char* GetTextureName(const WVector& pos);
	void Display();
	bool TraceAABB_BackGround(const WVector& start, const WVector& end,
		const Waabb& box, trace_s* pTrace, WPolySoup::sModel* pModel);

	void SetRandSeed(unsigned long seed);
	float GetMaxPowerOnGround() const;
	int GetObjColNum();
	void ResetVariable();
	const std::vector<sColData>& GetColList() { return m_colList; }

	void SetCaddieBox(const Waabb& box) { m_caddieBox = box; }
	unsigned char CollideBetweenBallandCaddie()
	{
		return m_bCollideBallAndCaddie;
	}

	WPolySoup* m_pPolySoup;
	sQuadPuppetHolder* m_pHolder;
	int m_minCol;
	int m_minRow;
	int m_maxCol;
	int m_maxRow;
	int m_meshList[0x800];
	int m_meshNum;
	short m_objList[0x20];
	unsigned char m_objNum;
	unsigned char m_unused205d[0x3];
	int m_quadWidth;
	int m_quadHeight;
	WVector m_quadOrigin;
	std::vector<sWater> m_water;
	WVector m_penaltyPos;
	float m_rollFactor;
	float m_bounceFactor;
	float m_condition;
	Waabb m_greenAabb;
	WVector m_greenPoint;
	float m_greenFactor;
	WPlane m_greenPlane;
	int m_paintIndex;
	int m_bounceCount;
	WVector* m_pDecalVerts;
	int m_decalVertNum;
	int m_decalVertMax;
	WPlane m_decalPlanes[6];
	Waabb m_aabb2148;
	WPolySoup::sQuad* m_pQuad;
	Waabb m_caddieBox;
	unsigned char m_bCollideBallAndCaddie;
	unsigned char m_unused217d[0x3];
	// 983: o m_holeCupRadius do 645 (+0x2180) saiu; cada função calcula o raio do copo com o 0046f540
	// (Scale983, jp/aiplayer.cpp). Os nomes abaixo guardam o deslocamento do 645; o do 983 vai no comentário.
	float m_unk2184;          // 983: +0x2180
	int m_unk2188;            // +0x2184
	WVector m_holeDist;       // +0x2188
	float m_groundHeight;     // +0x2194
	bool m_b219c;             // +0x2198
	bool m_b219d;             // +0x2199
	bool m_b219e;             // +0x219a
	WVector m_baseColor;      // +0x219c
	WVector m_objColor;       // +0x21a8
	int m_unk21b8;            // +0x21b4
	float m_frameTime;        // +0x21b8
	unsigned long m_frame;    // +0x21bc
	std::vector<CAniObj*> m_aniObjs; // +0x21c0
	unsigned long m_randSeed; // +0x21d0
	float m_unk21d8;          // +0x21d4
	WVector m_vec21d8_983;    // +0x21d8 (novo; ZERO no construtor 0095f8c0; o BounceProcess 00965516 soma à velocidade)
	sColData m_colData;       // +0x21e4
	std::vector<sColData> m_colList; // +0x2208
	unsigned char m_unused2210[0x10]; // +0x2218
	int* m_pArray2220;        // +0x2228
	int* m_pArray2224;        // +0x222c
	float m_gravity;          // +0x2230
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbParsepuppetscripFunclets(); // HACK: EH funclets of the naked ParsePuppetScript (nakedify)
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbGetmeshindexFunclets(); // HACK: EH funclets of the naked GetMeshIndex (nakedify)
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbGetobjindexFunclets(); // HACK: EH funclets of the naked GetObjIndex (nakedify)
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbMakebasestructurFunclets(); // HACK: EH funclets of the naked MakeBaseStructure (nakedify)
#endif
#ifndef REBANG_SEMANTIC_ONLY
public:
	static void __cdecl
	RbMakeobjstructureFunclets(); // HACK: EH funclets of the naked MakeObjStructure (nakedify)
#endif
#ifdef REBANG_GOLFRULE_PCH // HACK: golfrule's inline accessors (other includers keep their IL)
public:
	void SetSlopeFactor(float factor) { m_unk21d8 = factor; }
	float GetLowest() const { return m_groundHeight; }
	WVector GetPenaltyPos() { return m_penaltyPos; }
	void SetFrame(unsigned long frame)
	{
		m_frame = frame;
		*(unsigned long*)&m_frameTime = 0;
	}
	unsigned long GetFrame() { return m_frame; }
#endif
#ifdef REBANG_GOLFTASK_CPP // HACK: other includers keep their IL (emission order)
	void SetFrame(unsigned long frame)
	{
		m_frame = frame;
		*(unsigned long*)&m_frameTime = 0;
	}
	unsigned long GetFrame() { return m_frame; }
#endif
};

class CPVSPool
{
public:
	CQuadTree& GetInstance();
	static void __fastcall SetInstanceIdx(int idx);

	CQuadTree m_pool[2];
	static int ms_InstanceIdx;
};

extern int g_colNum;
extern char g_colTex[16][32];

CQuadTree& GetPVS();
void __fastcall SetPVSIndex(int idx);
