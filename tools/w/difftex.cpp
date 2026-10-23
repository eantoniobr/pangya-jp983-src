// F2.13 (frente W): teste diferencial do caminho de upload de textura — chama por RVA, numa wangreal.dll, as funções
// que levam o bitmap (texto, glyphs, sprites) à textura, sem dispositivo D3D, e imprime um resumo (FNV-1a) das saídas;
// tools/w/difftex.sh roda na nossa dll e na do 983 e compara.
//   UpdateTextureSurface(buff,w,h,pitch,pix,bi,data,type)  (despacha Normal/Direct/Filtering/Sampling; usada pelo xFillTexture)
//   FixTexturePart(h,rc,bi,data,type)                       (cópia parcial / mistura alfa no bitmap da textura)
//   UpdateTextureSurface(h,bi,data,type)                    (cópia inteira para o bitmap da textura)
//   CreateTextureSurface(w,h,mip,0,h,chroma,bits,x)         (tamanho/mip/formato escolhidos; só sem render target)
// uso: difftex.exe caminho.dll rvaFindPixInfo rvaBitmapCtor rvaUpd8 rvaFixPart rvaUpd4 rvaCreate
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef void* (__fastcall *FnFindPix)(int fmt);
typedef void* (__fastcall *FnBitmapCtor)(void* self, int edx, int w, int h, int bpp);
typedef void (__fastcall *FnUpd8)(void* self, int edx, void* buff, int w, int h, int pitch, void* pix, BITMAPINFO* bi, void* data, int type);
typedef void (__fastcall *FnFixPart)(void* self, int edx, int h, const RECT* rc, BITMAPINFO* bi, void* data, int type);
typedef void (__fastcall *FnUpd4)(void* self, int edx, int h, BITMAPINFO* bi, void* data, int type);
typedef void (__fastcall *FnCreate)(void* self, int edx, unsigned long w, unsigned long h, int mip, int rt, int idx, int chroma, int bits, int x);

enum { TEXLIST = 0x3d90, CAPS_TEXCAPS = 0x23ef8, CAPS_MAXW = 0x23f14, CAPS_MAXH = 0x23f18, SELF_SIZE = 0x24400 };

static unsigned int g_seed = 0x2013;
static unsigned int Rnd() { g_seed = g_seed * 1664525u + 1013904223u; return g_seed >> 8; }
static unsigned int Fnv(unsigned int h, const void* p, int n)
{
	const unsigned char* b = (const unsigned char*)p;
	for (int i = 0; i < n; i++) h = (h ^ b[i]) * 16777619u;
	return h;
}

static unsigned char* g_self;
static FnFindPix g_findPix;
static FnBitmapCtor g_bmCtor;

// BITMAPINFO + dados do jeito do jogo: linhas alinhadas a 4, paleta de 256 se 8 bits; conteúdo aleatório, com "texto"
// (faixas de 0/255 e alfa 0/255) em parte dos casos
static BITMAPINFO* MakeBi(int w, int h, int bpp, unsigned char** data)
{
	int pitch = ((bpp / 8) * w + 3) & ~3;
	BITMAPINFO* bi = (BITMAPINFO*)calloc(1, sizeof(BITMAPINFOHEADER) + 256 * 4);
	bi->bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
	bi->bmiHeader.biWidth = w; bi->bmiHeader.biHeight = h; bi->bmiHeader.biPlanes = 1; bi->bmiHeader.biBitCount = (WORD)bpp;
	for (int i = 0; i < 256 * 4; i++) ((unsigned char*)bi->bmiColors)[i] = (unsigned char)Rnd();
	*data = (unsigned char*)malloc(pitch * h + 64);
	int texto = Rnd() % 2;
	for (int i = 0; i < pitch * h + 64; i++) (*data)[i] = texto ? ((Rnd() % 3) ? 0 : 255) : (unsigned char)Rnd();
	return bi;
}

