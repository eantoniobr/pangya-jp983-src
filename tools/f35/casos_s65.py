#!/usr/bin/env python3
"""casos_s65.py — sessão 65: escreve em src/projectg/taskmanager.cpp (ramo em C do CTask::OnPacketCommon) os casos do 983
lidos no desmonte do despachante comum 009c20a0. Idempotente (marca 'S65'). Arquivo em latin1 (não passar por editor UTF-8)."""
import re, sys
P = '/root/jp983src/src/projectg/taskmanager.cpp'
s = open(P, encoding='latin1', newline='').read()
if 'S65:' in s: sys.exit('ja aplicado')
nl = '\r\n' if '\r\n' in s else '\n'

# 1) caso 0x11f: corpo do 983 (009c8bd6)
old = re.search(r'\tcase 0x11f:\r?\n\t\{.*?\r?\n\t\}\r?\n\tbreak;\r?\n', s[s.index('int CTask::OnPacketCommon(WReceivedPacket& packet)\n{') if 'int CTask::OnPacketCommon(WReceivedPacket& packet)\n{' in s else 0:], re.S)
start = s.rindex('\nint CTask::OnPacketCommon(WReceivedPacket& packet)')
m = re.compile(r'\tcase 0x11f:\r?\n\t\{.*?\r?\n\t\}\r?\n\tbreak;\r?\n', re.S).search(s, start)
assert m and 'm_tutorialComplete' in m.group(0) and m.group(0).count('case ') == 1, m
new11f = '''\tcase 0x11f:
\t{
\t\t// S65: corpo do 983 (009c8bd6). O 645 testava IS_EXACTKINDOF(CTutorialTask) e postava 0x151 a "TutorialMain".
\t\tunsigned char kind = packet.Decode1();
\t\tunsigned char value = packet.Decode1();

\t\tif (kind == 3)
\t\t\tpacket.DecodeBuffer(Doc()->m_tutorialComplete, 12);

\t\tIContentsDataContainer* pContainer;
\t\tCContentsDoc::Instance()->GetContainer((localContentType_t)0xa4, pContainer); // 006ab7d0; resultado sem uso no 983

\t\tif (AfxGetTask()->IsCurrentActor983("tutorialmain"))
\t\t\tAfxGetTask()->SendMsgToMainActor(MsgObject(NULL, 0x1bc, kind, value, 0, 0, 0));
\t}
\tbreak;
'''
s = s[:m.start()] + new11f.replace('\n', nl) + s[m.end():]

GW = 'GetActor(s_gatewayActor[1])'
def gw(idp, msg, sub, pre2=True, ctx='AfxGetTask()->', arg='(int)&packet', extra0=False):
    a = '%s, %s, %s, 0, 0' % (sub, '0' if extra0 else arg, '0') if not extra0 else '%s, 0, 0, 0, 0' % sub
    if not extra0: a = '%s, %s, 0, 0, 0' % (sub, arg)
    o = '\tcase %s:\n\t{\n' % idp
    if pre2: o += '\t\tAfxGetTask()->SendMsgToMainActor(MsgObject(NULL, 2, 0, 0, 0, 0, 0));\n'
    o += '\t\tint error = packet.Decode4();\n\t\tif (error)\n\t\t{\n\t\t\tAfxGetTask()->SendMsgToMainActor(MsgObject(NULL, 0x27, error, 0, 0, 0, 0));\n\t\t\tbreak;\n\t\t}\n'
    o += '\t\t%s%s\n\t\t\t<< MsgObject(NULL, %s, %s);\n\t}\n\tbreak;\n' % (ctx, GW, msg, a)
    return o

