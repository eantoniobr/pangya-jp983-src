#!/usr/bin/env python3
"""A178: "quarentena" de frees para achar a escrita após free do heap 0xC0000374 (PATCH_PY do wt_build.sh; inclui
heap_trace.py e caddie_trace.py). Só no worktree.

operator delete/delete[] globais (taskmanager.cpp): por 20 s a partir de cada CTaskManager::ClearTask, o bloco liberado é
preenchido com 0xDD; os de até 4 KB não voltam ao heap (até 65536). A cada HeapProbe (quadro da thread principal e
antes/depois de cada ator) os blocos em quarentena são conferidos: o 1º byte mudado vira "rastro: UAF ..." com o bloco,
tamanho, deslocamento, dword escrito e o endereço de quem liberou (??_G/??_E = a classe).
"""
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'caddie_trace.py')).read())

QUAR = r'''#include <intrin.h>
#pragma intrinsic(_ReturnAddress)
namespace
{
struct QBlock
{
	unsigned char* p;
	unsigned size;
	void* ret;
};
const long QMAX = 65536;
QBlock g_q[QMAX];
volatile long g_qn, g_qlock, g_qBad;
volatile unsigned long g_qStart;
void QLock()
{
	while (InterlockedExchange(&g_qlock, 1))
		Sleep(0);
}
void QUnlock()
{
	InterlockedExchange(&g_qlock, 0);
}
void QCheckLocked(const char* where)
{
	for (long i = 0; i < g_qn; ++i)
	{
		unsigned char* p = g_q[i].p;
		for (unsigned k = 0; k < g_q[i].size; ++k)
			if (p[k] != 0xdd)
			{
				if (InterlockedIncrement(&g_qBad) <= 40)
					jp983_rastro("UAF %s bloco=%p tam=%u off=%u dw=%08x liberado_por=%p tid=%lu t=%lu", where, p,
						g_q[i].size, k, *(unsigned*)(p + (k & ~3u)), g_q[i].ret, GetCurrentThreadId(),
						GetTickCount() - g_qStart);
				memset(p, 0xdd, g_q[i].size);
				break;
			}
	}
}
}
void JpQuarantineCheck(const char* where)
{
	if (!g_qStart)
		return;
	QLock();
	QCheckLocked(where);
	QUnlock();
}
void JpQuarantineStart()
{
	QLock();
	QCheckLocked("start");
	for (long i = 0; i < g_qn; ++i)
		free(g_q[i].p);
	g_qn = 0;
	g_qStart = GetTickCount() | 1;
	QUnlock();
	jp983_rastro("quarentena ligada tid=%lu", GetCurrentThreadId());
}
static void QFree(void* p, void* ret)
{
	if (!p)
		return;
	unsigned long t = g_qStart;
	if (t && GetTickCount() - t < 20000)
	{
		unsigned n = (unsigned)_msize(p);
		memset(p, 0xdd, n);
		if (n <= 4096)
		{
			QLock();
			if (g_qn < QMAX)
			{
				g_q[g_qn].p = (unsigned char*)p;
				g_q[g_qn].size = n;
				g_q[g_qn].ret = ret;
				++g_qn;
				QUnlock();
				return;
			}
			QUnlock();
		}
	}
	free(p);
}
void __cdecl operator delete(void* p)
{
	QFree(p, _ReturnAddress());
}
void __cdecl operator delete[](void* p)
{
	QFree(p, _ReturnAddress());
}

'''

patch('src/projectg/taskmanager.cpp', [
    ('static void HeapProbe(const char* where, int n, const void* p)\n{\n',
     QUAR + 'static void HeapProbe(const char* where, int n, const void* p)\n{\n\tJpQuarantineCheck(where);\n'),
    ('void CTaskManager::ClearTask()\n{\n', 'void CTaskManager::ClearTask()\n{\n\tJpQuarantineStart();\n'),
])
print('uaf_trace: ok')
