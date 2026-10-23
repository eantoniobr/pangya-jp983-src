#!/usr/bin/env python3
"""C93: .obj provisório com jp983_rastro() sem editar o arquivo da A.

Uso: python3 tools/v6/f4rastro/rastro_obj.py TAG_PCH TAG_SAIDA [unidade ...]   (sem unidade: todas de RASTROS)
Para cada unidade: lê a fonte original, insere as linhas de rastro depois da âncora (texto exato, 1 ocorrência),
grava a cópia em build/TAG_SAIDA/rastro_src/ e compila com as mesmas flags do pgbuild (pch da TAG_PCH) para
build/TAG_SAIDA/obj/<unidade>.obj (o make exe com V6_SEM=TAG_SAIDA põe esse .obj no lugar do da A).
"""
import os, sys
ROOT = '/root/jp983src'
sys.path.insert(0, ROOT + '/tools/f32')
import pgbuild as P

DECL = 'extern "C" void __cdecl jp983_rastro(const char* fmt, ...);\n#include <intrin.h>\n#pragma intrinsic(_ReturnAddress)\n'

# (unidade, [(âncora, texto inserido depois da âncora)])
RASTROS = [
    ('src/fresh/source/frform.cpp', [
        ('\tFrElementForm* pForm = pDoc->GetForm(lpszTemplateID);\n',
         '\tjp983_rastro("FrForm::_Init form=%s ret=%p this=%p", lpszTemplateID ? lpszTemplateID : "(null)", _ReturnAddress(), this);\n'),
        ('void FrForm::SetMessage(const char* msg, bool spaceAlign)\n{\n',
         '\t{ char hx[100]; int i = 0; const unsigned char* p = (const unsigned char*)(msg ? msg : "");\n'
         '\t  for (; p[i] && i < 32; ++i) { static const char d[] = "0123456789abcdef"; hx[i*3] = d[p[i]>>4]; hx[i*3+1] = d[p[i]&15]; hx[i*3+2] = 32; }\n'
         '\t  hx[i*3] = 0;\n'
         '\t  jp983_rastro("FrForm::SetMessage form=%p ret=%p static=%p edit=%p len=%d txt=[%.200s] hex=%s", this, _ReturnAddress(),\n'
         '\t    m_pMsgStatic, m_pMsgEdit, msg ? (int)strlen(msg) : -1, msg ? msg : "(null)", hx); }\n'),
    ]),
    # C93 (c93-2): campo ID com lixo e senha "******" no formulário de login: de onde vem o texto?
    ('src/projectg/logindlg.cpp', [
        ('\tm_pId->SetCharLimit(22, true);\n',
         '\t{ const char* l = COption::Instance()->gGetLastLoginID();\n'
         '\t  jp983_rastro("FrLoginDlg::OnIdInit last=[%.40s] move=%d web=%d moveId=[%.40s] pg=%p", l ? l : "(null)",\n'
         '\t    (int)CProjectG::Instance()->m_bMoveLoginServer, (int)CLoginInfo::Instance()->IsWebLogin(),\n'
         '\t    CProjectG::Instance()->m_moveLoginId.c_str(), CProjectG::Instance()); }\n'),
        ('\tm_pPassword = DYNAMIC_CAST(FrEdit, (FrWnd*)param);\n',
         '\tjp983_rastro("FrLoginDlg::OnPasswordInit move=%d web=%d pwlen=%d", (int)CProjectG::Instance()->m_bMoveLoginServer,\n'
         '\t  (int)CLoginInfo::Instance()->IsWebLogin(), (int)CProjectG::Instance()->m_moveLoginPassword.size());\n'),
    ]),
]

def main():
    tag_pch, tag_out = sys.argv[1], sys.argv[2]
    units = {u[0]: u for u in P.units()}
    class A: pass
    a = A(); a.flags = None; a.B = ROOT + '/build/' + tag_pch
    ok = True
    sel = sys.argv[3:]
    for src, ins in RASTROS:
        if sel and src not in sel: continue
        txt = open(ROOT + '/' + src, encoding='latin-1').read()
        for anc, add in ins:
            n = txt.count(anc)
            if n != 1:
                print('FALHA âncora (%d ocorrências) em %s: %r' % (n, src, anc[:60])); ok = False; continue
            txt = txt.replace(anc, anc + add)
        cp = '%s/build/%s/rastro_src/%s' % (ROOT, tag_out, src)
        os.makedirs(os.path.dirname(cp), exist_ok=True)
        open(cp, 'w', encoding='latin-1').write(DECL + txt)
        _, _, pch, fi, einc = units[src]
        args = P.base_args(a, einc, src) + fi + ['/I' + ROOT + '/' + os.path.dirname(src)]
        if pch: args += ['/Yu' + os.path.basename(pch)[:-4] + '.h', '/Fp' + P.pch_file(a, pch)]
        obj = '%s/build/%s/obj/%s.obj' % (ROOT, tag_out, src[:-4])
        os.makedirs(os.path.dirname(obj), exist_ok=True)
        rc = P.cl(args + ['/Fo' + obj, cp], obj[:-4] + '.log')
        print(src, 'rc=%d' % rc, obj if rc == 0 else open(obj[:-4] + '.log', errors='replace').read()[-800:])
        ok = ok and rc == 0
    sys.exit(0 if ok else 1)

main()
