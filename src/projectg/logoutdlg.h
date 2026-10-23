#pragma once

#include "frform.h"

class FrButton;
class FrLogoutDlg : public FrForm
{
	DECLARE_OBJECT(FrLogoutDlg)
	FrLogoutDlg();

	void DisableServerSelect();

protected:
	virtual void OnProc(const float dt);

	void OnServerBtnInit(int param);
	void OnServerBtnUp();
	void OnLogoutBtnInit(int param);
	void OnLogoutBtnUp();
	void OnExitBtnInit(int param);
	void OnExitBtnUp();

	FrButton* m_pServerBtn;
	FrButton* m_pLogoutBtn;
	FrButton* m_pExitBtn;
	FrButton* m_pDescBtn;

	void DoLogout983(); // 983: 00adc440 (o corpo antigo do OnLogoutBtnUp)

	DECLARE_FRESH_MSGMAP()
public:
	bool m_bExitRequested983;   // 983 +0x120: "exit" fora das telas de login: fecha e o CTaskMain::OnQuitDlgResult (00657200) decide
	bool m_bLogoutRequested983; // 983 +0x121: idem para "logout" (o construtor 00adbdb0 zera os dois com um word)
	char unk983_fim[0xe]; // 983: sizeof 0x130 (push antes do operator new em 00adbe50); 0x122-0x12f sem escrita na unidade
};
