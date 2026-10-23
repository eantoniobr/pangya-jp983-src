// JP 983: unidade 005a7010–005aaf50 (CMyRoomWidget). Classe nova do 983; ver include/jp/myroomwidget.h. Sessão B53: os 9
// métodos próprios. O `OnPacket` 005a8360 (10409 B) NÃO está aqui (pedido B → A da B52). O resto da faixa (005a7060–005a8350
// menos os daqui) são cópias fora de linha usadas pelo `OnPacket`: `CItemStorage::Instance` 005a7060 / 005a7070, moldes de
// `std::vector` e `std::map`, e os construtores de três blocos de pacote (005a73d0 de 0x26 bytes, 005a7400 de 0xac, 005a7530).
#include "minatl.h"
#include "projectg.h"
#include "actor.h"
#include "taskmanager.h"
#include "itemstorage.h"
#include "wview.h"
#include "engine/wlocalize.h" // K2L_Compatibility 00b4ec60
#include "frform.h"
#include "taskform.h"
#include "myroomwidget.h"
#include "fortunedlg.h"
#include "caddieinfodlg.h"
#include "mascotinfodlg.h"
#include "frwndmanager.h"
#include "taskwidget.h"
#include "frstatic.h"
#include "statushelper.h"
#include "frtabbutton.h"
#include "../../shared/localize.h"
#include "frlistbox.h"
#include "frscrollbar.h"
#include "frdesktop.h"
#include "frgraphicinterface.h"
#include "wresrcmng.h"
#include "woverlay.h"
#include "fresh.h"
extern Fresh* g_pFresh; // 00f02340
#include "shareddoc.h"
#include "jp/shareddocjp.h"
#include "packet.h"
#include "../s5/utilities.h"
#include "createcharacteroption.h"
#include "mascot.h"
#include "clientsetting.h"
// D308: offsetof(m_myInfo.userEquip.tidItemSlot)==0xa36 provado (jpbuild obj ok); o 0xa36 cru abaixo e o mesmo campo
C_ASSERT(offsetof(CSharedDoc, m_myInfo.userEquip.tidItemSlot) == 0xa36);
#include "jp/grandprixroomdlg.h"
#include "cardsystem.h"
#include "deleteitem.h"
#include "setitemdlg.h"
#include "ucclibrary.h"
#include "uccmanager.h"
#include "ccardbook.h"
#include "cardboxdlg.h"
#include "refresh/rfcharmasteryaboutdlg.h"
#include "downgradedlg.h"
#include "jp/clubsetworkshopmaindlg.h"
#include "jp/clubsetinfodlg.h"
#include "tooltip.h"
#include "exhibition.h"
#include "petframe.h"
#include "wbone.h"
bool __fastcall EmptyCompares(const void* a, const void* b); // realmyroommainui.cpp (00604b40)
#include "refresh/rflobbydesktop.h"
#include "jp/clubsetstat.h"
#include "jp/lobbyjp.h" // DOCLOBBYJP (taco/bola em uso do doc)
#include "realmyroom_authoritydlg.h" // SelectMenu(6): "realmyroom_authority" (0060c150)

// 00e0f64c / 00e0f668: dois textos montados pelo mesmo inicializador estático (00cd1672); o 1º não tem leitor no 983
static const std::string s_widgetName("CMyRoomWidget");
static const std::string s_formName("realmyroom");

IMPLEMENT_OBJECT(CMyRoomWidget, CTaskWidget)

// 005a7010
CMyRoomWidget::CMyRoomWidget()
{
}

// 005a7040
void CMyRoomWidget::Process(float delta)
{
	CTaskWidget::Process(delta);
}

// 005a7790
void CMyRoomWidget::Activate()
{
	if (m_pForm)
	{
		if (AfxGetTask()->GetActor("Lobby"))
		{
			WRect rect = m_pForm->GetRect();
			rect.x = (g_view->GetWidth() - 800.0) * 0.3f + rect.x;
			m_pForm->SetRect(rect);
		}
		m_pForm->Open(NULL, 1);
	}
	CTaskWidget::Activate();
}

// 005a7870
void CMyRoomWidget::Close()
{
	AfxGetTask()->GetActor("LobbyAvatar") << MsgObject(NULL, 0x2af, 0, 0, 0, 0, 0);
	AfxGetTask()->GetActor("LobbyCaddie") << MsgObject(NULL, 0x2af, 0, 0, 0, 0, 0);
	if (CItemStorage::Instance())
		delete CItemStorage::Instance();
}

// 005a7b00
CMyRoomWidget::~CMyRoomWidget()
{
	CMyRoomWidget::Close();
}

// 005a7f60
void CMyRoomWidget::Open()
{
	m_formName = s_formName;
	new CItemStorage;
	CTaskWidget::Open();
}

template <class T> static void Bind983(T& dst, T w)
{
	dst = w;
	if (w)
		w->SetVisible(false);
}

// Form "realmyroom" do 983 (FrTaskForm de 0xae0 B; criador 00620b90 -> 00620a00, ctor 0061f1f0, vtable 00d1497c).
// ESQUELETO (B339): so registra o criador na fabrica de forms para o My Room abrir sem o erro 0x1389. A logica (itens, avatar,
// armazem, pacotes) ainda esta no CRealMyRoomMain (645) e migra para ca por metodos do 983 (out/F5/myroom/DIFERENCAS.md).
void MyRoomPreview983(char* form, unsigned long tid, bool force);
void MyRoomPetClear983(char* form);
void MyRoomShowPet983(char* form, unsigned long tid);
void MyRoomPetSelectWnd983(char* form);
void MyRoomPetDraw983(char* form);
extern int g_lobbyModal983; // 00e78cac
int MyRoomPetFrameSetParts983(CPetFrame* pFrame, CPartTidList* pList, unsigned long tid, unsigned long uid); // lobbyplayer.cpp

class CRealMyRoomForm983 : public FrTaskForm
{
	DECLARE_OBJECT(CRealMyRoomForm983)

public:
	CRealMyRoomForm983() { memset(m_pad, 0, sizeof(m_pad)); }
	// X do My Room apaga o form antes da widget: ~FrTaskForm zera CTaskWidget::m_pForm e o Close() da widget nao chega aqui (C180.1);
	// m_pTask != NULL = OnCloseWidget983 ainda nao rodou
	virtual ~CRealMyRoomForm983() { if (m_pTask) CRealMyRoomForm983::OnCloseWidget983(); delete CardBook983(); }
	CCardBook*& CardBook983() { return *(CCardBook**)((char*)this + 0xa78); } // CCardBook do 983 (FUN_00605720/007f6d20)
	void ShowCardHolic983(bool show); // 00605720
	void SetViewMode983(int mode); // 006208f0
	void SelectMenu983(int menu); // 00622630 (0, 6, 9)
	bool OnAuthDlgResult983(int result, FrForm* form); // 00610980
	bool OnAuthDlgFailResult983(int result, FrForm* form); // 00622940
	void BuildCardPackList983();
	void OnCardBookDraw983(int) { if (CardBook983()) CardBook983()->Draw(); }
	void OnCardBookBackDraw983(int) { if (CardBook983()) CardBook983()->DrawBackground(); } // 006056e0
	void OnCardPackListDraw983(int param);
	void OnCardPackListDown983();
	void OnItemListDown983();
	void OnItemListRDown983(); // 00622330 (item_list, RBUTTONDOWN)
	bool OnFortuneResult983(int result, FrForm* form); // 0060fa40
	bool OnCaddieInfoResult983(int result, FrForm* form); // 00613a50
	bool OnClubInfoResult983(int result, FrForm* form); // 00605ea0
	bool OnMascotInfoResult983(int result, FrForm* form); // 00605580
	void OpenCaddieInfo983(const sCaddieInfo& info); // 00613b00
	void OpenInformation983(FrListItem* item); // 0061a8a0
	void ShowInformation983(unsigned long typeId, const sItemInfo* info = NULL); // 00615010
	void OnCardPackListRDown983(); // 00615c10
	void OnStorageListRDown983(); // 00615fa0
	void ItemEquip983(FrListBox* box, FrListItem* item, bool equip);
	void OnCardTabDown983(int tab);
	void OnCardPackTab983() { OnCardTabDown983(0); }
	void OnCardVol1Tab983() { OnCardTabDown983(1); }
	void OnCardVol2Tab983() { OnCardTabDown983(2); }
	void OnCardVol3Tab983() { OnCardTabDown983(3); }
	void OnCardVol4Tab983() { OnCardTabDown983(4); }
	void OnCardVol5Tab983() { OnCardTabDown983(5); }
	void OnCardSpTab983() { OnCardTabDown983(100); } // 00605900: ButtonTabControl(100)
	void OnCardIndexDown983() { if (CardBook983()) CardBook983()->PageIndexBehavior(g_pFresh->GetManager()->GetMousePos(), 1); }
	void OnCardIndexMove983() { if (CardBook983()) CardBook983()->PageIndexBehavior(g_pFresh->GetManager()->GetMousePos(), 2); }
	void OnCardUseDown983(); // 006142e0 (card_use, LBUTTONDOWN)
	void OnMasteryMUp983(); // 0060d460 (updown_group.mastery_m, LBUTTONUP)
	void OnUpgradeUp983() { OnUpDownUp983(0); } // 0060d220 (updown_group.upgrade, LBUTTONUP)
	void OnDowngradeUp983() { OnUpDownUp983(1); } // 0060d340 (updown_group.downgrade, LBUTTONUP)
	void OnUpDownUp983(int mode);
	void OnClubWorkMUp983(); // 0061f850 (updown_group.clubwork_m, LBUTTONUP)
	bool OnClubWorkResult983(int result, FrForm* form); // 0061e4a0
	bool OnUpDownResult983(int result, FrForm* form) { *(FrForm**)((char*)this + 0x1f8) = NULL; return true; }
	void OnTooltipHoverOff983(); // 0060cf70(NULL)
	void OnCardSlotDown983(unsigned char slot, unsigned char type); // 006107f0 (645 CardBehavior)
	// card_slot1..12 LBUTTONDOWN 00612380..00612430: 006107f0(slot, 1); o 983 nao tem RBUTTONDOWN nas casas
	void OnCardSlot1Down983() { OnCardSlotDown983(0, 1); }
	void OnCardSlot2Down983() { OnCardSlotDown983(1, 1); }
	void OnCardSlot3Down983() { OnCardSlotDown983(2, 1); }
	void OnCardSlot4Down983() { OnCardSlotDown983(3, 1); }
	void OnCardSlot5Down983() { OnCardSlotDown983(4, 1); }
	void OnCardSlot6Down983() { OnCardSlotDown983(5, 1); }
	void OnCardSlot7Down983() { OnCardSlotDown983(6, 1); }
	void OnCardSlot8Down983() { OnCardSlotDown983(7, 1); }
	void OnCardSlot9Down983() { OnCardSlotDown983(8, 1); }
	void OnCardSlot10Down983() { OnCardSlotDown983(9, 1); }
	void OnCardSlot11Down983() { OnCardSlotDown983(10, 1); }
	void OnCardSlot12Down983() { OnCardSlotDown983(11, 1); }
	virtual bool OnOpenWidget983() { return true; }
	virtual bool OnCloseWidget983(); // 006165d0 (slot 39): so os 0x0020 sub 9 e sub 2 (B431, C174.1)
	virtual bool OnInit(); // 00620c30 (slot 32): parte ja portada, ver .cpp
	void SetMainTab983(int tab, bool select); // 0061e4e0
	void SelectSubTab983(int sub, bool force); // 0061d7a0 (so visibilidade; listas/helpers ainda nao portados)
	void AddMainTabs983(); // INIT 00607080 de middle_ui.tab_main
	void FillItemList983(int sub); // 0061af80 casos 2-4 (preenchimento; a selecao dos slots equipados nao esta portada)
	void SelectCharacter983(); // 0061eaa0
	void SelectCharacterByKey983(unsigned long key, int p3); // 0061eaa0 (com chave, chamada pela msg 0x48)
	int SelectClub983(unsigned long uid); // 0061cc80
	void SelectBall983(unsigned long tid); // 0061ce00
	void InitForm983(bool keepCaddieMascot); // 00620770
	virtual bool OnMsg983(const MsgObject& msg); // 00623500 (+0xa0): 0x48/49/4a/4b/75/e5/e6/eb, 0x297/0x2a7 (cartas)
	bool SelectCaddie983(unsigned long key); // 0061c960 (sem a checagem de nivel do item 00a172a0 e sem o painel 0x1a6/0x1a9)
	void SelectMascot983(unsigned long key); // 0061cb70 (parcial)
	void OnTabMainUp983(); // 0061f530 (middle_ui.tab_main, LBUTTONUP)
	void OnTabSubUp983(); // 0061f6b0 (middle_ui.tab_sub, LBUTTONUP)
	void UnequipItem983(unsigned long* slot); // 00615ab0
	void EquipActiveItem983(sItemInfo* info); // 00613d50
	void OnItemListDClick983(); // 00614be0
	void OnItemSlotDClick983(); // 0061a710
	void OnItemSlotOwnerDraw983(int param); // 0060d0d0 (middle_ui.sbox.item_slot, OWNERDRAW: barra dos itens ativos equipados)
	void DrawCutin983(); // 0061ee90
	void DrawSkinBack983(); // 0060da80
	void DrawSkinSlot983(); // 0060de60
	void OnPetOwnerDraw983(int param); // 0061f6d0 (middle_ui.pet, OWNERDRAW: previa 3D)
	void OnItemListOwnerDraw983(int param); // 006166b0 (item_list, OWNERDRAW; B410: so fundo + icone + nome, sem botoes/ucc/rental)
	// 0060ca50 (slot 9 da vtbl): a previa (+0x584) roda Process a cada quadro (D323.1); sem isso o CExhibition nunca monta a pose.
	// A secao critica +0x5b8 do 983 nao e criada aqui (um so thread), so a flag +0x58c em volta.
	virtual void OnProc(const float deltaTime)
	{
		FrTaskForm::OnProc(deltaTime);
		CExhibition* pv = *(CExhibition**)((char*)this + 0x584);
		if (pv)
		{
			int tab = *(int*)((char*)this + 0x52c);
			*(int*)((char*)this + 0x58c) = 1;
			pv->Process(deltaTime, !(tab == 1 || tab == 4));
			*(int*)((char*)this + 0x58c) = 0;
		}
	}
	void OnCloseWndUp983() { Close(true); } // 00604eb0 (close_wnd, cmd 4): vtable[2](1) + SetB7a983(false) (feito no Close)

	DECLARE_FRESH_MSGMAP()

private:
	char m_pad[0xae0 - 0x120]; // campos do 983 ainda nao mapeados
};

// Controles do layout "realmyroom" ligados a campos do 983 pelos handlers INIT do msgmap 00e1347c (tabela gerada por
// tools/f37/myroom_binds.py -> out/F5/myroom/binds983.tsv). off = deslocamento no objeto; hide = o INIT so esconde o controle.
// O 983 grava o ponteiro durante a criacao do layout; aqui a busca por nome e feita no OnInit (equivalente). B340
struct MyRoomBind983
{
	const char* path;
	unsigned int off;
	bool hide;
};
static const MyRoomBind983 s_myRoomBinds983[] =
{
	{"middle_ui.item_list", 0x144, false}, // 00606e90 bind+logica
	{"middle_ui.tab_main", 0x134, false}, // 00607080 bind+logica
	{"middle_ui.tab_sub", 0x138, false}, // 00607190 bind
	{"item_search_btn", 0x248, false}, // 00607200 bind
	{"chat_bg", 0x1ec, false}, // 00607270 bind
	{"middle_ui.main_bg1", 0x1dc, false}, // 006072f0 bind
	{"middle_ui.main_bg2", 0x1e0, false}, // 00607360 bind
	{"middle_ui.main_bg3", 0x1e4, false}, // 006073d0 bind
	{"middle_ui.main_bg4", 0x1e8, false}, // 00607440 bind
	{"middle_ui", 0x128, false}, // 006074b0 bind
	{"middle_ui.tabtxt2", 0x148, false}, // 00607520 bind
	{"middle_ui.tabtxt2", 0x14c, false}, // 00607590 bind
	{"middle_ui.pet", 0x18c, false}, // 00607600 bind
	{"middle_ui.skin_pet", 0x184, false}, // 00607670 bind
	{"middle_ui.skin_pet2", 0x188, false}, // 006076e0 bind
	{"middle_ui.item_desc_bg", 0x170, false}, // 00607750 bind
	{"middle_ui.item_desc", 0x174, false}, // 006078f0 bind+logica
	{"item_hide_desc", 0x17c, false}, // 00607990 bind+logica
	{"item_hide_name", 0x180, false}, // 00607a40 bind
	{"middle_ui.sbox", 0x194, false}, // 00607ac0 bind+logica
	{"middle_ui.sbox.equip_cancel", 0x19c, false}, // 00607b60 bind+logica
	{"middle_ui.sbox.equip_reset", 0x1a0, false}, // 00607c10 bind+logica
	{"middle_ui.sbox.item_slot", 0x190, false}, // 00607cc0 bind
	{"middle_ui.gift_bg", 0x1b8, false}, // 00607d40 bind
	{"middle_ui.gift_desc", 0x1bc, false}, // 00607dc0 bind
	{"stat_group", 0x158, false}, // 00607e40 bind
	{"stat_group.stat_text", 0x1c0, false}, // 00607ed0 bind
	{"stat_group.arrow_m", 0, true}, // 00607f40
	{"stat_group.epower", 0x15c, false}, // 00607fa0 bind
	{"stat_group.econtrol", 0x160, false}, // 00608010 bind
	{"stat_group.eimpact", 0x164, false}, // 00608080 bind
	{"stat_group.espin", 0x168, false}, // 006080f0 bind
	{"stat_group.ecurve", 0x16c, false}, // 00608160 bind
	{"updown_group", 0x198, false}, // 006081d0 bind
	{"updown_group.upgrade", 0x1a4, false}, // 00608240 bind
	{"updown_group.downgrade", 0x1a8, false}, // 006082c0 bind
	{"updown_group.clubwork_m", 0x1b0, false}, // 00608340 bind
	{"updown_group.mastery_m", 0x1b4, false}, // 006083c0 bind
	{"ftab_main", 0x1c4, false}, // 006091c0 bind+logica
	{"fitem_list", 0x1c8, false}, // 006092c0 bind+logica
	{"item_hide_desc_bg", 0x178, false}, // 00609350 bind
	{"card_book", 0, true}, // 006098a0
	{"cardpage_index", 0, true}, // 00609910
	{"card_property", 0, true}, // 006099d0
	{"card_pack", 0, true}, // 00609a40
	{"card_use", 0, true}, // 00609ad0
	{"card_volume1", 0, true}, // 00609b50
	{"card_volume2", 0, true}, // 00609be0
	{"card_volume3", 0, true}, // 00609c70
	{"card_volume4", 0, true}, // 00609d00
	{"card_sp", 0, true}, // 00609d90
	{"card_volume5", 0, true}, // 00609e20
	{"item_storage_pang", 0xa94, false}, // 0060a420 bind
	{"pang_minus", 0xa98, false}, // 0060a4a0 bind+logica
	{"pang_plus", 0xa9c, false}, // 0060a560 bind+logica
	{"item_storage_list", 0xaa0, false}, // 0060a620 bind
	{"item_storage_index", 0xaa4, false}, // 0060a850 bind
	{"item_storage_page_next", 0xaa8, false}, // 0060a940 bind+logica
	{"item_storage_page_prev", 0xaac, false}, // 0060aa00 bind+logica
	{"item_storage_close", 0xab0, false}, // 0060aac0 bind+logica
	{"item_storage_dragdrop", 0xab4, false}, // 0060ab70 bind
	{"cardpacklist", 0xab8, false}, // 00614260 bind
	{"item_storage_bgi", 0xa90, false}, // 00615dd0 bind+logica
};

extern "C" void __cdecl jp983_rastro(const char* fmt, ...); // B404 temporario
// B411: rastro temporario - arvore de controles do layout (nome, visivel, rect) para achar o painel azul / quadrados cinza
struct Dump983 { int depth; };
static bool DumpChild983(FrWnd* w, void* parm)
{
	int depth = ((Dump983*)parm)->depth;
	std::string nm;
	w->GetWindowName(nm);
	const WRect& r = w->GetRect();
	jp983_rastro("B411 T %*s%s vis=%d %.0f,%.0f %.0fx%.0f", depth * 2, "", nm.c_str(), (int)w->IsVisible(), r.x, r.y, r.w, r.h);
	if (depth < 4)
	{
		Dump983 d = { depth + 1 };
		w->EnumerateChildWindow(DumpChild983, &d);
	}
	return true;
}

static FrWnd* FindByPath983(FrWnd* root, const char* path)
{
	char buf[128];
	strncpy(buf, path, sizeof(buf) - 1);
	buf[sizeof(buf) - 1] = 0;
	FrWnd* w = root;
	for (char* tok = strtok(buf, "."); tok && w; tok = strtok(NULL, "."))
		w = w->FindChildByName(tok);
	return w;
}

// 00620c30: FUN_007f3860 (copia a lista do CSharedDoc), FUN_0061eaa0/0061e4e0/0061d7a0 (abas/lista/stats) e o ramo
// DAT_00e78cac==1 ainda NAO portados; aqui so os INIT do msgmap (campos de controle) e os campos fixos +0x52c/+0x530.
// 0098c3f0: sprintf em anel de 64 buffers de 0x240; aqui um anel local
static const char* TabImg983(const char* fmt, int n)
{
	static char s_ring[16][64];
	static unsigned s_i = 0;
	char* p = s_ring[s_i++ & 15];
	sprintf(p, fmt, n);
	return p;
}

// 00c07e10 com o trio n/o/d de "stext_%d_n"
static void AddSubTab983(FrTabButton* bar, int id)
{
	const char* img[3];
	img[0] = TabImg983("stext_%d_n", id);
	img[1] = TabImg983("stext_%d_n", id);
	img[2] = TabImg983("stext_%d_n", id);
	bar->AddTab(img, id);
}

// INIT 00607080 (middle_ui.tab_main): 6 abas, imagens stab_%d_n / _d / _d; a 1a usa o 7 e as outras 2..6 viram indices 1..5
void CRealMyRoomForm983::AddMainTabs983()
{
	FrTabButton* bar = *(FrTabButton**)((char*)this + 0x134);
	if (!bar)
		return;
	for (int k = 0; k < 6; ++k)
	{
		int img = (k == 0) ? 7 : k + 1;
		const char* names[3];
		names[0] = TabImg983("stab_%d_n", img);
		names[1] = TabImg983("stab_%d_d", img);
		names[2] = TabImg983("stab_%d_d", img);
		bar->AddTab(names, k);
	}
}

// 0061e4e0: troca a aba principal (+0x52c) e remonta as sub-abas (middle_ui.tab_sub, +0x138)
static void SendDresserParts983(CSharedDoc* sd);
void CRealMyRoomForm983::SetMainTab983(int tab, bool select)
{
	char* self = (char*)this;
	int& cur = *(int*)(self + 0x52c);
	if (!select)
	{
		if (cur == tab)
			return;
	}
	else
	{
		FrTabButton* main = *(FrTabButton**)(self + 0x134);
		if (main)
			main->Select(cur);
	}
	{
		int curSub = *(int*)(self + 0x530);
		if (cur == 0 && tab != 0 && (curSub < 6 || curSub == 0x16 || curSub == 0x17 || curSub == 0x1b))
			SendDresserParts983(Doc()); // C238.1: sair de Clothes pela aba principal -> 0x0020 sub 0
	}
	cur = tab;
	FrTabButton* sub = *(FrTabButton**)(self + 0x138);
	if (sub)
		sub->ClearTab();
	FrWnd* box = *(FrWnd**)(self + 0x198);
	bool boxOn = false;
	int sel = -1;
	if (sub)
	{
		switch (cur)
		{
		case 0:
			AddSubTab983(sub, 0x16);
			for (int i = 2; i < 6; ++i)
				AddSubTab983(sub, i);
			if (IsLocalContent((localContentType_t)0x58))
				AddSubTab983(sub, 0x1b);
			AddSubTab983(sub, 0x17);
			boxOn = true; sel = 1;
			break;
		case 1:
			for (int i = 7; i < 11; ++i)
				AddSubTab983(sub, i);
			if (IsLocalContent((localContentType_t)0x52))
				AddSubTab983(sub, 0x1c);
			break;
		case 2:
			AddSubTab983(sub, 0xc);
			boxOn = true; sel = 1;
			break;
		case 3:
			AddSubTab983(sub, 0xd);
			boxOn = true; sel = 1;
			break;
		case 4:
			for (int i = 0xe; i < 0x12; ++i)
				AddSubTab983(sub, i);
			AddSubTab983(sub, 0x22);
			AddSubTab983(sub, 0x23);
			AddSubTab983(sub, 0x20);
			sel = 0;
			break;
		case 5:
			for (int i = 0x13; i < 0x16; ++i)
				AddSubTab983(sub, i);
			if (IsLocalContent((localContentType_t)0x14))
				AddSubTab983(sub, 0x19);
			if (IsLocalContent((localContentType_t)0x50))
				AddSubTab983(sub, 0x18);
			AddSubTab983(sub, 0x26);
			sel = 0;
			break;
		}
	}
	if (sel >= 0)
	{
		// FUN_00605010(sel, 0): +0x1b4 recebe sel; +0x1b0, +0x1a4, +0x1a8 recebem 0
		FrWnd* w[4] = { *(FrWnd**)(self + 0x1b4), *(FrWnd**)(self + 0x1b0), *(FrWnd**)(self + 0x1a4), *(FrWnd**)(self + 0x1a8) };
		if (w[0]) w[0]->SetVisible(sel != 0);
		for (int i = 1; i < 4; ++i)
			if (w[i]) w[i]->SetVisible(false);
		if (box)
			box->SetVisible(boxOn);
	}
	FrWnd* a = *(FrWnd**)(self + 0x174);
	FrWnd* c = *(FrWnd**)(self + 0x170);
	if (a) a->SetVisible(false);
	if (c) c->SetVisible(false);
	{
		static const int firstSub[6] = { 0x16, 7, 0xc, 0xd, 0xe, 0x13 };
		SelectSubTab983(cur == 0 ? 0x16 : firstSub[cur], true);
	}
}