static const int g_fmts[] = { 20, 21, 22, 23, 24, 25, 26, 28 }; // R8G8B8 A8R8G8B8 X8R8G8B8 R5G6B5 X1R5G5B5 A1R5G5B5 A4R4G4B4 A8
static void* g_pix[8];
static int g_cpp[8];
static int g_npix;

static void ListPix()
{
	for (int i = 0; i < sizeof(g_fmts) / sizeof(g_fmts[0]); i++)
	{
		unsigned int* p = (unsigned int*)g_findPix(g_fmts[i]);
		if (!p) { printf("pix fmt=%d (nenhum)\n", g_fmts[i]); continue; }
		printf("pix fmt=%d", g_fmts[i]);
		for (int k = 0; k < 10; k++) printf(" %u", p[k]);
		printf("\n");
		g_pix[g_npix] = p; g_cpp[g_npix] = p[1]; g_npix++;
	}
}

static int RndW()
{
	static const int esp[] = { 1, 2, 3, 63, 64, 65, 127, 128, 129, 255, 256, 257, 300, 511, 512, 513, 640, 1023, 1024 };
	return (Rnd() % 3) ? esp[Rnd() % (sizeof(esp) / sizeof(esp[0]))] : 1 + Rnd() % 700;
}

static int TestUpd8(FnUpd8 fn)
{
	static const int types[] = { 0, 0x800, 0x20000, 0x80000, 0x80800, 0x40000, 0x880000, 0x100 };
	static const int bpps[] = { 8, 24, 32 };
	unsigned int hall = 2166136261u; int n = 0;
	for (int c = 0; c < 3000; c++)
	{
		int sw = RndW(), sh = 1 + Rnd() % 40, bpp = bpps[Rnd() % 3], type = types[Rnd() % 8];
		int pi = Rnd() % g_npix;
		int dw, dh;
		switch (Rnd() % 4)
		{
		case 0: dw = sw; dh = sh; break;                                              // mesmo tamanho (Direct)
		case 1: for (dw = 1; dw < sw; dw *= 2); for (dh = 1; dh < sh; dh *= 2); break; // potência de 2 (Sampling/Filtering)
		case 2: dw = (sw >> (1 + Rnd() % 2)) + 1; dh = (sh >> 1) + 1; break;          // mip menor
		default: dw = 1 + Rnd() % 600; dh = 1 + Rnd() % 48; break;
		}
		if (bpp == 8 && dw > 160) dw = 160 + Rnd() % 40;  // Filtering em float é lento sob o Wine; limita o tamanho
		// a Normal (0x20000) escreve biWidth x biHeight sem olhar w/h: o buffer cobre o maior dos dois
		int pitch = (dw > sw ? dw : sw) * g_cpp[pi] + ((Rnd() % 2) ? 0 : 4 * (Rnd() % 9));
		unsigned char* data; BITMAPINFO* bi = MakeBi(sw, sh, bpp, &data);
		int sz = pitch * (dh > sh ? dh : sh) + 256;
		unsigned char* buff = (unsigned char*)malloc(sz);
		memset(buff, 0xA5, sz);
		__try { fn(g_self, 0, buff, dw, dh, pitch, g_pix[pi], bi, data, type); }
		__except (1) { printf("Upd8 #%d EXCECAO %08lx\n", c, GetExceptionCode()); free(buff); free(bi); free(data); continue; }
		unsigned int h = Fnv(2166136261u, buff, sz);
		hall = Fnv(hall, &h, 4);
		if (c < 400 || h % 16 == 0)
			printf("Upd8 #%d src %dx%dx%d dst %dx%d pitch %d pix %d type %x -> %08x\n", c, sw, sh, bpp, dw, dh, pitch, g_fmts[pi], type, h);
		free(buff); free(bi); free(data); n++;
	}
	printf("Upd8 %d casos %08x\n", n, hall);
	return n;
}

