#pragma once

// Game summary the server sends for each ghost-mode map (list node value).
struct GHOST_GAME_BRIEF
{
	int unk0;
	int id;
	int ball;
	int pang;
	int score;
	int unk14;
	int unk18;

	bool operator==(int _id) const { return id == _id; }
};
