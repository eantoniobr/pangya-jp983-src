// JP 983: CGolfRuleHoleInOne (unidade 00544ce0–005469a0, tabela virtual 00d09774, sizeof 0x28 — `push 0x28` em 0067743d).
// Regra dos modos de jogo 0x0d/0x0e (hole-in-one). A classe existe no KR 839 (construtor 00547d20).
#pragma once
#include "golfrulebase.h"
#include <vector>

class CGolfRule;

// JP 983: deriva da CGolfRuleBase (17 virtuais na ordem do 983, vtable 00d1978c); a copia CGolfRuleBaseJp so existia em stubs.
class CGolfRuleHoleInOne : public CGolfRuleBase
{
public:
	CGolfRuleHoleInOne(CGolfRule* pGolfRule);
	virtual ~CGolfRuleHoleInOne();

	virtual void SetPlayer();
	virtual void SetGrade();
	virtual void SetReady();
	virtual void EnableShotReview();
	virtual void OnHoleIn();
	virtual void ReadyNextShot();
	virtual void RequestShotReview(float time);
	virtual void ShowScore(int arg);

	void ResetComboGauge(); // 00545bb0
	void OnShotEnd(); // 00545d20 (chamada pelo CGolfRule::HandleMsg, 00698ae2)

private:
	std::vector<unsigned long> m_list; // +0x18: zerado no construtor, apagado no destrutor; ninguém da unidade usa (tipo suposto)
};

// JP 983: globais e métodos do 983 sem nome no fonte da frente A (empréstimo; endereços em src/projectg/jp/jp.tsv).
class CCameraWorkJp
{
public:
	void Fn6db6c0_983(int arg); // 006db6c0 (camerawork.cpp/capturedbg.cpp; corpo não lido)
};
extern CCameraWorkJp* g_pCameraWork983; // 00e74d30

class CUnk983_e47e20
{
public:
	void SetC(float f) { m_c = f; } // cópia fora de linha 00544f40
	int m_0;
	int m_4;
	int m_8;
	float m_c;
};
extern CUnk983_e47e20* g_pUnk983_e47e20; // 00e47e20
extern bool g_bUnk983_e47e88; // 00e47e88: com ele ligado o fim da tacada conta em +0x1c da estatística do buraco
