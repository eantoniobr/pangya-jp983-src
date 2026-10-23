// F2.11: teste diferencial sob Wine — chama por RVA funções internas puras (sem dispositivo) de uma wangreal.dll
// e imprime um resumo (FNV-1a) das saídas; tools/f211/difftest.sh roda na nossa dll e na do 983 e compara.
// uso: difftest.exe caminho.dll rvaFillVertex rvaSetFromAxisAngle rvaWIsInTriangle rvaWCollisionTest
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef void (__fastcall *FnFillVertex)(unsigned char* dest, const unsigned char* src, int fvf, int n, int stride, const float* m);
typedef void (__fastcall *FnAxisAngle)(float* self, int edx, const float* v, float theta);
typedef bool (__fastcall *FnInTri)(const float* p, const float* a, const float* b, const float* c, int direct);
typedef float (__fastcall *FnColl)(const float* aabb, const float* v0, const float* v1, float* plane);

static unsigned int g_seed = 0x983;
static unsigned int Rnd() { g_seed = g_seed * 1664525u + 1013904223u; return g_seed >> 8; }
static float RndF(float r) { return ((int)(Rnd() % 20001) - 10000) / 10000.0f * r; }
static unsigned int Fnv(unsigned int h, const void* p, int n)
{
	const unsigned char* b = (const unsigned char*)p;
	for (int i = 0; i < n; i++) h = (h ^ b[i]) * 16777619u;
	return h;
}

static unsigned char g_src[64 * 96], g_dst[64 * 96 + 256];
static float g_pal[256 * 16];

static int TestFillVertex(FnFillVertex fn)
{
	static const int fvfs[] = { 0x002, 0x012, 0x142, 0x152, 0x004, 0x144, 0x006, 0x016, 0x008, 0x018, 0x00a, 0x01a, 0x00c, 0x01c,
		0x116, 0x118, 0x11a, 0x11c, 0x106, 0x108, 0x10a, 0x10c, 0x00e, 0x01e };
	static const int strides[] = { 48, 64, 80 };
	int n = 0;
	for (int f = 0; f < sizeof(fvfs) / sizeof(fvfs[0]); f++)
		for (int s = 0; s < 3; s++)
			for (int rep = 0; rep < 4; rep++)
			{
				int nv = 1 + Rnd() % 60;
				for (int i = 0; i < sizeof(g_src) / 4; i++) ((float*)g_src)[i] = RndF(2.0f);
				for (int i = 0; i < 256 * 16; i++) g_pal[i] = RndF(1.5f);
				memset(g_dst, 0xA5, sizeof(g_dst));
				__try { fn(g_dst, g_src, fvfs[f], nv, strides[s], g_pal); }
				__except (1) { printf("FillVertex fvf=%03x stride=%d n=%d EXCECAO %08lx\n", fvfs[f], strides[s], nv, GetExceptionCode()); continue; }
				printf("FillVertex fvf=%03x stride=%d n=%2d %08x\n", fvfs[f], strides[s], nv, Fnv(2166136261u, g_dst, sizeof(g_dst)));
				n++;
			}
	return n;
}

static int TestAxisAngle(FnAxisAngle fn)
{
	unsigned int h = 2166136261u;
	for (int i = 0; i < 20000; i++)
	{
		float q[6] = { 9, 9, 9, 9, 9, 9 }, v[3] = { RndF(3.0f), RndF(3.0f), RndF(3.0f) };
		float th = (i % 50 == 0) ? 0.0f : RndF(7.0f);
		if (i % 97 == 0) v[0] = v[1] = v[2] = 0.0f;
		if (i % 89 == 0) { v[0] = 1.0f; v[1] = v[2] = 0.0f; }
		fn(q, 0, v, th);
		h = Fnv(h, q, sizeof(q));
		if (i < 6) printf("SetFromAxisAngle #%d %08x %08x %08x %08x\n", i, *(unsigned*)&q[0], *(unsigned*)&q[1], *(unsigned*)&q[2], *(unsigned*)&q[3]);
	}
	printf("SetFromAxisAngle 20000 casos %08x\n", h);
	return 20000;
}

static int TestInTri(FnInTri fn)
{
	unsigned int h = 2166136261u; int t = 0;
	for (int i = 0; i < 60000; i++)
	{
		float a[3], b[3], c[3], p[3];
		for (int k = 0; k < 3; k++) { a[k] = RndF(1.0f); b[k] = RndF(1.0f); c[k] = RndF(1.0f); p[k] = RndF(0.6f); }
		if (i % 11 == 0) for (int k = 0; k < 3; k++) p[k] = (a[k] + b[k]) * 0.5f;      // sobre uma aresta
		if (i % 13 == 0) for (int k = 0; k < 3; k++) p[k] = a[k];                      // sobre um vértice
		if (i % 17 == 0) for (int k = 0; k < 3; k++) c[k] = b[k];                      // triângulo degenerado
		unsigned char r = fn(p, a, b, c, i % 6) ? 1 : 0;
		t += r; h = Fnv(h, &r, 1);
	}
	printf("WIsInTriangle 60000 casos, verdadeiros %d, %08x\n", t, h);
	return 60000;
}

static int TestColl(FnColl fn)
{
	unsigned int h = 2166136261u; int hit = 0;
	for (int i = 0; i < 60000; i++)
	{
		float bb[6], v0[3], v1[3], pl[6] = { 7, 7, 7, 7, 7, 7 };
		for (int k = 0; k < 3; k++)
		{
			float x = RndF(1.0f), y = RndF(1.0f);
			bb[k] = x < y ? x : y; bb[3 + k] = x < y ? y : x;
			v0[k] = RndF(3.0f); v1[k] = RndF(3.0f);
		}
		if (i % 7 == 0) for (int k = 0; k < 3; k++) v0[k] = (bb[k] + bb[3 + k]) * 0.5f; // começa dentro
		if (i % 19 == 0) v1[i % 3] = v0[i % 3];                                         // paralelo a um eixo
		if (i % 23 == 0) for (int k = 0; k < 3; k++) v1[k] = v0[k];                     // sem deslocamento
		float r = (i % 5 == 4) ? fn(bb, v0, v1, 0) : fn(bb, v0, v1, pl);
		if (pl[0] != 7) hit++;
		h = Fnv(h, &r, 4); h = Fnv(h, pl, sizeof(pl));
		if (i < 6) printf("WCollisionTest #%d %08x plano %08x %08x %08x %08x\n", i, *(unsigned*)&r, *(unsigned*)&pl[0], *(unsigned*)&pl[1], *(unsigned*)&pl[2], *(unsigned*)&pl[3]);
	}
	printf("WCollisionTest 60000 casos, plano escrito %d, %08x\n", hit, h);
	return 60000;
}

int __cdecl main(int argc, char** argv)
{
	if (argc < 6) { printf("uso: difftest caminho.dll rva*4\n"); return 2; }
	HMODULE h = LoadLibraryA(argv[1]);
	if (!h) { printf("LoadLibrary falhou: %lu\n", GetLastError()); return 1; }
	char* base = (char*)h;
	int n = 0;
	n += TestFillVertex((FnFillVertex)(base + strtoul(argv[2], 0, 16)));
	n += TestAxisAngle((FnAxisAngle)(base + strtoul(argv[3], 0, 16)));
	n += TestInTri((FnInTri)(base + strtoul(argv[4], 0, 16)));
	n += TestColl((FnColl)(base + strtoul(argv[5], 0, 16)));
	printf("casos executados: %d\n", n);
	return 0;
}