// 983: o mesmo espelho do gameroomdlg.cpp (005e48a0 = CStatusHelper::GetMyFreeSlot983, alias em rfapelidos983.cpp)
class CStatusHelperJp
{
public:
	int GetBonus983(unsigned long type);
};

// Vis�o do FrWnd para o m_pScrBar (protegido) da lista: o 983 l� +0x90 direto (igual ao cardcomposedlg.cpp)
class FrWndScrJp983 : public FrWnd
{
public:
	FrScrollBar* GetScrBar983() { return m_pScrBar; }
};

// 0061a750: "%d/%d" (status / status + vagas livres) nos 5 textos stat_group.epower..ecurve (+0x15c..+0x16c);
// grava a string direto e liga +0x100 (m_smallFont) = SetCaption11, não SetCaption (C179: números grandes)
static void UpdateStats983(char* self)
{
	CStatusHelper helper;
	for (int i = 0; i < 5; ++i)
	{
		int cur = helper.GetStatus983(i);
		int free = ((CStatusHelperJp*)&helper)->GetBonus983(i);
		FrStatic* t = *(FrStatic**)(self + 0x15c + i * 4);
		if (t)
		{
			char buf[32];
			sprintf(buf, "%d/%d", cur, cur + free);
			t->SetCaption11(buf);
		}
	}
}

// 00b2e310: sub-aba -> mascara de categorias (S5::UnderCategory)
// 006336a0: cut-in escondido (0x1e00000 sempre, 0x1f00000 sem identidade 0x2804, senao IsNonVisibleItem)
static bool CutinHidden983(CSharedDoc* doc, unsigned long tid)
{
	if ((tid >> 26) == 6 && (tid & 0x1f00000) == 0x1e00000)
		return true;
	if ((tid >> 26) == 6 && (tid & 0x1f00000) == 0x1f00000)
		return !(doc->m_myInfo.info.dwIdentity & 0x2804);
	return ItemManager()->IsNonVisibleItem(tid) == true;
}

static unsigned long CutinTid983(CSharedDoc* doc, unsigned long uid)
{
	for (std::list<sItemInfo>::iterator o = doc->m_cutinList.begin(); o != doc->m_cutinList.end(); ++o)
		if (o->id == uid)
			return o->typeId;
	return 0;
}

// 0063f450(uid, 0xff): uid esta nos cutIn[4] (+0x1b8) do personagem atual
static bool CutinEquipped983(CSharedDoc* doc, unsigned long uid)
{
	sCharacterInfo* cur = doc->FindChar983((unsigned long)-1);
	if (!cur)
		return false;
	for (int i = 0; i < 4; ++i)
		if (cur->cutIn[i] == uid)
			return true;
	return false;
}

// 0063f4b0 (equipar cut-in uid/tid no personagem atual): cut-in 0x38 da lista do doc, do personagem atual; troca o slot de mesma
// categoria (CutinInfo+0x10 em comum) ou usa o 1o livre
static bool CutinEquip983(CSharedDoc* doc, unsigned long uid, unsigned long tid)
{
	if (tid == 0 || uid == 0xffffffff || (tid & 0xfc000000) != 0x38000000)
		return false;
	unsigned long ctid = CutinTid983(doc, uid);
	if (ctid == 0 || CutinEquipped983(doc, uid))
		return false;
	IFF_STRUCT::S5::sCutinInformation* ci = ItemManager()->FindCutinInformation(ctid);
	sCharacterInfo* cur = doc->FindChar983((unsigned long)-1);
	if (!ci || !cur || (cur->tid & 0x3ffffff) != (unsigned long)ci->CharIndex)
		return false;
	for (int i = 0; i < 4; ++i)
	{
		IFF_STRUCT::S5::sCutinInformation* oc = ItemManager()->FindCutinInformation(CutinTid983(doc, cur->cutIn[i]));
		if (oc && (ci->Condition & oc->Condition))
		{
			cur->cutIn[i] = uid;
			return true;
		}
	}
	for (int i = 0; i < 4; ++i)
		if (cur->cutIn[i] == 0 || cur->cutIn[i] == 0xffffffff)
		{
			cur->cutIn[i] = uid;
			return true;
		}
	return false;
}

// 0063f620 (tirar cut-in uid): zera o slot se o cut-in e do personagem atual
static bool CutinUnequip983(CSharedDoc* doc, unsigned long uid)
{
	sCharacterInfo* cur = doc->FindChar983((unsigned long)-1);
	if (!cur)
		return false;
	for (int i = 0; i < 4; ++i)
		if (cur->cutIn[i] == uid)
		{
			IFF_STRUCT::S5::sCutinInformation* oc = ItemManager()->FindCutinInformation(CutinTid983(doc, uid));
			if (oc && (cur->tid & 0x3ffffff) != (unsigned long)oc->CharIndex)
				return false;
			cur->cutIn[i] = 0;
			return true;
		}
	return false;
}

static unsigned long MyRoomTabMask983(int sub)
{
	switch (sub)
	{
	case 1: case 0xe: case 0x17: return 0;
	case 2: case 0xf: return 1;
	case 3: case 0x10: return 2;
	case 4: return 0x10;
	case 5: return 0x2c;
	case 6: return 0x40;
	case 0x11: return 3;
	case 0x16: return 0x3bf;
	case 0x1b: return 0x380;
	case 0x1d: return 7;
	case 0x1e: return 9;
	case 0x1f: return 8;
	case 0x23: return 6;
	}
	return 0;
}

static void SelectEquippedSlots983(CSharedDoc* doc, FrListBox* box, unsigned long* slotType, unsigned long* slotUid)
{
	std::map<unsigned int, sCharacterInfo>::iterator ci = doc->m_charMap.find(doc->m_myInfo.userEquip.guidChar);
	for (int s = 0; ci != doc->m_charMap.end() && slotType && s < 0x18; ++s)
	{
		for (FrListBox::ITEM_LIST::iterator li = box->m_itemList.begin(); li != box->m_itemList.end(); ++li)
		{
			sItemInfo* info = (sItemInfo*)(*li)->pData;
			if (!info)
				continue;
			unsigned int idx = (info->typeId >> 13) & 0x1f;
			bool hasUid = idx < 24 && ci->second.ItemIdList[idx] != 0;
			bool match = hasUid ? (info->typeId == slotType[s] && info->id == slotUid[s]) : (info->typeId == slotType[s]);
			if (match)
			{
				box->SelectItem(*li, false);
				break;
			}
		}
	}
}

// 0061af80 casos 2-4: esvazia o FrListBox (+0x144) e poe as pecas de m_partsList que nao estao equipadas (lista +0x111d8 do
// CSharedDoc, uid em +8 do elemento) e passam no filtro da aba (char em +0x4f8). Copia os 3 ushorts de FindPart(+0x228..22c)
// para +0xa4..a8 do item. Seleciona (SelectItem) os slots equipados; casos 5+ nao portados.

void CRealMyRoomForm983::FillItemList983(int sub)
{
	FrListBox* box = *(FrListBox**)((char*)this + 0x144);
	if (!box)
		return;
	box->ClearItem();
	CSharedDoc* doc = Doc();
	if (!doc)
		return;
	if (sub == 0xb)
	{
		// caso 0xb: m_caddieMap (+0x3718); seleciona o caddie do doc (+0xa26) ou o ja escolhido (+0x504). D
		unsigned long& selCaddie = *(unsigned long*)((char*)this + 0x504);
		// D341: +0x504 residual (ctor) que nao e chave do mapa nao pode bloquear a selecao do caddie equipado do doc
		if (selCaddie != 0 && doc->m_caddieMap.find(selCaddie) == doc->m_caddieMap.end())
			selCaddie = 0;
		for (std::map<unsigned int, sCaddieInfo>::iterator it = doc->m_caddieMap.begin(); it != doc->m_caddieMap.end(); ++it)
		{
			FrListItem* li = box->AddItem(&it->second);
			if (selCaddie == 0)
			{
				if (doc->m_myInfo.userEquip.guidCaddie == it->first)
				{
					selCaddie = it->first;
					box->SelectItem(li, true);
				}
			}
			else if (selCaddie == it->first)
				box->SelectItem(li, true);
		}
		return;
	}
	if (sub == 0xd)
	{
		// caso 0xd: m_mascotMap (+0x3728); seleciona o mascote do doc (+0xa8e). D
		for (std::map<unsigned int, sMascotInfo>::iterator it = doc->m_mascotMap.begin(); it != doc->m_mascotMap.end(); ++it)
		{
			FrListItem* li = box->AddItem(&it->second);
			if (doc->m_myInfo.userEquip.guidMascot == it->first)
				box->SelectItem(li, true);
		}
		return;
	}
	if (sub == 0x22)
	{
		// 0061af80 caso 0x22: m_cutinList visiveis (009da070, 006336a0 != 1) cujo personagem (CutinInfo+0x18) e o da aba (+0x4f8) ou >= 100;
		// os que estao nos cutIn[4] do personagem atual (0063f450) ficam selecionados
		unsigned long charTid = *(unsigned long*)((char*)this + 0x4f8) & 0x3ffffff;
		for (std::list<sItemInfo>::iterator it = doc->m_cutinList.begin(); it != doc->m_cutinList.end(); ++it)
		{
			unsigned long tid = it->typeId;
			if ((tid & 0xfc000000) != 0x38000000)
				continue;
			IFF_STRUCT::S5::sCutinInformation* ci = ItemManager()->FindCutinInformation(tid);
			if (!ci || CutinHidden983(doc, tid))
				continue;
			if (charTid != (unsigned long)ci->CharIndex && ci->CharIndex <= 99)
				continue;
			FrListItem* li = box->AddItem(&*it);
			if (CutinEquipped983(doc, it->id))
				box->SelectItem(li, false);
		}
		return;
	}
	if (sub == 0xe || sub == 0xf || sub == 0x10 || sub == 0x11 || sub == 0x23)
	{
		// 0061af80 casos 0xe-0x11/0x23: m_cutinList (+0x3798) filtrada pela categoria da aba (00b2e310; 5 = todas); 00b2d330 da o slot
		// (categoria do tid 0x38xxxxxx: 0-4, 6->5) e a peca equipada naquele slot (doc+0xa76+slot*4) fica selecionada
		unsigned long mask = MyRoomTabMask983(sub);
		for (std::list<sItemInfo>::iterator it = doc->m_cutinList.begin(); it != doc->m_cutinList.end(); ++it)
		{
			unsigned long tid = it->typeId;
			if (mask != 5 && ((tid >> 0x16) & 0xf) != mask)
				continue;
			FrListItem* li = box->AddItem(&*it);
			int slot = -1;
			if ((tid & 0xfc000000) == 0x38000000)
			{
				unsigned long c = (tid >> 0x16) & 0xf;
				if (c <= 4) slot = (int)c; else if (c == 6) slot = 5;
			}
			if (slot >= 0 && *(unsigned long*)((char*)doc + 0xa76 + slot * 4) == tid)
				box->SelectItem(li, true);
		}
		return;
	}
	if (sub == 0x1d || sub == 0x1e || sub == 0x1f)
	{
		// 0061af80 casos 0x1d-0x1f: com NT REAL_MYROOM (bit 0x57), m_furnitureList (+0x37d4) cuja categoria (tid>>11&0x7ff) = mascara da aba (00b2e310)
		if (!IsLocalContent(S4_REAL_MYROOM))
			return;
		unsigned long mask = MyRoomTabMask983(sub);
		for (std::list<sFurniture_List>::iterator it = doc->m_furnitureList.begin(); it != doc->m_furnitureList.end(); ++it)
			if (((it->typeId >> 0xb) & 0x7ff) == mask)
				box->AddItem(&*it);
		return;
	}
	if (sub == 0x1c)
	{
		// 0061af80 caso 0x1c: com NT REAL_MYROOM (00a7a8d0), m_cardList (+0x37e0) inteira. cauda 006141b0/007f58a0 portada (B458)
		if (IsLocalContent(S4_REAL_MYROOM))
			for (std::list<sCards>::iterator it = doc->m_cardList.begin(); it != doc->m_cardList.end(); ++it)
				box->AddItem(&*it);
		BuildCardPackList983(); // 006141b0 (so mexe se cardpacklist +0xab8 existe)
		// 0061c65x: com NT REAL_MYROOM e o CCardBook (+0xa78) ja aberto, 007f58a0 = ReBuildCurrentPage
		CCardBook* book = CardBook983();
		if (IsLocalContent(S4_REAL_MYROOM) && book && book->IsShow())
			book->ReBuildCurrentPage();
		return;
	}
	if (sub == 0x20 || sub == 0x21)
	{
		// 0061af80 caso 0x20: m_furnitureList inteira menos as categorias 7-9; categoria 0xe com o tid em doc+0xa92/0xa96 vem marcada (+0xd);
		// caso 0x21: toda a lista
		for (std::list<sFurniture_List>::iterator it = doc->m_furnitureList.begin(); it != doc->m_furnitureList.end(); ++it)
		{
			unsigned long cat = (it->typeId >> 0xb) & 0x7ff;
			if (sub == 0x20 && cat >= 7 && cat <= 9)
				continue;
			FrListItem* li = box->AddItem(&*it);
			if (sub == 0x20 && cat == 0xe && (*(unsigned long*)((char*)doc + 0xa92) == it->typeId || *(unsigned long*)((char*)doc + 0xa96) == it->typeId))
				li->selected = true;
		}
		return;
	}
	if (sub == 0x19)
	{
		// 0061af80 caso 0x19: com NT REAL_MYROOM (00a7a8d0), da m_myItemList (+0x375c) so o item 0x1a000042
		if (!IsLocalContent(S4_REAL_MYROOM))
			return;
		for (std::list<sItemInfo>::iterator it = doc->m_myItemList.begin(); it != doc->m_myItemList.end(); ++it)
			if ((it->typeId & 0x2000000) && it->typeId == 0x1a000042)
				box->AddItem(&*it);
		return;
	}
	if (sub == 0x14)
	{
		// 0061af80 caso 0x14: m_myItemList (+0x375c); so os itens de cupom (GetCouponKind != 0)
		for (std::list<sItemInfo>::iterator it = doc->m_myItemList.begin(); it != doc->m_myItemList.end(); ++it)
			if (doc->m_itemManager.GetCouponKind(it->typeId) != 0)
				box->AddItem(&*it);
		return;
	}
	if (sub == 0x15)
	{
		// 0061af80 caso 0x15: m_questList (+0x3834), todas as missoes
		for (std::list<sQuest>::iterator it = doc->m_questList.begin(); it != doc->m_questList.end(); ++it)
			box->AddItem(&*it);
		return;
	}
	if (sub == 7)
	{
		// casos 7: m_clubSetMap (+0x3744); seleciona o taco do jogo (+0xa2e) ou o ja escolhido (+0x514)
		unsigned long& selClub = *(unsigned long*)((char*)this + 0x514);
		for (std::map<unsigned int, sItemInfo>::iterator it = doc->m_clubSetMap.begin(); it != doc->m_clubSetMap.end(); ++it)
		{
			FrListItem* li = box->AddItem(&it->second);
			if (selClub == 0)
			{
				if (DOCLOBBYJP()->GetClubSetId983() == it->first)
				{
					selClub = it->first;
					box->SelectItem(li, true);
				}
			}
			else if (selClub == it->first)
				box->SelectItem(li, true);
		}
		return;
	}
	if (sub == 8)
	{
		// caso 8: m_ballList (+0x3750); bola em uso +0xa32 -> selecionada em +0x524
		unsigned long& selBall = *(unsigned long*)((char*)this + 0x524);
		unsigned long usedBall = *(unsigned long*)((char*)doc + 0xa32);
		bool flag = (*(unsigned long*)((char*)doc + 0x812) >> 0xe & 1) != 0;
		if (flag)
			for (std::list<sItemInfo>::iterator it = doc->m_ballList.begin(); it != doc->m_ballList.end(); ++it)
				if (it->typeId == 0x140000d8)
				{
					FrListItem* li = box->AddItem(&*it);
					if (usedBall == it->typeId)
					{
						selBall = it->typeId;
						box->SelectItem(li, true);
					}
					break;
				}
		for (std::list<sItemInfo>::iterator it = doc->m_ballList.begin(); it != doc->m_ballList.end(); ++it)
		{
			if (flag && (it->typeId == 0x14000000 || it->typeId == 0x140000d8))
				continue;
			FrListItem* li = box->AddItem(&*it);
			if (usedBall == it->typeId)
			{
				selBall = it->typeId;
				box->SelectItem(li, true);
			}
		}
		return;
	}
	if (sub == 10)
	{
		// caso 10 (0061af80): m_myItemList (+0x375c); passivos = sem cupom, nao escondidos (006336a0), sem flags 6 em +0xc0 do
		// IFF (00a17260), tid != 0x1a000042 e com 0x2000000 no tid
		for (std::list<sItemInfo>::iterator it = doc->m_myItemList.begin(); it != doc->m_myItemList.end(); ++it)
		{
			unsigned long tid = it->typeId;
			if (doc->m_itemManager.GetCouponKind(tid) != 0)
				continue;
			bool hidden;
			if ((tid >> 26) == 6 && (tid & 0x1f00000) == 0x1e00000)
				hidden = true;
			else if ((tid >> 26) == 6 && (tid & 0x1f00000) == 0x1f00000)
				hidden = !(doc->m_myInfo.info.dwIdentity & 0x2804);
			else
				hidden = ItemManager()->IsNonVisibleItem(tid) == true;
			if (hidden)
				continue;
			void* iff = doc->m_itemManager.FindItem(tid);
			if (iff && (*(unsigned long*)((char*)iff + 0xc0) & 6))
				continue;
			if (tid == 0x1a000042 || !(tid & 0x2000000))
				continue;
			box->AddItem(&*it);
		}
		return;
	}
	if (sub == 9)
	{
		// caso 9: m_myItemList (+0x375c); itens sem cupom (kind 0, tid sem 0x2000000) cuja quantidade (Common[0]) excede
		// quantas vezes o tid ja esta nos 10 slots +0xa36..0xa5a. FUN_005b6500 = list::push_back (listas locais de
		// tipo 1/2, sem efeito visivel). Slots: 2a metade abaixo. Ramo !NT_SC_ITEMSLOT: so AddItem dos n slots.
		for (std::list<sItemInfo>::iterator it = doc->m_myItemList.begin(); it != doc->m_myItemList.end(); ++it)
		{
			if (doc->m_itemManager.GetCouponKind(it->typeId) != 0 || (it->typeId & 0x2000000))
				continue;
			int used = 0;
			for (int k = 0; k < 10; ++k)
				if (it->typeId == *(unsigned long*)((char*)doc + 0xa36 + k * 4))
					++used;
			if (it->Common[0] != used && it->Common[0] - used >= 0)
				box->AddItem(&*it);
		}
		// 2a metade (0061bdb4): lista de slots (+0x190) a partir dos 10 slots doc+0xa36; so com a lista de slots criada.
		FrListBox* slotBox = *(FrListBox**)((char*)this + 0x190);
		jp983_rastro("D313 Active slotBox=%p slot0=%08x slot1=%08x nAdd=%d", slotBox, *(unsigned long*)((char*)doc + 0xa36), *(unsigned long*)((char*)doc + 0xa3a), (int)doc->GetNumAddItemSlotByMascot());
		if (!slotBox)
			return;
		slotBox->ClearItem();
		int n = doc->GetNumAddItemSlotByMascot() + 8;
		bool nt = IsLocalContent(S4_NT_SC_ITEMSLOT);
		if (IsLocalContent(S4_CARD_SYSTEM))
		{
			CCardManager::Instance()->SetPlayerIndex(0xff);
			CCardManager::Instance()->CalcCardPeriodAndStatus();
			int ps = CCardManager::Instance()->GetCardPeriodSlot();
			if (!nt || ps > 0)
				n += ps;
		}
		FrListBox* itemBox = *(FrListBox**)((char*)this + 0x144);
		for (int i = 0; i < 10; ++i)
		{
			unsigned long* slot = (unsigned long*)((char*)doc + 0xa36 + i * 4);
			if (i < n)
			{
				slotBox->AddItem(slot);
				continue;
			}
			if (!nt)
				continue; // 983: sem NT_SC_ITEMSLOT so os n primeiros slots entram
			// FUN_00615ab0 (UnequipItem do form): o slot fora da faixa volta ao inventario e e zerado
			UnequipItem983(slot);
		}
		int sz = slotBox->GetCurrentItemSize(true);
		for (int k = sz; k < 10; ++k)
			slotBox->AddItem(0);
		return;
	}
	unsigned long charType = *(unsigned long*)((char*)this + 0x4f8);
	unsigned long mask = MyRoomTabMask983(sub);
	jp983_rastro("B404 Fill sub=%d charType=%08x mask=%08x parts=%d box=%p", sub, charType, mask, (int)doc->m_partsList.size(), box);
	int* equipHead = *(int**)((char*)doc + 0x111d8);
	int nChar = 0, nCat = 0;
	for (std::list<sItemInfo>::iterator it = doc->m_partsList.begin(); it != doc->m_partsList.end(); ++it)
	{
		if (((it->typeId >> 18) & 0xff) == (charType & 0x3ffffff))
			++nChar;
		if (!S5::UnderCategory(charType, it->typeId, mask))
			continue;
		++nCat;
		// caso 5: pecas do grupo A (CreateCharacterOption) so com taxa de mau comportamento boa e nivel > 0x14
		if (sub == 5 && CreateCharacterOption::Instance()->IsPartGroupA983(it->typeId) &&
			!(IsGoodMannerRate983() && *((unsigned char*)doc + 0x91d) > 0x14))
			continue;
		bool equipped = false;
		if (equipHead)
			for (int* n = (int*)*equipHead; n != equipHead; n = (int*)*n)
				if ((unsigned long)n[4] == it->id) { equipped = true; break; }
		if (equipped)
			continue;
		const IFF_STRUCT::sPart* part = (sub == 0x16 && !IsLocalContent(S4_UCC)) ? 0 : ItemManager()->FindPart(it->typeId);
		if (part)
		{
			char* r = (char*)part;
			char* d = (char*)&*it;
			*(unsigned short*)(d + 0xa4) = *(unsigned short*)(r + 0x228);
			*(unsigned short*)(d + 0xa6) = *(unsigned short*)(r + 0x22a);
			*(unsigned short*)(d + 0xa8) = *(unsigned short*)(r + 0x22c);
		}
		box->AddItem(&*it);
	}
	jp983_rastro("B407 Fill porChar=%d porCat=%d equipHead=%p first=%08x", nChar, nCat, equipHead, doc->m_partsList.empty() ? 0 : doc->m_partsList.front().typeId);
	// selecao dos slots equipados (0061af80, laco 0..0x17): acha na lista o item cujo typeId (e uid, se o personagem tiver
	// ItemIdList no slot) bate com o slot do My Room (+0x490 = typeIds, +0x494 = uids) e o seleciona.
	SelectEquippedSlots983(doc, box, *(unsigned long**)((char*)this + 0x490), (unsigned long*)((char*)this + 0x494));
	if (sub != 5 && sub != 0x16)
		return;
	// caso 5: tambem a lista auxiliar (+0x37bc) e a selecao dos 0x14 typeIds de +0x4f4
	for (std::list<sItemInfo>::iterator it = doc->m_auxPartList.begin(); it != doc->m_auxPartList.end(); ++it)
		box->AddItem(&*it);
	unsigned long* auxType = (unsigned long*)((char*)this + 0x4f4);
	for (int s = 0; s < 0x14; ++s)
	{
		for (FrListBox::ITEM_LIST::iterator li = box->m_itemList.begin(); li != box->m_itemList.end(); ++li)
		{
			sItemInfo* info = (sItemInfo*)(*li)->pData;
			if (info && info->typeId == auxType[s])
			{
				box->SelectItem(*li, false);
				break;
			}
		}
	}
	if (sub != 0x16 || !IsLocalContent(S4_UCC))
		return;
	// caso 0x16 com UCC: lista +0x3878 (m_uccItemList) filtrada pela aba, depois a mesma selecao dos slots
	for (std::list<sItemInfo>::iterator it = doc->m_uccItemList.begin(); it != doc->m_uccItemList.end(); ++it)
	{
		if (!S5::UnderCategory(charType, it->typeId, mask))
			continue;
		const IFF_STRUCT::sPart* part = ItemManager()->FindPart(it->typeId);
		if (part)
		{
			char* r = (char*)part;
			char* d = (char*)&*it;
			*(unsigned short*)(d + 0xa4) = *(unsigned short*)(r + 0x228);
			*(unsigned short*)(d + 0xa6) = *(unsigned short*)(r + 0x22a);
			*(unsigned short*)(d + 0xa8) = *(unsigned short*)(r + 0x22c);
		}
		box->AddItem(&*it);
	}
	SelectEquippedSlots983(doc, box, *(unsigned long**)((char*)this + 0x490), (unsigned long*)((char*)this + 0x494));
}