blk = '''\t// S65: casos do 983 sem par no OnPacketCommon do 645, escritos pelo desmonte do despachante comum (009c20a0).
\t// Correio e móveis do my room: no 645 ficam em CRealMyRoomTask::OnPacket (ids 0x125, 0x13f, 0x141, 0x143, 0x145, 0x181);
\t// no 983 vão ao ator principal da tarefa. Mensagens do 983: 0x29d (era 0x228), 0x2bf (era 0x244), 0x2a6, 0x2a4, 0x107.
\tcase 0x12d: // 009d1b97
\t{
\t\tDoc()->m_furnitureList.clear();
\t\tunsigned long result = packet.Decode4();
\t\tif (result == 1)
\t\t{
\t\t\tDoc()->m_furnitureList.clear();
\t\t\tint count = packet.Decode2();
\t\t\tfor (; count > 0; --count)
\t\t\t{
\t\t\t\tsFurniture_List furniture;
\t\t\t\tmemset(&furniture, 0, 0x1b);
\t\t\t\tpacket.DecodeBuffer(&furniture, 0x1b);
\t\t\t\tDoc()->AddFurniture(furniture);
\t\t\t}
\t\t}
\t\telse
\t\t{
\t\t\tAfxGetTask()->GetMainActor() << MsgObject(NULL, 0x2a6, 0x12d, result, 0, 0, 0);
\t\t}
\t\tIActor* pMain = AfxGetTask()->GetMainActor();
\t\tif (pMain)
\t\t{
\t\t\tpMain << MsgObject(NULL, 0x107, 0, 0, 0, 0, 0);
\t\t\tpMain << MsgObject(NULL, 2, 0, 0, 0, 0, 0);
\t\t}
\t}
\tbreak;
\tcase 0x147: // 009d1fbb
\t{
\t\tunsigned char result = packet.Decode1();
\t\tAfxGetTask()->GetMainActor()
\t\t\t<< MsgObject(NULL, 0x29d, 0x147, result, 0, 0, 0)
\t\t\t<< MsgObject(NULL, 0x2bf, 1, 0, 0, 0, 0);
\t}
\tbreak;
\tcase 0x149: // 009d20fb
\tcase 0x14b: // 009d2184 (mesmo corpo; o 983 também manda 0x147 como subcódigo)
\t{
\t\tint result = packet.Decode1();
\t\tAfxGetTask()->GetMainActor()
\t\t\t<< MsgObject(NULL, 2, 0, 0, 0, 0, 0)
\t\t\t<< MsgObject(NULL, 0x29d, 0x147, result, 0, 0, 0)
\t\t\t<< MsgObject(NULL, 0x2bf, 1, 0, 0, 0, 0);
\t}
\tbreak;
\tcase 0x14d: // 009d22da
\t{
\t\tint result = packet.Decode1();
\t\tAfxGetTask()->GetMainActor()
\t\t\t<< MsgObject(NULL, 0x29d, 0x14d, result, 0, 0, 0)
\t\t\t<< MsgObject(NULL, 2, 0, 0, 0, 0, 0)
\t\t\t<< MsgObject(NULL, 0x2bf, 1, 0, 0, 0, 0);
\t}
\tbreak;
\tcase 0x164: // 009d21dd (sem leitura)
\t{
\t\tAfxGetTask()->GetMainActor()
\t\t\t<< MsgObject(NULL, 2, 0, 0, 0, 0, 0)
\t\t\t<< MsgObject(NULL, 0x2a4, 0, 0, 0, 0, 0)
\t\t\t<< MsgObject(NULL, 0x2bf, 1, 0, 0, 0, 0);
\t}
\tbreak;
\tcase 0x165: // 009d225a
\t{
\t\tint value = packet.Decode4();
\t\tAfxGetTask()->GetMainActor()
\t\t\t<< MsgObject(NULL, 0x29d, 0x165, value, 0, 0, 0)
\t\t\t<< MsgObject(NULL, 2, 0, 0, 0, 0, 0)
\t\t\t<< MsgObject(NULL, 0x2bf, 1, 0, 0, 0, 0);
\t}
\tbreak;
\tcase 0x17c: // 009d2022: envio 0x29 ao MSN (no 645, 0x27) e limpa m_giftName/m_giftIndex (983: Doc+0x10d60/+0x10d7c)
\t{
\t\tif (!WNetworkSystem::Instance()->IsConnected(WNetworkSystem::NET_MSN))
\t\t\tbreak;

\t\tWSendPacket send(0x29);
\t\tsend.EncodeStr(MyId());
\t\tsend.EncodeStr(MyId());
\t\tsend.Send(TO_MSN);
\t\tDoc()->m_giftName = "";
\t\tDoc()->m_giftIndex = -1;
\t}
\tbreak;
\t// S65: família do Gateway do 983 (mensagens 0x7534/0x7535/0x753a/0x753e/0x753f ao ator "Gateway"; erro != 0 vira a
\t// mensagem 0x27 ao ator principal). O tratador dessas mensagens no ator Gateway do 983 não está escrito.
\tcase 0x1ef: // 009d3553
\t{
\t\tint values[4];
\t\tvalues[0] = packet.Decode4();
\t\tvalues[1] = packet.Decode4();
\t\tvalues[2] = packet.Decode4();
\t\tvalues[3] = packet.Decode4();
\t\tAfxGetTask()->GetActor(s_gatewayActor[1])
\t\t\t<< MsgObject(NULL, 0x7535, 0xd, (int)values, 0, 0, 0);
\t}
\tbreak;
\tcase 0x202: // 009d36dc (o valor lido não é usado)
\t{
\t\tpacket.Decode4();
\t\tGetActor(s_gatewayActor[1])
\t\t\t<< MsgObject(NULL, 0x7534, 2, 0, 0, 0, 0);
\t}
\tbreak;
\tcase 0x25a: // 009d2d03
\t{
\t\tint error = packet.Decode4();
\t\tif (error)
\t\t{
\t\t\tSendMsgToMainActor(MsgObject(NULL, 0x27, error, 0, 0, 0, 0));
\t\t\tbreak;
\t\t}
\t\tGetActor(s_gatewayActor[1])
\t\t\t<< MsgObject(NULL, 0x753e, 1, (int)&packet, 0, 0, 0);
\t}
\tbreak;
'''
blk += gw('0x220', '0x753a', '4', pre2=False) .replace('case 0x220:', 'case 0x220: // 009d4d88')
for idp, sub, va in (('0x225', '2', '009d5116'), ('0x226', '3', '009d51a8'), ('0x227', '5', '009d523a'), ('0x228', '6', '009d52cc'), ('0x22c', '9', '009d542f')):
    blk += gw(idp, '0x753a', sub).replace('case %s:' % idp, 'case %s: // %s' % (idp, va))
