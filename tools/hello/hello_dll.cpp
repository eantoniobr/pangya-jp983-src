// "Olá" do build: uma dll com um export, no mesmo molde da wangreal.dll (def + /MD).
#include <windows.h>
#include <string>

const char* __cdecl HelloName()
{
    static std::string s = std::string("jp983src ") + "hello.dll";
    return s.c_str();
}

int __cdecl HelloVersion()
{
    return _MSC_FULL_VER;
}
