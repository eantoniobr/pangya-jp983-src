#pragma once

#include <string>

unsigned int __stdcall RSSThreadFunc(void* pParam);

class RSSManager
{
	friend unsigned int __stdcall RSSThreadFunc(void* pParam);

public:
	RSSManager();
	virtual ~RSSManager();

	void GetRSSFile(unsigned long guildIdx, void (*pfnCallback)(int));
	void GetRSSFile_JP(unsigned long guildIdx, void (*pfnCallback)(int),
		const char* address, const char* path);
	bool IsNewRss();
	void ResetVars();

private:
	void CallBackFunction(int result);
	const char* LoadFirstId(const char* filename);

	unsigned long m_guildIdx;
	bool m_bNewRss;
	bool m_bComplete;
	void (*m_pfnCallback)(int);
	std::string m_address;
	std::string m_path;
	unsigned char m_unknown48[4];

public:
	bool IsComplete() { return m_bComplete; }
};
