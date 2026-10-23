#include "minatl.h"
#include "projectg.h"
#include "wpuppet.h"
#include "wbone.h"
#include "fx.h"
#include "fxinterpreter.h"
#include "mathconsts.h"
const char* GetStrConst(const char* str, char* out);
const char* GetCharsTillSpace(const char* str, char* out);

const char FxInterpreter::TOKEN[][8] = { "*fx", "*playif" };

std::list<FxInterpreter::sFxInfo> FxInterpreter::ms_fxList645;
int FxInterpreter::ms_nextID645;
int FxInterpreter::ms_count983;

// 645: global. No 983 cada dono cria o seu; fica so para as chamadas naked que ainda o usam (gui_control.cpp).
FxInterpreter* GetFxInterpreter()
{
	static FxInterpreter fxInterpreter(NULL, 0);

	return &fxInterpreter;
}

FxInterpreter::sFxInfo::sFxInfo(int _id, eEffectType _type, void* _pFx)
{
	id = _id;
	type = _type;
	pFx = _pFx;
}

void FxInterpreter::sFxInfo::DetachSingleFx()
{
	if (CFx::Instance())
	{
		if (type == eET_SPRAY)
			CFx::Instance()->CloseSpray((CFxSpray*)pFx);
		else if (type == eET_SEQUENCE)
			CFx::Instance()->CloseSequence((CFxSequence*)pFx, true);
	}
}

// 983: 0088e520
FxInterpreter::FxInterpreter(CFxBox* pet, int n)
{
	m_pPet983 = pet;
	m_unk983_154 = n + 1;
	m_unk983_158 = 1;
	Init983();
	Unk983_880d40(pet);
	if (pet)
		Unk983_87f2d0(pet);
	ms_count983++;
}

// 983: o destrutor e 0088dee0 (nao escrito); este e o do 645
FxInterpreter::~FxInterpreter()
{
	if (!ms_fxList645.empty())
		DetachFxAll645();
}

// 983: 00889df0
void FxInterpreter::DetachFx(int id)
{
	for (int i = 0; i < 4; i++)
		DetachSlot983(id, i);
}

// 983: 0088c420
void FxInterpreter::DetachFxAll(int kind)
{
	DetachA983(kind);
	DetachB983(kind);
	DetachC983(kind);
	if (kind == -1)
		m_unk983_154 = 1;
}

bool FxInterpreter::ParseToken(const char** str, eScripFormat format) const
{
	*str = strstr(*str, TOKEN[format]);
	return *str != NULL;
}

bool FxInterpreter::ParseFxName(const char** str, char* name,
	eScripFormat format, eEffectType& type) const
{
	switch (format)
	{
	case eSF_FX:

		*str = GetCharsTillSpace(*str + 3, name);
		break;
	case eSF_PLAYIF:
		*str = GetStrConst(*str + 3, name);
		break;
	default:

		return false;
	}

	int len = strlen(name);

	if (len == 0 || len >= 64)
		return false;

	char* ext = strrchr(name, '.');

	if (ext == NULL || strlen(ext) < 4)
		return false;
	const char* szExt = ext + 1;

	if (!stricmp(szExt, "seq"))
	{
		type = eET_SEQUENCE;
		return true;
	}

	if (!stricmp(szExt, "spr"))
	{
		type = eET_SPRAY;
		return true;
	}
	type = eET_NONE;
	return false;
}
int FxInterpreter::ParseBoundingBoxScript_fx(WPuppet* pet, eScripFormat format)
{
	bool bAttached = false;

	for (w_bound_box* box = pet->m_bbList.Start(); box;
		box = pet->m_bbList.Next())
	{
		if (!box->info->option || !box->bone ||
			box->bone->m_flag.GetFlag(WBone::INVISIBLE))
			continue;

		const char* str = box->info->option;
		while (ParseToken(&str, format))
		{
			char name[64];
			eEffectType type;

			if (ParseFxName(&str, name, format, type))
			{
				Attacher attacher;
				attacher.mat[0] = &box->bone->m_matrix;
				attacher.pos[0] = &box->info->spherePivot;
				bAttached = AttachFx(name, &attacher, type);
			}
		}
	}
	if (bAttached)
		return ms_nextID645++;

	return -1;
}
int FxInterpreter::ParseCharBoundingBoxScript_fx(WPuppet* pet,
	eScripFormat format)
{
	return -1;
}

int FxInterpreter::ParseCharFrameDataScrip_fx(WPuppet* pet, eScripFormat format)
{
	return -1;
}

bool FxInterpreter::AttachFx(const char* name, const Attacher* attacher,
	eEffectType type)
{
	if (name && attacher)
	{
		if (type == eET_SPRAY)
		{
			void* pFx = CFx::Instance()->Attach(*attacher, name, false, NULL);
			ms_fxList645.push_back(sFxInfo(ms_nextID645, eET_SPRAY, pFx));
			return true;
		}
		else if (type == eET_SEQUENCE)
		{
			void* pFx = CFx::Instance()->Attach(*attacher, name, false, NULL);
			ms_fxList645.push_back(sFxInfo(ms_nextID645, eET_SEQUENCE, pFx));
			return true;
		}
	}
	return false;
}

void FxInterpreter::DetachFx645(int id)
{
	if (id < 0)
		return;
	std::list<sFxInfo>::iterator it = ms_fxList645.begin();
	while (it != ms_fxList645.end())
	{
		if ((*it).id == id)
		{
			std::list<sFxInfo>::iterator del = it++;
			(*del).DetachSingleFx();
			ms_fxList645.erase(del);
		}
		else
		{
			if ((*it).id > id)
				return;
			it++;
		}
	}
}

void FxInterpreter::DetachFxAll645()
{
	for (std::list<sFxInfo>::iterator it = ms_fxList645.begin();
		it != ms_fxList645.end(); it++)
		(*it).DetachSingleFx();
	ms_fxList645.clear();
}