// 0061cc80: seleciona o taco pelo uid (m_clubSetMap): grava +0x514 (uid), +0x518 (tid), +0x51c/+0x520 (dados). Taco (bit 0x80) abaixo do nivel do
// jogador vira o taco padrao (tid 0x10000000, ret 2); senao vira o taco do jogo (doc+0xa2e, ret 1). Nao achou: 0. Na aba 7: previa
// 3D do taco (0061cde2: 00605640(+0x518, 0)).
int CRealMyRoomForm983::SelectClub983(unsigned long uid)
{
	char* self = (char*)this;
	CSharedDoc* doc = Doc();
	std::map<unsigned int, sItemInfo>::iterator it = doc->m_clubSetMap.find(uid);
	if (it == doc->m_clubSetMap.end())
	{
		return 0;
	}
	*(unsigned long*)(self + 0x518) = it->second.typeId;
	*(unsigned long*)(self + 0x514) = it->first;
	*(char**)(self + 0x51c) = (char*)&it->second + 8;
	*(char**)(self + 0x520) = (char*)&it->second + 0xa6;
	int ret = 0;
	IFF_ITEM_COMMON* common = ItemManager()->FindCommonItem(it->second.typeId);
	if (common)
	{
		unsigned char lvl = common->Level & 0x7f;
		unsigned char my = *((unsigned char*)doc + 0x91d);
		if (common->Level & 0x80)
		{
			if (lvl >= my)
				*(unsigned long*)((char*)doc + 0xa2e) = it->first, ret = 1;
			else
			{
				ret = 2;
				for (std::map<unsigned int, sItemInfo>::iterator d = doc->m_clubSetMap.begin(); d != doc->m_clubSetMap.end(); ++d)
					if (d->second.typeId == 0x10000000)
					{
						*(unsigned long*)((char*)doc + 0xa2e) = d->first;
						*(unsigned long*)(self + 0x518) = d->second.typeId;
						*(unsigned long*)(self + 0x514) = d->first;
						*(char**)(self + 0x51c) = (char*)&d->second + 8;
						*(char**)(self + 0x520) = (char*)&d->second + 0xa6;
						break;
					}
			}
		}
		else if (lvl <= my)
			*(unsigned long*)((char*)doc + 0xa2e) = it->first, ret = 1;
	}
	if (*(int*)(self + 0x530) == 7)
	{
		MyRoomPreview983(self, *(unsigned long*)(self + 0x518), false);
		*(int*)(self + 0x528) = 0; // 0061aa80
		UpdateStats983(self);
	}
	return ret;
}

// 0061ce00: bola escolhida (aba 8): +0x524 e a bola em uso (doc+0xa32); na aba 8 previa 00605640(&+0x524) e 0061aab0
void CRealMyRoomForm983::SelectBall983(unsigned long tid)
{
	char* self = (char*)this;
	*(unsigned long*)(self + 0x524) = tid;
	*(unsigned long*)((char*)Doc() + 0xa32) = tid;
	if (*(int*)(self + 0x530) == 8)
	{
		MyRoomPreview983(self, tid, false);
		if (FrWnd* w = *(FrWnd**)(self + 0x12c))
			w->SetVisible(false);
		*(int*)(self + 0x528) = 1;
		UpdateStats983(self);
	}
}

static void SendDresserParts983(CSharedDoc* sd);
// 0061d7a0 (parcial): troca a sub-aba (+0x530) e ajusta a visibilidade dos grupos. NAO portados: 0061af80 (selecao nas listas
// do CSharedDoc), 0061a750 (stats %d/%d), 00605640 (abre widget do storage), pacotes ao LobbyAvatar/Caddie.
void CRealMyRoomForm983::SelectSubTab983(int sub, bool force)
{
	char* self = (char*)this;
	int& cur = *(int*)(self + 0x530);
	bool& dirty = *(bool*)(self + 0xa12);
	if (!force && cur == sub && !dirty)
		return;
	dirty = false;
	// 0061d7f0: refaz a previa a forca ao entrar/sair das sub-abas de skin (0xe-0x10) e da 0x11/0x22
	int mainTab = *(int*)(self + 0x52c);
	bool fromSkin = cur == 0xe || cur == 0xf || cur == 0x10 || cur == 0x22;
	bool repaint = ((cur < 6 || cur == 0x16 || cur == 0x17 || cur == 0x1b || cur == 0x11 || cur == 0x22) && sub >= 0xe && sub <= 0x10)
		|| (mainTab == 0 && (fromSkin || cur == 0x11));
	if (mainTab == 0 && (cur < 6 || cur == 0x16 || cur == 0x17 || cur == 0x1b) && !(sub < 6 || sub == 0x16 || sub == 0x17 || sub == 0x1b))
		SendDresserParts983(Doc()); // C231.1: sair de Clothes -> 0x0020 sub 0
	if (sub == 6)
		sub = 2;
	cur = sub;
	FrTabButton* subBar = *(FrTabButton**)(self + 0x138);
	if (subBar)
		subBar->Select(cur);
	FrWnd* giftBg = *(FrWnd**)(self + 0x1b8);
	FrWnd* giftDesc = *(FrWnd**)(self + 0x1bc);
	FrWnd* stats = *(FrWnd**)(self + 0x158);
	FrWnd* list = *(FrWnd**)(self + 0x144);
	FrWnd* box = *(FrWnd**)(self + 0x198);
	FrWnd* sbox = *(FrWnd**)(self + 0x194);
	if (giftBg) giftBg->SetVisible(false);
	if (giftDesc) giftDesc->SetVisible(false);
	if (stats) stats->SetVisible(false);
	if (list) list->SetVisible(true);
	bool statsOn = false;
	int boxOn = -1; // -1: nao mexe
	switch (cur)
	{
	case 2: case 3: case 4: case 5: case 0x16: case 0x17: case 0x1b: case 7:
		statsOn = true; boxOn = 1; break;
	case 0xb: case 0xd:
		statsOn = true; break;
	case 8: case 9: case 10: case 0xe: case 0xf: case 0x10: case 0x11: case 0x1c: case 0x20:
		boxOn = 0; break;
	}
	ShowCardHolic983(false); // 0061d8b8: 00605720(0) (so mexe se o Card Holic ja foi criado)
	if (cur == 0x1c)
	{
		// 0061db9e..0061dbc2 (case 0x1c): lista do item some, Card Holic aparece (00605720(1)); updown_group some
		if (list) list->SetVisible(false);
		ShowCardHolic983(true);
		if (box) box->SetVisible(false);
	}
	if (stats) stats->SetVisible(statsOn);
	if (box && boxOn >= 0) box->SetVisible(boxOn != 0);
	if (sbox) sbox->SetVisible(cur == 9);
	if (cur == 7)
	{
		// 0061d933: 00605010(0, 1): mastery_m (+0x1b4) some; clubwork_m, upgrade, downgrade (+0x1b0/0x1a4/0x1a8) aparecem
		FrWnd* w[4] = { *(FrWnd**)(self + 0x1b4), *(FrWnd**)(self + 0x1b0), *(FrWnd**)(self + 0x1a4), *(FrWnd**)(self + 0x1a8) };
		if (w[0]) w[0]->SetVisible(false);
		for (int i = 1; i < 4; ++i)
			if (w[i]) w[i]->SetVisible(true);
	}
	// 0061d8d6 (switch da sub-aba): previa do personagem (+0x4f8) ou apaga (00605530). 0x22/0x23 e 0x18/0x1c portados (B461; resto de 0x1c: 00605720 nao)
	// O 983 escolhe a janela (00604ed0) no fim e o ShowPet roda depois na thread do CAnotherHand; aqui e na hora, entao antes.
	// 0061d7a0: byte +0xf8 da lista (+0x144): 1 nas abas 2-5/0x16/0x17/0x1b e 0x20; 0 em 7-0x15 e 0x18/0x1c (estes so com NT REAL_MYROOM)
	if (list)
	{
		bool f8 = cur == 2 || cur == 3 || cur == 4 || cur == 5 || cur == 0x16 || cur == 0x17 || cur == 0x1b || cur == 0x20;
		bool zero = (cur >= 7 && cur <= 0x15 && cur != 0xc && cur != 0x12) || ((cur == 0x18 || cur == 0x1c) && IsLocalContent(S4_REAL_MYROOM));
		if (f8 || zero)
			*((unsigned char*)list + 0xf8) = f8 ? 1 : 0;
	}
	MyRoomPetSelectWnd983(self);
	if (cur == 7)
	{
		FillItemList983(7); // B527: o 983 chama 0061af80 antes do switch; ela grava +0x514 (taco do doc) e sem isso SelectClub983(0) falhava (b526-1: uid=0)
		SelectClub983(*(unsigned long*)(self + 0x514)); // 0061d948; B524: depois de escolher a janela da previa (antes o ShowPet caia sem wnd)
	}
	switch (cur)
	{
	case 2: case 3: case 4: case 5: case 0x16: case 0x17: case 0x1b:
		if ((repaint || *(int*)(self + 0xa3c) != 1) && g_lobbyModal983)
			MyRoomPreview983(self, *(unsigned long*)(self + 0x4f8), repaint);
		else if (repaint || *(int*)(self + 0xa3c) != 1)
			MyRoomPetClear983(self);
		break;
	case 8: // 0061d7a0 caso 8: 0061ce00(+0x524) = previa da bola (d408-1/015 x orig-d405-1/015)
		FillItemList983(8); // D417: 0061af80 roda antes do switch e grava +0x524 (bola em uso); sem isso a previa saia de tid 0 (d414-1/015)
		SelectBall983(*(unsigned long*)(self + 0x524));
		break;
	case 9: case 10: case 0xb: case 0x20:
		MyRoomPetClear983(self);
		break;
	case 0x22: case 0x23: // 0061d7a0: 0x22 poe o fundo st_cutin; ambos 0061aab0 (esconde +0x12c, +0x528 = 1, stats) e 00605640(+0x4f8)
		if (cur == 0x22)
			if (FrArea* t = (FrArea*)*(FrWnd**)(self + 0x148)) // 0061db0b: ecx = middle_ui.tabtxt2
				t->SetBgImg("st_cutin");
		if (FrWnd* w = *(FrWnd**)(self + 0x12c))
			w->SetVisible(false);
		*(int*)(self + 0x528) = 1;
		UpdateStats983(self);
		MyRoomPreview983(self, *(unsigned long*)(self + 0x4f8), repaint);
		break;
	case 0xe: case 0xf: case 0x10: case 0x11:
		MyRoomPreview983(self, *(unsigned long*)(self + 0x4f8), repaint);
		// 0061d7a0: as 6 skins equipadas (doc+0xa76) vao para +0x964..+0x978; sem categoria (tid & 0x3c00000 == 0) zera o deslocamento
		for (int i = 0; i < 6; i++)
		{
			unsigned long t = *(unsigned long*)((char*)Doc() + 0xa76 + i * 4);
			*(unsigned long*)(self + 0x964 + i * 4) = t;
			if (t && ItemManager()->FindSkin(t) && (t & 0x3c00000) == 0)
			{
				*(float*)(self + 0x97c) = 0.0f;
				*(float*)(self + 0x980) = 0.0f;
				*(int*)(self + 0x984) = ItemManager()->FindSkin(t)->HScroll;
				*(int*)(self + 0x988) = ItemManager()->FindSkin(t)->VScroll;
			}
		}
		break;
	case 0x18: case 0x1c: // com NT REAL_MYROOM (00a7a8d0): 00605530(1) apaga a previa
		if (IsLocalContent(S4_REAL_MYROOM))
			MyRoomPetClear983(self);
		break;
	}
	UpdateStats983(self);
	if ((cur >= 2 && cur <= 5) || cur == 0x16 || cur == 7 || cur == 8 || cur == 9 || cur == 10 || cur == 0xb || cur == 0xd || (cur >= 0xe && cur <= 0x11) || cur == 0x23)
		FillItemList983(cur);
	else if (FrListBox* list = *(FrListBox**)(self + 0x144))
		list->ClearItem(); // abas ainda sem lista (Decoration etc.): vazia, nao a grade da aba anterior (d259-1/014 x orig-d247-1/016)
	// 0061af80 (fim): completa a grade com casas vazias ate 8 (item_base_empty via OwnerDraw), em todas as abas (C169.1; a 0x13 so nao ordena)
	if (FrListBox* pad = *(FrListBox**)(self + 0x144))
	{
		// 0061af80 (fim): AddItem(0) ate 8 em TODAS as abas; so o SortItem(00604b40) e pulado na 0x13 (Trophies; d405-1 x orig-d405-1/017)
		for (int n = pad->GetCurrentItemSize(true); n < 8; ++n)
			pad->AddItem(0);
		if (cur != 0x13)
			pad->SortItem(EmptyCompares);
	}
	// B559/C324.1: trocar de sub-aba abre a lista no TOPO (o SelectItem(true) acima rolava ate o selecionado; c322-1 x orig-c322-1)
	if (FrWnd* topList = *(FrWnd**)(self + 0x144))
		if (FrScrollBar* topBar = ((FrWndScrJp983*)topList)->GetScrBar983())
			topBar->SetCurTopRow(0);
	// 0061df17..: tela/camera do lobby conforme a aba principal (+0x52c): Clothes e Decoration(sub 0x20) = 5; Caddie = 6; as demais = 7
	// (ItemCamera, C159/M4); LobbyAvatar/LobbyCaddie recebem 0x1ce/0x1cf e o lobby recalcula atores/camera (005f8020)
	if (RFLobbyDesktop* lobby = RFLobbyDesktop::Instance983())
	{
		int screen = 7, ma = 0x1cf, mc = 0x1cf;
		if (mainTab == 0 || (mainTab == 4 && cur == 0x20))
		{
			screen = 5; ma = 0x1ce; mc = 0x1cf;
		}
		else if (mainTab == 2)
		{
			screen = 6; ma = 0x1cf; mc = 0x1ce;
		}
		lobby->SetScreen983(screen);
		AfxGetTask()->GetActor("LobbyAvatar") << MsgObject(NULL, ma, 1, 0, 0, 0, 0);
		AfxGetTask()->GetActor("LobbyCaddie") << MsgObject(NULL, mc, 1, 0, 0, 0, 0);
		lobby->UpdateLobbyActors983();
	}
}

// 0061eaa0 (parte local, param_3 = 0): acha o personagem do guidChar do CSharedDoc em m_charMap e guarda os ponteiros
// do no (tidParts +0x490, tidAuxParts +0x4f4, PCL +0x48c), tid +0x4f8, guid +0x4fc e a copia de ItemIdList (+0x494, 24 dwords).
// A copia e condicionada a 00a7a8d0(tid) (bitset de tipos); aqui sempre. Pacote 0x9 do 0060e810 e o resto (0061af80 etc.) nao portados. B383
void CRealMyRoomForm983::SelectCharacter983()
{
	char* self = (char*)this;
	CSharedDoc* doc = Doc();
	std::map<unsigned int, sCharacterInfo>::iterator ci = doc->m_charMap.find(doc->m_myInfo.userEquip.guidChar);
	if (ci == doc->m_charMap.end())
		return;
	sCharacterInfo& c = ci->second;
	*(unsigned long*)(self + 0x4f8) = c.tid;
	*(unsigned long**)(self + 0x490) = c.tidParts;
	memcpy(self + 0x494, c.ItemIdList, 24 * sizeof(unsigned long));
	*(unsigned long**)(self + 0x4f4) = c.tidAuxParts;
	*(char**)(self + 0x48c) = c.PCL;
	*(unsigned long*)(self + 0x4fc) = c.guid;
}

// 0061eaa0 (com chave): achou o personagem `key` em m_charMap -> mesmos campos do SelectCharacter983 + guidChar do doc (+0xa2a);
// se o doc esta no modo +0x8cb == +0x10708 e a aba principal e 0/4: reconstroi a PartTidList (632df0) e a lista da sub-aba (0061af80).
// Nao portado: 0050cf40 (entrada do personagem num mapa do doc). B449; previa 00605640 (A264); +0x124/abas A277
void CRealMyRoomForm983::SelectCharacterByKey983(unsigned long key, int p3)
{
	char* self = (char*)this;
	CSharedDoc* doc = Doc();
	if (*(char*)(self + 0x124) == 1)
	{
		// 0060e810: o cut-in do personagem atual mudou (0063f4b0/0063f620 no equipar/tirar) -> 0x0020 sub 9 antes de trocar
		if (sCharacterInfo* cur = doc->FindChar983((unsigned long)-1))
		{
			WSendPacket w((enumClientPacket)0x20);
			w.Encode1(9);
			w.Encode4(cur->guid);
			w.EncodeBuffer(cur->cutIn, 0x10);
			w.Send(TO_GAME);
		}
		*(char*)(self + 0x124) = 0;
	}
	if (p3 != 0 && doc->m_myInfo.userEquip.guidChar != key)
		return;
	std::map<unsigned int, sCharacterInfo>::iterator ci = doc->m_charMap.find(key);
	if (ci == doc->m_charMap.end())
		return;
	sCharacterInfo& c = ci->second;
	*(unsigned long*)(self + 0x4f8) = c.tid;
	*(unsigned long**)(self + 0x490) = c.tidParts;
	memcpy(self + 0x494, c.ItemIdList, 24 * sizeof(unsigned long));
	*(unsigned long**)(self + 0x4f4) = c.tidAuxParts;
	*(char**)(self + 0x48c) = c.PCL;
	*(unsigned long*)(self + 0x4fc) = c.guid;
	doc->m_myInfo.userEquip.guidChar = c.guid;
	int mainTab = *(int*)(self + 0x52c);
	if (*(int*)((char*)doc + 0x8cb) == *(int*)((char*)doc + 0x10708))
	{
		if (mainTab == 0 || mainTab == 4)
		{
			doc->BuildMyPartTidList(c);
			FillItemList983(*(int*)(self + 0x530));
			MyRoomPreview983(self, c.tid, false); // 0061ebe5/0061ec40: 00605640(+0x4f8)
			if (mainTab == 0)
			{
				// 0061aa80: mostra +0x12c (vtbl +0x18), +0x528 = 0 e refaz os stats
				if (FrWnd* w = *(FrWnd**)(self + 0x12c))
					w->SetVisible(true);
				*(int*)(self + 0x528) = 0;
				UpdateStats983(self);
			}
		}
		else if (*(int*)(self + 0x528) == 1)
			UpdateStats983(self); // 0061a750
		// 006091a0: lista +0x144 volta ao topo (FrScrollBar::SetCurTopRow(0) do +0x90)
		if (FrWnd* list = *(FrWnd**)(self + 0x144))
			if (FrScrollBar* bar = ((FrWndScrJp983*)list)->GetScrBar983())
				bar->SetCurTopRow(0);
	}
	else if (mainTab == 0)
		doc->BuildMyPartTidList(c);
}

// 00620770 (init do form, msg 0x75): com o doc no modo +0x8cb == +0x10708 reaplica personagem (0061eaa0), taco (0061cc80), bola (0061ce00)
// e, se !keep, caddie (0061c960) e mascote (0061cb70) do CSharedDoc; refaz aba/sub-aba (+0x52c/+0x530) e mostra/esconde +0x12c (0061aa60:
// aba > 2 esconde, como 0061aab0). NAO portado: 00605630(0) (previa); as skins +0x964 ja vem de SelectSubTab983.
void CRealMyRoomForm983::InitForm983(bool keepCaddieMascot)
{
	char* self = (char*)this;
	CSharedDoc* doc = Doc();
	if (*(int*)((char*)doc + 0x8cb) != *(int*)((char*)doc + 0x10708))
		return;
	SelectCharacterByKey983(*(unsigned long*)((char*)doc + 0xa2a), 0);
	SelectClub983(*(unsigned long*)((char*)doc + 0xa2e));
	SelectBall983(*(unsigned long*)((char*)doc + 0xa32));
	if (!keepCaddieMascot)
	{
		SelectCaddie983(*(unsigned long*)((char*)doc + 0xa26));
		SelectMascot983(*(unsigned long*)((char*)doc + 0xa8e));
	}
	SetMainTab983(*(int*)(self + 0x52c), true);
	SelectSubTab983(*(int*)(self + 0x530), true);
	if (FrWnd* w = *(FrWnd**)(self + 0x12c))
		w->SetVisible(*(int*)(self + 0x52c) <= 2);
	*(int*)(self + 0x528) = *(int*)(self + 0x52c) > 2 ? 1 : 0;
}

static void SelectMascotTail983(CSharedDoc* doc);
// C231.1: o original compara o doc com o cache do form (+0x720..) ao fechar e manda 0x0020 sub 1/3/8 so do que mudou;
// aqui o cache = o estado do doc no fim da sincronizacao de abertura (caddie, taco, bola, mascote)
static unsigned long s_syncCaddie983, s_syncClub983, s_syncBall983, s_syncMascot983;
static std::map<unsigned int, sCharacterInfo> s_syncChars983;
// 0x0020 sub 0 (C231.1, 516 B): ao sair da aba Clothes/fechar o original manda o personagem inteiro se as partes do doc
// diferem do cache do form (Net_EquipDresserParts do 645; orig-c229-1). Cache = doc na abertura.
static void SendDresserParts983(CSharedDoc* sd)
{
	typedef std::map<unsigned int, sCharacterInfo> CharMap;
	for (CharMap::iterator it = s_syncChars983.begin(); it != s_syncChars983.end(); ++it)
	{
		CharMap::iterator dc = sd->m_charMap.find(it->first);
		if (dc == sd->m_charMap.end())
			continue;
		if (memcmp(dc->second.tidParts, it->second.tidParts, sizeof(it->second.tidParts)) == 0 &&
			memcmp(dc->second.ItemIdList, it->second.ItemIdList, sizeof(it->second.ItemIdList)) == 0 &&
			memcmp(dc->second.tidAuxParts, it->second.tidAuxParts, sizeof(it->second.tidAuxParts)) == 0)
			continue;
		WSendPacket w((enumClientPacket)0x20);
		// no fio sao 513 B (516 do original com 2 de id + sub): sem o padding de 3 B entre PCL[5] e mastery
		unsigned char wire[513];
		const unsigned char* src = (const unsigned char*)&dc->second;
		size_t pre = offsetof(sCharacterInfo, PCL) + sizeof(dc->second.PCL);
		memcpy(wire, src, pre);
		memcpy(wire + pre, &dc->second.mastery, sizeof(dc->second.mastery) + sizeof(dc->second.card));
		w.Encode1(0); w.EncodeBuffer(wire, sizeof(wire)); w.Send(TO_GAME);
		it->second = dc->second;
	}
}
// 0060e4b0..0060e810 (apos 00615dd0 e apos o caso 0x75 de HandleMsg): 0x0020 subs 1,2,3,4,8,2,9 com o estado do doc.
static void SendDocSyncPackets983(CSharedDoc* sd)
{
	// C159.1 (00615dd0, apos 0060e4b0): os caches do form (+0x720..) nunca sao gravados aqui, entao no original
	// (orig-c151-1/009) cada helper envia 0x0020 com o estado do doc: sub 1 caddie (00614d20), 2 partes (0060e550),
	// 3 (0060e600), 4 (00613930), 8 mascote (00614de0), 2 de novo (0063de40), 9 (0060e810).
	char* d = (char*)sd;
	s_syncCaddie983 = *(unsigned long*)(d + 0xa26);
	s_syncClub983 = *(unsigned long*)(d + 0xa2e);
	s_syncBall983 = *(unsigned long*)(d + 0xa32);
	s_syncMascot983 = *(unsigned long*)(d + 0xa8e);
	s_syncChars983 = sd->m_charMap;
	// 00614d20/00614de0: mandam se o cache do form (+0x720/+0x788) difere do doc, salvo id != 0 fora do mapa (doc+0x3718/
	// +0x3728 = end). Na abertura o cache e lixo de heap (ctor 0061f1f0 nao o inicia; so o OnInit 00620c76 copia o doc
	// depois): quase sempre != doc -> sub 1/8 = 0 tambem saem (orig-d324-1, orig-a315-1, orig-c151-1; orig-a307-1 = lixo 0).
	unsigned long caddie = *(unsigned long*)(d + 0xa26), mascot = *(unsigned long*)(d + 0xa8e);
	if (caddie == 0 || sd->m_caddieMap.find(caddie) != sd->m_caddieMap.end())
	{ WSendPacket w((enumClientPacket)0x20); w.Encode1(1); w.Encode4(caddie); w.Send(TO_GAME); }
	{ WSendPacket w((enumClientPacket)0x20); w.Encode1(2); w.EncodeBuffer(d + 0xa36, 0x28); w.Send(TO_GAME); }
	{
		WSendPacket w((enumClientPacket)0x20); w.Encode1(3);
		w.Encode4(*(unsigned long*)(d + 0xa32)); w.Encode4(*(unsigned long*)(d + 0xa2e)); w.Send(TO_GAME);
	}
	{ WSendPacket w((enumClientPacket)0x20); w.Encode1(4); w.EncodeBuffer(d + 0xa76, 0x18); w.Send(TO_GAME); }
	if (mascot == 0 || sd->m_mascotMap.find(mascot) != sd->m_mascotMap.end())
	{ WSendPacket w((enumClientPacket)0x20); w.Encode1(8); w.Encode4(mascot); w.Send(TO_GAME); }
	{ WSendPacket w((enumClientPacket)0x20); w.Encode1(2); w.EncodeBuffer(d + 0xa36, 0x28); w.Send(TO_GAME); }
	{
		std::map<unsigned int, sCharacterInfo>::iterator ci = sd->m_charMap.find(*(unsigned long*)(d + 0xa2a));
		if (ci != sd->m_charMap.end())
		{
			// 0060e810: 16 bytes em sCharacterInfo+0x1b8 = cutIn[4] (A277; antes +0x1b4, deslocado 4 bytes)
			WSendPacket w((enumClientPacket)0x20); w.Encode1(9);
			w.Encode4(ci->second.guid); w.EncodeBuffer(ci->second.cutIn, 0x10); w.Send(TO_GAME);
		}
	}
}

