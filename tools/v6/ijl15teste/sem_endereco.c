/*
 * ijl15_teste.dll (frente C, C-F4.6): troca o src/hooks/comctl32/dynamic_patch.c do rugburn público.
 * O original, no 1º InitCommonControlsEx/GetStartupInfo do exe, reconhece a versão pelos bytes e grava patches em
 * ENDEREÇOS FIXOS do exe original (GameGuard, ranking US 852) e depois os "PatchAddress" do rugburn.json. No exe compilado
 * (ProjectG_983.exe) esses endereços caem em código qualquer — então aqui não há nenhum: nem os de versão, nem os do json.
 * O GameGuard já sai do exe compilado pela chave JP983_SEM_GAMEGUARD (ggc_wrapper.cpp); o resto do rugburn (connect/
 * wininet/PANGYA_ARG/CreateProcess do GameGuard/_stricmp do Wine/janela/navegador) fica igual, por gancho de API.
 */
#include "dynamic_patch.h"
#include "../../config.h"

VOID InitComCtl32Hook() {
    Log("ijl15_teste (jp983src C-F4.6): sem patches de endereco fixo (GG por versao e PatchAddress desligados).\r\n");
    if (Config.NumPatchAddress > 0) {
        Log("ijl15_teste: %d PatchAddress do rugburn.json IGNORADOS (sao enderecos do exe original).\r\n",
            Config.NumPatchAddress);
    }
}
