// crc983_check.cpp — compila o CRC_32 REAL do src/projectg/ccrc32.cpp (ctor, Reflect, Calculate; extraídos por sed no
// Makefile.C/linha de comando, "unsigned long" -> uint32_t porque no Win32 long = 32 bits) e imprime o CRC de cada arquivo.
#include <cstdio>
#include <cstdint>
#include <vector>
#define Sleep(x)
class CRC_32 {
public:
	CRC_32();
	void Calculate(unsigned char* const data, unsigned int size, uint32_t& crc, uint32_t sleepTime);
	uint32_t Reflect(uint32_t ref, char ch);
	uint32_t m_table[256];
};
#include "crc983_trecho.inc"
int main(int argc, char** argv) {
	CRC_32 c;
	for (int a = 1; a < argc; a++) {
		FILE* f = fopen(argv[a], "rb"); if (!f) return 1;
		std::vector<unsigned char> d; unsigned char b[65536]; size_t n;
		while ((n = fread(b, 1, sizeof b, f)) > 0) d.insert(d.end(), b, b + n);
		fclose(f);
		uint32_t crc = 0xffffffff; c.Calculate(d.data(), (unsigned int)d.size(), crc, 0); crc ^= 0xffffffff;
		printf("%08x %d %zu %s\n", crc, (int32_t)crc, d.size(), argv[a]);
	}
}
