#pragma once

#include "wmath.h"

// TODO: incomplete
struct sBgModel
{
	unsigned char flag;
	int faceNum;
	char name[32];
	Waabb localAabb;
	Waabb sceneAabb;
	WMatrix mat;
	int detail;
	char option[32];

	sBgModel() { flag = 0; }
};
