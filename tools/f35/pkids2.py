#!/usr/bin/env python3
"""Ids de pacote ENVIADO que a sessao 61 deixou pendentes (out/F3.5/s61/pendentes_envio.tsv): decisao id a id (sessao 63).
  pkids2.py plano  OUT -> OUT/pkids2_envio.tsv (arquivo, linha, id_645, decisao, id_983, prova)
  pkids2.py aplica OUT -> edita as linhas e grava o plano. Nao roda duas vezes (confere o texto da linha).
Decisao:
  troca   = o id do 983 e conhecido (prova: par/assinatura+unidade no exe 983, ou faixa com os dois vizinhos no mesmo salto)
  mantem  = faixa +0 (ate 0x82) ou id 0 de pacote local: o numero vale no 983 mesmo sem o cliente 983 enviar
  sem983  = o id nao tem lugar no enum do 983 (0xc4-0xcd: 10 ids retirados entre 0xcb e 0xcc) ou o salto e desconhecido
            (guilda 0xfe-0x112, 0x113, 0x11a, 0x15e): a declaracao vira WSendPacketSem983 (packet.h), que nao envia nada
"""
import sys, os, csv, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PEND = os.path.join(R, 'out/F3.5/s61/pendentes_envio.tsv')
TROCA = {  # id_645: (id_983, prova)
    0x85: (0x88, 'assinatura: GameGuardMsgHandler::Process do 983 envia P(0x88) EB(0x10)'),
    0x86: (0x89, 'assinatura: CConsole::Command do 983 envia P(0x89) sem campos (+3)'),
    0xa2: (0xaa, 'assinatura: 00afa810 P(0xaa) EB(0x109) (+8)'),
    0xa3: (0xab, 'assinatura+unidade: 0060f5c0 P(0xab) E4 E4 (+8)'),
    0xc3: (0xcb, 'assinatura+unidade: 00505380 P(0xcb) E4 (+8)'),
    0xce: (0xcc, 'assinatura+unidade: 007fce20 P(0xcc) ES (-2)'),
    0xcf: (0xcd, 'assinatura+unidade: 007fc660/005a8360 P(0xcd) E4 E2 (-2)'),
    0xd0: (0xce, 'assinatura+unidade: 007fc930/007fcab0 P(0xce) E1 EB(0xb0) (-2; bloco 0xae no fonte)'),
    0xd1: (0xcf, 'assinatura+unidade: 007fc930/007fcab0 P(0xcf) E1 EB(0xb0) (-2; bloco 0xae no fonte)'),
    0xd2: (0xd0, 'assinatura+unidade: 007fce20 P(0xd0) ES (-2)'),
    0xd3: (0xd1, 'assinatura+unidade: 007fce20 P(0xd1) ES ES (-2)'),
    0xd4: (0xd2, 'assinatura+unidade: 007fce20 P(0xd2) E1 ES (-2)'),
    0xef: (0xed, 'assinatura+unidade: 00594f90 P(0xed) sem campos (-2)'),
    0xf1: (0xef, 'assinatura: FrRandomBoxProgress 008c5610 P(0xef) E4 (-2)'),
    0xf6: (0xf4, 'assinatura: CWorkAliveCheck::Act 009be990 P(0xf4) E4 (-2)'),
    0x7e: (0x158, 'par 008e2d70 P(0x158); CAMPOS DIFEREM (983: E2 E4 E1 E4 E4 ED)'),
    0x92: (0x95, 'faixa +3 (0x8e e 0x95 vizinhos); o cliente 983 nao envia'),
    0x93: (0x96, 'faixa +3 (0x8e e 0x95 vizinhos); o cliente 983 nao envia'),
    0xae: (0xb6, 'faixa +8; o cliente 983 nao envia'),
    0xbb: (0xc3, 'faixa +8; o cliente 983 nao envia (correio novo do 983: 0x145 em 0065c2d0, outros campos)'),
    0xd9: (0xd7, 'faixa -2; o cliente 983 nao envia'),
    0xdc: (0xda, 'faixa -2; o cliente 983 nao envia'),
    0xdd: (0xdb, 'faixa -2; o cliente 983 nao envia'),
    0xf0: (0xee, 'faixa -2 (0xee e 0xf1 vizinhos); o cliente 983 nao envia'),
}
MANTEM = {0x0: 'id 0 (pacote local/preenchido depois)', 0x83: 'assinatura+unidade: 00af5e00 P(0x83) (+0)',
          0x2b: 'faixa +0', 0x4c: 'faixa +0', 0x52: 'faixa +0', 0x59: 'faixa +0', 0x6d: 'faixa +0', 0x72: 'faixa +0'}
JA = {0xbc, 0xbe}  # correio, sessao 62
def decide(i):
    if i in JA: return ('ja_s62', '', '')
    if i in TROCA: return ('troca', '0x%x' % TROCA[i][0], TROCA[i][1])
    if i in MANTEM: return ('mantem', '0x%x' % i, MANTEM[i])
    if 0xc4 <= i <= 0xcd: return ('sem983', '', '10 ids retirados do enum entre 0xcb (=645 0xc3) e 0xcc (=645 0xce)')
    return ('sem983', '', 'salto desconhecido nesta faixa; o 983 nao tem envio com a mesma forma')
def main():
    modo, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    rows = list(csv.DictReader(open(PEND), delimiter='\t'))
    plano = []; ed = {}
    for r in rows:
        i = int(r['id_645'], 16); d, novo, prova = decide(i)
        plano.append([r['arquivo'], r['linha'], r['id_645'], d, novo, prova])
        if modo == 'aplica' and d in ('troca', 'sem983'):
            ed.setdefault(r['arquivo'], []).append((int(r['linha']), r['texto'], d, novo, i))
    for arq, lst in ed.items():
        p = os.path.join(R, arq); L = open(p, 'rb').read().split(b'\n')
        for ln, txt, d, novo, i in lst:
            s = L[ln - 1]; cr = s.endswith(b'\r'); s = s.rstrip(b'\r')
            m = re.search(rb'\b(WSendPacket|RbSendPacketExtern)\b(.*?\(\s*(?:\(enumClientPacket\)\s*)?)' + re.escape(txt.encode()) + rb'(\s*\))', s)
            assert m and b'JP 983 (s6' not in s, (arq, ln, s)
            if d == 'troca':
                s = s[:m.start(3)-len(txt)] + novo.encode() + s[m.start(3):] + b' // JP 983 (s63): 0x%x no KR 645' % i
            else:
                assert m.group(1) == b'WSendPacket'
                s = s[:m.start(1)] + b'WSendPacketSem983' + s[m.end(1):] + b' // JP 983 (s63): id do KR 645 sem id do 983; nao envia'
            L[ln - 1] = s + (b'\r' if cr else b'')
        open(p, 'wb').write(b'\n'.join(L))
    with open(os.path.join(out, 'pkids2_envio.tsv'), 'w') as f:
        f.write('arquivo\tlinha\tid_645\tdecisao\tid_983\tprova\n')
        for x in plano: f.write('\t'.join(x) + '\n')
    import collections
    print(collections.Counter(x[3] for x in plano), 'arquivos editados:', len(ed))
main()
