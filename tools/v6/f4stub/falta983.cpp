// ---- tempo de execução dos stubs (tools/v6/f4stub/falta983.cpp, copiado no começo do stubs983.cpp)
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>

// Chamada por todo stub de função. Grava em jp983_stubs.log (pasta do exe) e, no padrão, mostra o nome e fecha o jogo.
// Modo "continuar" (o stub volta e devolve 0; menos os "fatal": não dá para voltar com a pilha certa), por qualquer um de:
//   - arquivo jp983_stub_continuar.txt na pasta do exe (o jeito robusto: não depende de como o exe foi lançado);
//   - JP983_STUB=continuar no ambiente.
// O modo é lido a cada chamada (nada guardado em .data: um ijl15 de terceiro com patches de endereço fixo do exe original
// escreve por cima do nosso .data — teste 2, out/F4/RESPOSTA_USUARIO_2a.md) e sem o _stricmp do msvcr100 (o rugburn o engancha).
// Texto das caixas só em ASCII (MessageBoxA usa a página de código do sistema; UTF-8 sai quebrado).
static int jp983_pasta_exe(char* p, const char* arq)
{
	DWORD n = GetModuleFileNameA(NULL, p, MAX_PATH);
	while (n && p[n - 1] != '\\') --n;
	if (n + lstrlenA(arq) + 1 > MAX_PATH) return 0;
	lstrcpyA(p + n, arq);
	return 1;
}

extern "C" int __cdecl jp983_modo_continuar(void)
{
	char p[MAX_PATH];
	if (jp983_pasta_exe(p, "jp983_stub_continuar.txt") && GetFileAttributesA(p) != INVALID_FILE_ATTRIBUTES) return 2;
	char v[32] = { 0 };
	DWORD n = GetEnvironmentVariableA("JP983_STUB", v, sizeof(v));
	if (n && n < sizeof(v) && lstrcmpiA(v, "continuar") == 0) return 1;
	return 0;
}

extern "C" void __cdecl jp983_falta(const char* nome, unsigned va983, int fatal)
{
	static int s_n = 0;
	int modo = jp983_modo_continuar();
	char msg[512];
	_snprintf(msg, sizeof(msg) - 1, "falta: %s (983 %08x)%s [modo %s]", nome, va983, fatal ? " [fatal]" : "",
		modo == 2 ? "continuar: arquivo" : modo == 1 ? "continuar: ambiente" : "padrao");
	msg[sizeof(msg) - 1] = 0;
	OutputDebugStringA(msg);
	if (s_n < 5000)
	{
		++s_n;
		char p[MAX_PATH];
		if (jp983_pasta_exe(p, "jp983_stubs.log"))
		{
			FILE* f = fopen(p, "a");
			if (f) { fprintf(f, "%s\n", msg); fclose(f); }
		}
	}
	if (modo && !fatal) return;
	char cx[700];
	_snprintf(cx, sizeof(cx) - 1, "%s\n\n%s", msg, fatal
		? "Esta funcao nao pode ser pulada (fatal). O jogo vai fechar."
		: "O jogo vai fechar. Para pular os stubs: criar jp983_stub_continuar.txt na pasta do exe.");
	cx[sizeof(cx) - 1] = 0;
	MessageBoxA(NULL, cx, "ProjectG 983 - funcao sem corpo (stub)", MB_OK | MB_ICONSTOP);
	ExitProcess(983);
}

// C92: rastro para diagnóstico no PC (o robô coleta o jp983_stubs.log). Qualquer frente pode declarar
//   extern "C" void __cdecl jp983_rastro(const char* fmt, ...);
// e chamar (ex.: no FrForm::SetMessage, para saber o texto de uma caixa que sai vazia). Linha "rastro: ..." no log.
extern "C" void __cdecl jp983_rastro(const char* fmt, ...)
{
	static int s_n = 0;
	if (s_n >= 2000) return;
	++s_n;
	char msg[600];
	lstrcpyA(msg, "rastro: ");
	va_list va;
	va_start(va, fmt);
	_vsnprintf(msg + 8, sizeof(msg) - 9, fmt, va);
	va_end(va);
	msg[sizeof(msg) - 1] = 0;
	OutputDebugStringA(msg);
	char p[MAX_PATH];
	if (jp983_pasta_exe(p, "jp983_stubs.log"))
	{
		FILE* f = fopen(p, "a");
		if (f) { fprintf(f, "%s\n", msg); fclose(f); }
	}
}

