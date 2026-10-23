#!/usr/bin/env python3
"""casos_s66.py — sessão 66: mais casos do 983 no ramo em C do CTask::OnPacketCommon (src/projectg/taskmanager.cpp), lidos no
desmonte do despachante comum 009c20a0 (out/F3.5/s66/dx/). Idempotente (marca 'S66:'). Arquivo em latin1."""
import sys
P = '/root/jp983src/src/projectg/taskmanager.cpp'
s = open(P, encoding='latin1', newline='').read()
if 'S66:' in s: sys.exit('ja aplicado')
nl = '\r\n' if '\r\n' in s else '\n'
i = s.index('\t// 983: 0x1dd-0x1e0 = fam', s.index('S65b:'))
MSG2 = '\t\tAfxGetTask()->SendMsgToMainActor(MsgObject(NULL, 2, 0, 0, 0, 0, 0));\n'
ERR = ('\t\tint error = packet.Decode4();\n\t\tif (error)\n\t\t{\n'
       '\t\t\tAfxGetTask()->SendMsgToMainActor(MsgObject(NULL, 0x27, error, 0, 0, 0, 0));\n\t\t\tbreak;\n\t\t}\n')
blk = '''\t// S66: mais casos do 983 sem par no OnPacketCommon do 645 (desmonte em out/F3.5/s66/dx/).
\tcase 0x1d4: // 009d3421
\t{
\t\tif (packet.Decode4() != 0)
\t\t\tbreak;
\t\tDoc()->m_unk983_11254 = packet.DecodeStr();
\t\tAfxGetTask()->SendMsgToMainActor(MsgObject(NULL, 0x1b2, 0, 0, 0, 0, 0));
\t}
\tbreak;
\tcase 0x1d9: // 009d2670: nível (só o byte baixo) e experiência do próprio jogador
\t{
\t\tunsigned long level = packet.Decode4();
\t\tunsigned long exp = packet.Decode4();
\t\tDoc()->m_myInfo.stat.Level = (unsigned char)level;
\t\tDoc()->m_myInfo.stat.dwExp = exp;
\t}
\tbreak;
\tcase 0x21c: // 009d4aee
\tcase 0x224: // 009d50e8
\t{
\t\tint error = packet.Decode4();
\t\tif (error)
\t\t\tAfxGetTask()->SendMsgToMainActor(MsgObject(NULL, 0x27, error, 0, 0, 0, 0));
\t}
\tbreak;
\tcase 0x22a: // 009d5391
\t{
''' + MSG2 + ERR + '''\t\tint value = packet.Decode4();
\t\tAfxGetTask()->SendMsgToMainActor(MsgObject(NULL, 0x326, (int)&value, 0, 0, 0, 0));
\t}
\tbreak;
\tcase 0x235: // 009d55b6: os 10 itens equipados (sMyInfo +0x296)
\t{
\t\tfor (int i = 0; i < 10; i++)
\t\t\tDoc()->m_myInfo.userEquip.tidItemSlot[i] = packet.Decode4();
\t}
\tbreak;
\tcase 0x24d: // 009d5fea (os três ids no mesmo corpo; o id escolhe 0, 1 ou 2)
\tcase 0x24e:
\tcase 0x24f:
\t{
''' + MSG2 + ERR + '''\t\tAfxGetTask()->GetActor(s_gatewayActor[1])
\t\t\t<< MsgObject(NULL, 0x753c, type == 0x24d ? 0 : (type == 0x24e ? 1 : 2), (int)&packet, 0, 0, 0);
\t}
\tbreak;
\tcase 0x253: // 009d63b3 (0062bf80 = grava CSharedDoc+0x11638)
\t{
''' + MSG2 + ERR + '''\t\tDoc()->m_unk983_11638 = 6;
\t}
\tbreak;
\tcase 0x25b: // 009d2cc6
\t{
\t\tint error = packet.Decode4();
\t\tif (error)
\t\t{
\t\t\tSendMsgToMainActor(MsgObject(NULL, 0x27, error, 0, 0, 0, 0));
\t\t\tbreak;
\t\t}
\t\tGetActor(s_gatewayActor[1])
\t\t\t<< MsgObject(NULL, 0x753e, 2, (int)&packet, 0, 0, 0);
\t}
\tbreak;
\tcase 0x276: // 009d4332: o valor vai a WNetworkSystem 00a4d6d0, que no 983 é vazia (`ret 4`)
\t\tpacket.Decode4();
\t\tbreak;
\tcase 0x277: // 009d6f8d
\tcase 0x27d: // 009d2b9c
\t{
''' + MSG2 + '''\t\tint error = packet.Decode4();
\t\tif (error)
\t\t\tAfxGetTask()->SendMsgToMainActor(MsgObject(NULL, 0x27, error, 0, 0, 0, 0));
\t}
\tbreak;
'''
s = s[:i] + blk.replace('\n', nl) + s[i:]
open(P, 'w', encoding='latin1', newline='').write(s)
print('ok')
