// messengerpackets.h - frente C (pacotes). JP 983: blocos do sub-protocolo do mensageiro (caso 0x30 do CTask::OnPacketCommon,
// 009c70b0). Os nomes são nossos; tamanho e campos medidos no exe 983.
#pragma once

#include <vector>
// usa sUserPosition (src/shared/globalgamedefine.h): incluir depois dele

#pragma pack(push, 1)
// sub-caso 0x115 (009c80f9): estado de um amigo. Bloco de 0x54 lido de uma vez (construtor 009baa30).
struct sFriendStateNotify983
{
	unsigned long uid;		// +0x00
	unsigned long state;	// +0x04 (0 jogando, 1 ausente, 3 ocupado, 4 voltou, 5 saiu da partida)
	unsigned char unk8;		// +0x08
	sUserPosition pos;		// +0x09

	sFriendStateNotify983()
	{
		uid = 0xffffffff;
		state = 5;
		unk8 = 0;
	}
};
#pragma pack(pop)
C_ASSERT(sizeof(sFriendStateNotify983) == 0x54);
C_ASSERT(offsetof(sFriendStateNotify983, pos.iServerGUID) == 0xf);

// sub-caso 0x127 (009c82c4) e caso 0x118 (009cfc0a): convite de guilda recebido; elemento (0x2c) do vetor de CSharedDoc+0x10ff8
// (construtor 008fe430, cópia 009ba540 = rep movsd de 0xb dwords, push_back 009c08a0, esvaziar 009bf8f0).
// O 983 monta um por volta do laço no caso 0x118 e não chama destrutor: os quatro dwords do fim não são um std::vector
// (embora o desenho - três zerados + um solto - seja o do std::vector deste build, que tem 0x10).
struct sGuildInvite983
{
	unsigned long dw0;			// +0x00: 2o Decode4 do pacote (-1 no construtor)
	unsigned long dw4;			// +0x04: 1o Decode4 do pacote
	char szName[20];			// +0x08: nome da guilda
	unsigned long dw1c[3];		// +0x1c: zerados no construtor (uso não lido)
	unsigned long dw28;			// +0x28: o construtor não toca

	sGuildInvite983() { dw0 = 0xffffffff; dw1c[0] = dw1c[1] = dw1c[2] = 0; }
};
C_ASSERT(sizeof(sGuildInvite983) == 0x2c);
C_ASSERT(offsetof(sGuildInvite983, dw1c) == 0x1c);
