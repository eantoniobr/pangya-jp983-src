#include <stdio.h>
#include <string>
class CRealMyRoom_AvatarBurden { public: CRealMyRoom_AvatarBurden(int, struct sCharacterInfo*, class CPetFrame*); int x; };
class CTimerManagerGpJp { public: int AddTimer983(float, const char*, class CTimerEvent*); };
const char* __fastcall GetGameString(unsigned int);
class RFWnd { public: static const std::wstring EventDraw; };
class WVector { public: float x, y, z; };
extern const WVector g_vUp983_e42538;
extern const char* g_lobbyBgLua983;
int main()
{
	int esp0, esp1;
	__asm mov esp0, esp
	char buf[16];
	CRealMyRoom_AvatarBurden* p = new (buf) CRealMyRoom_AvatarBurden(1, 0, 0);
	int r = ((CTimerManagerGpJp*)buf)->AddTimer983(1.0f, "x", 0);
	const char* s = GetGameString(5);
	__asm mov esp1, esp
	printf("this=%d r=%d s=%p esp_ok=%d\n", p == (void*)buf, r, s, esp0 == esp1);
	printf("EventDraw=%S vUp=(%g,%g,%g) bg=%s\n", RFWnd::EventDraw.c_str(), g_vUp983_e42538.x, g_vUp983_e42538.y, g_vUp983_e42538.z, g_lobbyBgLua983);
	return 0;
}
