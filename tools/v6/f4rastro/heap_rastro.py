#!/usr/bin/env python3
"""C106: rastro do heap corrompido (0xC0000374 nos campos 0x01/0x04/0x05/0x0D/0x10/0x13), só na cópia (PATCH_PY do wt_build.sh).
jp983_heap_check(ponto, nome): guarda "ponto nome" em jp983_file_cur/prev (o VEH do falta983.cpp imprime) e valida o heap do
CRT e o do processo; na 1ª falha grava "rastro: heap quebrado em <ponto> <nome> (antes: <anterior>)" no jp983_stubs.log.
Pontos: GetCFile (todo arquivo aberto), fim do LoadBitmap, Combine4Alpha (máscara), FixTexturePart, tela de carga (thread principal).
Uso: tools/v6/f4rastro/wt_build.sh TAG REV tools/v6/f4rastro/heap_rastro.py   (roda dentro do worktree)"""

DECL = 'extern "C" void __cdecl jp983_heap_check(const char* where, const char* name);\n'

def patch(f, trocas):
    s = DECL + open(f, encoding='latin-1').read()  # protótipo no topo: usado antes da definição
    for velho, novo in trocas:
        assert s.count(velho) == 1, (f, velho)
        s = s.replace(velho, novo)
    b = s.encode('latin-1')  # antes de abrir: erro de codificação não trunca o arquivo
    open(f, 'wb').write(b)

check = '''#include <malloc.h>
extern "C" char jp983_file_cur[128], jp983_file_prev[128];
extern "C" void __cdecl jp983_rastro(const char* fmt, ...);
extern "C" void __cdecl jp983_heap_check(const char* where, const char* name)
{
	static bool s_bad;
	lstrcpynA(jp983_file_prev, jp983_file_cur, 128);
	_snprintf(jp983_file_cur, 127, "%s %s t%u", where, name ? name : "", GetCurrentThreadId());
	if (!s_bad && !(HeapValidate((HANDLE)_get_heap_handle(), 0, NULL) && HeapValidate(GetProcessHeap(), 0, NULL)))
	{
		s_bad = true;
		jp983_rastro("heap quebrado em %s (antes: %s)", jp983_file_cur, jp983_file_prev);
	}
}

'''
getc = 'cFile* WResourceManager::GetCFile(const char* filename, int len)\n{\n'
patch('src/engine/wresrcmng.cpp', [
    (getc, check + getc + '\tjp983_heap_check("GetCFile", filename);\n'),
    ('\tif (level == 0 && bitmap)\n\t\tbitmap->Update();\n\n\treturn bitmap;',
     '\tif (level == 0 && bitmap)\n\t\tbitmap->Update();\n\tjp983_heap_check("LoadBitmap.fim", filename);\n\n\treturn bitmap;'),
    ('\t\t\tBitmap* bitmap = Combine4Alpha(*ppBitmap, mask);\n',
     '\t\t\tBitmap* bitmap = Combine4Alpha(*ppBitmap, mask);\n\t\t\tjp983_heap_check("Combine4Alpha", afname);\n'),
    ('\t\t\tvideo->FixTexturePart(hDstTex, rc, pSrc->bi, pSrc->vram, nFlag);\n',
     '\t\t\tjp983_heap_check("FixTexturePart.antes", srcName);\n\t\t\tvideo->FixTexturePart(hDstTex, rc, pSrc->bi, pSrc->vram, nFlag);\n'
     '\t\t\tjp983_heap_check("FixTexturePart.depois", srcName);\n'),
    # C106 v3: janela entre o new[] do DecodeHeader e o delete[] do Create (c106-2/c106-11 detectam ali)
    ('\t\tbi->bmiHeader.biBitCount = image.JPGChannels == 1 ? 8 : 24;\n\t\tijlFree(&image);\n',
     '\t\tbi->bmiHeader.biBitCount = image.JPGChannels == 1 ? 8 : 24;\n\t\tjp983_heap_check("DecodeHeader.new", 0);\n'
     '\t\tijlFree(&image);\n\t\tjp983_heap_check("DecodeHeader.ijlFree", 0);\n'),
    ('\tif (ijlRead(&image, IJL_JBUFF_READPARAMS) == IJL_OK)\n\t{\n\t\tCreate(image.JPGWidth, image.JPGHeight,\n',
     '\tjp983_heap_check("DecodeImage.ijlInit", 0);\n\tif (ijlRead(&image, IJL_JBUFF_READPARAMS) == IJL_OK)\n\t{\n'
     '\t\tjp983_heap_check("DecodeImage.READPARAMS", 0);\n\t\tCreate(image.JPGWidth, image.JPGHeight,\n'),
    ('\t\tif (ijlRead(&image, IJL_JBUFF_READWHOLEIMAGE) == IJL_OK)\n\t\t{\n',
     '\t\tjp983_heap_check("DecodeImage.Create", 0);\n\t\tif (ijlRead(&image, IJL_JBUFF_READWHOLEIMAGE) == IJL_OK)\n\t\t{\n'
     '\t\t\tjp983_heap_check("DecodeImage.WHOLEIMAGE", 0);\n'),
])
patch('src/projectg/taskmanager.cpp', [
    ('\tif (m_pLoadingFresh)\n\t\tm_pLoadingFresh->OnDisplay(true);\n',
     '\tjp983_heap_check("TelaCarga.antes", 0);\n'
     '\tif (m_pLoadingFresh)\n\t\tm_pLoadingFresh->OnDisplay(true);\n\tjp983_heap_check("TelaCarga.depois", 0);\n'),
])
print('heap_rastro: 12 pontos instrumentados')