// 00623500 (+0xa0): CRealMyRoomMain::HandleMsg do 645 reduzido ao que o 983 manda ao form. 0x48 (param2->guid, param3):
// trocou o personagem. Os outros casos (0x49 caddie, 0x4a mascote, ...) ainda nao portados -> falso.
bool CRealMyRoomForm983::OnMsg983(const MsgObject& msg)
{
	switch (msg.message)
	{
	case 0x48:
		SelectCharacterByKey983(((sCharacterInfo*)msg.param2)->guid, msg.param3);
		return true;
	case 0x49: // 006241b4: caddie (*param2 = chave) + 0061a750
		SelectCaddie983(*(unsigned long*)msg.param2);
		UpdateStats983((char*)this);
		return true;
	case 0x4a: // HandleMsg: taco (*param2 = uid) + 0061a750 (0098ad40 = espera de mutex, sem efeito)
		SelectClub983(*(unsigned long*)msg.param2);
		UpdateStats983((char*)this);
		return true;
	case 0x75: // 0062433x: 525b10 = CLoginInfo::IsPcBang (vtable+0x34); !PcBang -> 00620770(0). Ramo PcBang (00605af0 flags doc+0xa44..a47 por aba -> 0061e460 caddie/mascote) so para conta PC bang: nao portado
		InitForm983(false);
		SendDocSyncPackets983(Doc()); // 0060e4b0/613590/614d20/60e550/60e600/614de0/60e810 (sem cache gravado = sempre envia)
		return true;
	case 0x4b: // bola (*param2 = tid), sem stats
		SelectBall983(*(unsigned long*)msg.param2);
		return true;
	case 0x297: // 645 0x21a (00625510): cartas mudaram; caderno so se aberto (+4) -> 007f58a0, e refaz a lista Pack (006141b0)
		if (CardBook983() && CardBook983()->IsShow())
			CardBook983()->ReBuildCurrentPage();
		BuildCardPackList983();
		return true;
	case 0x2a7: // 645 0x229 (0062552d): abriu o Card Pack (C360.1) -> 007f58a0 + 006141b0; a lista refeita perde a selecao
		if (CardBook983())
			CardBook983()->ReBuildCurrentPage();
		BuildCardPackList983();
		return true;
	case 0xe5: // 983: devolve aba principal (+0x52c) e sub-aba (+0x530) pelos ponteiros param1/param2
		*(int*)msg.param1 = *(int*)((char*)this + 0x52c);
		*(int*)msg.param2 = *(int*)((char*)this + 0x530);
		return true;
	case 0xe6: // 983: grava aba principal (param1 < 6, senao 0 e sub 2) e sub-aba (param2; 1 vira 0x16)
	{
		char* self = (char*)this;
		if (msg.param1 < 6)
			*(int*)(self + 0x52c) = msg.param1;
		else
		{
			*(int*)(self + 0x52c) = 0;
			*(int*)(self + 0x530) = 2;
		}
		*(int*)(self + 0x530) = (msg.param2 == 1) ? 0x16 : msg.param2;
		return true;
	}
	case 0xeb: // 983 (6235bd): param1 = atalho de aba. 0 chama SelectMenu983(0) (00622630); 6 so aba 0/0x16 (SelectMenu(6) autoridade: nao portado); 1/6 -> aba 0/sub 0x16; 2: aba 5/0x18; 3: 0/0x1b; 4: 1/0x1c (2/3/4 so com NT REAL_MYROOM, 00a7a8d0)
	{
		char* self = (char*)this;
		int sel = msg.param1;
		int tab, sub;
		bool clearPet = false;
		bool local = IsLocalContent(S4_REAL_MYROOM);
		if (sel == 1 || sel == 6) { tab = 0; sub = 0x16; }
		else if (local && sel == 2) { tab = 5; sub = 0x18; clearPet = true; }
		else if (local && sel == 3) { tab = 0; sub = 0x1b; }
		else if (local && sel == 4) { tab = 1; sub = 0x1c; clearPet = true; }
		else if (sel == 0)
			return true; // 006235bd: 00622630(1) = default da tabela (nada)
		else
			return true;
		if (sel == 6 && local)
			SelectMenu983(9); // 00622630(9): 0xd3 + 0x0020 do doc (ou msg 0x2af ao main actor com +0xa84)
		*(int*)(self + 0x52c) = tab;
		*(int*)(self + 0x530) = sub;
		SetMainTab983(tab, true); // 0061e4e0
		SelectSubTab983(sub, true); // 0061d7a0
		if (clearPet)
			MyRoomPetClear983(self); // 00605530
		else
			SelectCharacter983(); // 0061eaa0
		return true;
	}
	case 0xf7: // 983: se [form+0x1f4] != 0, grava param1 (byte) em [+0x1f4]+0x149; cai em 0x109
	{
		char* tgt = *(char**)((char*)this + 0x1f4);
		if (tgt)
			*(tgt + 0x149) = (char)msg.param1;
	}
	// fallthrough
	case 0x109: // 983: refaz os stats (0061a750)
		UpdateStats983((char*)this);
		return true;
	case 0x5b: // 00624235: mascote (param2 -> {key, tid, texto +0xd, pcbang +0x3d}); 0061cb70 + msg na textura + stats + lista + 0063de40
	{
		char* self = (char*)this;
		unsigned long* pInfo = (unsigned long*)msg.param2;
		SelectMascot983(pInfo[0]);
		*(unsigned long*)((char*)Doc() + 0xa8e) = pInfo[0];
		char* pv = *(char**)(self + 0x584);
		if (pv && *(WPuppet**)(pv + 0xac) && pInfo[1])
		{
			if (IFF_STRUCT::sMascot* pMascot = Doc()->m_itemManager.FindMascot(pInfo[1]))
				CMascot::ChangeMascotMsgInTex((const char*)((char*)pInfo + 0xd), pMascot, *(WPuppet**)(pv + 0xac),
					MakeStr("myroom%02d", *(unsigned long*)((char*)pMascot + 4) & 0x3ffffff));
		}
		if (*((char*)pInfo + 0x3d) != 0)
			COption::Instance()->mSetPCBangMascotMsg((const char*)((char*)pInfo + 0xd));
		UpdateStats983(self);
		FillItemList983(*(int*)(self + 0x530));
		SelectMascotTail983(Doc());
		return true;
	}
	}
	return false;
}

// 0061c960: seleciona o caddie `key` (guid) em m_caddieMap: +0x504 = key, +0x500 = tid, +0x508 = tidPart (ou tid se 0);
// grava guidCaddie do doc (+0xa26) e, na aba 0xb, reenche a grade. Nao achou: zera. B384
static void HideAllChildren983(FrWnd* wnd);
static void ResetStatsPanel983(char* self);

// 0061aa80: mostra +0x12c, +0x528 = 0 e refaz os stats
static void ResetStatsPanel983(char* self)
{
	if (FrWnd* w = *(FrWnd**)(self + 0x12c))
		w->SetVisible(true);
	*(int*)(self + 0x528) = 0;
	UpdateStats983(self);
}

bool CRealMyRoomForm983::SelectCaddie983(unsigned long key)
{
	char* self = (char*)this;
	CSharedDoc* doc = Doc();
	std::map<unsigned int, sCaddieInfo>::iterator ci = doc->m_caddieMap.find(key);
	bool changed = false;
	if (ci == doc->m_caddieMap.end())
	{
		jp983_rastro("D389 SelCaddie key=%u NAO esta em m_caddieMap (n=%d) tab=%d", (unsigned)key, (int)doc->m_caddieMap.size(), *(int*)(self + 0x530));
		*(unsigned long*)(self + 0x500) = 0;
		*(unsigned long*)(self + 0x504) = 0;
		doc->m_myInfo.userEquip.guidCaddie = 0;
		if (*(int*)(self + 0x530) == 0xb)
		{
			MyRoomPetClear983(self); // 00605530(1)
			HideAllChildren983(*(FrWnd**)(self + 0x144)); // 00befe70
			ResetStatsPanel983(self); // 0061aa80
			if (IActor* lc = AfxGetTask()->GetActor("LobbyCaddie"))
				lc << MsgObject(NULL, 0x1a6, 0, 0, 0, 0, 0);
		}
		if (key == 0)
			*(unsigned long*)((char*)doc + 0x1103c) = 0;
		return false;
	}
	const sCaddieInfo& c = ci->second;
	*(unsigned long*)(self + 0x504) = ci->first;
	// 983 0061c960: no do map (VS2010) chave +0xc, valor +0x10: guid +0x10, tid +0x14, tidPart +0x18
	*(unsigned long*)(self + 0x500) = c.tid;
	*(unsigned long*)(self + 0x508) = c.tidPart ? c.tidPart : c.tid;
	// 0061c960: so o caddie com nivel do item <= nivel do jogador (doc +0x91d) vira o equipado (00a172a0 = FindCommonItem)
	IFF_ITEM_COMMON* common = ItemManager()->FindCommonItem(c.tid); // 983 0061c960: 00a172a0(+0x14 = tid) (D331.1)
	if (common && (common->Level & 0x7f) <= *((unsigned char*)doc + 0x91d))
	{
		if (ci->first != doc->m_myInfo.userEquip.guidCaddie)
			changed = true;
		doc->m_myInfo.userEquip.guidCaddie = ci->first;
		*(unsigned long*)((char*)doc + 0x1103c) = ci->first;
	}
	jp983_rastro("D316 SelCaddie key=%u tid=%08x common=%p lv=%d doclv=%d equip=%u changed=%d st0=%d", key, c.tid, common, common ? (common->Level & 0x7f) : -1, (int)*((unsigned char*)doc + 0x91d), doc->m_myInfo.userEquip.guidCaddie, (int)changed, CStatusHelper().GetStatus983(0));
	{ int n=0; char b[512]=""; for (std::map<unsigned int, IFF_STRUCT::sCaddie>::iterator it = ItemManager()->m_CaddieMap.begin(); it != ItemManager()->m_CaddieMap.end() && n < 12; ++it, ++n) sprintf(b + strlen(b), "%08x ", it->first); jp983_rastro("D326 CaddieKeys %s tid=%08x", b, c.tid); }
	jp983_rastro("D320 IFF caddies=%d cadItems=%d chars=%d items=%d findCad=%p", ItemManager()->GetNumItems(PIG_CADDIE), ItemManager()->GetNumItems(PIG_CADITEM), ItemManager()->GetNumItems(PIG_CHAR), ItemManager()->GetNumItems(PIG_ITEM), ItemManager()->FindCaddie(c.tid));
	if (*(int*)(self + 0x530) == 0xb)
	{
		FillItemList983(0xb);
		if (g_lobbyModal983)
			MyRoomPreview983(self, *(unsigned long*)(self + 0x508), false); // 00605640: previa (ShowPet)
		else if (changed)
		{
			// 00643f40 so procura (sem efeito); TOPPAGE: o caddie 3D do lobby recarrega pela msg 0x1a9
			if (IActor* lc = AfxGetTask()->GetActor("LobbyCaddie"))
				lc << MsgObject(NULL, 0x1a9, 0, 0, 0, 0, 0);
		}
		ResetStatsPanel983(self); // 0061aa80
	}
	return changed;
}

// 00befe70 (FrWnd, ecx = item_list +0x144): zera o byte visivel (+0xd) de cada filho da lista +0xd0 e, se o filho era o
// foco (+0x108), limpa +0x108/+0x10c
static void HideAllChildren983(FrWnd* wnd)
{
	if (!wnd)
		return;
	char* w = (char*)wnd;
	int* head = *(int**)(w + 0xd0);
	if (!head)
		return;
	for (int* node = (int*)*head; node != head; node = (int*)*node)
	{
		char* child = (char*)node[2];
		if (!child)
			continue;
		child[0xd] = 0;
		if (*(char**)(w + 0x108) == child)
		{
			*(unsigned long*)(w + 0x108) = 0;
			*(unsigned long*)(w + 0x10c) = 0;
		}
	}
}

// cauda do 0061cb70: com NT REAL_MYROOM (00a7a8d0) 0063de40 (0x0020 sub 2 com o estado do doc), senao 0063dd00 (SendEquipItemSlotByMascot)
static void SelectMascotTail983(CSharedDoc* doc)
{
	if (IsLocalContent(S4_REAL_MYROOM))
	{
		WSendPacket w((enumClientPacket)0x20); w.Encode1(2); w.EncodeBuffer((char*)doc + 0xa36, 0x28); w.Send(TO_GAME);
	}
	else
		doc->SendEquipItemSlotByMascot();
}

// 0061cb70: seleciona o mascote `key` em m_mascotMap: +0x510 = key, +0x50c = guid; grava guidMascot do doc (+0xa8e)
// e +0x110a4 (key; 0 = nao achou/sem selecao); na aba 0xd reenche a grade. Cauda 63dd00/63de40 portada (B476); 00befe70 portado (B477). B385
void CRealMyRoomForm983::SelectMascot983(unsigned long key)
{
	char* self = (char*)this;
	CSharedDoc* doc = Doc();
	std::map<unsigned int, sMascotInfo>::iterator mi = doc->m_mascotMap.find(key);
	if (mi == doc->m_mascotMap.end())
	{
		*(unsigned long*)(self + 0x50c) = 0;
		*(unsigned long*)(self + 0x510) = 0;
		doc->m_myInfo.userEquip.guidMascot = 0;
		if (*(int*)(self + 0x530) == 0xd)
		{
			MyRoomPetClear983(self); // 0061cb70: aba 0xd sem mascote -> 00605530(1)
			HideAllChildren983(*(FrWnd**)(self + 0x144)); // 00befe70
		}
		if (key == 0)
			*(unsigned long*)((char*)doc + 0x110a4) = 0;
		SelectMascotTail983(doc);
		return;
	}
	*(unsigned long*)(self + 0x50c) = mi->second.guid;
	*(unsigned long*)(self + 0x510) = mi->first;
	doc->m_myInfo.userEquip.guidMascot = mi->first;
	*(unsigned long*)((char*)doc + 0x110a4) = mi->first;
	if (*(int*)(self + 0x530) == 0xd)
		FillItemList983(0xd);
	if (*(int*)(self + 0x530) == 0xd)
	{
		MyRoomPreview983(self, mi->second.tid ? mi->second.tid : mi->second.guid, false); // 00605640: previa (ShowPet)
		// 0061aab0: esconde +0x12c, +0x528 = 1 e refaz os stats
		if (FrWnd* w = *(FrWnd**)(self + 0x12c))
			w->SetVisible(false);
		*(int*)(self + 0x528) = 1;
		UpdateStats983(self);
	}
	else
		MyRoomPreview983(self, mi->second.tid ? mi->second.tid : mi->second.guid, false); // 00605640: previa (ShowPet)
	SelectMascotTail983(doc);
}

// 006165d0 (parcial, B431/C174.1): ao fechar, o original manda 0x0020 sub 9 (60e810) e sub 2 (63de40) com o estado do doc
// (orig-c154-2: os caches do form nunca sao gravados). Os demais helpers nao portados.
bool CRealMyRoomForm983::OnCloseWidget983()
{
	CSharedDoc* sd = Doc();
	MyRoomPetClear983((char*)this); // 00605530
	char* d = (char*)sd;
	SendDresserParts983(sd);
	// C231.1: ordem do original (orig-c229-1): sub 1 caddie, 3 taco/bola, 8 mascote, 9, 2
	if (*(unsigned long*)(d + 0xa26) != s_syncCaddie983)
	{ WSendPacket w((enumClientPacket)0x20); w.Encode1(1); w.Encode4(*(unsigned long*)(d + 0xa26)); w.Send(TO_GAME); }
	if (*(unsigned long*)(d + 0xa2e) != s_syncClub983 || *(unsigned long*)(d + 0xa32) != s_syncBall983)
	{
		WSendPacket w((enumClientPacket)0x20); w.Encode1(3);
		w.Encode4(*(unsigned long*)(d + 0xa32)); w.Encode4(*(unsigned long*)(d + 0xa2e)); w.Send(TO_GAME);
	}
	if (*(unsigned long*)(d + 0xa8e) != s_syncMascot983)
	{ WSendPacket w((enumClientPacket)0x20); w.Encode1(8); w.Encode4(*(unsigned long*)(d + 0xa8e)); w.Send(TO_GAME); }
	s_syncCaddie983 = *(unsigned long*)(d + 0xa26); s_syncClub983 = *(unsigned long*)(d + 0xa2e);
	s_syncBall983 = *(unsigned long*)(d + 0xa32); s_syncMascot983 = *(unsigned long*)(d + 0xa8e);
	std::map<unsigned int, sCharacterInfo>::iterator ci = sd->m_charMap.find(*(unsigned long*)(d + 0xa2a));
	if (ci != sd->m_charMap.end())
	{
		char* c = (char*)&ci->second;
		WSendPacket w((enumClientPacket)0x20); w.Encode1(9);
		w.Encode4(ci->second.guid); w.EncodeBuffer(c + 0x1b4, 0x10); w.Send(TO_GAME);
	}
	{ WSendPacket w((enumClientPacket)0x20); w.Encode1(2); w.EncodeBuffer(d + 0xa36, 0x28); w.Send(TO_GAME); }
	return FrTaskForm::OnCloseWidget983();
}


bool CRealMyRoomForm983::OnInit()
{
	char* self = (char*)this;
	for (size_t i = 0; i < sizeof(s_myRoomBinds983) / sizeof(s_myRoomBinds983[0]); ++i)
	{
		const MyRoomBind983& e = s_myRoomBinds983[i];
		FrWnd* w = FindByPath983(this, e.path);
		if (!w)
			continue;
		if (e.hide)
			w->SetVisible(false);
		else
			*(FrWnd**)(self + e.off) = w;
	}
	if (FrListBox* il = *(FrListBox**)(self + 0x144))
	{
		// 00606e90: item_list liga o botao direito (+0xfc = 1; sem isso o FrListBox ignora o RBUTTONDOWN), +0x114 = 1 e sem som de clique
		il->UseRightButton(true);
		*((unsigned char*)il + 0x114) = 1;
		il->SetPushSound(NULL);
	}
	{
		// 00609850..00609e20: CCardBook em +0xa78 e os controles do Card Holic (INIT de card_book/tabs/card_use/cardpage_index/card_property)
		CCardBook* book = new CCardBook;
		CardBook983() = book;
		Bind983(book->m_pBackground, DYNAMIC_CAST(FrArea, FindByPath983(this, "card_book")));
		Bind983(book->m_pProperty, DYNAMIC_CAST(FrArea, FindByPath983(this, "card_property")));
		Bind983(book->m_pIndexList, DYNAMIC_CAST(FrListBox, FindByPath983(this, "cardpage_index")));
		Bind983(book->m_pUseButton, DYNAMIC_CAST(FrButton, FindByPath983(this, "card_use")));
		static const char* const tabNames[7] = { "card_pack", "card_volume1", "card_volume2", "card_volume3", "card_volume4", "card_volume5", "card_sp" };
		for (int i = 0; i < 7; ++i)
		{
			FrButton* tb = DYNAMIC_CAST(FrButton, FindByPath983(this, tabNames[i]));
			Bind983(book->m_pTabButton[i], tb);
			if (tb)
				tb->SetPushDelay(0.0f);
		}
		// card_slot1..12 -> CCardPage::BoundSlotControl (645 CRealMyRoomMain::BoundCardPage); cardpack_slot* ficam escondidos
		CCardPage* pPage = book->GetCardPage();
		for (int i = 0; i < 12 && pPage; ++i)
		{
			char nm[32];
			sprintf(nm, "card_slot%d", i + 1);
			FrButton* sb = DYNAMIC_CAST(FrButton, FindByPath983(this, nm));
			if (sb)
			{
				pPage->BoundSlotControl((unsigned char)i, sb);
				sb->UseRightButton(true);
			}
		}
	}
	{
		// 00615dd0 (bind item_storage_bgi): com doc+0x110c8 == 0 e +0xa84 == 0 o original manda 0x00D3 (vazio) e, via 0060e4b0,
		// 0x0020 sub 5 + guid do personagem (doc+0xa2a) quando +0x724 difere; +0x724 nunca e gravado aqui. A cond. 00a7a8d0
		// (bitset) e os helpers 00613590/614d20/60e550/60e600/613930/614de0/63dd00/63de40/60e810 (so enviam em diferencas) nao portados. B386
		CSharedDoc* sd = Doc();
		if (!*(char*)((char*)sd + 0x110c8) && !*(char*)(self + 0xa84))
		{
			WSendPacket p((enumClientPacket)0xd3);
			p.Send(TO_GAME);
			if (*(int*)(self + 0x724) != *(int*)((char*)sd + 0xa2a))
			{
				WSendPacket q((enumClientPacket)0x20);
				q.Encode1(5);
				q.Encode4(*(unsigned long*)((char*)sd + 0xa2a));
				q.Send(TO_GAME);
			}
			SendDocSyncPackets983(sd);
		}
	}
	SelectCharacter983();
	{
		// 0061e460 (kind 1/2): reaplica a ultima selecao guardada no doc (+0x1103c caddie, +0x110a4 mascote); so se != 0
		// (o original zera guidCaddie/guidMascot do doc se nao achar; aqui nao mexemos no equip sem selecao previa). B385
		CSharedDoc* d = Doc();
		unsigned long kc = *(unsigned long*)((char*)d + 0x1103c);
		unsigned long km = *(unsigned long*)((char*)d + 0x110a4);
		if (kc)
			SelectCaddie983(kc);
		if (km)
			SelectMascot983(km);
	}
	AddMainTabs983();
	*(int*)(self + 0x52c) = 0;
	*(int*)(self + 0x530) = 0x16;
	SetMainTab983(0, true);
	// B400: b393-1 (g_lobbyModal983 == 0 no lobby: TOPPAGE zera 00e78cac) ainda mostrava o painel azul (C1): teste = esconder
	// main_bg1..4 (+0x1dc..+0x1e8) sempre; chat_bg (+0x1ec) so no modal (00620db3, g == 1).
	for (int i = 0; i < 4; ++i)
	{
		FrWnd* bg = *(FrWnd**)(self + 0x1dc + i * 4);
		if (bg) bg->SetVisible(g_lobbyModal983 != 1); // B422: 983 00620db3 (cmp [e78cac],1; jne): com ==1 ESCONDE main_bg1..4 e mostra chat_bg; B417 estava invertido
	}
	// B403: b400-1 ainda mostra o painel azul com -/+ (nao e main_bg). Teste: esconde tambem item_hide_desc_bg/desc/name
	// (+0x178..0x180). A264: pet/skin_pet/skin_pet2 (+0x184..0x18c) ficam como no layout: o 983 nunca os esconde e a previa
	// e desenhada no OWNERDRAW deles (0061f6d0); o painel azul era o item_storage_* (B411).
	for (int off = 0x178; off <= 0x180; off += 4)
	{
		FrWnd* w = *(FrWnd**)(self + off);
		if (w) w->SetVisible(false);
	}
	{
		// B412: b412-1 ainda mostra o painel azul; chat_bg (+0x1ec, 800x600) vem visivel do layout. 983 (00620db3) so o mostra com g == 1.
		FrWnd* chat = *(FrWnd**)(self + 0x1ec);
		if (chat) chat->SetVisible(g_lobbyModal983 == 1);
	}
	// B411: rastro b411-1: card_slot1..12/cardpack_slot1..8 (quadrados cinza) e item_storage_* (painel azul com -/+) vinham visiveis
	// no lobby; o original so os mostra nas abas My Box/Storage.
	{
		static const char* const hideNames[] = {
			"card_book_back_bg", "cardpacklist", "card_count", "cardpage_index", "click_area_list",
			"item_storage_bgi", "item_storage_pang", "pang_minus", "pang_plus", "item_storage_list", "item_storage_index",
			"item_storage_page_next", "item_storage_page_prev", "item_storage_close", "item_storage_dragdrop" };
		for (int i = 0; i < (int)(sizeof(hideNames) / sizeof(hideNames[0])); ++i)
		{
			FrWnd* w = FindChildByName(hideNames[i]);
			if (w) w->SetVisible(false);
		}
		char nm[32];
		for (int i = 1; i <= 12; ++i)
		{
			sprintf(nm, "card_slot%d", i);
			FrWnd* w = FindChildByName(nm);
			if (w) w->SetVisible(false);
			if (i <= 8)
			{
				sprintf(nm, "cardpack_slot%d", i);
				w = FindChildByName(nm);
				if (w) w->SetVisible(false);
			}
		}
	}
	{
		Dump983 d = { 0 };
		EnumerateChildWindow(DumpChild983, &d);
	}
	FrForm::ms_bModalLock983 = true; // 983 00620cd2: call 00be7950 -> o Open nao liga o escurecimento modal (lobby nao escurece)
	return FrTaskForm::OnInit();
}

IMPLEMENT_OBJECT(CRealMyRoomForm983, FrTaskForm)

