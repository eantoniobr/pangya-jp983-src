#pragma once

#include "frcmdtarget.h"

class GGC_Dlg;
class FrForm;

class GGC_Helper : public FrCmdTarget
{
	friend GGC_Helper* GGC_GetHelper();

protected:
	GGC_Helper();

public:
	virtual ~GGC_Helper();

	bool StackError(unsigned long error, bool bCritical);
	bool GetFirstCriticalErrorMessage(unsigned long& error,
		std::string& message);
	unsigned int GetCriticalErrorCount() const
	{
		return m_criticalErrors.size();
	}
	void ForceShutdown();
	void Reset();

protected:
	bool StackApprovableError(unsigned long error);
	bool StackCriticalError(unsigned long error);
	void GetErrorMessage(unsigned long error, std::string& message);
	bool OnGameGuardDlgResult(int result, FrForm* form);

	typedef std::vector<unsigned long>::iterator ErrorIterator;

	std::map<unsigned long, std::string> m_errorMessages;
	std::vector<unsigned long> m_approvableErrors;
	std::vector<unsigned long> m_criticalErrors;
	char m_buffer[1024];
	GGC_Dlg* m_pDlg;
};

GGC_Helper* GGC_GetHelper();
