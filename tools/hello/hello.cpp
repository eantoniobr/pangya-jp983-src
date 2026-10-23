// "Olá" do build: exe que carrega a hello.dll pelos exports, como o ProjectG faz com a wangreal.dll.
#include <windows.h>
#include <stdio.h>

int main()
{
    HMODULE h = LoadLibraryA("hello.dll");
    if (!h) { printf("LoadLibrary falhou: %lu\n", GetLastError()); return 1; }
    typedef const char* (__cdecl *NameFn)();
    typedef int (__cdecl *VerFn)();
    NameFn name = (NameFn)GetProcAddress(h, "HelloName");
    VerFn ver = (VerFn)GetProcAddress(h, "HelloVersion");
    if (!name || !ver) { printf("GetProcAddress falhou\n"); return 2; }
    printf("ola de %s, _MSC_FULL_VER=%d\n", name(), ver());
    return 0;
}