// 0061f530: clique na aba principal: troca a aba (0061e4e0) e seleciona a 1a sub-aba do caso
// (0061d7a0: 0x16,7,0xb,0xd,0xe,0x13). A fila de pacotes (+0x5a0/+0x598) e os helpers
// 0061eaa0/0061c960/0061cb70/0061aab0/00613590/00605530 ainda nao portados. B380
void CRealMyRoomForm983::OnTabMainUp983()
{
	FrTabButton* main = *(FrTabButton**)((char*)this + 0x134);
	if (!main || !main->GetSelected())
		return;
	int tab = (int)main->GetSelected()->index;
	SetMainTab983(tab, false);
	static const int firstSub[6] = { 0x16, 7, 0xb, 0xd, 0xe, 0x13 };
	if (tab >= 0 && tab < 6)
	{
		SelectSubTab983(firstSub[tab], false);
		// 0061f530: abas Caddie/Mascot reaplicam a selecao do doc (0061c960/0061cb70 -> 0x0020 sub 2; C240)
		if (tab == 2)
			SelectCaddie983(*(unsigned long*)((char*)Doc() + 0xa26));
		else if (tab == 3)
			SelectMascot983(*(unsigned long*)((char*)Doc() + 0xa8e));
	}
}

// 0061f6b0: clique na sub-aba: SelectSubTab(index da aba selecionada, 0). B382
void CRealMyRoomForm983::OnTabSubUp983()
{
	FrTabButton* sub = *(FrTabButton**)((char*)this + 0x138);
	if (!sub || !sub->GetSelected())
		return;
	SelectSubTab983((int)sub->GetSelected()->index, false);
}

void __fastcall ReviseItemIconPoint(unsigned long tid, WPoint& pt);
namespace S5 { bool __fastcall ISCutinItem(unsigned long tid); }
// 006166b0 casos de aba 0xb (caddie) e 0xd (mascote), parte basica (D): icone centrado, nome e, no mascote, "Time:" + dias/horas
// restantes (006333c0: fim - hora do servidor em horas; sem prazo -> "No Limit"; <1h em vermelho).
static void DrawCaddieMascotRow983(FrGraphicInterface* pGI, FrListItem* pItem, int tab)
{
	if (pItem->pData == NULL)
		return;
	unsigned long tid = *(unsigned long*)((char*)pItem->pData + 4);
	const char* name = NULL;
	const char* icon = NULL;
	IFF_ITEM_COMMON* cm = NULL;
	if (tab == 0xb)
	{
		IFF_STRUCT::sCaddie* cd = ItemManager()->FindCaddie(tid);
		if (cd == NULL)
			return;
		name = cd->c.Name;
		icon = cd->c.Icon;
	}
	else
	{
		cm = ItemManager()->FindCommonItem(tid);
		if (cm == NULL)
			return;
		name = cm->Name;
		icon = cm->Icon;
	}
	const Bitmap* pIcon = g_pFresh->GetBitmap(icon);
	if (pIcon != NULL)
	{
		// 983: os casos 0xb (00616a6b) e 0xd (00616b20) saltam para o caminho comum 00617958 = aba Item: ponto = pos (cutin: y-12)
		// + ReviseItemIconPoint(tid), tamanho nativo; no mascote o tid vai sem o nibble baixo (tid&~0xf). Centrar em (41,52) punha o
		// icone do mascote 4-9 px abaixo do original (d271-1/013 x orig-c151-1/014).
		unsigned long rtid = (tab == 0xd && (tid & 0x3000000) != 0x3000000) ? (tid & 0xfffffff0) : tid;
		WPoint iconPt(pItem->pos.x, pItem->pos.y);
		if (S5::ISCutinItem(rtid))
			iconPt.y -= 12.0f;
		ReviseItemIconPoint(rtid, iconPt);
		WRect rect(iconPt.x, iconPt.y, (float)pIcon->Width(), (float)pIcon->Height());
		pGI->DrawTexture(pIcon, rect, 0xffffffff, 0);
	}
	// botao "Stats" da linha (state_view_n, ~60x16 em x+82,y+66 no original; C155.1/M3)
	const Bitmap* pStat = g_pFresh->GetBitmap("state_view_n");
	if (pStat != NULL)
	{
		WRect rcStat(pItem->pos.x + 80.0f, pItem->pos.y + 64.0f, (float)pStat->Width(), (float)pStat->Height());
		pGI->DrawTexture(pStat, rcStat, 0xffffffff, 0);
	}
	pGI->Print11(WPoint(pItem->pos.x + 182.0f, pItem->pos.y + 7.0f), 2, "%s", name);
	if (tab == 0xb)
	{
		// 006166b0 caso 7 (caddie sem aluguel): com parte (tidPart&0x1fff) escreve "Remaining Time:" e Remain_Partdate em dias/horas (C156.1)
		sCaddieInfo* ci = (sCaddieInfo*)pItem->pData;
		WPoint q1(pItem->pos.x + 182.0f, pItem->pos.y + 23.0f);
		WPoint q2(pItem->pos.x + 182.0f, pItem->pos.y + 39.0f);
		IFF_STRUCT::sCaddie* cdr = ItemManager()->FindCaddie(tid);
		if (ci->Rent_flag && cdr != NULL && cdr->MonthlyFee != 0)
		{
			// 006166b0 caso 7 aluguel: Remain_Date em dias; com parte, "Remaining Time" da parte em +16/+32 (C156.1)
			if (ci->Remain_Date == 0)
			{
				pGI->SetTextColor(0xffff0000, 0xffffffff);
				pGI->Print11(q1, 2, "%s", K2L_Compatibility("\xc8\xde\xb0\xa1\xc1\xdf"));
				return;
			}
			pGI->SetTextColor(0xff4d4d4d, 0xffffffff);
			pGI->Print11(q1, 2, "%s", K2L_Compatibility("\xb3\xb2\xc0\xba \xb0\xed\xbf\xeb\xb1\xe2\xb0\xa3:"));
			pGI->Print11(q2, 2, K2L_Compatibility("%d\xc0\xcf"), (int)ci->Remain_Date);
			if ((ci->tidPart & 0x1fff) != 0)
			{
				pGI->SetTextColor(0xff4d4d4d, 0xffffffff);
				pGI->Print11(WPoint(q2.x, q2.y + 16.0f), 2, "%s", K2L_Compatibility("\xb2\xd9\xb9\xcc\xb1\xe2 \xb3\xb2\xc0\xba \xb1\xe2\xb0\xa3:"));
				pGI->Print11(WPoint(q2.x, q2.y + 32.0f), 2, K2L_Compatibility("%d\xc0\xcf %d\xbd\xc3\xb0\xa3"), ci->Remain_Partdate / 24, ci->Remain_Partdate % 24);
			}
			return;
		}
		if ((ci->tidPart & 0x1fff) == 0)
			return;
		pGI->SetTextColor(0xff4d4d4d, 0xffffffff);
		pGI->Print11(WPoint(pItem->pos.x + 182.0f, pItem->pos.y + 23.0f), 2, "%s", K2L_Compatibility("\xb2\xd9\xb9\xcc\xb1\xe2 \xb3\xb2\xc0\xba \xb1\xe2\xb0\xa3:"));
		pGI->Print11(WPoint(pItem->pos.x + 182.0f, pItem->pos.y + 39.0f), 2, K2L_Compatibility("%d\xc0\xcf %d\xbd\xc3\xb0\xa3"), ci->Remain_Partdate / 24, ci->Remain_Partdate % 24);
		return;
	}
	bool timed = *((char*)cm + 0x82) == 1;
	int days = 0, hours = 0;
	if (timed)
	{
		sMascotInfo* mi = (sMascotInfo*)pItem->pData;
		// 00616b20: FUN_006333c0 = GetRemainHours983 (horas em SystemTimeToHours983, nao o FILETIME exato)
		__int64 h = DOCJP()->GetRemainHours983(&mi->endDate);
		if (h != 0)
		{
			days = (int)(h / 24);
			hours = (int)(h % 24);
		}
	}
	WPoint p1(pItem->pos.x + 182.0f, pItem->pos.y + 23.0f);
	WPoint p2(pItem->pos.x + 182.0f, pItem->pos.y + 39.0f);
	pGI->SetTextColor(0xff4d4d4d, 0xffffffff);
	pGI->Print11(p1, 2, "%s", K2L_Compatibility("\xb3\xb2\xc0\xba\xbd\xc3\xb0\xa3:"));
	if (!timed)
		pGI->Print11(p2, 2, "%s", K2L_Compatibility("\xb9\xab\xc1\xa6\xc7\xd1"));
	else if (days == 0 && hours == 0)
	{
		pGI->SetTextColor(0xffff0000, 0xffffffff);
		pGI->Print11(p2, 2, "%s", K2L_Compatibility("1\xbd\xc3\xb0\xa3\xb9\xcc\xb8\xb8"));
	}
	else
		pGI->Print11(p2, 2, K2L_Compatibility("%d\xc0\xcf %d\xbd\xc3\xb0\xa3"), days, hours);
}

char const* __fastcall MakeStatusString(int a, int b, int c); // 983 b2e010 (shopmain.h)

// 006166b0 (parcial, B410): a grade de itens do My Room. Fundo (item_base_n/d/empty), icone da FindCommonItem e nome.
// Faltam: icone UCC, grade/rental, botoes por aba, ItemBuff, caddie_no.
// 983 00615ab0 (UnequipItem): o item do slot volta a lista do inventario (se nao estiver la) e o slot e zerado
void CRealMyRoomForm983::UnequipItem983(unsigned long* slot)
{
	CSharedDoc* doc = Doc();
	FrListBox* itemBox = *(FrListBox**)((char*)this + 0x144);
	for (std::list<sItemInfo>::iterator it = doc->m_myItemList.begin(); it != doc->m_myItemList.end(); ++it)
	{
		if (it->typeId != *slot)
			continue;
		bool inList = false;
		for (FrListBox::ITEM_LIST::iterator li = itemBox->m_itemList.begin(); li != itemBox->m_itemList.end(); ++li)
		{
			sItemInfo* pi = (sItemInfo*)(*li)->pData;
			if (pi && pi->typeId == *slot)
			{
				inList = true;
				break;
			}
		}
		if (!inList)
		{
			itemBox->AddItem(&*it);
			itemBox->SortItem(EmptyCompares);
		}
	}
	*slot = 0;
}

// 983 0061a710 (OnItemSlotDClick): com NT_SC_ITEMSLOT ligado e +0xa84 == 0 (ou sem NT_SC_ITEMSLOT), desequipa o slot sob o cursor
void CRealMyRoomForm983::OnItemSlotDClick983()
{
	if (IsLocalContent(S4_NT_SC_ITEMSLOT) && *(char*)((char*)this + 0xa84))
		return;
	FrListBox* slotBox = *(FrListBox**)((char*)this + 0x190);
	if (!slotBox)
		return;
	FrListItem* item = slotBox->GetItemUnderCursor();
	if (!item || !item->pData || !*(unsigned long*)item->pData)
		return;
	UnequipItem983((unsigned long*)item->pData);
}

// 983 0061f6d0 CRealMyRoomMain::OnPetOwnerDraw: fora da aba principal 4 (e na sub-aba 0x20 dela) desenha a previa (0060d9b0).
// Portao 00e78ca8+0x240 (lobby travado): nao desenha nada. 00605e70 (UCC pronto: +0x228 -> +0x110) = sempre falso aqui (nao ha objeto UCC em +0x228).
void CRealMyRoomForm983::OnPetOwnerDraw983(int)
{
	if (CLobbyState983::ms_pInstance && *((char*)CLobbyState983::ms_pInstance + 0x240))
		return;
	// 0061f6d0: fora da aba 4, sub-aba 0x1c com card pack selecionado (tid&0x3c00000 == 0x1000000, cardCount < 10): mostra os dummies card_pack*_Dummy
	if (*(int*)((char*)this + 0x52c) != 4 && *(int*)((char*)this + 0x530) == 0x1c)
	{
		FrListBox* pack = *(FrListBox**)((char*)this + 0xab8);
		FrListItem* sel = pack ? pack->GetSelected() : NULL;
		sCards* pInfo = sel ? (sCards*)sel->pData : NULL;
		CExhibition* pv = *(CExhibition**)((char*)this + 0x584);
		if (pInfo && pv && (pInfo->tid & 0x3c00000) == 0x1000000 && pInfo->cardCount < 10)
		{
			WBone* pRoot = pv->GetModel()->GetRootBone();
			WBone* pBone = pRoot->FindBone("card_pack_Dummy", 0);
			if (pBone)
				pBone->SetInvisible(false, true);
			for (int i = 1; i < 10 - (int)pInfo->cardCount; i++)
			{
				pBone = pRoot->FindBone(MakeStr("card_pack%02d_Dummy", i), 0);
				if (pBone)
					pBone->SetInvisible(false, true);
			}
		}
	}
	if (*(int*)((char*)this + 0x52c) != 4 || *(int*)((char*)this + 0x530) == 0x20)
		MyRoomPetDraw983((char*)this);
	else if (*(int*)((char*)this + 0x530) == 0x22)
		DrawCutin983(); // 0061ee90
	else if (*(int*)((char*)this + 0x530) >= 0xe && *(int*)((char*)this + 0x530) <= 0x10)
		DrawSkinBack983(); // 0060da80
	else if (*(int*)((char*)this + 0x530) == 0x11 || *(int*)((char*)this + 0x530) == 0x23)
		DrawSkinSlot983(); // 0060de60
}

// 983 0060de60 (sub-abas 0x11/0x23 da aba 4): cartao do jogador em (116, 308) (origem; o 983 soma o deslocamento da view, 0 aqui):
// fundo, skin +0x970, personagem (+0x4f8) em (+8,+36) com a skin +0x974, bandeira de sexo (Doc+0x832 bit 3) em (+5,+98),
// nivel (skin +0x978 ou level_%03d do Doc+0x91d) centrado em (+90,+78), selo em (+63,+5) e o nome (Doc+0x7b8) em (139,415).
// Mesmo desenho do 645 DrawSkinSlot; os bitmaps +0x320..+0x32c do 983 sao os mesmos nomes (team_base/i_male/i_female/master_sign).
void CRealMyRoomForm983::DrawSkinSlot983()
{
	FrGraphicInterface* pGI = g_pFresh->GetManager()->GetGDI();
	if (!pGI)
		return;
	const float ox = 116.0f, oy = 308.0f;
	const Bitmap* pBase = g_pFresh->GetBitmap("team_base");
	if (!pBase)
		return;
	pGI->DrawTexture(pBase, WRect(ox, oy, (float)pBase->Width(), (float)pBase->Height()), 0xffffffff, 0);
	IFF_STRUCT::sSkin* pSkin;
	const Bitmap* pBitmap;
	unsigned long tid = *(unsigned long*)((char*)this + 0x970);
	if (tid && (pSkin = ItemManager()->FindSkin(tid)) != NULL && (pBitmap = g_pFresh->GetBitmap(pSkin->Tex)) != NULL)
		pGI->DrawTexture(pBitmap, WRect(ox, oy, (float)pBitmap->Width(), (float)pBitmap->Height()), 0xffffffff, 0);
	IFF_STRUCT::sChar* pChar = ItemManager()->FindChar(*(unsigned long*)((char*)this + 0x4f8));
	if (pChar && (pBitmap = g_pFresh->GetBitmap(pChar->Data)) != NULL)
		pGI->DrawTexture(pBitmap, WRect(ox + 8.0f, oy + 36.0f, (float)pBitmap->Width(), (float)pBitmap->Height()), 0xffffffff, 0);
	tid = *(unsigned long*)((char*)this + 0x974);
	if (tid && (pSkin = ItemManager()->FindSkin(tid)) != NULL && (pBitmap = g_pFresh->GetBitmap(pSkin->Tex)) != NULL)
		pGI->DrawTexture(pBitmap, WRect(ox + 8.0f, oy + 36.0f, (float)pBitmap->Width(), (float)pBitmap->Height()), 0xffffffff, 0);
	pBitmap = g_pFresh->GetBitmap((*((unsigned char*)Doc() + 0x832) >> 3) & 1 ? "i_female" : "i_male");
	if (pBitmap)
		pGI->DrawTexture(pBitmap, WRect(ox + 5.0f, oy + 98.0f, (float)pBitmap->Width(), (float)pBitmap->Height()), 0xffffffff, 0);
	tid = *(unsigned long*)((char*)this + 0x978);
	const char* pszIcon;
	if (tid == 0 || (pSkin = ItemManager()->FindSkin(tid)) == NULL)
		pszIcon = MakeStr("level_%03d", *((unsigned char*)Doc() + 0x91d) + 1);
	else
		pszIcon = pSkin->Tex;
	pBitmap = g_pFresh->GetBitmap(pszIcon);
	if (pBitmap)
		pGI->DrawTexture(pBitmap, WRect(ox + 90.0f - (int)(pBitmap->Width() * 0.5f), oy + 78.0f - (int)(pBitmap->Height() * 0.5f),
			(float)pBitmap->Width(), (float)pBitmap->Height()), 0xffffffff, 0);
	pBitmap = g_pFresh->GetBitmap("master_sign");
	if (pBitmap)
		pGI->DrawTexture(pBitmap, WRect((int)(ox + 63.5f - pBitmap->Width() * 0.5f), oy + 5.0f,
			(float)pBitmap->Width(), (float)pBitmap->Height()), 0xffffffff, 0);
	pGI->SetTextColor(0xffffffff, 0xff808080);
	pGI->SetTextStyle(2);
	g_pFresh->GetManager()->PrintText(WPoint(139.0f, 415.0f), 0, (char*)Doc() + 0x7b8, -1.0f, 0xffffffff);
}

// 983 0060da80 (sub-abas 0xe-0x10 da aba 4): fundo rolante da skin +0x964 ladrilhado na janela +0x150 (deslocamento +0x97c/+0x980),
// previa (Display) e as skins +0x968/+0x96c esticadas sobre a janela. Mesmo desenho do 645 DrawSkinFrame.
void CRealMyRoomForm983::DrawSkinBack983()
{
	FrGraphicInterface* pGI = g_pFresh->GetManager()->GetGDI();
	FrWnd* wnd = *(FrWnd**)((char*)this + 0x150);
	if (!pGI || !wnd)
		return;
	WRect area = wnd->GetRect();
	float* scroll = (float*)((char*)this + 0x97c);
	IFF_STRUCT::sSkin* pSkin;
	const Bitmap* pBitmap;
	unsigned long tid = *(unsigned long*)((char*)this + 0x964);
	if (tid && (pSkin = ItemManager()->FindSkin(tid)) != NULL && (pBitmap = g_pFresh->GetBitmap(pSkin->Tex)) != NULL)
	{
		float texW = (float)pBitmap->Width();
		float texH = (float)pBitmap->Height();
		for (int i = 0; i < 2; i++)
		{
			float t = i ? texH : texW;
			if (scroll[i] > t)
				scroll[i] -= t;
			else if (scroll[i] < 0.0f)
				scroll[i] += t;
		}
		float endX = area.x + area.w, endY = area.y + area.h;
		float dy = area.y;
		float sy = scroll[1];
		float h = texH - sy;
		while (dy < endY)
		{
			if (dy + h > endY)
				h = endY - dy;
			float dx = area.x;
			float sx = scroll[0];
			float w = texW - sx;
			while (dx < endX)
			{
				if (dx + w > endX)
					w = endX - dx;
				WRect src(sx, sy, w, h);
				WRect dst(dx, dy, w, h);
				pGI->DrawTexture(pBitmap, src, dst, 0xffffffff, 0);
				dx += w;
				sx = 0.0f;
				w = texW;
			}
			dy += h;
			sy = 0.0f;
			h = texH;
		}
	}
	MyRoomPetDraw983((char*)this);
	for (int off = 0x968; off <= 0x96c; off += 4)
	{
		tid = *(unsigned long*)((char*)this + off);
		if (tid && (pSkin = ItemManager()->FindSkin(tid)) != NULL && (pBitmap = g_pFresh->GetBitmap(pSkin->Tex)) != NULL)
			pGI->DrawTexture(pBitmap, area, 0xffffffff, 0);
	}
}

// 983 0061d180: imagem "<Tex>.jpg" da skin (tid), em cache por tid (std::map em +0x474; aqui um map estatico)
static std::map<unsigned long, WOverlay*> s_cutin983;

// 983 0061ee90 (sub-aba 0x22 da aba 4): Display da previa e, se ha item selecionado na lista (+0x144), a imagem da skin em (72, 67)
// (DAT_00d09468/00d14a2c = 72/67, como o 645 DrawCutinFrame). NAO portado: a fila +0x598/+0x59c e o deslocamento da view (009b7810).
void CRealMyRoomForm983::DrawCutin983()
{
	MyRoomPetDraw983((char*)this);
	FrListBox* box = *(FrListBox**)((char*)this + 0x144);
	FrListItem* sel = box ? box->GetSelected() : NULL;
	sItemInfo* info = sel ? (sItemInfo*)sel->pData : NULL;
	if (!info)
		return;
	WOverlay* img = NULL;
	std::map<unsigned long, WOverlay*>::iterator it = s_cutin983.find(info->typeId);
	if (it != s_cutin983.end())
		img = it->second;
	else if (IFF_STRUCT::sSkin* skin = ItemManager()->FindSkin(info->typeId))
	{
		char name[64];
		sprintf(name, "%s.jpg", skin->Tex);
		img = g_resrcmng->GetOverlay(name, 0);
		if (img)
			s_cutin983[info->typeId] = img;
	}
	if (!img)
		return;
	WRect dst(72.0f, 67.0f, (float)img->GetWidth(), (float)img->GetHeight());
	WRect src(0.0f, 0.0f, 1.0f, 1.0f);
	img->Render(g_view, src, dst, 0, 0xffffffff, 0, 0);
}

// 983 0060d0d0: fundo item_slot_n/o/d (normal/cursor/selecionado; vazio = normal) e, com o tid != 0, o icone em (x+2, y+4)
void CRealMyRoomForm983::OnItemSlotOwnerDraw983(int param)
{
	FrListItem* pItem = (FrListItem*)param;
	if (pItem == NULL || pItem->pData == NULL)
		return;
	FrGraphicInterface* pGI = g_pFresh->GetManager()->GetGDI();
	if (pGI == NULL)
		return;
	unsigned long tid = *(unsigned long*)pItem->pData;
	const char* bn = "item_slot_n";
	if (tid != 0)
	{
		if (pItem->selected)
			bn = "item_slot_d";
		else if (pItem->underCursor)
			bn = "item_slot_o";
	}
	const Bitmap* pSlot = g_pFresh->GetBitmap(bn);
	if (pSlot != NULL)
	{
		WRect rect(pItem->pos.x, pItem->pos.y, (float)pSlot->Width(), (float)pSlot->Height());
		pGI->DrawTexture(pSlot, rect, 0xffffffff, 0);
	}
	if (tid == 0)
		return;
	IFF_ITEM_COMMON* pCommon = ItemManager()->FindCommonItem(tid);
	if (pCommon == NULL)
		return;
	const Bitmap* pIcon = g_pFresh->GetBitmap(pCommon->Icon);
	if (pIcon != NULL)
	{
		WRect rect(pItem->pos.x + 2.0f, pItem->pos.y + 4.0f, (float)pIcon->Width(), (float)pIcon->Height());
		pGI->DrawTexture(pIcon, rect, 0xffffffff, 0);
	}
}

