#!/usr/bin/env python3
"""A178: rastro provisório do heap 0xC0000374 da carga da partida (PATCH_PY do tools/v6/f4rastro/wt_build.sh).

Roda DENTRO do worktree; não vai para o repositório. Insere:
- exceptionreport.cpp: handler vetorizado que grava exception.log/.dmp/stack.log no 0xC0000374 (o filtro de exceção
  não-tratada não é chamado nele -> hoje morre sem dump);
- taskmanager.cpp (caminho C): HeapValidate antes/depois do OnLoad de cada ator (thread de carga, com o vtable) e a cada
  quadro do OnProcessWhileLoading (thread principal). Primeira falha vira linha "rastro: HEAP ..." no jp983_stubs.log.
"""

def patch(path, pairs):
    s = open(path, encoding='latin-1').read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old)
        s = s.replace(old, new)
    open(path, 'w', encoding='latin-1').write(s)

patch('src/shared/exceptionreport.cpp', [
    ('void CExceptionReport::Init()\n{\n',
     'extern "C" __declspec(dllimport) void* __stdcall AddVectoredExceptionHandler(unsigned long, LONG(__stdcall*)(EXCEPTION_POINTERS*));\n'
     'static LONG __stdcall HeapVeh(EXCEPTION_POINTERS* p)\n{\n'
     '\tif (p->ExceptionRecord->ExceptionCode == 0xC0000374)\n\t\tRecordExceptionInfo(p);\n'
     '\treturn EXCEPTION_CONTINUE_SEARCH;\n}\n\n'
     'void CExceptionReport::Init()\n{\n\tAddVectoredExceptionHandler(1, HeapVeh);\n'),
])

PROBE = ('#include <malloc.h>\n'
         'extern "C" void __cdecl jp983_rastro(const char* fmt, ...);\n'
         'static void HeapProbe(const char* where, int n, const void* p)\n{\n'
         '\tstatic volatile long s_bad;\n'
         '\tif (s_bad)\n\t\treturn;\n'
         '\tif (!HeapValidate((HANDLE)_get_heap_handle(), 0, NULL))\n\t{\n\t\ts_bad = 1;\n'
         '\t\tjp983_rastro("HEAP RUIM %s n=%d p=%p tid=%lu", where, n, p, GetCurrentThreadId());\n\t}\n}\n\n')

patch('src/projectg/taskmanager.cpp', [
    ('struct sLoadParam\n', PROBE + 'struct sLoadParam\n'),
    ('\n\t\t\tpActor->actor->OnLoad();\n',
     '\n\t\t\tjp983_rastro("load %d vt=%p tid=%lu", pLoad->loaded, *(void**)pActor->actor, GetCurrentThreadId());\n'
     '\t\t\tHeapProbe("antes", pLoad->loaded, *(void**)pActor->actor);\n'
     '\t\t\tpActor->actor->OnLoad();\n'
     '\t\t\tHeapProbe("depois", pLoad->loaded, *(void**)pActor->actor);\n'),
    ('\t\tm_pLoadingFresh->OnProcess(delta);\n',
     '\t\tHeapProbe("principal", g_LoadParam.loaded, m_pLoadingFresh);\n'
     '\t\tm_pLoadingFresh->OnProcess(delta);\n'),
])
print('heap_trace: ok')

# A178 (2ª rodada): a178-3 e c106-2 morreram no delete[] do bi (0x28, do DecodeHeader) dentro do Bitmap::Create do
# DecodeImage. Valida só esse bloco em 3 pontos e conta decodificações JPEG simultâneas (threads).
JPG = ('#include <malloc.h>\nextern "C" void __cdecl jp983_rastro(const char* fmt, ...);\n'
       'static volatile long s_jpegIn;\n'
       'static void BiProbe(const char* where, const void* bi, const char* name)\n{\n'
       '\tstatic volatile long s_n;\n'
       '\tif (bi && !HeapValidate((HANDLE)_get_heap_handle(), 0, (void*)bi) && InterlockedIncrement(&s_n) < 20)\n'
       '\t\tjp983_rastro("BI RUIM %s bi=%p tid=%lu jpeg_simult=%ld", where, bi, GetCurrentThreadId(), s_jpegIn);\n}\n\n')
patch('src/engine/wresrcmng.cpp', [
    ('bool JpegBitmap::DecodeHeader()\n{\n',
     JPG + 'bool JpegBitmap::DecodeHeader()\n{\n'
     '\tif (InterlockedIncrement(&s_jpegIn) > 1)\n\t\tjp983_rastro("jpeg simultaneo header tid=%lu n=%ld", GetCurrentThreadId(), s_jpegIn);\n'
     '\tstruct Out { ~Out() { InterlockedDecrement(&s_jpegIn); } } out;\n'),
    ('\t\tbi->bmiHeader.biBitCount = image.JPGChannels == 1 ? 8 : 24;\n\t\tijlFree(&image);\n',
     '\t\tbi->bmiHeader.biBitCount = image.JPGChannels == 1 ? 8 : 24;\n\t\tBiProbe("header", bi, 0);\n\t\tijlFree(&image);\n'
     '\t\tBiProbe("header_ijlFree", bi, 0);\n'),
    ('bool JpegBitmap::DecodeImage()\n{\n',
     'bool JpegBitmap::DecodeImage()\n{\n'
     '\tif (InterlockedIncrement(&s_jpegIn) > 1)\n\t\tjp983_rastro("jpeg simultaneo image tid=%lu n=%ld", GetCurrentThreadId(), s_jpegIn);\n'
     '\tstruct Out { ~Out() { InterlockedDecrement(&s_jpegIn); } } out;\n'
     '\tBiProbe("image_inicio", bi, 0);\n'),
    ('\tif (ijlRead(&image, IJL_JBUFF_READPARAMS) == IJL_OK)\n\t{\n\t\tCreate(',
     '\tif (ijlRead(&image, IJL_JBUFF_READPARAMS) == IJL_OK)\n\t{\n\t\tBiProbe("image_ijlRead", bi, 0);\n\t\tCreate('),
])
print('heap_trace (jpeg): ok')
