// C-F4.8 (C85): confere a updatelist com o DecodeTEA_NBYTE do proprio cliente (src/shared/tea.cpp), g++ nativo.
// g++ -O1 -o /tmp/t tools/v6/updatelist_teacheck.cpp && /tmp/t <updatelist cifrada>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "/root/jp983src/src/shared/tea.cpp"
static const unsigned int key[4] = { 0x020a5fd4, 0x01eebdff, 0x02b3c6a0, 0x04f6a3e1 };
int main(int c, char** v) {
  FILE* f = fopen(v[1], "rb"); fseek(f, 0, SEEK_END); long n = ftell(f); rewind(f);
  char* d = (char*)malloc(n); if (fread(d, 1, n, f) != (size_t)n) return 1;
  int padded = n + ((n & 7) ? 8 - (n & 7) : 0);
  char* x = (char*)calloc(padded + 1, 1);
  DecodeTEA_NBYTE(x, padded, d, key);
  const char* p = strstr(x, "fname=\"ProjectG.exe\"");
  const char* e = p ? strchr(p, '>') : 0;
  if (!p) { puts("sem linha ProjectG.exe"); return 1; }
  printf("strlen=%zu padded=%d nul_dentro=%d linha: %.*s\n", strlen(x), padded, (int)(strlen(x) < (size_t)padded), e ? (int)(e - p + 1) : 0, p);
  printf("atoi(fcrc)=%d\n", p ? atoi(strstr(p, "fcrc=\"") + 6) : 0);
}