void CRealMyRoomForm983::OnItemListOwnerDraw983(int param)
{
	FrListItem* pItem = (FrListItem*)param;
	if (pItem == NULL)
		return;
	FrGraphicInterface* pGI = g_pFresh->GetManager()->GetGDI();
	if (pGI == NULL)
		return;
	const Bitmap* pBack;
	if (pItem->pData == NULL)
		pBack = g_pFresh->GetBitmap("item_base_empty");
	else
	{
		unsigned long color = 0xff000000;
		const char* bn = "item_base_n";
		if (pItem->selected)
		{
			color = 0xffff0000;
			bn = "item_base_d";
		}
		else if (pItem->underCursor)
			bn = "item_base_o";
		pBack = g_pFresh->GetBitmap(bn);
		pGI->SetTextColor(color, 0xffffffff);
	}
	pGI->SetTextStyle(0);
	if (pBack != NULL)
	{
		WRect rect(pItem->pos.x, pItem->pos.y, (float)pBack->Width(), (float)pBack->Height());
		pGI->DrawTexture(pBack, rect, 0xffffffff, 0);
	}
	int curTab = *(int*)((char*)this + 0x530);
	if (curTab == 0xb || curTab == 0xd)
	{
		DrawCaddieMascotRow983(pGI, pItem, curTab);
		return;
	}
	sItemInfo* pInfo = (sItemInfo*)pItem->pData;
	if (pInfo == NULL)
		return;
	IFF_ITEM_COMMON* pCommon = ItemManager()->FindCommonItem(pInfo->typeId);
	if (pCommon == NULL)
		return;
	const Bitmap* pIcon = g_pFresh->GetBitmap(pCommon->Icon);
	if (pIcon != NULL)
	{
		// 983 (00617a1b): ponto do icone = pos (cutin: y-12) + ReviseItemIconPoint(typeId)
		WPoint iconPt(pItem->pos.x, pItem->pos.y);
		if (S5::ISCutinItem(pInfo->typeId))
			iconPt.y -= 12.0f;
		ReviseItemIconPoint(pInfo->typeId, iconPt);
		WRect rect(iconPt.x, iconPt.y, (float)pIcon->Width(), (float)pIcon->Height());
		pGI->DrawTexture(pIcon, rect, 0xffffffff, 0);
	}
	pGI->Print11(WPoint(pItem->pos.x + 182.0f, pItem->pos.y + 7.0f), 2, "%s", pCommon->Name);
	// 983 (006196fe/0061977c, caso 6 = itens ativos/passivos): "%d<gae>" (DAT_00d144c0) em (x+182, y+23) com a quantidade (Common[0], +0xc)
	// 00619cc6: tid 0x1a000006 (Lucky Necklace) nao mostra quantidade; 0x1a000010 (Pang) mostra "%d<pa>" (DAT_00d14818)
	if ((pInfo->typeId >> 26) == 6 && (curTab == 9 || curTab == 10) && pInfo->typeId != 0x1a000006)
	{
		if (pInfo->typeId == 0x1a000010)
			pGI->Print11(WPoint(pItem->pos.x + 182.0f, pItem->pos.y + 23.0f), 2, K2L_Compatibility("%d\xc6\xce"), (int)pInfo->Common[0]);
		else
			pGI->Print11(WPoint(pItem->pos.x + 182.0f, pItem->pos.y + 23.0f), 2, K2L_Compatibility("%d\xb0\xb3"), (int)pInfo->Common[0]);
	}
	// 983 (006191f2 case 5, D407): bola mostra a quantidade em (x+182, y+23), exceto a bola padrao/sem bound+COM (00a18f90) e,
	// com bit 0xe de doc+0x812, a 0x140000d8
	if ((pInfo->typeId >> 26) == 5)
	{
		bool plain = false;
		if (pInfo->typeId == 0x14000000)
			plain = true;
		else if (IFF_STRUCT::sBall* pBall = ItemManager()->FindBall(pInfo->typeId))
			plain = *(int*)((char*)pBall + 0x74) == 0 && *(short*)((char*)pBall + 0x324) == 0;
		CSharedDoc* doc983 = CSharedDoc::Instance();
		bool hideD8 = pInfo->typeId == 0x140000d8 && doc983 && (*(unsigned long*)((char*)doc983 + 0x812) >> 0xe & 1) != 0;
		if (!plain && !hideD8)
			pGI->Print11(WPoint(pItem->pos.x + 182.0f, pItem->pos.y + 23.0f), 2, K2L_Compatibility("%d\xb0\xb3"), (int)pInfo->Common[0]);
	}
	// 983 (006181ac..0061895c, aba 9 = Active): botao equip_btn_n em (x+103,y+66) e, se o item pode ser apagado (!(Common+0x80 & 1)),
	// delete_btn_n em (x+144,y+66) (bitmaps/retangulos criados em 00608801..00608909)
	if (curTab == 9)
	{
		const Bitmap* pEquip = g_pFresh->GetBitmap("equip_btn_n");
		if (pEquip != NULL)
		{
			WRect rcEquip(pItem->pos.x + 103.0f, pItem->pos.y + 66.0f, (float)pEquip->Width(), (float)pEquip->Height());
			pGI->DrawTexture(pEquip, rcEquip, 0xffffffff, 0);
		}
		const Bitmap* pDel = g_pFresh->GetBitmap("delete_btn_n");
		if (pDel != NULL && !(*((unsigned char*)pCommon + 0x80) & 1))
		{
			WRect rcDel(pItem->pos.x + 144.0f, pItem->pos.y + 66.0f, (float)pDel->Width(), (float)pDel->Height());
			pGI->DrawTexture(pDel, rcDel, 0xffffffff, 0);
		}
	}
	// 983 (0061a2ab, caso 4 = taco): "Cost of Upgrades:" (verde) em (x+182, y+23) e "%d Pang" em +16; soma de ReqdPang dos Enchant (D267)
	if ((pInfo->typeId >> 26) == 4)
	{
		int total = 0;
		if (curTab != 0x12)
			for (int stat = 0; stat < 5; ++stat)
				for (int n = 0; n < pInfo->Common[stat]; ++n)
				{
					IFF_STRUCT::sEnchant* pEnchant = ItemManager()->FindEnchant(((stat | 0x340) << 20) | n);
					if (pEnchant != NULL)
						total += pEnchant->ReqdPang;
				}
		pGI->SetTextColor(0xff009000, 0xffffffff);
		pGI->Print11(WPoint(pItem->pos.x + 182.0f, pItem->pos.y + 23.0f), 2, "%s", K2L_Compatibility("\xbe\xf7\xb1\xd7\xb7\xb9\xc0\xcc\xb5\xe5\xc7\xd1 \xba\xf1\xbf\xeb:"));
		pGI->Print11(WPoint(pItem->pos.x + 182.0f, pItem->pos.y + 39.0f), 2, K2L_Compatibility("%d\xc6\xce"), total);
		// botao "Stats" do taco (state_view_n em x+80,y+64 como o do caddie; D272)
		const Bitmap* pStat = g_pFresh->GetBitmap("state_view_n");
		if (pStat != NULL)
		{
			WRect rcStat(pItem->pos.x + 80.0f, pItem->pos.y + 64.0f, (float)pStat->Width(), (float)pStat->Height());
			pGI->DrawTexture(pStat, rcStat, 0xffffffff, 0);
		}
		// 006166b0 caso 4 (0061a14f): icone de oficina (clubmade_icon_make) em (x+155, y+53) se o taco mudou de passo/grau (C192.1)
		if (curTab != 0x12 && (IsClubStepChanged983(pInfo->id) || IsClubGradeChanged983(pInfo->id)))
		{
			const Bitmap* pMade = g_pFresh->GetBitmap("clubmade_icon_make");
			if (pMade != NULL)
			{
				WRect rcMade(pItem->pos.x + 155.0f, pItem->pos.y + 53.0f, (float)pMade->Width(), (float)pMade->Height());
				pGI->DrawTexture(pMade, rcMade, 0xffffffff, 0);
			}
		}
	}
	// 983 (006191f2 case 2 -> 00604d10): partes mostram as linhas de bonus ("Spin+1/Slot+1"), azul, passo 14 a partir de y+36
	if ((pInfo->typeId >> 26) == 2)
	{
		IFF_STRUCT::sPart* pPart = ItemManager()->FindPart(pInfo->typeId);
		if (pPart != NULL)
		{
			float dy = 0.0f;
			for (int i = 0; i < 5; ++i)
			{
				if (pPart->Attr[i] == 0 && pPart->Slot[i] == 0)
					continue;
				pGI->SetTextColor(0xff0000ff, 0xffffffff);
				pGI->Print11(WPoint(pItem->pos.x + 182.0f, pItem->pos.y + 36.0f + dy), 2, "%s", MakeStatusString(i, pPart->Attr[i], pPart->Slot[i]));
				dy += 14.0f;
			}
		}
	}
}

// 00605720 (+007f6d20/00befe70): mostra/esconde o Card Holic (CCardBook em +0xa78 e a lista cardpacklist em +0xab8)
// 006208f0 (+0060a390/00605a50, 00605b60, 0061ee10): modo da janela em +0xa3c (1 = normal, 2, 4 = bit 8); +0xa40 guarda o anterior
void CRealMyRoomForm983::SetViewMode983(int mode)
{
	char* self = (char*)this;
	for (;;)
	{
		int& cur = *(int*)(self + 0xa3c);
		if (mode != cur && mode != 5)
			*(int*)(self + 0xa40) = cur;
		if (mode == 5) { mode = 2; continue; }
		if (mode != 1 && mode != 2 && mode != 4)
		{
			cur = mode;
			return;
		}
		unsigned bit = mode == 4 ? 8 : mode;
		cur = (cur & bit) ? (cur & ~bit) : (cur | bit); // 0060a390
		*(unsigned*)(self + 0xa44) = 0; // 00605a50
		self[0xa48] = 0;
		if (bit == 1) self[0xa44] = 1;
		else if (bit == 2) self[0xa45] = !self[0xa45];
		else if (bit == 4) { self[0xa46] = !self[0xa46]; self[0xa44] = self[0xa45] = self[0xa46]; }
		else if (bit == 8) self[0xa47] = !self[0xa47];
		self[0xa35] = (mode == 1);
		bool on = mode == 1;
		FrWnd* mid = *(FrWnd**)(self + 0x128);
		FrWnd* menu = *(FrWnd**)(self + 0x248);
		if (on)
		{
			if (mid) mid->SetElementFadeOut(false);
			SetMainTab983(*(int*)(self + 0x52c), true);
			if (menu) menu->SetVisible(true);
		}
		else
		{
			if (mid && (*(unsigned char*)((char*)mid + 0x44) & 1)) mid->SetElementFadeOut(true);
			if (menu) menu->SetVisible(false);
		}
		bool showTab = (mode == 4);
		if (FrWnd* f = *(FrWnd**)(self + 0x1c8)) f->SetVisible(showTab); // 00605b60
		if (FrWnd* f = *(FrWnd**)(self + 0x1c4)) f->SetElementFadeOut(!showTab);
		if (FrTabButton* t = (FrTabButton*)*(FrWnd**)(self + 0x134)) t->Select(*(unsigned long*)(self + 0x554));
		cur = mode;
		return;
	}
}

// 00622630 casos 0 e 2 (8 = aviso notify so sem flag a47, sem chamador direto: nao portado) (so o ramo sem PC bang importa: flags +0xa44.. por modo)
void CRealMyRoomForm983::SelectMenu983(int menu)
{
	char* self = (char*)this;
	if (menu == 6)
	{
		// 00622730: abre "realmyroom_authority" (+0x244) modal 0x81, sem fade
		if (*(FrForm**)(self + 0x244) == NULL)
		{
			CRealMyRoom_AuthorityDlg* dlg = CreateForm<CRealMyRoom_AuthorityDlg>(g_pFresh->GetManager(), this, "realmyroom_authority", NULL);
			*(FrForm**)(self + 0x244) = dlg;
			FrForm::ms_bHasTail = false;
			dlg->Open((FRESH_PFN_RESULT)&CRealMyRoomForm983::OnAuthDlgResult983, 0x81);
			dlg->SetFadeout(false);
		}
		return;
	}
	if (menu == 9)
	{
		// 00622795 (so com NT REAL_MYROOM)
		if (!IsLocalContent(S4_REAL_MYROOM))
			return;
		if (self[0xa84] == 0)
		{
			WSendPacket p((enumClientPacket)0xd3);
			p.Send(TO_GAME);
			SendDocSyncPackets983(Doc());
		}
		else
			AfxGetTask()->SendMsgToMainActor(MsgObject(NULL, 0x2af, 0, 0, 0, 0, 0));
		return;
	}
	if (menu == 2)
	{
		// 006226c0: modo 2 (flag a47 = 00605af0(8)) ou 4; Card Holic some; aba +0x554 = 0
		SetViewMode983(self[0xa47] ? 2 : 4);
		ShowCardHolic983(false);
		*(unsigned long*)(self + 0x554) = 0;
		return;
	}
	if (menu != 0)
		return;
	if (self[0xa44]) // 00605af0(1)
	{
		SetViewMode983(2);
		ShowCardHolic983(false);
		return;
	}
	SetViewMode983(1);
	if (self[0xa74] == 1)
		ShowCardHolic983(true);
}

void CRealMyRoomForm983::ShowCardHolic983(bool show)
{
	CCardBook* book = CardBook983();
	if (book)
	{
		book->Show(show);
		if (show)
			for (int i = 3; i < 7; ++i)
				if (book->m_pTabButton[i])
					book->m_pTabButton[i]->SetVisible(true);
	}
	// C187.1: caderno (espiral/papel/"Pangya. Card Book"): card_book_back_bg, escondido no init (B411), so com o Card Holic aberto
	{
		FrWnd* back = FindChildByName("card_book_back_bg");
		if (back)
			back->SetVisible(show);
	}
	FrListBox* pack = *(FrListBox**)((char*)this + 0xab8);
	if (pack)
	{
		pack->SetVisible(show);
		if (show)
			BuildCardPackList983();
	}
}

// aba Pack: cartas/pacotes do doc (tipos 3 e 4), completando ate 6 casas (645 BuildCardPackList)
void CRealMyRoomForm983::BuildCardPackList983()
{
	FrListBox* pack = *(FrListBox**)((char*)this + 0xab8);
	if (!pack)
		return;
	pack->ClearItem();
	std::list<sCards>& cards = Doc()->m_cardList;
	for (std::list<sCards>::iterator it = cards.begin(); it != cards.end(); ++it)
	{
		unsigned int type = (it->tid >> 22) & 0xf;
		if (type == 4 || type == 3)
			pack->AddItem(&(*it));
	}
	if (cards.size() & 1)
		pack->AddItem(NULL);
	for (int n = pack->GetCurrentItemSize(true); n < 6; ++n)
		pack->AddItem(NULL);
	pack->UseRightButton(true);
	pack->UseDummy(true);
}

void CRealMyRoomForm983::OnCardTabDown983(int tab)
{
	CCardBook* book = CardBook983();
	if (book)
	{
		book->ButtonTabControl((unsigned char)tab);
		book->ShowSlotControl(true);
	}
	FrListBox* pack = *(FrListBox**)((char*)this + 0xab8);
	if (pack)
	{
		pack->SetVisible(tab == 0);
		if (tab == 0)
			pack->UnselectAllItem();
	}
	if (tab != 0)
		MyRoomPetClear983((char*)this); // 00605810..00605950: 00605530(0)
}

// cardpacklist OWNERDRAW (645 OnCardPackListDraw, mesmos bitmaps do item_list)
void CRealMyRoomForm983::OnCardPackListDraw983(int param)
{
	FrListBox* pack = *(FrListBox**)((char*)this + 0xab8);
	if (!pack || !param)
		return;
	FrGraphicInterface* pGI = g_pFresh->GetManager()->GetGDI();
	FrListItem* pItem = (FrListItem*)param;
	pGI->SetTextStyle(0);
	const char* bn;
	if (!pItem->pData)
		bn = "item_base_empty";
	else if (pItem->selected)
	{
		bn = "item_base_d";
		pGI->SetTextColor(0xffff0000, 0xffffffff);
	}
	else
	{
		pGI->SetTextColor(0xff000000, 0xffffffff);
		bn = pItem->underCursor ? "item_base_o" : "item_base_n";
	}
	const Bitmap* pBitmap = g_pFresh->GetBitmap(bn);
	if (pBitmap)
	{
		WRect dst(pItem->pos.x, pItem->pos.y, (float)pack->GetItemWidth(), (float)pack->GetItemHeight());
		// 0060ff10: src = bitmap inteiro (Width/Height do Bitmap), esticado na casa -> margem entre as casas como no 983 (foto 45)
		WRect src(0.0f, 0.0f, (float)(unsigned)pBitmap->Width(), (float)(unsigned)pBitmap->Height());
		pGI->DrawTexture(pBitmap, src, dst, 0xffffffff, 0);
	}
	sCards* pCard = (sCards*)pItem->pData;
	if (!pCard)
		return;
	const char* name = K2L_Compatibility("\xbe\xcb \xbc\xf6 \xbe\xf8\xb4\xc2 \xbe\xc6\xc0\xcc\xc5\xdb");
	const char* icon = "caddie_no";
	IFF_STRUCT::sCard* pInfo = ItemManager()->FindCard(pCard->tid);
	if (pInfo)
	{
		icon = pInfo->c.Icon;
		name = pInfo->c.Name;
	}
	pBitmap = g_pFresh->GetBitmap(icon);
	float w = (float)pack->GetItemWidth();
	if (pBitmap)
	{
		WRect rect(pItem->pos.x + 12.0f, pItem->pos.y + 12.0f, (float)pBitmap->Width(), (float)pBitmap->Height());
		pGI->DrawTexture(pBitmap, rect, 0xffffffff, 0);
	}
	WPoint pt(w - 12.0f + pItem->pos.x, pItem->pos.y + 12.0f);
	pGI->Print11(pt, 2, "%s", name);
	int h = pGI->GetFontHeight11();
	pt = WPoint(w - 12.0f + pItem->pos.x, (float)h + 17.0f + pItem->pos.y);
	if ((pCard->tid & 0x3c00000) == 0x1000000)
		pGI->Print11(pt, 2, K2L_Compatibility("\xb3\xb2\xc0\xba \xc4\xab\xb5\xe5 \xc6\xd1 %d\xb0\xb3"), (int)pCard->cardCount);
	else
		pGI->Print11(pt, 2, K2L_Compatibility("%d\xb0\xb3"), (int)pCard->cardCount);
	if (CardBook983() && pItem == pack->GetSelected())
		CardBook983()->DrawCardPackHelp(pCard->tid);
}

// 0061f8b0 (equipar) / 0061dfb0 (tirar), casos 2-4 e 0x1b: manda 0x18a ao "LobbyAvatar" (lista do doc, &tid, &uid, &ret, &equip);
// com sucesso grava as pecas no personagem da conta e em +0x490/+0x494. NAO portados: mensagens de erro (CanSetPart/nivel/aluguel),
// 00613520 (pecas tiradas por sobreposicao) e o ramo do pet frame (+0x584, so quando DAT_00e78cac != 0).
void CRealMyRoomForm983::ItemEquip983(FrListBox* box, FrListItem* item, bool equip)
{
	char* self = (char*)this;
	CSharedDoc* doc = Doc();
	CPartTidList* list = &doc->m_partTidList;
	sItemInfo* info = (sItemInfo*)item->pData;
	if (!info)
		return;
	if (*(int*)((char*)this + 0x530) == 0x22)
	{
		// 0061f8b0/0061dfb0 caso 0x22: equipar = 0063f4b0 (liga +0x124 se mudou), tirar = 0063f620; depois limpa a selecao (00befe70)
		// e remarca os cut-ins equipados (0063f450)
		g_audio->PlaySfx("ui_desktop_icon_click");
		bool ok = equip ? CutinEquip983(doc, info->id, info->typeId) : CutinUnequip983(doc, info->id);
		if (ok)
			*(char*)((char*)this + 0x124) = 1;
		HideAllChildren983(box);
		for (FrListBox::ITEM_LIST::iterator li = box->m_itemList.begin(); li != box->m_itemList.end(); ++li)
			if ((*li)->pData && CutinEquipped983(doc, ((sItemInfo*)(*li)->pData)->id))
				box->SelectItem(*li, false);
		if (CutinEquipped983(doc, info->id))
			box->SelectItem(item, true);
		return;
	}
	if (equip)
	{
		if (!list->CanSetPart(info->typeId))
		{
			jp983_rastro("A294 equip CanSetPart=0 tid=%08x", info->typeId);
			box->SelectItem(item, false);
			return;
		}
		g_audio->PlaySfx("item_select_cloth");
		unsigned long mask = list->GetOverlapped(info->typeId);
		if (mask)
		{
			for (FrListBox::ITEM_LIST::iterator li = box->m_itemList.begin(); li != box->m_itemList.end(); ++li)
			{
				sItemInfo* o = (sItemInfo*)(*li)->pData;
				if (o && (*li)->selected && *li != item && list->IsEquipped(o->typeId, o->id) && (mask & list->GetOverlapped(o->typeId)))
				{
					box->SelectItem(*li, false);
					ItemEquip983(box, *li, false);
				}
			}
		}
	}
	else if (!list->IsEquipped(info->typeId, info->id))
	{
		box->SelectItem(item, true);
		return;
	}
	int ret = 0;
	bool bEquip = equip;
	CExhibition* pv = *(CExhibition**)(self + 0x584);
	if (g_lobbyModal983)
	{
		// My Room (00e78cac != 0): o 983 nao manda a 0x18a; troca as pecas no frame da previa (+0x584) e refresca (0061a810)
		if (pv && pv->GetPetFrame())
		{
			ret = MyRoomPetFrameSetParts983(pv->GetPetFrame(), list, info->typeId, info->id);
			pv->GetPetFrame()->Refresh(list); // 008b1030
		}
	}
	else
		AfxGetTask()->GetActor("LobbyAvatar") << MsgObject(NULL, 0x18a, (int)list, (int)&info->typeId, (int)&info->id, (int)&ret, (int)&bEquip);
	jp983_rastro("D296 equip 0x18a tid=%08x equip=%d ret=%d modal=%d pet584=%08x", info->typeId, (int)equip, ret, g_lobbyModal983, *(unsigned int*)((char*)this + 0x584));
	if (ret)
	{
		std::map<unsigned int, sCharacterInfo>::iterator ci = doc->m_charMap.find(doc->m_myInfo.userEquip.guidChar);
		if (ci != doc->m_charMap.end())
			for (int j = 0; j < list->m_partNum && j < 24; ++j)
			{
				ci->second.tidParts[j] = list->m_tid[j];
				ci->second.ItemIdList[j] = list->m_uid[j];
			}
		*(unsigned long**)(self + 0x490) = list->m_tid;
	}
	memcpy(self + 0x494, list->m_uid, 24 * sizeof(unsigned long));
	// C231.1: trocar a peca (chapeu) deixava as duas vermelhas; a marca da lista segue o que esta equipado (IsEquipped)
	for (FrListBox::ITEM_LIST::iterator li = box->m_itemList.begin(); li != box->m_itemList.end(); ++li)
	{
		sItemInfo* o = (sItemInfo*)(*li)->pData;
		if (!o)
			continue;
		bool want = list->IsEquipped(o->typeId, o->id);
		if (((*li)->selected != 0) != want)
			box->SelectItem(*li, want);
	}
	UpdateStats983(self);
}

// 00613d50 (aba Active, equipar): poe o tid na 1a casa livre dos slots doc+0xa36 (n = 8 + casas do mascote [+ cartas]; 10 sem
// NT_SC_ITEMSLOT); 1800002d/2f nao repetem (msg 0x23); se todas as copias ja estao nos slots, o item sai da lista. Sem pacote (o 0x20/2 sai no fechar).
// NAO portado: fechar o pet frame (+0x584, 00605530).
void CRealMyRoomForm983::EquipActiveItem983(sItemInfo* info)
{
	CSharedDoc* doc = Doc();
	unsigned long* slots = (unsigned long*)((char*)doc + 0xa36);
	int n = 10;
	if (IsLocalContent(S4_NT_SC_ITEMSLOT))
		n = doc->GetNumAddItemSlotByMascot() + 8;
	if (IsLocalContent(S4_CARD_SYSTEM))
	{
		CCardManager::Instance()->SetPlayerIndex(0xff);
		CCardManager::Instance()->CalcCardPeriodAndStatus();
		int ps = CCardManager::Instance()->GetCardPeriodSlot();
		if (ps < 1)
		{
			if (doc->GetNumAddItemSlotByMascot() == 1)
				slots[4] = 0;
			else
				slots[3] = slots[4] = 0;
		}
		else
			n += ps;
	}
	int i = 0;
	while (i < n && i < 10 && slots[i] != 0)
		++i;
	if (i >= n || i >= 10)
	{
		// 613e15: slots cheios -> aviso 0x23 ao ator principal (texto 00d1462c)
		AfxGetTask()->SendMsgToMainActor(MsgObject(NULL, 0x23, (int)K2L_Compatibility("\xb4\xf5 \xc0\xcc\xbb\xf3 \xc0\xe5\xc2\xf8\xc7\xd2 \xbc\xf6 \xbe\xf8\xbd\xc0\xb4\xcf\xb4\xd9"), 0, 0, 0, 0));
		return;
	}
	if (info->typeId == 0x1800002d || info->typeId == 0x1800002f)
		for (int k = 0; k < 10; ++k)
			if (slots[k] == info->typeId)
				return;
	slots[i] = info->typeId;
	int used = 0;
	for (int k = 0; k < 10; ++k)
		if (slots[k] == info->typeId)
			++used;
	if (info->Common[0] <= used)
	{
		FrListBox* box = *(FrListBox**)((char*)this + 0x144);
		for (FrListBox::ITEM_LIST::iterator li = box->m_itemList.begin(); li != box->m_itemList.end(); ++li)
			if ((*li)->pData == info)
			{
				box->_DelItem(li);
				break;
			}
	}
}

// item_list DBLCLICK (00614be0): na aba Active (sub 9) equipa o item sob o cursor
void CRealMyRoomForm983::OnItemListDClick983()
{
	if (*(int*)((char*)this + 0x530) != 9)
		return;
	FrListBox* box = *(FrListBox**)((char*)this + 0x144);
	FrListItem* item = box ? box->GetItemUnderCursor() : NULL;
	if (item && item->pData)
		EquipActiveItem983((sItemInfo*)item->pData);
}

