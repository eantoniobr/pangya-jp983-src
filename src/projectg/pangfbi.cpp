#include "minatl.h"
#include "pangfbi.h"
#include "generichttpclient.h"

CPangFBI::CPangFBI()
{
}

CPangFBI::~CPangFBI()
{
}

void CPangFBI::ProcessReport(const char* type, const char* data)
{
	if (strcmpi("crime_log", type) == 0)
	{
		int crimeType = 0;
		char szFile[1024];

		char szID[128] = { 0 };
		sscanf(data, "%s %d %s", szID, &crimeType, szFile);

		FILE* fp = fopen(szFile, "rb");

		if (fp == NULL)
			return;
		fclose(fp);

		GenericHTTPClient* pClient = new GenericHTTPClient;

		pClient->InitilizePostArguments();

		pClient->AddPostArguments("id", std::string(szID).c_str(), FALSE);
		pClient->AddPostArguments("type", crimeType);
		pClient->AddPostArguments("file", std::string(szFile).c_str(), TRUE);

		if (pClient->Request(
				"http://157.7.172.65:50007/Report/CrimeReport.aspx",
				3, "MERONG(0.9/;p)"))
		{
			pClient->QueryHTTPResponse();
		}

		delete pClient;
		DeleteFile(szFile);
	}
	else if (strcmpi("app_log", type) == 0)
	{
		int code = 0;
		char szUserID[128] = { 0 };
		char szPacketVer[64];
		char szClientVer[64], szComment[128];

		sscanf(data, "%d %s %s %s %s", &code, szUserID, szPacketVer,
			szClientVer, szComment);

		GenericHTTPClient* pClient = new GenericHTTPClient;
		if (pClient == NULL)
			return;
		pClient->InitilizePostArguments();

		pClient->AddPostArguments("code", code);
		pClient->AddPostArguments("userid", std::string(szUserID).c_str(), FALSE);
		pClient->AddPostArguments("packet_ver", std::string(szPacketVer).c_str(), FALSE);
		pClient->AddPostArguments("client_ver", std::string(szClientVer).c_str(), FALSE);
		pClient->AddPostArguments("comment", std::string(szComment).c_str(), FALSE);

		if (pClient->Request(
				"http://157.7.172.65:50007/Report/ReportError.aspx",
				3, "MERONG(0.9/;p)"))
		{
			pClient->QueryHTTPResponse();
		}

		delete pClient;
	}
}
