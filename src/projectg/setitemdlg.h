#pragma once

#include "frform.h"

class FrArea;
class FrEdit;
class FrListBox;

class FrSetItemDlg : public FrForm
{
	DECLARE_OBJECT(FrSetItemDlg)

	FrSetItemDlg();

	void SetSetItem(unsigned long typeId);

protected:
	void OnPortraitInit(int param);
	void OnNameInit(int param);
	void OnComponentInit(int param);
	void OnComponentOwnerDraw(int param);
	void OnComponentRBtnDown();

	FrArea* m_pPortrait;
	FrEdit* m_pName;
	FrListBox* m_pComponent;
	IFF_STRUCT::sSetItem* m_pSetItem;

	DECLARE_FRESH_MSGMAP()
};
