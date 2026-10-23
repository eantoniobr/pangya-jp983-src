#pragma once

#include "frform.h"

class FrEdit;

class GGC_Dlg : public FrForm
{
public:
	DECLARE_OBJECT(GGC_Dlg)

	GGC_Dlg()
		: m_pEdit(NULL)
	{
	}

protected:
	void OnMessage_Init(int param);

	FrEdit* m_pEdit;

	DECLARE_FRESH_MSGMAP()
};
