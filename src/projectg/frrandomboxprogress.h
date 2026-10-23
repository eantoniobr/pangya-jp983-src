#pragma once
// JP 983: sizeof 0x130 (operator new de 008c53d0), com o "image" (FrArea, +0x118) que as derivadas do 983 animam.
// FRRANDOMBOXPROGRESS_983 liga o campo e o C_ASSERT da FrClubSetResetProgress (include/jp/clubsetresetwnd.h, frente B).
#define FRRANDOMBOXPROGRESS_983 1
class FrGaugeBar;
class FrArea;
#include "frform.h"
class FrStatic;
class FrRandomBoxProgress : public FrForm
{
public:
	DECLARE_OBJECT(FrRandomBoxProgress)

	FrRandomBoxProgress();
	virtual ~FrRandomBoxProgress();

	void SetExplane(const char* text);

protected:
	virtual bool OnInit();
	virtual void OnProc(const float dt);

	void OnCancelUp(int param);
	void OnProgressInit(int param);
	void OnExplaneStatic_Init(int param);
	void OnImageInit983(int param); // 008c55a0: "image" FRCMD_INIT

	FrGaugeBar* m_pProgress; // +0x110
	FrStatic* m_pExplaneStatic; // +0x114
	FrArea* m_pImage983; // +0x118
	unsigned long m_boxTid; // +0x11c
	float m_totalTime; // +0x120
	float m_elapsedTime; // +0x124
	unsigned char m_unk983_128[8]; // +0x128 (sem uso visto no 983)

	DECLARE_FRESH_MSGMAP()

public:
	void SetBoxTid(unsigned long tid) { m_boxTid = tid; }
};
