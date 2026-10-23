// Trecho de github.com/pangbox/rugburn, src/hooks/comctl32/dynamic_patch.c, commit 7158511d52b6150f091890187cf81b8718b97438
// Copiado só para conferência (frente C, V5). Aviso da licença ISC do original:
// Copyright 2018-2024 John Chadwick <john@jchw.io>
// Permission to use, copy, modify, and/or distribute this software for any purpose with or without
// fee is hereby granted, provided that the above copyright notice and this permission notice appear
// in all copies. THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
// TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
// THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
// WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
// OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
static void PatchGG_JP() {
    if (compare_virtual_memory(0x00A5CD10, 0x1BA43D83)) {
        Patch((LPVOID)0x00A5CD10, "\xC3\x90\x90\x90\x90\x90\x90", 7);
        Patch((LPVOID)0x00A5CDA0, "\xC3\x90\x90\x90\x90\x90\x90", 7);
        Patch((LPVOID)0x00A5CDC0, "\xC3\x90\x90\x90\x90\x90\x90", 7);
        Patch((LPVOID)0x00A5CDE0, "\x90\x90\x90\x90\x90\x90\x90", 7);
        Patch((LPVOID)0x00A5CE10, "\xC3", 1);
        Patch((LPVOID)0x00A5CE40, "\xC3", 1);
        Log("Patched GG check routines (JP 972)\r\n");
    } else if (compare_virtual_memory(0x00A5CF80, 0x1BA43D83)) {
        Patch((LPVOID)0x00A5CF80, "\xC3\x90\x90\x90\x90\x90\x90", 7);
        Patch((LPVOID)0x00A5C010, "\xC3\x90\x90\x90\x90\x90\x90", 7);
        Patch((LPVOID)0x00A5C030, "\xC3\x90\x90\x90\x90\x90\x90", 7);
        Patch((LPVOID)0x00A5C050, "\x90\x90\x90\x90\x90\x90\x90", 7);
        Patch((LPVOID)0x00A5CE80, "\xC3", 1);
        Patch((LPVOID)0x00A5CEB0, "\xC3", 1);
        Log("Patched GG check routines (JP 974)\r\n");
    } else if (compare_virtual_memory(0x00A5CF80, 0x1C143D83)) {
        Patch((LPVOID)0x00A5CF80, "\xC3\x90\x90\x90\x90\x90\x90", 7);
        Patch((LPVOID)0x00A5C010, "\xC3\x90\x90\x90\x90\x90\x90", 7);
        Patch((LPVOID)0x00A5C030, "\xC3\x90\x90\x90\x90\x90\x90", 7);
        Patch((LPVOID)0x00A5C050, "\x90\x90\x90\x90\x90\x90\x90", 7);
        Patch((LPVOID)0x00A5CE80, "\xC3", 1);
        Patch((LPVOID)0x00A5CEB0, "\xC3", 1);
        Log("Patched GG check routines (JP 983)\r\n");
    } else if (compare_virtual_memory(0x005E345A, 0xFF83F1E8)) {
        Patch((LPVOID)0x005E345A, "\xB8\x01\x00\x00\x00", 5);
        Log("Patched HSHIELD check routines (JP S1 2.11)\r\n");
    } else if (compare_virtual_memory(0x006208A8, 0xFF0923E8)) {
        Patch((LPVOID)0x006208A8, "\xB8\x00\x00\x00\x00", 5);
        Patch((LPVOID)0x006208AD, "\xE9\x00\x00\x00\x00", 5);
        Log("Patched HSHIELD check routines (JP S1 2.25b)\r\n");
    } else if (compare_virtual_memory(0x00673DC3, 0xFF7C18E8)) {
        Patch((LPVOID)0x00673DC3, "\xE9\x00\x00\x00\x00", 5);
        Log("Patched GG check routines (JP S3 4.00a)\r\n");
    } else if (compare_virtual_memory(0x0067BF95, 0xFF6A76E8)) {
        Patch((LPVOID)0x0067BF95, "\xE9\x00\x00\x00\x00", 5);
        Log("Patched GG check routines (JP S3 4.01h1)\r\n");
    } else if (compare_virtual_memory(0x00752E8B, 0xFF2AA0E8)) {
        Patch((LPVOID)0x00752E8B, "\xE9\x00\x00\x00\x00", 5);
        Log("Patched GG check routines (JP S4 585)\r\n");
    }
}