static unsigned long s_fortuneTid983;
// 00aa85e0: tipos de caixa abriveis pelo botao direito (230 tids)
static bool IsFortuneBox983(unsigned long tid)
{
	static const unsigned long k[] = { 0x1a000004,0x1a00001b,0x1a000039,0x1a00004d,0x1a000054,0x1a0000b5,0x1a0000bb,0x1a0000d4,0x1a0000d5,0x1a0000e5,0x1a0000e6,0x1a0000ec,0x1a0000fd,0x1a00010f,0x1a000116,0x1a000118,0x1a000138,0x1a00013e,0x1a00013f,0x1a000148,0x1a000149,0x1a00014c,0x1a000165,0x1a00016a,0x1a000185,0x1a00018a,0x1a00018b,0x1a00018c,0x1a000195,0x1a000196,0x1a000197,0x1a000198,0x1a000199,0x1a00019a,0x1a00019b,0x1a00019c,0x1a00019d,0x1a00019e,0x1a0001a2,0x1a0001cf,0x1a0001d6,0x1a000212,0x1a00021d,0x1a00021e,0x1a00021f,0x1a000220,0x1a00023c,0x1a000240,0x1a000242,0x1a000248,0x1a000249,0x1a00024a,0x1a000263,0x1a000271,0x1a00027b,0x1a00027c,0x1a00027d,0x1a00027e,0x1a00028d,0x1a000294,0x1a00029c,0x1a00029d,0x1a0002a1,0x1a0002a3,0x1a0002a5,0x1a0002aa,0x1a0002b4,0x1a0002cc,0x1a0002cd,0x1a0002ce,0x1a0002cf,0x1a0002d0,0x1a0002d1,0x1a0002d2,0x1a0002d3,0x1a0002d4,0x1a0002d5,0x1a0002d6,0x1a0002d8,0x1a0002da,0x1a0002db,0x1a0002dc,0x1a0002dd,0x1a0002de,0x1a0002df,0x1a0002e0,0x1a0002e1,0x1a0002e2,0x1a0002e3,0x1a0002e4,0x1a0002e5,0x1a0002ee,0x1a0002ef,0x1a0002fa,0x1a0002fb,0x1a0002fc,0x1a000309,0x1a00030b,0x1a00030d,0x1a00030e,0x1a00030f,0x1a000310,0x1a000311,0x1a000312,0x1a000313,0x1a000317,0x1a000318,0x1a00031b,0x1a00031c,0x1a00031d,0x1a00031e,0x1a00031f,0x1a000320,0x1a00032d,0x1a00032e,0x1a00032f,0x1a000330,0x1a000331,0x1a000332,0x1a000333,0x1a000334,0x1a000335,0x1a000336,0x1a000337,0x1a000339,0x1a00033a,0x1a00033b,0x1a00033c,0x1a00033d,0x1a00033e,0x1a00033f,0x1a000340,0x1a000341,0x1a000342,0x1a000343,0x1a000349,0x1a00034c,0x1a00034d,0x1a00034f,0x1a000350,0x1a000351,0x1a000355,0x1a000356,0x1a00035a,0x1a00035c,0x1a00035d,0x1a00035e,0x1a00035f,0x1a000360,0x1a000361,0x1a000363,0x1a000364,0x1a000366,0x1a000367,0x1a000369,0x1a00036a,0x1a00036b,0x1a00036e,0x1a00036f,0x1a000370,0x1a000371,0x1a000372,0x1a000373,0x1a000374,0x1a000375,0x1a000376,0x1a000377,0x1a000378,0x1a000379,0x1a00037a,0x1a00037b,0x1a00037c,0x1a00037d,0x1a00037e,0x1a00037f,0x1a000380,0x1a000381,0x1a000382,0x1a000383,0x1a000384,0x1a000385,0x1a000386,0x1a000387,0x1a000388,0x1a000389,0x1a00038a,0x1a00038c,0x1a00038d,0x1a00038f,0x1a000391,0x1a000397,0x1a000398,0x1a00039c,0x1a00039d,0x1a0003a2,0x1a0003a3,0x1a0003a5,0x1a0003a6,0x1a0003b5,0x1a0003b8,0x1a0003ba,0x1a0003bb,0x1a0003bc,0x1a0003bd,0x1a0003be,0x1a0003c0,0x1a0003c3,0x1a0003c4,0x1a0003c5,0x1a0003c6,0x1a0003c7,0x1a0003c8,0x1a0003c9,0x1a0003ca,0x1a0003cb,0x1a0003cc,0x1a0003cd,0x1a0003ce,0x1a0003cf,0x1a0003d0,0x1a0003d1,0x1a0003d2,0x1a0003d3,0x1a0003d4,0x1a0003d5,0x1a0003d6,0x1a0003d7,0x1a0003d8,0x1a0003d9,0x1a0003da };
	for (size_t i = 0; i < sizeof(k) / sizeof(k[0]); ++i)
		if (k[i] == tid)
			return true;
	return false;
}

// item_list LBUTTONDOWN (620e00, so abas de roupa 2-4/0x1b): o FrListBox ja alternou a selecao; selecionado = equipa, senao tira
// 00622330 (parcial, D290): botao direito na grade abre a janela "information" do item sob o cursor (caso padrao do
// 0061a8a0). B846: porta a selecao (00befeb0), abas 0x17/0x22, UCC e o 61f8b0 (via OnItemListDown983).
void CRealMyRoomForm983::OnItemListRDown983()
{
	char* self = (char*)this;
	FrListBox* box = *(FrListBox**)(self + 0x144);
	FrListItem* it = box ? box->GetItemUnderCursor() : NULL;
	if (!it || !it->pData)
		return;
	int sub = *(int*)(self + 0x530);
	// 00622330: (004d5200 = CAnotherHand::IsWorking nao existe aqui, previa sincrona.) Com +0xa84, na aba 0x20 ou nas abas 2-5/0x16/0x1b
	// com item de periodo (ItemType 6) vencido: alterna a selecao (00befeb0) e abre a janela de informacao, sem equipar
	bool onlyInfo = *(char*)(self + 0xa84) != 0 || sub == 0x20;
	if (sub == 2 || sub == 3 || sub == 4 || sub == 5 || sub == 0x16 || sub == 0x1b)
	{
		sItemInfo* flag = (sItemInfo*)it->pData;
		if (flag->ItemType == 6 && flag->Expired)
			onlyInfo = true;
	}
	if (onlyInfo)
	{
		box->ToggleItem(it);
		OpenInformation983(it);
		return;
	}
	// 00622330, sub 10 (Passive/Item): caixa (00aa85e0) abre "fortune_new" ("Do you want open it?"); o resultado 1 manda 0xb2 (0060fa40)
	if (sub == 10 && IsFortuneBox983(((sItemInfo*)it->pData)->typeId))
	{
		FrFortuneDlg*& dlg = *(FrFortuneDlg**)(self + 0x20c);
		if (!dlg)
			dlg = CreateForm<FrFortuneDlg>(g_pFresh->GetManager(), this, "fortune_new", NULL);
		if (!dlg)
			return;
		s_fortuneTid983 = ((sItemInfo*)it->pData)->typeId;
		// 00aa78a0/00aa7860: ret=portrait(+0x110)->SetBgImg(FindCommonItem(tid)->Icon); FrFortuneDlg liga "fortune_img"
		IFF_ITEM_COMMON* fcommon = ItemManager()->FindCommonItem(s_fortuneTid983);
		if (fcommon)
			dlg->SetIcon983(fcommon->Icon);
		IFF_STRUCT::sDesc* desc = ItemManager()->FindDesc(s_fortuneTid983);
		dlg->SetMessage(desc ? desc->Desc : "Do you want open it?", false);
		dlg->Open((FRESH_PFN_RESULT)&CRealMyRoomForm983::OnFortuneResult983, 3);
	}
	else
		OpenInformation983(it);
	// 00622330 depois da janela: aba 0x17 so alterna; aba 0x22 limpa a selecao e remarca o cut-in clicado se equipado
	if (sub == 0x17)
	{
		box->ToggleItem(it);
		return;
	}
	if (sub == 0x22)
	{
		CSharedDoc* doc = Doc();
		box->UnselectAllItem();
		for (FrListBox::ITEM_LIST::iterator li = box->m_itemList.begin(); li != box->m_itemList.end(); ++li)
			if ((*li)->pData && CutinEquipped983(doc, ((sItemInfo*)(*li)->pData)->id))
				box->SelectItem(*li, false);
		if (CutinEquipped983(doc, ((sItemInfo*)it->pData)->id))
			box->SelectItem(it, true);
		return;
	}
	// UCC (007e9580): roupa UCC sem desenho baixado so alterna a selecao
	sItemInfo* info = (sItemInfo*)it->pData;
	if (IsLocalContent(S4_REAL_MYROOM) && IsUccClothes(info->typeId))
	{
		if (!(info->status & 1) || !UccManager()->IsDownloadComplete(info->typeId, info->UccIndex))
		{
			box->ToggleItem(it);
			return;
		}
	}
	// item ja selecionado = 0061f8b0 (mesmo caminho do clique esquerdo; o 983 so pre-visualiza nas abas de caixa); senao so seleciona
	if (!it->selected)
	{
		box->ToggleItem(it);
		return;
	}
	if (sub == 9 || sub == 10)
	{
		MyRoomPreview983(self, info->typeId, false);
		g_audio->PlaySfx("ui_desktop_icon_click");
		return;
	}
	OnItemListDown983();
}

bool CRealMyRoomForm983::OnFortuneResult983(int result, FrForm* form)
{
	if (result == 1)
	{
		AfxGetTask()->SendMsgToMainActor(MsgObject(NULL, M983(0x1), 0, 0, 0, 0, 0));
		WSendPacket packet((enumClientPacket)0xb2);
		packet.Encode4(s_fortuneTid983);
		packet.Send(TO_GAME);
	}
	*(FrForm**)((char*)this + 0x20c) = NULL;
	return true;
}

// 00613b00: sem "caddie_info" aberta, cria a janela (modal 3), SetCaddieInfo (a9a6c0) e desabilita o widget +0x1ac
void CRealMyRoomForm983::OpenCaddieInfo983(const sCaddieInfo& info)
{
	if (g_pFresh->GetManager()->GetDesktop()->FindChildByName("caddie_info"))
		return;
	FrCaddieInfoDlg* dlg = CreateForm<FrCaddieInfoDlg>(g_pFresh->GetManager(), this, "caddie_info", NULL);
	if (!dlg)
		return;
	dlg->SetCaddieInfo(info);
	dlg->Open((FRESH_PFN_RESULT)&CRealMyRoomForm983::OnCaddieInfoResult983, 3);
	FrWnd* w = *(FrWnd**)((char*)this + 0x1ac);
	if (w)
		w->Enable(false);
}

// 00613a50 (= OnCaddieInfoDlgResult do 645): resultado 2 (contratar) reabilita +0x1ac, salvo se o nivel do caddie > o do jogador
// 00605ea0: mov [ecx+0x240], 0; return true
// 00605580: mov [ecx+0x204], 0; return true
bool CRealMyRoomForm983::OnMascotInfoResult983(int result, FrForm* form)
{
	*(FrForm**)((char*)this + 0x204) = NULL;
	return true;
}

bool CRealMyRoomForm983::OnClubInfoResult983(int result, FrForm* form)
{
	*(FrForm**)((char*)this + 0x240) = NULL;
	return true;
}

bool CRealMyRoomForm983::OnCaddieInfoResult983(int result, FrForm* form)
{
	FrWnd* w = *(FrWnd**)((char*)this + 0x1ac);
	if (result == 2 && w)
	{
		w->Enable(true);
		if (form)
		{
			sCaddieInfo info = ((FrCaddieInfoDlg*)form)->GetCaddieInfo();
			for (CaddieIterator it = ItemManager()->m_CaddieMap.begin(); it != ItemManager()->m_CaddieMap.end(); ++it)
			{
				if ((*it).second.c.TypeId == info.tid)
				{
					if (((*it).second.c.Level & 0x7f) > Doc()->m_myInfo.stat.Level) // 613a50: (byte)node.Level & 0x7f
						w->Enable(false);
					break;
				}
			}
		}
	}
	return true;
}

// 0061a8a0 (parcial, D290): grava a posicao do item em +0x440/+0x444 (x-300.0, y-450.0 em double) e, no caso padrao
// (615010), abre "information" (portrait, nivel, descricao). Nao portados: abas 7 (information/499730), 0xb (613b00),
// 0xd (mascot_info/mascot_info_ok, a81710); em 615010 faltam nome/nivel em texto, avility, preco de aluguel/UCC e o setitem 0x24.
void CRealMyRoomForm983::OpenInformation983(FrListItem* item)
{
	char* self = (char*)this;
	*(float*)(self + 0x440) = (float)(item->pos.x - 300.0);
	*(float*)(self + 0x444) = (float)(item->pos.y - 450.0);
	int sub = *(int*)(self + 0x530);
	// 0061a8a0 aba 0xb (Caddie): "caddie_info" (613b00) com o sCaddieInfo do item
	if (sub == 0xb)
	{
		OpenCaddieInfo983(*(sCaddieInfo*)item->pData);
		return;
	}
	// 0061a8a0 aba 7 (tacos, tid 0x10xxxxxx): "information" = FrClubSetInfoDlg guardada em +0x240 (0060bea0), SetItem983 (00499730)
	if (sub == 7)
	{
		FrClubSetInfoDlg*& dlg = *(FrClubSetInfoDlg**)(self + 0x240);
		if (!dlg)
			dlg = CreateForm<FrClubSetInfoDlg>(g_pFresh->GetManager(), this, "information", NULL);
		if (dlg)
		{
			dlg->SetItem983((sItemInfo*)item->pData);
			dlg->Open((FRESH_PFN_RESULT)&CRealMyRoomForm983::OnClubInfoResult983, 1);
		}
		return;
	}
	// 0061a8a0 aba 0xd (Mascote): "mascot_info" para os tids 40000000/4/5/8/f, senao "mascot_info_ok"; a81710 = SetMascotInfo(info, +0x584->+0xac);
	// guardada em +0x204; callback 00605580 zera +0x204
	if (sub == 0xd)
	{
		sMascotInfo* mi = (sMascotInfo*)item->pData;
		unsigned long t = mi->tid;
		const char* nm = (t == 0x40000000 || t == 0x40000004 || t == 0x40000005 || t == 0x40000008 || t == 0x4000000f) ? "mascot_info" : "mascot_info_ok";
		FrMascotInfoDlg* dlg = CreateForm<FrMascotInfoDlg>(g_pFresh->GetManager(), this, nm, NULL);
		*(FrMascotInfoDlg**)(self + 0x204) = dlg;
		char* pv = *(char**)(self + 0x584);
		if (dlg)
		{
			dlg->SetMascotInfo(*mi, pv ? *(WPuppet**)(pv + 0xac) : NULL);
			dlg->Open((FRESH_PFN_RESULT)&CRealMyRoomForm983::OnMascotInfoResult983, 1);
		}
		return;
	}
	if (sub == 0x12)
		return;
	ShowInformation983(((sItemInfo*)item->pData)->typeId, (sItemInfo*)item->pData);
}

// 00606c30: tid na tabela de 35 em d13d80 (mesma de IsSpecialPartTid983)
static bool IsSpecialUccTid983(unsigned long tid)
{
	static const unsigned long tbl[35] = {
		0x08006055, 0x0800a035, 0x08044085, 0x08048025, 0x080440b3, 0x08084044, 0x0808a025, 0x080c408b, 0x080ca023, 0x080c40b2,
		0x0810404f, 0x08108030, 0x08144084, 0x0814a02c, 0x081440bf, 0x08184087, 0x08188020, 0x081840c7, 0x081c404b, 0x081ca01f,
		0x0820404a, 0x0820a00e, 0x08204091, 0x08244064, 0x0824a004, 0x0824408f, 0x08284026, 0x08284027, 0x0828a012, 0x0830401b,
		0x0830401e, 0x0830a00c, 0x0838400e, 0x08384011, 0x0838a006,
	};
	for (int i = 0; i < 35; i++)
		if (tbl[i] == tid)
			return true;
	return false;
}

// 00615010(&typeId, 0, 0): janela "information" do item (tambem pelo botao direito do cardpacklist, 00615c10)
void CRealMyRoomForm983::ShowInformation983(unsigned long typeId, const sItemInfo* info)
{
	IFF_ITEM_COMMON* common = ItemManager()->FindCommonItem(typeId);
	if (!common)
		return;
	FrDesktop* desk = g_pFresh->GetManager()->GetDesktop();
	if (desk->FindChildByName("information") || desk->FindChildByName("information_setitem"))
		return;
	// 615010: item de conjunto (tid & fc000000 == 24000000) abre "information_setitem" (0060bf70) com SetSetItem (008ed8a0)
	if ((common->TypeId & 0xfc000000) == 0x24000000)
	{
		FrSetItemDlg* setDlg = CreateForm<FrSetItemDlg>(g_pFresh->GetManager(), this, "information_setitem", NULL);
		if (setDlg)
		{
			setDlg->SetSetItem(common->TypeId);
			setDlg->Open(NULL, 3);
		}
		return;
	}
	FrForm* form = CreateForm<FrForm>(g_pFresh->GetManager(), this, "information", NULL);
	if (!form)
		return;
	FrArea* portrait = DYNAMIC_CAST(FrArea, form->FindChildByName("portrait"));
	// 615010 (007e9580 + 007ea620/007ea690): roupa UCC com uid usa o icone e o nome do desenho (FindClothes); o icone so
	// existe com o desenho baixado (+0x60 == 1), senao o retrato fica sem imagem
	sUccClothes* ucc = NULL;
	if (info && info->id != 0 && IsLocalContent(S4_REAL_MYROOM) && IsUccClothes(common->TypeId))
		ucc = UccManager()->FindClothes(info->id);
	if (portrait)
	{
		if (!ucc)
			portrait->SetBgImg(common->Icon);
		else if (ucc->downloadCount == 1 && ucc->icon)
			portrait->SetBgImg(ucc->icon);
	}
	// 615010: "reset" e "icon_clubsetworkshop" (FrArea) comecam escondidos na janela
	const char* hide[2] = { "reset", "icon_clubsetworkshop" };
	for (int h = 0; h < 2; ++h)
	{
		FrArea* ha = DYNAMIC_CAST(FrArea, form->FindChildByName(hide[h]));
		if (ha)
			ha->SetVisible(false);
	}
	FrEdit* name = DYNAMIC_CAST(FrEdit, form->FindChildByName("name"));
	FrArea* level = DYNAMIC_CAST(FrArea, form->FindChildByName("level"));
	if (name && level)
	{
		// 615010: nome do item (strncpy common+8, 0x80) seguido de quebra de linha no campo "name"
		char nm[0x80];
		strncpy(nm, ucc ? ucc->uccName : common->Name, sizeof(nm));
		nm[sizeof(nm) - 1] = 0;
		// 615010: formato coreano "nome: %s\n\n" (d00464) passa por K2L_Compatibility (00b4ec60) e MakeStr (98c3f0). Peca do grupo A
		// (004ce760) com taxa de mau comportamento ruim (!0050f810): d14754 acrescenta "(uso proibido)" em vermelho.
		bool noWear = CreateCharacterOption::Instance()->IsPartGroupA983(common->TypeId) && !IsGoodMannerRate983();
		name->AddText(MakeStr(K2L_Compatibility(noWear ? "\xc0\xcc\xb8\xa7: %s \\c0xffff0000\\c(\xc2\xf8\xbf\xeb\xba\xd2\xb0\xa1)\\c0xff000000\\c\n\n" : "\xc0\xcc\xb8\xa7: %s\n\n"), nm), false, true);
	}
	if (name && level)
	{
		// 615010 apos o nome: linha de nivel (d0042c "nivel: ... acima" / d00448 "... abaixo" pelo bit 0x80 do Level); 613bc0 da tipo/horas/expirado
		// do item (ItemType, HourRemain, Expired): tipo 1 = "periodo de uso: %dd %dh" (d00580); tipos 2..6 = expirado (d005e8), leitura
		// (S3_CADDIE_REPORT + 1a000042, d005c8), "menos de 1h" (d005b0) ou "tempo restante" (d00598). Variante de aluguel (param_3) portada abaixo.
		name->AddText(K2L_Compatibility((common->Level & 0x80) ? "\xb7\xb9\xba\xa7:                \xc0\xcc\xc7\xcf\n" : "\xb7\xb9\xba\xa7:                \xc0\xcc\xbb\xf3\n"), false, true);
	}
	if (level)
		level->SetBgImg(MakeStr("level_%03d", (common->Level & 0x7f) + 1));
	if (name && level && info && info->ItemType != 0)
	{
		int days = info->HourRemain / 24, hours = info->HourRemain % 24;
		name->AddText(K2L_Compatibility("\n"), false, true);
		const char* txt = NULL;
		if (info->ItemType == 1)
			txt = MakeStr(K2L_Compatibility("\xbb\xe7\xbf\xeb\xb1\xe2\xb0\xa3: %d\xc0\xcf %d\xbd\xc3\xb0\xa3"), days, hours);
		else if (info->ItemType <= 6)
		{
			if (info->Expired)
				txt = K2L_Compatibility("\\c0xffff0000\\c\xbb\xe7\xbf\xeb\xb1\xe2\xb0\xa3\\c0xff000000\\c\xc0\xcc \\c0xffff0000\\c\xb8\xb8\xb7\xe1\\c0xff000000\\c\xb5\xc7\xbe\xfa\xbd\xc0\xb4\xcf\xb4\xd9.\n");
			else if (IsLocalContent(S3_CADDIE_REPORT) && common->TypeId == 0x1a000042)
				txt = MakeStr(K2L_Compatibility("\xbf\xad\xb6\xf7 \xb0\xa1\xb4\xc9 \xb1\xe2\xb0\xa3: %d\xc0\xcf %d\xbd\xc3\xb0\xa3\n"), days, hours);
			else if (days == 0 && hours == 0)
				txt = K2L_Compatibility("\xb3\xb2\xc0\xba\xbd\xc3\xb0\xa3: 1\xbd\xc3\xb0\xa3\xb9\xcc\xb8\xb8\n");
			else
				txt = MakeStr(K2L_Compatibility("\xb3\xb2\xc0\xba\xbd\xc3\xb0\xa3: %d\xc0\xcf %d\xbd\xc3\xb0\xa3\n"), days, hours);
		}
		if (txt)
			name->AddText(txt, false, true);
	}
	// 615010 (S4_CARD_SYSTEM): "avility" recebe uma linha azul por atributo da peca (FindPart, 00a17160; Attr/Slot x5, MakeStatusString
	// b2e010) e "static_avility" sobe 3.0 (d66cf8). Aba 0x26 portada (00a19320). Variante de aluguel (local_49a, com param_3 e
	// ItemType != 0 via 613bc0): linha vazia antes dos atributos e "static_avility" desce 25.0 (cfebf8).
	if (IsLocalContent(S4_CARD_SYSTEM))
	{
		bool rental = info && info->ItemType != 0; // 615010: local_49a = 1 quando 613bc0 acha ItemType != 0 (param_3 e sempre 0)
		FrEdit* ability = DYNAMIC_CAST(FrEdit, form->FindChildByName("avility"));
		FrStatic* abilityBg = DYNAMIC_CAST(FrStatic, form->FindChildByName("static_avility"));
		if (ability)
		{
			if (abilityBg)
			{
				WRect rc = abilityBg->GetRect();
				rc.y += rental ? 25.0f : -3.0f;
				abilityBg->SetRect(rc);
			}
			if (rental)
				ability->AddText("", false, true);
			IFF_STRUCT::sPart* part = ItemManager()->FindPart(common->TypeId);
			if (part)
			{
				for (int i = 0; i < 5; ++i)
				{
					if (part->Attr[i] != 0 || part->Slot[i] != 0)
						ability->AddText(MakeStr("\\c0xff0000ff\\c%s\\c0xff000000\\c", MakeStatusString(i, part->Attr[i], part->Slot[i])), false, true);
				}
			}
			// 615010: aba 0x26 (this+0x530) acrescenta o texto do artefato (00a19320) ao final de "avility"
			if (*(int*)((char*)this + 0x530) == 0x26)
			{
				const char* art = ItemManager()->FindArtifactDesc983(common->TypeId);
				if (art)
					ability->AddText(art, false, true);
			}
		}
	}
	IFF_STRUCT::sDesc* desc = ItemManager()->FindDesc(common->TypeId);
	if (desc)
	{
		// 615010 (S4_CARD_SYSTEM + 007e9580 + !00606c30 = tid fora da tabela de 35 em d13d80): a descricao de roupa UCC ganha dois avisos
		// em vermelho, cada um precedido de "\n": d14704 (direitos de terceiros) e d14694 (ou d146bc se a peca for categoria 7/9)
		std::string text(desc->Desc);
		if (IsLocalContent(S4_CARD_SYSTEM) && IsUccClothes(common->TypeId) && !IsSpecialUccTid983(common->TypeId))
		{
			static const char* red = "\\c0xffff0000\\c";
			static const char* black = "\\c0xff000000\\c";
			IFF_STRUCT::sPart* up = ItemManager()->FindPart(common->TypeId);
			bool copy = up && (up->Category == 7 || up->Category == 9);
			text += "\n";
			text += red;
			text += K2L_Compatibility("\xc1\xa6\x33\xc0\xda\xc0\xc7 \xb1\xc7\xb8\xae\xb8\xa6 \xc4\xa7\xc7\xd8/\xb9\xcc\xc7\xb3\xbe\xe7\xbd\xc4\xc0\xbb");
			text += black;
			text += "\n";
			text += red;
			text += K2L_Compatibility(copy ? "\xc7\xd8\xc4\xa5 \xbf\xec\xb7\xc1\xb0\xa1 \xc0\xd6\xb4\xc2 \xb5\xf0\xc0\xda\xc0\xce\xc0\xc7 \xba\xb9\xbb\xe7 \xb9\xd7 \xb1\xb8\xc0\xd4\xc0\xba \xc7\xc7\xc7\xd8 \xc1\xd6\xbd\xca\xbd\xc3\xbf\xc0"
				: "\xc7\xd8\xc4\xa5 \xbf\xec\xb7\xc1\xb0\xa1 \xc0\xd6\xb4\xc2 \xb5\xf0\xc0\xda\xc0\xce\xc0\xba \xc7\xc7\xc7\xd8 \xc1\xd6\xbd\xca\xbd\xc3\xbf\xc0");
			text += black;
		}
		// 615010: so chama SetMessage (vt+0x74) com texto nao vazio
		if (!text.empty())
			form->SetMessage(text.c_str(), false);
	}
	form->Open(NULL, 3);
}

