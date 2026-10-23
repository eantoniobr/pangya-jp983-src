#pragma once
// JP 983: empréstimos comuns dos atores Lobby* (LobbyCaddie, LobbyItems, LobbyMascot, LobbyPlayer). Tudo aqui é de território
// da frente A ou ainda sem dono; nomes meus, endereços do exe 983. PROVISÓRIO: pedido em out/PEDIDOS.md (sessão B28).

// functor "objeto + método" que os atores guardam num std::tr1::function (RTTI `_util::WMemFun<LobbyCaddie,bool>`): 0x10, com
// o ponteiro de método em +8 (o +4 não é gravado: alinhamento natural de 8, sem alinhar a pilha)
namespace _util
{
	template <class T, class R>
	struct WMemFun983
	{
		typedef R (T::*Func)();
		T* m_pObj;
		union
		{
			Func m_pFun; // +0x08
			__int64 m_align;
		};
		R operator()() const { return (m_pObj->*m_pFun)(); }
	};
	// 00560160: recebe o destino em ecx e o objeto em edx (não é construtor)
	template <class T, class R>
	WMemFun983<T, R>* __fastcall InitMemFun983(WMemFun983<T, R>* pOut, T* pObj, R (T::*pFun)())
	{
		pOut->m_pObj = pObj;
		pOut->m_pFun = pFun;
		return pOut;
	}
}

// botões do mouse (objeto em +0x34 do singleton 00e73e4c): 1 apertou, 2 soltou, 4 clique, 0x100 segurando
class CMouseButtons983
{
public:
	unsigned int Get983(); // 005f3b90
};

// RFWnd / RFManager (frente A, sem cabeçalho no 983): só o que o ponteiro do mouse usa
class CRFWndJp
{
public:
	WSize GetSize983(); // 00406750 (RFWnd::GetSize)
};
class CRFManagerJp
{
public:
	bool IsModalExist983(); // 00418990 (RFManager::IsModalExist)
	char m_00[0x4c];
	CRFWndJp* m_pRoot; // +0x4c
};

// singleton 00e73e4c: ponteiro do mouse da interface
class CUiPointer983
{
public:
	static CUiPointer983* Instance983() { return ms_pInstance; }
	CMouseButtons983* GetButtons983() { return m_pButtons; }
	WVector* GetPos983(); // 006038b0
	bool IsOverWnd983(float x, float y); // 00604320
	void SetCursor983(int cursor, int flag); // 00603710

	// 00565570: tamanho da tela da interface (800 × 600 sem o gerente)
	WSize GetScreenSize983()
	{
		if (m_pRF)
			return m_pRF->m_pRoot->GetSize983();
		return WSize(800.0f, 600.0f);
	}

	static CUiPointer983* ms_pInstance; // 00e73e4c
	char m_00[0x28];
	CRFManagerJp* m_pRF; // +0x28
	char m_2c[8];
	CMouseButtons983* m_pButtons; // +0x34
	char m_38[8];
	bool m_show40; // +0x40: ligado/desligado junto do HIDE da sala de avatar (ProcessUI 007b3347); nome meu
};

// singleton 00f02340 (só o teste de +0x40)
struct sF02340_983
{
	char m_00[0x40];
	void* m_40;
};
extern sF02340_983* g_pF02340_983;

extern int g_lobbyModal983; // 00e78cac: 0 = lobby (CLobbyMain), 1 = conversa de avatar (definido no rflobbydesktop.cpp)

// singleton 00e78ca8 = o RFLobbyDesktop (include/jp/refresh/rflobbydesktop.h; visão): estado do lobby (+0x1fc: 2…4 e 5…7 são dois grupos de telas; 3 e 6 = a variante em que os bonecos atendem o mouse)
class CLobbyState983
{
public:
	static CLobbyState983* Instance983() { return ms_pInstance; }
	bool IsGroupB983() const; // 0055fe60: 5, 6 ou 7
	bool IsGroupA983() const; // 0055fe80: 2, 3 ou 4
	bool IsPickable983() const; // 0055fea0: 3 ou 6
	int IsState10_983() const { return m_state == 10; } // embutida (cópia fora de linha em 004ff190)
	int IsState11_983() const { return m_state == 11; } // idem (004ff1a0)

	static CLobbyState983* ms_pInstance; // 00e78ca8
	char m_000[0x1fc];
	int m_state; // +0x1fc
	char m_200[0x44];
	bool m_bCursorBusy; // +0x244
	bool m_bOverPet; // +0x245
	char m_246[0x12];
	bool m_bChanged; // +0x258: o boneco do jogador mudou de peça (LobbyPlayer)
	int IsMain983() const; // 00565af0 (unidade lobbyplayer): 2 ou 5
	void Refresh983(); // 005fbe40: refaz o lobby depois de compra/presente/my room (16 chamadores; 005f8380, 005fa980,
	                   // 005fa900, 005fae60(1)); nome meu, corpo não escrito (unidade do lobby, 005f…)
};

// 00565a90 (unidade lobbyplayer): o ponteiro do mouse está em cima do boneco que fica em `pos`?
bool __fastcall IsMouseOverPet983(const WVector& mouse, const WVector& pos);
// 004db4b0: interpola de `from` a `to` em `duration` segundos
float __cdecl Fade983(float from, float to, float time, float duration);

extern bool g_bAppActive983; // 00e33794
extern const char* g_lobbyAppearFx983; // 00e0c02c

// CSceneManager (frente A): 009b2900 e o ponteiro do singleton 00e74230
class CSceneManagerJp
{
public:
	static CSceneManagerJp* Instance983() { return ms_pInstance; }
	void AddElement983(int type, int a, int b, const char* name, int layer, int c); // 009b2900
	void SetPuppet(const char* name, WPuppet* puppet); // 009b0eb0
	void DeleteElement(const char* name); // 009b4130
	static CSceneManagerJp* ms_pInstance; // 00e74230
};

// CSharedDoc (frente A): caddie do jogador
struct sCaddie983
{
	int m_00;
	unsigned long typeId; // +0x04
	unsigned long skinId; // +0x08
};
class CSharedDocLobbyJp
{
public:
	unsigned long FindCharIdByTid983(unsigned long tid); // 00643ed0 (-1 = não tem)
	unsigned long GetClubSetId983() const { return *(unsigned long*)((char*)this + 0xa2e); }
	unsigned long GetMascotId983() const { return *(unsigned long*)((char*)this + 0xa8e); } // mascote em uso
	unsigned long GetUid983() const { return *(unsigned long*)((char*)this + 0x8cb); }
	unsigned long GetCaddieId983() const { return *(unsigned long*)((char*)this + 0xa26); }
	unsigned long* GetCaddieIdPtr983() { return (unsigned long*)((char*)this + 0xa26); }
};
#define DOCLOBBYJP() ((CSharedDocLobbyJp*)Doc())

// CItemManager do 983 (CSharedDoc+0x20c)
struct sItem983
{
	int m_00;
	unsigned long typeId; // +0x04
};
class CItemManagerLobbyJp
{
public:
	char* Find1e0_983(unsigned long typeId); // 00a171e0 (registro com o nome em +0x49 e o taco em +0xc0)
	sItem983* Find2a0_983(unsigned long typeId); // 00a172a0
	sItem983* FindCadItem983(unsigned long typeId); // 00a172f0 (par 839: CItemManager::FindCadItem)
};
#define ITEMMGRLOBBYJP() ((CItemManagerLobbyJp*)((char*)Doc() + 0x20c))
