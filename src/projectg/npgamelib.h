#pragma once

struct _GG_AUTH_DATA
{
	unsigned long dwIndex;
	unsigned long dwValue1;
	unsigned long dwValue2;
	unsigned long dwValue3;
};
typedef _GG_AUTH_DATA GG_AUTH_DATA;
typedef _GG_AUTH_DATA* PGG_AUTH_DATA;

#define NPGAMEMON_SUCCESS 0x755
#define NPGAMEMON_CHECK_CSAUTH2 1017

extern "C"
{
	DWORD __cdecl InitNPGameMon();
	void __cdecl SetHwndToGameMon(HWND hWnd);
	DWORD __cdecl GGGetLastError();
	DWORD __cdecl PreInitNPGameMonA(LPCSTR szGameName);
	DWORD __cdecl CheckNPGameMon();
	DWORD __cdecl SendUserIDToGameMonA(LPCSTR szUserID);
	DWORD __cdecl SendCSAuthToGameMon(DWORD dwAuth);
	DWORD __cdecl SendCSAuth2ToGameMon(PGG_AUTH_DATA pAuth);
	LPCSTR __cdecl GetInfoFromGameMon();
	LPBYTE __cdecl GetHackInfoFromGameMon(LPDWORD pdwSize);
	DWORD __cdecl CloseNPGameMon();
}

class CNPGameLib
{
public:
	CNPGameLib(LPCSTR lpszGameName) { PreInitNPGameMonA(lpszGameName); }

	~CNPGameLib() { CloseNPGameMon(); }

	DWORD Init() { return InitNPGameMon(); }

	void SetHwnd(HWND hWnd) { SetHwndToGameMon(hWnd); }

	DWORD Check() { return CheckNPGameMon(); }

	DWORD Send(LPCSTR lpszUserID) { return SendUserIDToGameMonA(lpszUserID); }

	DWORD Auth2(PGG_AUTH_DATA pCallbackData)
	{
		return SendCSAuth2ToGameMon(pCallbackData);
	}
};

#define NPGAMEMON_COMM_ERROR 1001
#define NPGAMEMON_COMM_CLOSE 1002
#define NPGAMEMON_SPEEDHACK 1011
#define NPGAMEMON_GAMEHACK_KILLED 1012
#define NPGAMEMON_GAMEHACK_DETECT 1013
#define NPGAMEMON_INIT_ERROR 1014
#define NPGAMEMON_GAMEHACK_DOUBT 1015

#define NPGAMEMON_ERROR_EXIST 110
#define NPGAMEMON_ERROR_NPSCAN 112
#define NPGAMEMON_ERROR_INIT 114
#define NPGAMEMON_ERROR_GAME_EXIST 115
#define NPGAMEMON_ERROR_AUTH_INI 120
#define NPGAMEMON_ERROR_AUTH_GAMEGUARD 124
#define NPGAMEMON_ERROR_NFOUND_INI 150
#define NPGAMEMON_ERROR_NFOUND_GAMEMON 153
#define NPGAMEMON_ERROR_CRYPTOAPI 155
#define NPGAMEMON_ERROR_EXECUTE 170
#define NPGAMEMON_ERROR_ILLEGAL_PRG 200
#define NPGMUP_ERROR_DOWNCFG 340
#define NPGMUP_ERROR_ABORT 350
#define NPGMUP_ERROR_AUTH 360
#define NPGMUP_ERROR_CONNECT 380