void CRealMyRoomForm983::OnItemListDown983()
{
	int sub = *(int*)((char*)this + 0x530);
	jp983_rastro("A294 OnItemListDown983 sub=%x", sub);
	if (sub == 9)
	{
		// 620e00 case 9: clique no botao equip_btn (x+103,y+66, tamanho do bitmap) equipa (00613d50); delete_btn (x+144) nao portado
		FrListBox* b9 = *(FrListBox**)((char*)this + 0x144);
		FrListItem* it9 = b9 ? b9->GetItemUnderCursor() : NULL;
		const Bitmap* pEq = g_pFresh->GetBitmap("equip_btn_n");
		if (it9 && it9->pData && pEq != NULL)
		{
			WRect rcEq(it9->pos.x + 103.0f, it9->pos.y + 66.0f, (float)pEq->Width(), (float)pEq->Height());
			if (rcEq.IsInRect(g_pFresh->GetManager()->GetMousePos()))
			{
				EquipActiveItem983((sItemInfo*)it9->pData);
				return;
			}
		}
		// 620e00 case 9 (2o retangulo, delete_btn x+144,y+66): item apagavel e com copias fora dos slots abre o FrDeleteItemDlg (60b590 "delete")
		const Bitmap* pDel = g_pFresh->GetBitmap("delete_btn_n");
		if (it9 && it9->pData && pDel != NULL)
		{
			sItemInfo* di = (sItemInfo*)it9->pData;
			WRect rcDel(it9->pos.x + 144.0f, it9->pos.y + 66.0f, (float)pDel->Width(), (float)pDel->Height());
			IFF_ITEM_COMMON* dc = ItemManager()->FindCommonItem(di->typeId);
			if (rcDel.IsInRect(g_pFresh->GetManager()->GetMousePos()) && dc != NULL && !(*((unsigned char*)dc + 0x80) & 1))
			{
				int used = 0;
				if (!(di->typeId & 0x2000000))
				{
					unsigned long* slots = (unsigned long*)((char*)Doc() + 0xa36);
					for (int k = 0; k < 10; ++k)
						if (slots[k] == di->typeId)
							++used;
				}
				int cnt = (int)(short)di->Common[0] - used;
				if (cnt > 0)
				{
					FrDeleteItemDlg* dlg = CreateForm<FrDeleteItemDlg>(g_pFresh->GetManager(), this, "delete", NULL);
					dlg->SetDelItem(di->typeId, cnt);
					dlg->Open(NULL, 1);
				}
			}
		}
		return;
	}
	if (sub == 7)
	{
		// 0061f8b0 caso 7: SelectClub983 (0061cc80) do uid clicado; ret 0 (nao achou) ou 2 (nivel incompativel, vira o padrao) -> aviso 0x23
		// "Chagyong level-eul chogwa..." (00d14a7c); depois "item_select_club"
		FrListBox* b7 = *(FrListBox**)((char*)this + 0x144);
		FrListItem* it7 = b7 ? b7->GetItemUnderCursor() : NULL;
		if (!it7 || !it7->pData)
			return;
		if (!it7->selected)
		{
			b7->SelectItem(it7, true); // 0061dfb0 default (clique no ja selecionado): remarca; sem nova selecao
			return;
		}
		int r7 = SelectClub983(((sItemInfo*)it7->pData)->id);
		if (r7 == 0 || r7 == 2)
			AfxGetTask()->SendMsgToMainActor(MsgObject(NULL, M983(0x23), (int)K2L_Compatibility("\xc2\xf8\xbf\xeb \xb7\xb9\xba\xa7\xc0\xbb \xc3\xca\xb0\xfa\xc7\xdf\xbd\xc0\xb4\xcf\xb4\xd9. \xbb\xe7\xbf\xeb\xc7\xd2 \xbc\xf6 \xbe\xf8\xbd\xc0\xb4\xcf\xb4\xd9."), 0, 0, 0, 0));
		g_audio->PlaySfx("item_select_club");
		return;
	}
	if (sub == 8)
	{
		// 0061f8b0 caso 8: 0061ce00(typeId do item clicado) e sfx item_select_aztec
		FrListBox* b8 = *(FrListBox**)((char*)this + 0x144);
		FrListItem* it8 = b8 ? b8->GetItemUnderCursor() : NULL;
		if (!it8 || !it8->pData)
			return;
		if (!it8->selected)
		{
			b8->SelectItem(it8, true); // 0061dfb0 default: remarca
			return;
		}
		SelectBall983(((sItemInfo*)it8->pData)->typeId);
		g_audio->PlaySfx("item_select_aztec");
		return;
	}
	if (sub == 0xb || sub == 0xd)
	{
		// 0061f8b0 casos 0xb/0xd (006205b5/00620639): caddie = 0061c960(chave), sem troca -> aviso 0x23 de nivel (00d14bc4);
		// mascote = 0061cb70(chave); os dois tocam "ui_desktop_icon_click"
		FrListBox* bk = *(FrListBox**)((char*)this + 0x144);
		FrListItem* ik = bk ? bk->GetItemUnderCursor() : NULL;
		if (!ik || !ik->pData)
			return;
		unsigned long key = *(unsigned long*)ik->pData; // sCaddieInfo/sMascotInfo::guid = chave do mapa
		jp983_rastro("A296 listdown sub=%x key=%08x sel=%d", sub, key, (int)ik->selected);
		// B529 (C240, orig-c238-1): clicar no mascote JA equipado (+0x510 == chave) desequipa no original (X manda sub 08 = 0)
		bool unequipMascot = (sub == 0xd && *(unsigned long*)((char*)this + 0x510) == key);
		if (!ik->selected || unequipMascot)
		{
			// 00620e00: item sem selecao (clique no ja equipado) -> 0061dfb0 (tirar) caso 0xb = 0061c960(0) + 0061aab0; caso 0xd = 0061cb70(0)
			if (sub == 0xd)
				SelectMascot983(0);
			else
				SelectCaddie983(0);
			g_audio->PlaySfx("ui_desktop_icon_click");
			return;
		}
		if (sub == 0xd)
			SelectMascot983(key);
		else if (!SelectCaddie983(key))
			AfxGetTask()->SendMsgToMainActor(MsgObject(NULL, M983(0x23), (int)K2L_Compatibility("\xb7\xb9\xba\xa7\xc0\xcc \xc3\xe6\xba\xd0\xc7\xcf\xc1\xf6 \xbe\xca\xbd\xc0\xb4\xcf\xb4\xd9. \xb7\xb9\xba\xa7\xbe\xf7 \xc8\xc4\xbf\xa1 \xc2\xf8\xbf\xeb\xc7\xd8\xc1\xd6\xbc\xbc\xbf\xe4."), 0, 0, 0, 0));
		g_audio->PlaySfx("ui_desktop_icon_click");
		return;
	}
	// 0061f8b0 casos 9/10/0x13/0x14/0x18/0x19/0x1d-0x1f/0x21/0x26 (fim do 00620e00, item ja selecionado): 00605640 (previa 3D do item)
	// e sfx ui_desktop_icon_click. D431: orig-d430-1/016 (clique no Lucky Bag, Passive) mostra a selecao e a bolsa 3D; o nosso nada.
	if (sub == 10 || sub == 0x13 || sub == 0x14 || sub == 0x18 || sub == 0x19 || (sub >= 0x1d && sub <= 0x1f) || sub == 0x21 || sub == 0x26)
	{
		FrListBox* pb = *(FrListBox**)((char*)this + 0x144);
		FrListItem* pi = pb ? pb->GetItemUnderCursor() : NULL;
		if (pi && pi->pData && pi->selected)
		{
			MyRoomPreview983((char*)this, ((sItemInfo*)pi->pData)->typeId, false);
			g_audio->PlaySfx("ui_desktop_icon_click");
		}
		return;
	}
	// 0061f8b0 casos 5/0x16 (Clothes/All): fora de tid 0x70xxxxxx (set, nao portado) caem no caso 2 (equipar)
	if (sub != 2 && sub != 3 && sub != 4 && sub != 5 && sub != 0x16 && sub != 0x1b && sub != 0x22)
		return;
	FrListBox* box = *(FrListBox**)((char*)this + 0x144);
	if (!box)
		return;
	FrListItem* item = box->GetItemUnderCursor();
	jp983_rastro("A294 listdown sub=%x item=%p data=%p tid=%08x sel=%d", sub, item, item ? item->pData : NULL,
		(item && item->pData) ? ((sItemInfo*)item->pData)->typeId : 0, item ? (int)item->selected : -1);
	if (!item || !item->pData)
		return;
	if ((sub == 5 || sub == 0x16) && (((sItemInfo*)item->pData)->typeId & 0xfc000000) == 0x70000000)
		return;
	ItemEquip983(box, item, item->selected);
}

// cardpacklist LBUTTONDOWN (645 OnCardPackListDown): seleciona o item; segundo clique mostra o botao de uso
void CRealMyRoomForm983::OnCardPackListDown983()
{
	FrListBox* pack = *(FrListBox**)((char*)this + 0xab8);
	if (!pack)
		return;
	// 006101e0: so na sub-aba Card Holic (0x1c); o ramo CAnotherHand::IsWorking -> ToggleItem nao existe aqui (previa sincrona)
	if (*(int*)((char*)this + 0x530) != 0x1c)
		return;
	FrListItem* pItem = pack->GetItemUnderCursor();
	if (pItem == NULL || pItem->pData == NULL)
		return;
	if (pItem->selected)
	{
		g_audio->PlaySfx("ui_desktop_icon_click");
		if (CardBook983() && CardBook983()->m_pUseButton)
			CardBook983()->m_pUseButton->SetVisible(true);
		MyRoomShowPet983((char*)this, ((sCards*)pItem->pData)->tid); // 0060e8b0
		return;
	}
	pack->SelectItem(pItem, true);
}

// cardpacklist RBUTTONDOWN 00615c10: item selecionado = mesmo caminho do clique (006101e0); senao alterna a selecao;
// depois abre a "information" do pacote (00615010(&tid, 0, 0))
void CRealMyRoomForm983::OnCardPackListRDown983()
{
	FrListBox* pack = *(FrListBox**)((char*)this + 0xab8);
	if (!pack || *(int*)((char*)this + 0x530) != 0x1c)
		return;
	FrListItem* pItem = pack->GetItemUnderCursor();
	if (pItem == NULL || pItem->pData == NULL)
		return;
	if (pItem->selected)
		OnCardPackListDown983();
	else
		pack->ToggleItem(pItem);
	ShowInformation983(((sCards*)pItem->pData)->tid);
}

// item_storage_list RBUTTONDOWN 00615fa0: so com NT REAL_MYROOM (00a7a8d0) e o armazem aberto (+0xa84): abre a "information" do
// item (00615010(&tid, 0, ...)) e seleciona o item sob o cursor (SelectItem 1). (O teste de DAT_00e768fc+0x2d nao tem par aqui.)
void CRealMyRoomForm983::OnStorageListRDown983()
{
	char* self = (char*)this;
	FrListBox* box = *(FrListBox**)(self + 0xaa0);
	if (!IsLocalContent(S4_REAL_MYROOM) || !*(char*)(self + 0xa84) || !box)
		return;
	FrListItem* it = box->GetItemUnderCursor();
	if (!it)
		return;
	if (it->pData)
		ShowInformation983(((sItemInfo*)it->pData)->typeId, (sItemInfo*)it->pData);
	box->SelectItem(it, true);
}

// card_use LBUTTONDOWN 006142e0. Lista do Card Holic visivel (+0xab8): o item selecionado (+0x108) abre o FrCardBoxDlg
// (Init(tid, uid, cardCount), Open modal) e apaga a previa (00605530(0)); ja aberto = nada. Senao, no caderno (+0xa78):
// carta SP (tid & 0x3c00000 == 0x800000) na casa selecionada da pagina de cartas -> UseCard 007f3190; outra carta ->
// janela de maestria kam_mastery_main_dialog (005be450(NULL) + DoModal 004783e0), se ainda nao aberta (00e78154).
void CRealMyRoomForm983::OnCardUseDown983()
{
	FrListBox* pack = *(FrListBox**)((char*)this + 0xab8);
	if (pack->IsVisible())
	{
		FrListItem* pItem = pack->GetSelected();
		if (pItem == NULL || pItem->pData == NULL)
			return;
		FrWnd* pOpen = g_pFresh->GetDesktop()->FindChildForm("FrCardBoxDlg");
		if (pOpen && DYNAMIC_CAST(FrCardBoxDlg, pOpen))
			return;
		sCards* pCards = (sCards*)pItem->pData;
		FrCardBoxDlg* pDlg = CreateForm<FrCardBoxDlg>(g_pFresh->GetManager(), this, "FrCardBoxDlg", NULL);
		pDlg->Init(pCards->tid, pCards->uid, pCards->cardCount);
		pDlg->Open(NULL, 1);
		MyRoomPetClear983((char*)this);
		return;
	}
	CCardBook* book = CardBook983();
	if (book == NULL)
		return;
	CCardPage* page = book->GetCardPage();
	if (page)
	{
		sCards* pCards = page->GetCardSlot()[book->m_selectedSlot].GetCards();
		if (pCards && (pCards->tid & 0x3c00000) == 0x800000)
		{
			book->UseCard();
			return;
		}
	}
	if (RFCharMasteryMainDlg::ms_pInstance == NULL)
	{
		RFCharMasteryMainDlg* dlg = RFCharMasteryMainDlg::Create983(NULL);
		if (dlg)
			dlg->DoModal();
	}
}

// updown_group.mastery_m LBUTTONUP 0060d460 (o botao "Char. Mastery"; antes sem manipulador no form, o clique nao fazia nada).
// Servico 0x40000000 suspenso -> so o aviso (00b2e8c0); janela de maestria (00e78154) aberta -> nada; senao avisa o ator principal
// (msg 1), liga +0x11411 e pede ao servidor (0x157 com o meu UID).
void CRealMyRoomForm983::OnMasteryMUp983()
{
	if (DOCJP()->IsControlServerService983(0x40000000))
	{
		S5::UTIL::NotifyServiceStopped983(0x40000000);
		return;
	}
	if (RFCharMasteryMainDlg::ms_pInstance != NULL)
		return;
	AfxGetTask()->SendMsgToMainActor(MsgObject(NULL, 1, 0, 0, 0, 0, 0));
	Doc()->m_goStopMode = true;
	WSendPacket packet((enumClientPacket)0x157);
	packet.Encode4(Doc()->m_myInfo.info.dwUID);
	packet.Send(TO_GAME);
}

// 0060d220 (upgrade, modo 0) / 0060d340 (downgrade, modo 1): clube (+0x518) com nivel incompativel -> aviso (msg 0x23); senao abre
// o dialogo "downgrade" (+0x1f8) para o clubset equipado (doc+0xa2e)
void CRealMyRoomForm983::OnUpDownUp983(int mode)
{
	IFF_STRUCT::sClubSet* pClubSet = Doc()->m_itemManager.FindClubSet(*(unsigned long*)((char*)this + 0x518));
	if (pClubSet)
	{
		if ((pClubSet->c.Level > Doc()->m_myInfo.stat.Level && !pClubSet->c.IsUnderLvl) ||
			(pClubSet->c.Level < Doc()->m_myInfo.stat.Level && pClubSet->c.IsUnderLvl))
		{
			AfxGetTask()->SendMsgToMainActor(MsgObject(NULL, M983(0x23),
				(int)"\xb7\xb9\xba\xa7\xc0\xcc \xc3\xe6\xba\xd0\xc7\xcf\xc1\xf6 \xbe\xca\xbd\xc0\xb4\xcf\xb4\xd9. \xb7\xb9\xba\xa7\xbe\xf7 \xc8\xc4\xbf\xa1 \xc0\xcc\xbf\xeb\xc7\xcf\xbd\xca\xbd\xc3\xbf\xc0.",
				0, 0, 0, 0));
			return;
		}
	}
	FrDowngradeDlg* dlg = CreateForm<FrDowngradeDlg>(g_pFresh->GetManager(), this, "downgrade", NULL);
	*(FrDowngradeDlg**)((char*)this + 0x1f8) = dlg;
	dlg->SetInfo(Doc()->m_myInfo.userEquip.guidClubSet, mode);
	dlg->Open((FRESH_PFN_RESULT)&CRealMyRoomForm983::OnUpDownResult983, 3);
	OnTooltipHoverOff983();
}

// 0060cf70 com param NULL: sempre limpa o tooltip
void CRealMyRoomForm983::OnTooltipHoverOff983()
{
	CIconToolTip::GetInstance()->ClearToolTip();
}

// 00610980: resultado do dialogo de autoridade: OK (1) manda 0x00B8 com o bloco do doc (+0x1070c, 0x6b) salvo senha vazia com
// autoridade ligada (aviso rmr_notify -> reabre pelo 00622940)
bool CRealMyRoomForm983::OnAuthDlgResult983(int result, FrForm* form)
{
	char* self = (char*)this;
	if (form)
		FrForm::ms_bHasTail = true;
	CRealMyRoom_AuthorityDlg* dlg = *(CRealMyRoom_AuthorityDlg**)(self + 0x244);
	if (result == 1 && dlg != NULL)
	{
		bool bAuth = dlg->GetAuthSetting();
		dlg->GetPassWord();
		char* d = (char*)Doc();
		if (strlen(d + 0x10713) == 0 && bAuth)
		{
			FrForm* pNotify = CreateForm<FrForm>(g_pFresh->GetManager(), this, "rmr_notify", NULL);
			pNotify->SetMessage("\xba\xf1\xb9\xd0\xb9\xf8\xc8\xa3 \xc0\xd4\xb7\xc2\xc0\xcc \xb5\xc7\xc1\xf6 \xbe\xca\xbe\xc6\xbc\xad \xb1\xc7\xc7\xd1 \xbc\xb3\xc1\xa4\xbf\xa1 \xbd\xc7\xc6\xd0\xc7\xcf\xbf\xb4\xbd\xc0\xb4\xcf\xb4\xd9.", false);
			pNotify->Open((FRESH_PFN_RESULT)&CRealMyRoomForm983::OnAuthDlgFailResult983, 2);
		}
		else
		{
			d[0x10712] = dlg->GetAuthSetting();
			WSendPacket packet((enumClientPacket)0xb8);
			packet.EncodeBuffer(d + 0x1070c, 0x6b);
			packet.Send(TO_GAME);
		}
	}
	*(FrForm**)(self + 0x244) = NULL;
	return true;
}

// 00622940: aviso fechado com OK -> abre o dialogo de novo
bool CRealMyRoomForm983::OnAuthDlgFailResult983(int result, FrForm* form)
{
	if (result == 1)
		SelectMenu983(6);
	return true;
}

// 0061f850: abre a oficina de clubset (clubset_workshop, +0x23c)
void CRealMyRoomForm983::OnClubWorkMUp983()
{
	FrClubSetWorkshopMainDlg* dlg = FrClubSetWorkshopMainDlg::Create983(g_pFresh->GetManager(), this);
	*(FrForm**)((char*)this + 0x23c) = dlg;
	dlg->Open((FRESH_PFN_RESULT)&CRealMyRoomForm983::OnClubWorkResult983, 3);
	OnTooltipHoverOff983();
}

// 0061e4a0: fecha a oficina com a aba 7 selecionada -> volta a sub-aba 7
bool CRealMyRoomForm983::OnClubWorkResult983(int result, FrForm* form)
{
	FrForm* dlg = *(FrForm**)((char*)this + 0x23c);
	if (dlg != NULL && *((char*)dlg + 0x168) != 0 && *(int*)((char*)this + 0x530) == 7)
		SelectSubTab983(7, true);
	*(FrForm**)((char*)this + 0x23c) = NULL;
	return true;
}

// card_slot1..12 LBUTTONDOWN -> 006107f0(slot, type). Com o caderno (+0xa78) e +0xa84 == 0: casa selecionada (book+10),
// page->SelectSlot(type, slot); botao usar (book+0x8c) so com casa selecionada e carta usavel (009d9d40: tid != 0x7c800026 e
// != 0x7c800041; o 645 so excluia 0x7c800026)
void CRealMyRoomForm983::OnCardSlotDown983(unsigned char slot, unsigned char type)
{
	CCardBook* book = CardBook983();
	if (book == NULL || *(char*)((char*)this + 0xa84))
		return;
	CCardPage* page = book->GetCardPage();
	if (page == NULL)
		return;
	book->SetSelectedSlot(slot);
	page->SelectSlot(type, slot);
	if (book->m_pUseButton == NULL)
		return;
	bool use = false;
	if (page->IsSelectedSlot())
	{
		sCards* pCards = page->GetCardSlot()[slot].GetCards();
		use = pCards == NULL || (pCards->tid != 0x7c800026 && pCards->tid != 0x7c800041);
	}
	book->m_pUseButton->SetVisible(use);
}

// msgmap 00e1347c: so o X (close_wnd) por enquanto; os demais handlers ainda estao no CRealMyRoomMain (B379)
BEGIN_FRESH_MSGMAP(CRealMyRoomForm983, FrTaskForm)
ON_FRESH_VV("close_wnd", FRCMD_LBUTTONUP, CRealMyRoomForm983::OnCloseWndUp983)
ON_FRESH_VV("middle_ui.tab_main", FRCMD_LBUTTONUP, CRealMyRoomForm983::OnTabMainUp983)
ON_FRESH_VV("middle_ui.item_list", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnItemListDown983)
ON_FRESH_VV("middle_ui.item_list", FRCMD_DBLCLICK, CRealMyRoomForm983::OnItemListDClick983)
ON_FRESH_VV("middle_ui.item_list", FRCMD_RBUTTONDOWN, CRealMyRoomForm983::OnItemListRDown983)
ON_FRESH_VV("middle_ui.sbox.item_slot", FRCMD_DBLCLICK, CRealMyRoomForm983::OnItemSlotDClick983)
ON_FRESH_VI("middle_ui.sbox.item_slot", FRCMD_OWNERDRAW, CRealMyRoomForm983::OnItemSlotOwnerDraw983)
ON_FRESH_VI("middle_ui.pet", FRCMD_OWNERDRAW, CRealMyRoomForm983::OnPetOwnerDraw983)
ON_FRESH_VI("middle_ui.item_list", FRCMD_OWNERDRAW, CRealMyRoomForm983::OnItemListOwnerDraw983)
ON_FRESH_VV("middle_ui.tab_sub", FRCMD_LBUTTONUP, CRealMyRoomForm983::OnTabSubUp983)
ON_FRESH_VI("card_book_back_bg", FRCMD_OWNERDRAW, CRealMyRoomForm983::OnCardBookBackDraw983)
ON_FRESH_VI("card_book", FRCMD_OWNERDRAW, CRealMyRoomForm983::OnCardBookDraw983)
ON_FRESH_VI("cardpacklist", FRCMD_OWNERDRAW, CRealMyRoomForm983::OnCardPackListDraw983)
ON_FRESH_VV("cardpacklist", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardPackListDown983)
ON_FRESH_VV("cardpacklist", FRCMD_RBUTTONDOWN, CRealMyRoomForm983::OnCardPackListRDown983)
ON_FRESH_VV("item_storage_list", FRCMD_RBUTTONDOWN, CRealMyRoomForm983::OnStorageListRDown983)
ON_FRESH_VV("card_pack", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardPackTab983)
ON_FRESH_VV("card_volume1", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardVol1Tab983)
ON_FRESH_VV("card_volume2", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardVol2Tab983)
ON_FRESH_VV("card_volume3", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardVol3Tab983)
ON_FRESH_VV("card_volume4", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardVol4Tab983)
ON_FRESH_VV("card_volume5", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardVol5Tab983)
ON_FRESH_VV("card_sp", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardSpTab983)
ON_FRESH_VV("cardpage_index", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardIndexDown983)
ON_FRESH_VV("cardpage_index", FRCMD_MOUSEMOVE, CRealMyRoomForm983::OnCardIndexMove983)
ON_FRESH_VV("card_use", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardUseDown983)
ON_FRESH_VV("updown_group.mastery_m", FRCMD_LBUTTONUP, CRealMyRoomForm983::OnMasteryMUp983)
ON_FRESH_VV("updown_group.upgrade", FRCMD_LBUTTONUP, CRealMyRoomForm983::OnUpgradeUp983)
ON_FRESH_VV("updown_group.downgrade", FRCMD_LBUTTONUP, CRealMyRoomForm983::OnDowngradeUp983)
ON_FRESH_VV("updown_group.clubwork_m", FRCMD_LBUTTONUP, CRealMyRoomForm983::OnClubWorkMUp983)
ON_FRESH_VV("card_slot1", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardSlot1Down983)
ON_FRESH_VV("card_slot2", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardSlot2Down983)
ON_FRESH_VV("card_slot3", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardSlot3Down983)
ON_FRESH_VV("card_slot4", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardSlot4Down983)
ON_FRESH_VV("card_slot5", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardSlot5Down983)
ON_FRESH_VV("card_slot6", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardSlot6Down983)
ON_FRESH_VV("card_slot7", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardSlot7Down983)
ON_FRESH_VV("card_slot8", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardSlot8Down983)
ON_FRESH_VV("card_slot9", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardSlot9Down983)
ON_FRESH_VV("card_slot10", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardSlot10Down983)
ON_FRESH_VV("card_slot11", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardSlot11Down983)
ON_FRESH_VV("card_slot12", FRCMD_LBUTTONDOWN, CRealMyRoomForm983::OnCardSlot12Down983)
END_FRESH_MSGMAP()

static FrForm* CreateRealMyRoom983(FrWndManager* pManager, const char* name)
{
	return CreateForm<CRealMyRoomForm983>(pManager, NULL, name);
}
static FrFormRegistrar983 s_realMyRoomRegistrar("realmyroom", CreateRealMyRoom983);
