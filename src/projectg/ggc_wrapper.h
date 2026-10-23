#pragma once

class WReceivedPacket;

BOOL _GGC_Init();
void _GGC_End();
void _GGC_SetHwnd(HWND hWnd);
void _GGC_SendUserID(const char* id);
BOOL _GGC_CheckGameMon();
void _GGC_CSAuth2(WReceivedPacket& packet);
BOOL CALLBACK NPGameMonCallback(DWORD dwMsg, DWORD dwArg);
