#!/usr/bin/env python3
"""A179: guarda de bytes em cada bloco do operator new para achar o estouro do heap 0xC0000374 da carga (PATCH_PY do
wt_build.sh; inclui heap_trace.py e caddie_trace.py, NÃO o uaf_trace.py). Só no worktree.

operator new/new[] globais (taskmanager.cpp): cabeçalho de 24 bytes (lista dupla de blocos vivos, tamanho, quem alocou,
magia) + 8 bytes 0xFD depois do bloco. Conferido no delete (o próprio bloco), em cada HeapProbe (todos os blocos vivos:
quadro da thread principal e antes/depois de cada ator) e no VEH do 0xC0000374. Achado vira "rastro: GUARDA ..." com bloco,
tamanho, onde (cab/fim), dword escrito e o endereço de quem alocou.
"""
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'caddie_trace.py')).read())

GUARD = r'''#include <intrin.h>
#pragma intrinsic(_ReturnAddress)
namespace
{
struct GHdr
{
	GHdr* prev;
	GHdr* next;
	unsigned size;
	void* ret;
	unsigned magic;
	unsigned seq;
};
const unsigned GMAGIC = 0x6a983a17;
GHdr* g_gHead;
volatile long g_glock, g_gBad, g_gSeq;
void GLock()
{
	while (InterlockedExchange(&g_glock, 1))
		Sleep(0);
}
void GUnlock()
{
	InterlockedExchange(&g_glock, 0);
}
// 0 = ok; senão grava o achado e conserta (para não repetir)
void GCheck(GHdr* h, const char* where)
{
	unsigned char* tail = (unsigned char*)(h + 1) + h->size;
	const char* what = h->magic != GMAGIC ? "cab" : 0;
	if (!what)
		for (int k = 0; k < 8; ++k)
			if (tail[k] != 0xfd)
			{
				what = "fim";
				break;
			}
	if (!what)
		return;
	if (InterlockedIncrement(&g_gBad) <= 40)
		jp983_rastro("GUARDA %s %s bloco=%p tam=%u fim=%08x %08x alocado_por=%p seq=%u tid=%lu", where, what, h + 1,
			h->size, *(unsigned*)tail, *(unsigned*)(tail + 4), h->ret, h->seq, GetCurrentThreadId());
	h->magic = GMAGIC;
	memset(tail, 0xfd, 8);
}
void* GNew(size_t n, void* ret)
{
	GHdr* h = (GHdr*)malloc(sizeof(GHdr) + n + 8);
	if (!h)
		throw std::bad_alloc();
	h->size = (unsigned)n;
	h->ret = ret;
	h->magic = GMAGIC;
	h->seq = (unsigned)InterlockedIncrement(&g_gSeq);
	memset((unsigned char*)(h + 1) + n, 0xfd, 8);
	h->prev = 0;
	GLock();
	h->next = g_gHead;
	if (g_gHead)
		g_gHead->prev = h;
	g_gHead = h;
	GUnlock();
	return h + 1;
}
void GDelete(void* p)
{
	if (!p)
		return;
	GHdr* h = (GHdr*)p - 1;
	GLock();
	GCheck(h, "delete");
	if (h->prev)
		h->prev->next = h->next;
	else
		g_gHead = h->next;
	if (h->next)
		h->next->prev = h->prev;
	GUnlock();
	h->magic = 0;
	free(h);
}
}
void JpGuardCheck(const char* where)
{
	GLock();
	for (GHdr* h = g_gHead; h; h = h->next)
		GCheck(h, where);
	GUnlock();
}
void* __cdecl operator new(size_t n)
{
	return GNew(n, _ReturnAddress());
}
void* __cdecl operator new[](size_t n)
{
	return GNew(n, _ReturnAddress());
}
void __cdecl operator delete(void* p)
{
	GDelete(p);
}
void __cdecl operator delete[](void* p)
{
	GDelete(p);
}

'''

patch('src/projectg/taskmanager.cpp', [
    ('static void HeapProbe(const char* where, int n, const void* p)\n{\n',
     GUARD + 'static void HeapProbe(const char* where, int n, const void* p)\n{\n\tJpGuardCheck(where);\n'),
])
patch('src/shared/exceptionreport.cpp', [
    ('static LONG __stdcall HeapVeh(EXCEPTION_POINTERS* p)\n{\n\tif (p->ExceptionRecord->ExceptionCode == 0xC0000374)\n',
     'void JpGuardCheck(const char* where);\n'
     'static LONG __stdcall HeapVeh(EXCEPTION_POINTERS* p)\n{\n\tif (p->ExceptionRecord->ExceptionCode == 0xC0000374)\n'
     '\t\tJpGuardCheck("veh");\n\tif (p->ExceptionRecord->ExceptionCode == 0xC0000374)\n'),
])
print('guard_trace: ok')
