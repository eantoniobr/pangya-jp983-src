#pragma once

#include <list>
#include <string>
#include "singleton.h"

class CTimerEvent
{
public:
	CTimerEvent();
	virtual ~CTimerEvent();

	virtual void OnTimer() = 0;
	void ClearTimer(const char* name);
	bool AddTimer(float time, const char* name);

protected:	// B72: a FrGrandPrixAwardDlg::OnTimer (00549210) compara e limpa o nome
	std::string m_timerName;
};

class CTimerManager : public WSingleton<CTimerManager>
{
public:
	CTimerManager();
	virtual ~CTimerManager();

	bool AddTimer(float time, const char* name, CTimerEvent* event);
	void AllClear();
	void ClearTimer(const char* name);
	void UpdateTimer(float dt);

private:
	struct sTimer
	{
		float time;
		float elapsed;
		CTimerEvent* event;
		int unk983_c; // 983: dword novo antes de name (lugar pelos votos)
		std::string name;
		bool active;

		void Clear()
		{
			time = 0.0f;
			elapsed = 0.0f;
			event = NULL;
			name.clear();
			active = false;
		}
	};

	std::list<sTimer*> m_timerList;
	sTimer m_timers[10];
};
