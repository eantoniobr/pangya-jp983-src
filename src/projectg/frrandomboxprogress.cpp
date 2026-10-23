#include "minatl.h"
#include "frrandomboxprogress.h"
#include "frgaugebar.h"
#include "frstatic.h"
#include "frarea.h"
#include "actor.h"
IMPLEMENT_OBJECT(FrRandomBoxProgress, FrForm)

BEGIN_FRESH_MSGMAP(FrRandomBoxProgress, FrForm)

ON_FRESH_VI("waitbar", FRCMD_INIT, FrRandomBoxProgress::OnProgressInit)
ON_FRESH_VI("cancle", FRCMD_LBUTTONUP, FrRandomBoxProgress::OnCancelUp)
ON_FRESH_VI("explane", FRCMD_INIT, FrRandomBoxProgress::OnExplaneStatic_Init)
ON_FRESH_VI("image", FRCMD_INIT, FrRandomBoxProgress::OnImageInit983)

END_FRESH_MSGMAP()

C_ASSERT(sizeof(FrRandomBoxProgress) == 0x130);

FrRandomBoxProgress::FrRandomBoxProgress()
{
	m_elapsedTime = 0;
	m_pProgress = NULL;
	m_totalTime = 0;
	m_pExplaneStatic = NULL;
	m_pImage983 = NULL;
}

FrRandomBoxProgress::~FrRandomBoxProgress()
{
}

// 983 (008c5350): vazia; o texto do explane nao aparece mais
void FrRandomBoxProgress::SetExplane(const char* text)
{
}

void FrRandomBoxProgress::OnProgressInit(int param)
{
	m_pProgress = DYNAMIC_CAST(FrGaugeBar, param);
	m_pProgress->SetRange(0, 100, 0);
}

void FrRandomBoxProgress::OnCancelUp(int param)
{
	FrForm::OnCancel();
}

void FrRandomBoxProgress::OnExplaneStatic_Init(int param)
{
	m_pExplaneStatic = DYNAMIC_CAST(FrStatic, param);
	if (m_pExplaneStatic)
	{
		m_pExplaneStatic->SetVisible(false);
		m_pExplaneStatic->Enable(false);
	}
}

void FrRandomBoxProgress::OnImageInit983(int param)
{
	m_pImage983 = DYNAMIC_CAST(FrArea, param);
}

// 983 (008c5370): sem o ajuste da barra pelo explane; 3 a 5 segundos
bool FrRandomBoxProgress::OnInit()
{
	srand(GetTickCount());
	m_totalTime = rand() % 3 + 3;

	return true;
}

void FrRandomBoxProgress::OnProc(const float dt)
{
	m_elapsedTime += dt;

	if (m_elapsedTime > m_totalTime)
	{
		m_pProgress->SetPos(100);

		AfxGetTask()->GetMainActor() << MsgObject(NULL, M983(0x1), 0, 0, 0, 0, 0);
		WSendPacket send((enumClientPacket)0xef); // JP 983 (s63): 0xf1 no KR 645
		send.Encode4(m_boxTid);
		send.Send(TO_GAME);

		m_elapsedTime = 0;
		m_totalTime = 0;

		FrForm::OnCancel();
	}
	else
	{
		int pos = (int)((m_elapsedTime / m_totalTime) * 100.0f);
		if (pos < 100)
			m_pProgress->SetPos(pos);
	}
}
