#pragma once

#include <string>
#include "frform.h"

// NOTE: these guild forms live in the ingameguild*dlg units; only what the
// guild actor needs is declared here
namespace _guild
{
	class FrCreateGuildKit : public FrForm
	{
	public:
		static const WRTTI m_RTTI;

		FrCreateGuildKit();

		void SetConfirmGuildName(const char* name);

		// TODO: this class definition is incomplete
		unsigned char m_unused110[0x30];
	};

	class FrRegisterGuildMark : public FrForm
	{
	public:
		static const WRTTI m_RTTI;

		FrRegisterGuildMark();

		void RequestUpload(int result, const std::string& fileName);

		// TODO: this class definition is incomplete
		unsigned char m_unused110[0x40];
	};

	class FrChangeGuildName : public FrForm
	{
	public:
		static const WRTTI m_RTTI;

		FrChangeGuildName();

		bool IsHaveGuild();
		void SetConfirmedName(const char* name);

		// TODO: this class definition is incomplete
		unsigned char m_unused110[0x30];
	};

	class FrGuildJoin : public FrForm
	{
	public:
		static const WRTTI m_RTTI;

		FrGuildJoin();

		void SetGuildNumber(int guildNumber);
		void SetSuccessRequest();

		// TODO: this class definition is incomplete
		unsigned char m_unused110[0x20];
	};
}
