#pragma once

#include "frform.h"
struct IFF_ITEM_COMMON;
class FrArea;
class FrStatic;
class FrFortuneDlg : public FrForm
{
	DECLARE_OBJECT(FrFortuneDlg)

	FrFortuneDlg();
	virtual ~FrFortuneDlg();

	void SetTypeId(unsigned long typeId, IFF_ITEM_COMMON* item);

	void SetIcon983(const char* icon);

	unsigned long GetTypeId() { return m_typeId; }

protected:
	void OnPortraitInit(int param);
	void OnDescNameInit(int param);
	void OnDescLevelInit(int param);
	void OnDescDescInit(int param);

	unsigned long m_reserved;
	unsigned long m_typeId;
	FrArea* m_pPortrait;
	FrStatic* m_pDescName;
	FrStatic* m_pDescLevel;
	FrStatic* m_pDescDesc;

	DECLARE_FRESH_MSGMAP()
};