// C106: o heap corrompido (0xC0000374, campos 0x04/0x05/0x0D/0x13) fecha o jogo sem passar pelo filtro do crash handler
// (sem exception.log). O VEH vê a exceção: grava no jp983_stubs.log os endereços do exe achados na pilha (quem chamou o
// free/HeapFree). Só API do Windows e buffer na pilha: o heap já está quebrado.
// jp983_file_cur/prev: preenchidos pelo rastro tools/v6/f4rastro/heap_rastro.py (arquivo aberto no GetCFile), se houver.
extern "C" char jp983_file_cur[128] = "", jp983_file_prev[128] = "";
static void jp983_log_stack(const char* head, const unsigned* sp)
{
	char p[MAX_PATH], buf[4096];
	unsigned base = (unsigned)GetModuleHandleA(NULL);
	unsigned size = ((IMAGE_NT_HEADERS*)(base + ((IMAGE_DOS_HEADER*)base)->e_lfanew))->OptionalHeader.SizeOfImage;
	int n = wsprintfA(buf, "%s tid=%u arq=%.100s ant=%.100s pilha:", head, GetCurrentThreadId(), jp983_file_cur, jp983_file_prev);
	for (int i = 0, k = 0; i < 16384 && k < 160 && !IsBadReadPtr(sp + i, 4); ++i)
		if (sp[i] - base < size) { n += wsprintfA(buf + n, " %08x", sp[i]); ++k; }
	buf[n++] = '\n';
	if (!jp983_pasta_exe(p, "jp983_stubs.log")) return;
	HANDLE h = CreateFileA(p, FILE_APPEND_DATA, FILE_SHARE_READ, NULL, OPEN_ALWAYS, 0, NULL);
	if (h != INVALID_HANDLE_VALUE) { DWORD w; WriteFile(h, buf, n, &w, NULL); CloseHandle(h); }
}
static LONG CALLBACK jp983_heap_veh(EXCEPTION_POINTERS* ep)
{
	if (ep->ExceptionRecord->ExceptionCode != 0xC0000374) return EXCEPTION_CONTINUE_SEARCH;
	char head[64];
	wsprintfA(head, "heap corrompido (c0000374) eip=%08x", ep->ContextRecord->Eip);
	jp983_log_stack(head, (const unsigned*)ep->ContextRecord->Esp);
	return EXCEPTION_CONTINUE_SEARCH;
}
// C147: parametro invalido do CRT (_stricmp NULL, *_s estourado...) fecha com c0000417 sem excecao (o _invoke_watson
// termina o processo direto: nem VEH nem exception.log). Grava a pilha e termina com o mesmo codigo.
static void __cdecl jp983_invalid_param(const wchar_t*, const wchar_t*, const wchar_t*, unsigned, uintptr_t)
{
	unsigned mark;
	jp983_log_stack("parametro invalido do CRT (c0000417)", &mark);
	TerminateProcess(GetCurrentProcess(), 0xC0000417);
}
static _invalid_parameter_handler g_jp983_prev_ip = _set_invalid_parameter_handler(jp983_invalid_param);
// o SDK do build (_WIN32_WINNT antigo) não declara a API
extern "C" __declspec(dllimport) PVOID WINAPI AddVectoredExceptionHandler(ULONG, LONG (CALLBACK*)(EXCEPTION_POINTERS*));
static PVOID g_jp983_heap_veh = AddVectoredExceptionHandler(1, jp983_heap_veh);