blk += gw('0x22d', '0x753a', '8', pre2=False).replace('case 0x22d:', 'case 0x22d: // 009d54c1')
blk += '''\tcase 0x22e: // 009d5512 (sem leitura)
\t{
\t\tAfxGetTask()->SendMsgToMainActor(MsgObject(NULL, 2, 0, 0, 0, 0, 0));
\t\tAfxGetTask()->GetActor(s_gatewayActor[1])
\t\t\t<< MsgObject(NULL, 0x753a, 0xa, (int)&packet, 0, 0, 0);
\t}
\tbreak;
'''
for idp, sub, va in (('0x278', '3', '009d6ffc'), ('0x279', '2', '009d708f'), ('0x27a', '1', '009d7122'), ('0x27b', '4', '009d71b4'), ('0x27c', '5', '009d7246')):
    blk += gw(idp, '0x753f', sub, extra0=True).replace('case %s:' % idp, 'case %s: // %s' % (idp, va))
anchor = '\t// 983: 0x1dd-0x1e0 = fam'
i = s.index(anchor, start)
s = s[:i] + blk.replace('\n', nl) + s[i:]

# 2) CTask::IsCurrentActor983 (009bd4f0), antes de CTask::GetActor
fn = '''// S65: 983 009bd4f0 (sem par no 645): o ator de m_pDummyActor983 (+0x1fc), se não for o ms_pDummyActor, tem em +0x1a0 um
// objeto cujo nome (std::string em +0x64, via 00be76b0) é comparado com `name`. Nome e tipos provisórios.
bool CTask::IsCurrentActor983(const char* name)
{
\tif (m_pDummyActor983 == ms_pDummyActor)
\t\treturn false;
\tvoid* pObj = *(void**)((char*)m_pDummyActor983 + 0x1a0);
\tif (pObj == NULL)
\t\treturn false;
\treturn ((std::string*)((char*)pObj + 0x64))->compare(name) == 0;
}

'''
k = s.index('IActor* CTask::GetActor(const char* name)')
s = s[:k] + fn.replace('\n', nl) + s[k:]
open(P, 'w', encoding='latin1', newline='').write(s)

H = '/root/jp983src/src/projectg/taskmanager.h'
h = open(H, encoding='latin1', newline='').read()
a = '\tIActor* GetActor(const char* name);'
assert a in h
h = h.replace(a, a + nl + '\tbool IsCurrentActor983(const char* name); // S65: 983 009bd4f0', 1)
open(H, 'w', encoding='latin1', newline='').write(h)
print('ok')
# Nota: os 4 casos 'S65b' (0x229, 0x22b, 0x230, 0x231) foram inseridos depois, direto no fonte, antes do mesmo marcador
# ('// 983: 0x1dd-0x1e0'); o estado final é o do git.
