// JP 983: corpos dos métodos pequenos do CSharedDoc que a B usa pela visão CSharedDocJp (include/jp/shareddocjp.h). No 983
// ficam na unidade do CSharedDoc (0062be40–0062bf90, frente A); aqui só para o link não acusar (pedidos C28/C29). Quando os
// campos tiverem nome no shareddoc.h, estes corpos vão para o shareddoc.cpp. Deslocamentos medidos no 983. Sessão B77.
#include "minatl.h"
#include "projectg.h"
#include "shareddocjp.h"

#define DOC983(T, off) (*(T*)((char*)this + (off)))

// 0062be40
void CSharedDocJp::ClearSetEffect983()
{
	DOC983(unsigned long, 0x11448) = 0;
	DOC983(unsigned long, 0x1144c) = 0;
	DOC983(unsigned long, 0x11450) = 0;
	DOC983(unsigned long, 0x11454) = 0;
}

// 0062be60
void CSharedDocJp::SetSetEffect983(unsigned char player, unsigned long typeId)
{
	((unsigned long*)((char*)this + 0x11448))[player] = typeId;
}

// 0062bea0
void CSharedDocJp::SetAuxpartValues983(void* pValues, int player)
{
	((void**)((char*)this + 0x114b8))[player] = pValues;
}

// 0062bec0
void CSharedDocJp::ClearAuxpartValues983()
{
	DOC983(void*, 0x114b8) = 0;
	DOC983(void*, 0x114bc) = 0;
	DOC983(void*, 0x114c0) = 0;
	DOC983(void*, 0x114c4) = 0;
}

// 0062bf90
int CSharedDocJp::GetState983()
{
	return DOC983(int, 0x11638);
}
