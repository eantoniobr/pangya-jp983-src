#!/usr/bin/env python3
"""C101: .obj provisórios com jp983_rastro() nas unidades da B (src/projectg/jp/) e da A, sem editar os arquivos delas.

Uso: python3 tools/v6/f4rastro/rastro_jp.py TAG_PCH_A DIR_BOBJ TAG_SAIDA_A
  - unidades jp/: copia build/B/obj/*.obj para DIR_BOBJ (hardlink) e troca as instrumentadas (flags do jpbuild);
  - unidades da A: build/TAG_SAIDA_A/obj/<unidade>.obj (flags do pgbuild, pch da TAG_PCH_A).
  Depois: make exe ENTREGA=... V6_PG="TAG_SAIDA_A pg-aNNN" V6_BOBJ=DIR_BOBJ
Rastro atual: quem fecha o "Loading..." do lobby (LobbyPlayer -> 0x57 -> RFLobbyDesktop::HandleMsg983).
"""
import os, sys, shutil
ROOT = '/root/jp983src'
sys.path.insert(0, ROOT + '/tools/f32')
import pgbuild as P

DECL = 'extern "C" void __cdecl jp983_rastro(const char* fmt, ...);\n'

# C101 (lobbyplayer/rflobbydesktop: "Loading...") está no git (aa0f33dc). C102: Start Game da "Strategy" sem pacote 0x0E.
RASTRO_JP = [
    ('src/projectg/jp/gameroomdlg.cpp', [
        ('void FrGameRoomDlg::OnStartBtnUp()\n{\n',
         '\tjp983_rastro("C102 OnStartBtnUp start=%p en=%d doc=%p master=%08x my=%08x lock=%d req=%d ctl=%d ver=%d id=%08x", m_pStart, m_pStart ? (int)m_pStart->IsEnabled() : -1, m_pDoc, m_pDoc ? ROOMDOC_MASTER(m_pDoc) : 0, MyGuid(false), (int)m_bLockControls, (int)m_bRoomStateReq, (int)DOCJP()->IsControlServerService983(2), (int)LatestVersion983(), Doc()->m_myInfo.info.dwIdentity);\n'),
        ('\tstd::list<sSlotInfo>& slotList = Doc()->m_slotList;\n\tbool bMaster = false;\n',
         '\tjp983_rastro("C102 UpdateMaster983 slots=%d id=%08x", (int)slotList.size(), Doc()->m_myInfo.info.dwIdentity);\n'),
    ]),
]

# unidades da A (compila a fonte ATUAL da A); (âncora, texto, 'troca') troca a âncora em vez de inserir depois
RASTRO_A = []


def instr(src, ins, out_dir):
    txt = open(ROOT + '/' + src, encoding='latin-1').read()
    for e in ins:
        anc, add = e[0], e[1]
        n = txt.count(anc)
        if n != 1:
            sys.exit('FALHA âncora (%d ocorrências) em %s: %r' % (n, src, anc[:60]))
        txt = txt.replace(anc, add if len(e) > 2 and e[2] == 'troca' else anc + add)
    cp = '%s/rastro_src/%s' % (out_dir, src)
    os.makedirs(os.path.dirname(cp), exist_ok=True)
    open(cp, 'w', encoding='latin-1').write(DECL + txt)
    return cp


def main():
    tag_pch, bobj, tag_out = sys.argv[1], os.path.abspath(sys.argv[2]), sys.argv[3]
    os.makedirs(bobj, exist_ok=True)
    for f in os.listdir(ROOT + '/build/B/obj'):
        if f.endswith('.obj') and not os.path.exists(bobj + '/' + f):
            os.link(ROOT + '/build/B/obj/' + f, bobj + '/' + f)
    ok = True
    for src, ins in RASTRO_JP:
        cp = instr(src, ins, bobj + '/..')
        obj = '%s/%s.obj' % (bobj, os.path.basename(src)[:-4])
        if os.path.exists(obj):
            os.unlink(obj)
        args = P.OPT.split() + P.DEFS.split() + ['/I' + P.absp(i) for i in ['include/jp', 'src/projectg/jp'] + P.INC] + \
            ['/I' + ROOT + '/' + os.path.dirname(src), '/FIstdafx.h']
        rc = P.cl(args + ['/Fo' + obj, cp], obj[:-4] + '.log')
        print(src, 'rc=%d' % rc, '' if rc == 0 else open(obj[:-4] + '.log', errors='replace').read()[-800:])
        ok = ok and rc == 0
    units = {u[0]: u for u in P.units()}
    class A: pass
    a = A(); a.flags = None; a.B = ROOT + '/build/' + tag_pch
    for src, ins in RASTRO_A:
        cp = instr(src, ins, ROOT + '/build/' + tag_out)
        _, _, pch, fi, einc = units[src]
        args = P.base_args(a, einc, src) + fi + ['/I' + ROOT + '/' + os.path.dirname(src)]
        if pch: args += ['/Yu' + os.path.basename(pch)[:-4] + '.h', '/Fp' + P.pch_file(a, pch)]
        obj = '%s/build/%s/obj/%s.obj' % (ROOT, tag_out, src[:-4])
        os.makedirs(os.path.dirname(obj), exist_ok=True)
        rc = P.cl(args + ['/Fo' + obj, cp], obj[:-4] + '.log')
        print(src, 'rc=%d' % rc, '' if rc == 0 else open(obj[:-4] + '.log', errors='replace').read()[-800:])
        ok = ok and rc == 0
    sys.exit(0 if ok else 1)

main()