// textura 0 do m_texList com um Bitmap criado pelo construtor da própria dll
static void* NewTexBitmap(int w, int h, int bpp)
{
	void* bm = calloc(1, 64);
	g_bmCtor(bm, 0, w, h, bpp);
	unsigned char* vram = *(unsigned char**)((char*)bm + 0xc);  // o Create não zera a memória: conteúdo determinístico
	for (int i = 0; i < *(int*)((char*)bm + 8) * h; i++) vram[i] = (unsigned char)(i * 7 + 3);
	*(void**)(g_self + TEXLIST) = bm;
	return bm;
}
static unsigned int HashTex(unsigned int h)
{
	unsigned char* bm = *(unsigned char**)(g_self + TEXLIST);
	if (bm)
	{
		BITMAPINFO* bi = *(BITMAPINFO**)(bm + 4);
		int pitch = *(int*)(bm + 8);
		unsigned char* vram = *(unsigned char**)(bm + 0xc);
		h = Fnv(h, &bi->bmiHeader, sizeof(BITMAPINFOHEADER));
		h = Fnv(h, &pitch, 4);
		h = Fnv(h, vram, pitch * bi->bmiHeader.biHeight);
	}
	h = Fnv(h, g_self + TEXLIST + 4, 0x10);  // dxtcDataSize, dxtcData, updateType, needToBeFilled
	return h;
}

static int TestFixPart(FnFixPart fn)
{
	static const int types[] = { 0, 0x40000, 0x40800, 0x80000, 0x800 };
	unsigned int hall = 2166136261u; int n = 0;
	for (int c = 0; c < 1500; c++)
	{
		memset(g_self + TEXLIST, 0, 0x60);
		int tw = 1 << (5 + Rnd() % 6), th = 1 << (3 + Rnd() % 5), tb = (Rnd() % 4) ? 32 : ((Rnd() % 2) ? 24 : 8);
		void* bm = NewTexBitmap(tw, th, tb);
		unsigned char* vram = *(unsigned char**)((char*)bm + 0xc);
		int tpitch = *(int*)((char*)bm + 8);
		for (int i = 0; i < tpitch * th; i++) vram[i] = (unsigned char)Rnd();
		*(int*)(g_self + TEXLIST + 0xc) = (Rnd() % 2) ? 0x80000 : 0;
		RECT rc;
		rc.left = Rnd() % tw; rc.top = Rnd() % th;
		rc.right = rc.left + 1 + Rnd() % (tw - rc.left); rc.bottom = rc.top + 1 + Rnd() % (th - rc.top);
		int sb = (Rnd() % 3) ? 32 : tb;
		unsigned char* data; BITMAPINFO* bi = MakeBi(rc.right - rc.left, rc.bottom - rc.top, sb, &data);
		int type = types[Rnd() % 5];
		__try { fn(g_self, 0, 0, &rc, bi, data, type); }
		__except (1) { printf("FixPart #%d EXCECAO %08lx\n", c, GetExceptionCode()); free(bi); free(data); continue; }
		unsigned int h = HashTex(2166136261u);
		hall = Fnv(hall, &h, 4);
		if (c < 200 || h % 16 == 0)
			printf("FixPart #%d tex %dx%dx%d rc %ld,%ld-%ld,%ld src %d type %x -> %08x\n", c, tw, th, tb, rc.left, rc.top, rc.right, rc.bottom, sb, type, h);
		free(bi); free(data); n++;
	}
	memset(g_self + TEXLIST, 0, 0x60);
	printf("FixPart %d casos %08x\n", n, hall);
	return n;
}

