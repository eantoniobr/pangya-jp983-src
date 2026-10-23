// JP 983: CHoleInOneScoreInfo (construtor 0053ebc0, destrutor 0053ecc0, Process 0052bbd0, Display 0052bc70, auxiliares 00529080
// e 0052ba20; no 983 dentro do fontinfo.cpp) e as três funções 0053ef40/0053f010/0053f0d0 que vêm logo depois dela (vozes da
// sala do campo do hole-in-one). Fonte reconstruída do 983 (classes novas, sem par no 645). Sessão B27.
#include "minatl.h"
#include "projectg.h"
#include "holeinonescoreinfo.h"
#include "shareddoc.h"
#include "golfball.h"
#include "soundmanager.h"
#include "wview.h"
#include <stdio.h>
#include <stdlib.h>

// JP 983: estado do jogo, dword +0x158 do objeto apontado por CSharedDoc+0x11024 (o mesmo do holeinonemissiondlg.cpp)
struct sGameState983
{
	char m_pad000[0x158];
	unsigned int m_state; // +0x158
};
#define GAMESTATE983() ((*(sGameState983**)((char*)::Doc() + 0x11024))->m_state)

// nome da música que está tocando (CSoundManager+0x24; a frente A não tem leitor público — pedido B27)
struct CSoundManagerJp : CSoundManager
{
	const char* GetBGMName983() { return m_bgmName; }
};

// número do campo sem o bit 0x80 (0xfd fica como está); embutida no 983
static inline int COURSEINDEX983(unsigned char course)
{
	if (course > 0x7f && course != 0xfd)
		return course - 0x80;
	return course;
}

static inline float LERP983(const float& a, const float& b, const float& t)
{
	return (1.0f - t) * a + b * t;
}

// 00529080
void CHoleInOneScoreInfo::Reset983()
{
	m_t = 0.0f;
	m_state = 0;
	m_alpha = 255.0f;
	m_startX = g_view->GetWidth() * 0.5;
	m_startY = g_view->GetHeight() * 0.25;
	m_endX = 40.0f;
	m_endY = 65.0f;
	m_startX = g_view->GetWidth() * 0.5;
	m_startY = g_view->GetHeight() * 0.25;
	m_percent = 0;
	m_endX = 40.0f;
	m_endY = 80.0f;
	m_scale = 1.0f;
}

// 0052ba20
void CHoleInOneScoreInfo::Animate983()
{
	switch (m_state)
	{
	case 1:
		m_alpha += m_dt * 255.0;
		if (m_alpha >= 255.0)
		{
			m_alpha = 255.0f;
			m_state = 2;
			AfxGetTask()->GetActor("Screen") << MsgObject(NULL, 0x235, 0, 0, 0, 0, 0);
		}
		m_x = m_startX;
		m_y = m_startY;
		break;
	case 2:
		m_t += m_dt * 1.5;
		if (m_t > 1.0f)
		{
			m_t = 1.0f;
			m_state = 4;
		}
		m_x = LERP983(m_startX, m_endX, m_t);
		m_y = LERP983(m_startY, m_endY, m_t);
		m_scale = 1.0f - m_t * 0.3;
		break;
	case 4:
		m_t += m_dt * 1.5;
		if (m_t > 2.0f)
		{
			m_t = 2.0f;
			m_state = 3;
		}
		break;
	case 3:
		m_alpha -= m_dt * 255.0;
		if (m_alpha < 0.0f)
		{
			m_alpha = 0.0f;
			m_state = 0;
		}
		break;
	}
}

// 0052bbd0
void CHoleInOneScoreInfo::Process(float dt)
{
	if (GAMESTATE983() & 0x80)
	{
		if (GolfBall().m_state == 0)
		{
			m_dt = dt;
			Animate983();
		}
	}
}

// 0052bc70
void CHoleInOneScoreInfo::Display()
{
	if (GolfBall().m_state == 0 && m_state != 0)
	{
		m_color = ((int)m_alpha << 24) | 0xffffff;
		sprintf(m_buffer, "%%%d", m_percent);
		Print(m_x, m_y, m_buffer, 4.0f, 0, m_scale, NULL);
	}
}

// 0053ebc0
CHoleInOneScoreInfo::CHoleInOneScoreInfo()
{
	memset(&m_startX, 0, 0x28);
	Init("[bigfont.jpg", NULL);
	m_buffer = new char[32];
	Reset983();
}

// 0053ecc0
CHoleInOneScoreInfo::~CHoleInOneScoreInfo()
{
}

// 0053ef40
void CRoomCheer983::Process(const float& dt)
{
	if (m_enabled && !m_names.empty())
	{
		m_timer += dt;
		if (m_interval < m_timer)
		{
			m_timer = 0.0f;
			m_interval = (float)(rand() % 5 + 5);
			int count = m_names.size();
			g_audio->PlaySfx(m_names[rand() % count].c_str(), NULL, 0, NULL, NULL, 0.5f, 200.0f);
		}
	}
}

// 0053f010
CRoomCheer983::~CRoomCheer983()
{
	if (!m_prevBgm.empty() && m_restoreBgm)
		g_audio->PlayBGM(m_prevBgm.c_str(), false, true);
}

// 0053f0d0
CRoomCheer983::CRoomCheer983(unsigned char course)
	: m_timer(0.0f), m_interval(0.0f), m_enabled(true), m_restoreBgm(true)
{
	const char* bgm = ((CSoundManagerJp*)g_audio)->GetBGMName983();
	if (bgm != NULL)
		m_prevBgm = bgm;
	m_course = COURSEINDEX983(course);
	if (m_course == 0x40)
	{
		g_audio->StopBGM(true);
		Add983("oneshot_hio1_1");
		Add983("oneshot_hio1_2");
		Add983("oneshot_hio1_3");
		Add983("oneshot_hio1_4");
		Add983("oneshot_hio1_5");
		Add983("oneshot_hio1_6");
	}
}

// tamanhos medidos no 983: `push 0x74` em 0075200f; última gravação do CRoomCheer983 em +0x52
typedef char sizeof_CFontInfo_0x2c[sizeof(CFontInfo) == 0x2c ? 1 : -1];
typedef char sizeof_CHoleInOneScoreInfo_0x74[sizeof(CHoleInOneScoreInfo) == 0x74 ? 1 : -1];
typedef char sizeof_CRoomCheer983_0x54[sizeof(CRoomCheer983) == 0x54 ? 1 : -1];
