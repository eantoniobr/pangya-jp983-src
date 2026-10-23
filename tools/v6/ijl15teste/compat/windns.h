/* compat (tools/v6/ijl15teste): o SDK de agosto/2002 não tem os tipos do DnsQueryEx (Windows 8). O rugburn só os usa num
 * typedef de ponteiro de função (common-fnptr.h, nunca chamado); mesma definição que o rugburn dá para o mingw. */
#pragma once
typedef LONG DNS_STATUS;
typedef struct _DNS_QUERY_RESULT *PDNS_QUERY_RESULT;
typedef struct _DNS_QUERY_REQUEST {
    ULONG Version;
    PCWSTR QueryName;
    WORD QueryType;
    ULONG64 QueryOptions;
    PVOID pDnsServerList;
    ULONG InterfaceIndex;
    PVOID pQueryCompletionCallback;
    PVOID pQueryContext;
} DNS_QUERY_REQUEST, *PDNS_QUERY_REQUEST;
typedef struct _DNS_QUERY_CANCEL {
    CHAR Reserved[32];
} DNS_QUERY_CANCEL, *PDNS_QUERY_CANCEL;
