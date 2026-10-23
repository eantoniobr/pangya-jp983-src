// W4 (frente W): teste diferencial do WDirect3D::ModifyVertices (monta os vértices do 2D no formato do FVF) — chama
// por RVA, numa wangreal.dll, com `this` falso (vtable própria cujo slot 0xc0 aponta para o VertexSize da MESMA dll),
// sem dispositivo D3D, e imprime um resumo (FNV-1a) do buffer de vértices, do ponteiro devolvido e do m_dwOffset;
// tools/w/diffmv.sh roda na nossa dll e na do 983 e compara.
// uso: diffmv.exe caminho.dll rvaModifyVertices rvaVertexSize
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef void* (__fastcall *FnModify)(void* self, int edx, const void* vl, unsigned int n, unsigned long fvf, bool store);

enum { OFF_CHVERTEX = 0x41c, OFF_DWOFFSET = 0x420, SELF_SIZE = 0x40000, VTX = 0x58, BUF = 0x20000, MAXN = 48 };

static unsigned int g_seed = 0x4d56;
static unsigned int Rnd() { g_seed = g_seed * 1664525u + 1013904223u; return g_seed >> 8; }
static unsigned int Fnv(unsigned int h, const void* p, int n)
{
	const unsigned char* b = (const unsigned char*)p;
	for (int i = 0; i < n; i++) h = (h ^ b[i]) * 16777619u;
	return h;
}
static float RndF() { return (float)((int)(Rnd() % 20000) - 10000) / 37.0f; }

static void* g_vtbl[128];
static void __fastcall Armadilha(void*, int) { printf("FALHA: slot de vtable inesperado chamado\n"); ExitProcess(3); }

int main(int argc, char** argv)
{
	if (argc < 4) { printf("uso: diffmv.exe dll rvaModify rvaVertexSize\n"); return 1; }
	HMODULE h = LoadLibraryA(argv[1]);
	if (!h) { printf("FALHA: LoadLibrary %lu\n", GetLastError()); return 1; }
	unsigned char* base = (unsigned char*)h;
	FnModify modify = (FnModify)(base + strtoul(argv[2], 0, 16));
	for (int i = 0; i < 128; i++) g_vtbl[i] = (void*)Armadilha;
	g_vtbl[0xc0 / 4] = base + strtoul(argv[3], 0, 16);

	unsigned char* self = (unsigned char*)malloc(SELF_SIZE);
	unsigned char* buf = (unsigned char*)malloc(BUF + 256);
	unsigned char* verts = (unsigned char*)malloc(VTX * MAXN);
	const void* ptrs[MAXN];
	static const unsigned long posBits[] = { 0, 0x2, 0x4, 0x6, 0x8, 0xa, 0xc, 0xe, 0x4000, 0x4002, 0x4004 };
	unsigned int hall = 2166136261u; int casos = 0;
	for (int c = 0; c < 6000; c++)
	{
		// estado do objeto: floats "razoáveis" em tudo (campos do CalcFog: escala/near/fog), alguns zerados
		unsigned int s0 = g_seed;
		for (int i = 4; i < SELF_SIZE; i += 4) *(float*)(self + i) = (Rnd() % 8) ? RndF() : 0.0f;
		*(void***)self = g_vtbl;
		*(unsigned char**)(self + OFF_CHVERTEX) = buf;
		unsigned long off = Rnd() % (BUF - VTX * MAXN * 2);
		*(unsigned long*)(self + OFF_DWOFFSET) = off;
		for (int i = 0; i < BUF + 256; i++) buf[i] = (unsigned char)(i * 7 + c);
		for (int i = 0; i < VTX * MAXN / 4; i++) ((float*)verts)[i] = RndF();
		for (int i = 0; i < MAXN; i++) { *(unsigned long*)(verts + i * VTX + 0x10) = Rnd() * 0x101u; ptrs[i] = verts + ((i * 5) % MAXN) * VTX; }

		unsigned int n = Rnd() % MAXN;
		unsigned long fvf = posBits[Rnd() % (sizeof(posBits) / sizeof(posBits[0]))];
		if (Rnd() % 2) fvf |= 0x10;       // NORMAL
		if (Rnd() % 2) fvf |= 0x40;       // DIFFUSE
		if (Rnd() % 2) fvf |= 0x80;       // SPECULAR
		if (Rnd() % 4 == 0) fvf |= 0x80000000;
		fvf |= (Rnd() % 9) << 8;          // TEXCOUNT 0..8
		if (Rnd() % 8 == 0) fvf |= Rnd() & 0x00ff0000; // TEXCOORDSIZE
		bool store = Rnd() % 2 != 0;
		struct { const void* v; const void* const* pv; } vl;
		if (Rnd() % 2) { vl.v = verts; vl.pv = 0; } else { vl.v = 0; vl.pv = ptrs; }

		void* r = modify(self, 0, &vl, n, fvf, store);
		unsigned long noff = *(unsigned long*)(self + OFF_DWOFFSET);
		unsigned int hb = Fnv(2166136261u, buf, BUF + 256);
		unsigned int hs = Fnv(2166136261u, self, SELF_SIZE);
		int ret = (int)((unsigned char*)r - buf);
		if (c < 200 || c % 50 == 0)
			printf("mv c=%d n=%u fvf=%08lx st=%d off=%lu -> ret=%d noff=%lu buf=%08x self=%08x\n", c, n, fvf, store, off, ret, noff, hb, hs);
		hall = Fnv(hall, &ret, 4); hall = Fnv(hall, &noff, 4); hall = Fnv(hall, &hb, 4); hall = Fnv(hall, &hs, 4);
		casos++;
		(void)s0;
	}
	printf("resumo ModifyVertices %08x\n", hall);
	printf("casos executados: %d\n", casos);
	return 0;
}
