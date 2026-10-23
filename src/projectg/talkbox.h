#pragma once

#include <list>
#include <string>
#include <vector>

class WFont;
class WOverlay;

class CTalkBox
{
public:
	CTalkBox();
	~CTalkBox();

	void SetText(const char* text, float time);
	void AddText(const char* text);
	bool IsActive() { return m_time > 0.0f ? true : false; }
	void Process(float elapsed) { m_time -= elapsed; }
	void Render(WView* view, float x, float y, int align);

	void SetTransparency(float alpha) { m_transparency = alpha; }

private:
	struct sLine
	{
		char text[32];
		float width;
		unsigned long color;
		int newLine;
	};

	// 983: AddText guarda {texto, 2.0f} num vetor em +0x18 que nada mais le (Render/SetText nao usam)
	struct sChunk
	{
		std::string text;
		float time;
		sChunk(const char* t, float tm) : text(t), time(tm) {}
	};

	WFont* m_pFont;
	WOverlay* m_pOverlay;
	std::list<sLine> m_lines;
	int m_lineNum;
	std::vector<sChunk> m_chunks;
	char m_unk28;
	int m_chunkNum;
	float m_transparency;
	float m_time;
	WPoint m_pos;
	char m_text[512];
	unsigned char m_maxLineLen;
};