static int TestUpd4(FnUpd4 fn)
{
	unsigned int hall = 2166136261u; int n = 0;
	for (int c = 0; c < 800; c++)
	{
		memset(g_self + TEXLIST, 0, 0x60);
		int w = RndW(), hh = 1 + Rnd() % 40, bpp = (Rnd() % 3) ? 32 : ((Rnd() % 2) ? 24 : 8);
		if (Rnd() % 2) NewTexBitmap((Rnd() % 4) ? w : w + 1, hh, (Rnd() % 4) ? bpp : 32);
		unsigned char* data; BITMAPINFO* bi = MakeBi(w, hh, bpp, &data);
		int type = (Rnd() % 2) ? 0x80000 : 0x800;
		__try { fn(g_self, 0, 0, bi, data, type); }
		__except (1) { printf("Upd4 #%d EXCECAO %08lx\n", c, GetExceptionCode()); free(bi); free(data); continue; }
		unsigned int h = HashTex(2166136261u);
		hall = Fnv(hall, &h, 4);
		if (c < 200 || h % 16 == 0) printf("Upd4 #%d %dx%dx%d type %x -> %08x\n", c, w, hh, bpp, type, h);
		free(bi); free(data); n++;
	}
	memset(g_self + TEXLIST, 0, 0x60);
	printf("Upd4 %d casos %08x\n", n, hall);
	return n;
}

static int TestCreate(FnCreate fn)
{
	unsigned int hall = 2166136261u; int n = 0;
	for (int c = 0; c < 3000; c++)
	{
		for (int i = 0; i < SELF_SIZE / 4; i++) ((unsigned int*)g_self)[i] = 0x50000000 + i * 4;
		*(unsigned int*)(g_self + CAPS_TEXCAPS) = (Rnd() % 2) ? 2 : 0x40;
		*(unsigned int*)(g_self + CAPS_MAXW) = (Rnd() % 4) ? 4096 : 1 << (8 + Rnd() % 4);
		*(unsigned int*)(g_self + CAPS_MAXH) = (Rnd() % 4) ? 4096 : 1 << (8 + Rnd() % 4);
		int w = RndW(), hh = (Rnd() % 2) ? 1 + Rnd() % 64 : RndW(), mip = Rnd() % 10, chroma = Rnd() % 3, bits = (Rnd() % 2) ? 16 : 32;
		__try { fn(g_self, 0, w, hh, mip, 0, 0, chroma, bits, Rnd() % 2); }
		__except (1) { printf("Create #%d EXCECAO %08lx\n", c, GetExceptionCode()); continue; }
		unsigned int h = Fnv(2166136261u, g_self + TEXLIST, 0x60);
		hall = Fnv(hall, &h, 4);
		if (c < 100 || h % 32 == 0)
		{
			unsigned int* e = (unsigned int*)(g_self + TEXLIST);
			printf("Create #%d %dx%d mip %d ck %d bits %d -> w %u h %u mip %u pix %08x %08x\n", c, w, hh, mip, chroma, bits, e[7], e[8], e[9], e[10], h);
		}
		n++;
	}
	memset(g_self, 0, SELF_SIZE);
	printf("Create %d casos %08x\n", n, hall);
	return n;
}

int __cdecl main(int argc, char** argv)
{
	if (argc < 8) { printf("uso: difftex caminho.dll rva*6\n"); return 2; }
	setvbuf(stdout, 0, _IONBF, 0);
	HMODULE h = LoadLibraryA(argv[1]);
	if (!h) { printf("LoadLibrary falhou: %lu\n", GetLastError()); return 1; }
	char* base = (char*)h;
	g_self = (unsigned char*)calloc(1, SELF_SIZE);
	g_findPix = (FnFindPix)(base + strtoul(argv[2], 0, 16));
	g_bmCtor = (FnBitmapCtor)(base + strtoul(argv[3], 0, 16));
	ListPix();
	int n = 0;
	n += TestUpd8((FnUpd8)(base + strtoul(argv[4], 0, 16)));
	n += TestFixPart((FnFixPart)(base + strtoul(argv[5], 0, 16)));
	n += TestUpd4((FnUpd4)(base + strtoul(argv[6], 0, 16)));
	n += TestCreate((FnCreate)(base + strtoul(argv[7], 0, 16)));
	printf("casos executados: %d\n", n);
	return 0;
}
