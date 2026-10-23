#pragma once

class CMainFrame
{
public:
	CMainFrame();
	virtual ~CMainFrame();

	int Main(int flags);
	void SetFPS(float fps);
	float GetFPS() const { return m_fps / m_fpsDivisor; }
	void SetGameSpeed(float speed) { m_gameSpeed = speed; }
	float GetGameSpeed() const { return m_gameSpeed; }

protected:
	virtual void Process(float dt) = 0;
	virtual void Draw() = 0;
	virtual void Paint() { }
	virtual unsigned long GetSystemTime() const = 0;
	virtual void Update(int time) { }

	void ResetTimer();
	void Quit();
	void Restart();

	int m_result;
	float m_fps;
	float m_gameSpeed;
	float m_unknown10;
	float m_processedTime;
	unsigned long m_startTime;
	int m_frameCount;
	int m_drawCount;
	int m_fpsDivisor;
	float m_drawTime;

private:
	void FixFrameRate(bool bEnable);
	unsigned long GetTime() const { return GetSystemTime() - m_startTime; }
};
