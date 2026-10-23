// F2.10: carrega uma wangreal.dll e chama os 4 exports (sem criar dispositivo). uso: smoke.exe caminho.dll
#include <windows.h>
#include <stdio.h>
struct Dev { char pad[0x200]; };
int main(int argc, char** argv)
{
	HMODULE h = LoadLibraryA(argv[1]);
	if (!h) { printf("LoadLibrary falhou: %lu\n", GetLastError()); return 1; }
	typedef char* (__cdecl *FnStr)();
	typedef void* (__cdecl *FnEnum)(int);
	FnStr ver = (FnStr)GetProcAddress(h, "WVersion"), name = (FnStr)GetProcAddress(h, "WDeviceName");
	FnEnum ev = (FnEnum)GetProcAddress(h, "WEnumVideoDevices"), ei = (FnEnum)GetProcAddress(h, "WEnumInputDevices");
	printf("exports: %d %d %d %d\n", ver != 0, name != 0, ev != 0, ei != 0);
	printf("WVersion    = \"%s\"\n", ver());
	printf("WDeviceName = \"%s\"\n", name());
	for (int i = 0; i < 4; i++) printf("WEnumVideoDevices(%d) %s  WEnumInputDevices(%d) %s\n", i, ev(i) ? "!=0" : "0", i, ei(i) ? "!=0" : "0");
	FreeLibrary(h);
	printf("FreeLibrary ok\n");
	return 0;
}
