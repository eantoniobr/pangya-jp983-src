#pragma once

#include <map>

class CAztecHoleinEffect : public WSingleton<CAztecHoleinEffect>
{
public:
	CAztecHoleinEffect();
	virtual ~CAztecHoleinEffect();

	bool LoadEffectFromIFF();
	bool Initialize();
	bool PlayEffect(unsigned long effect);

protected:
	void Clear();
	const char* GetEffectName(unsigned long effect);
	bool RegisterEffect(unsigned long effect, const char* name);

protected:
	unsigned long m_unknown28;
	unsigned long m_unknown2c;
	std::map<unsigned long, const char*> m_iffEffectMap;
	std::map<unsigned long, const char*> m_effectMap;
};
