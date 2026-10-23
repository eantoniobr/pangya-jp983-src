/* compat (tools/v6/ijl15teste): o SDK de agosto/2002 do container não tem o ws2tcpip.h. Só o que o rugburn usa:
 * ADDRINFOA + getaddrinfo/freeaddrinfo (ws2_32.dll do Windows XP+; layout do ws2def.h do SDK do Windows). */
#pragma once
#include <winsock2.h>
typedef struct addrinfo {
    int ai_flags;
    int ai_family;
    int ai_socktype;
    int ai_protocol;
    size_t ai_addrlen;
    char *ai_canonname;
    struct sockaddr *ai_addr;
    struct addrinfo *ai_next;
} ADDRINFOA, *PADDRINFOA;
#ifdef __cplusplus
extern "C" {
#endif
int WSAAPI getaddrinfo(PCSTR pNodeName, PCSTR pServiceName, const ADDRINFOA *pHints, PADDRINFOA *ppResult);
VOID WSAAPI freeaddrinfo(PADDRINFOA pAddrInfo);
#ifdef __cplusplus
}
#endif
