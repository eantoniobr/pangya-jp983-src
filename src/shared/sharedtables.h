#pragma once

#include "s5/sharedutilities.h"

struct sLevelTable
{
	char name[16];
	unsigned long exp;
};

static const sLevelTable g_LevelTable[71] = {
	{ "\xb7\xe7\xc5\xb0"
	  "F", 30      },
	{ "\xb7\xe7\xc5\xb0"
	  "E", 40      },
	{ "\xb7\xe7\xc5\xb0"
	  "D", 50      },
	{ "\xb7\xe7\xc5\xb0"
	  "C", 60      },
	{ "\xb7\xe7\xc5\xb0"
	  "B", 70      },
	{ "\xb7\xe7\xc5\xb0"
	  "A", 100     },
	{ "\xba\xf1\xb1\xe2\xb3\xca"
	  "E", 133     },
	{ "\xba\xf1\xb1\xe2\xb3\xca"
	  "D", 148     },
	{ "\xba\xf1\xb1\xe2\xb3\xca"
	  "C", 163     },
	{ "\xba\xf1\xb1\xe2\xb3\xca"
	  "B", 178     },
	{ "\xba\xf1\xb1\xe2\xb3\xca"
	  "A", 213     },
	{ "\xc1\xd6\xb4\xcf\xbe\xee"
	  "E", 267     },
	{ "\xc1\xd6\xb4\xcf\xbe\xee"
	  "D", 288     },
	{ "\xc1\xd6\xb4\xcf\xbe\xee"
	  "C", 309     },
	{ "\xc1\xd6\xb4\xcf\xbe\xee"
	  "B", 330     },
	{ "\xc1\xd6\xb4\xcf\xbe\xee"
	  "A", 491     },
	{ "\xbd\xc3\xb4\xcf\xbe\xee"
	  "E", 660     },
	{ "\xbd\xc3\xb4\xcf\xbe\xee"
	  "D", 716     },
	{ "\xbd\xc3\xb4\xcf\xbe\xee"
	  "C", 772     },
	{ "\xbd\xc3\xb4\xcf\xbe\xee"
	  "B", 828     },
	{ "\xbd\xc3\xb4\xcf\xbe\xee"
	  "A", 1224    },
	{ "\xbe\xc6\xb8\xb6\xc3\xdf\xbe\xee"
	  "E", 1656    },
	{ "\xbe\xc6\xb8\xb6\xc3\xdf\xbe\xee"
	  "D", 1742    },
	{ "\xbe\xc6\xb8\xb6\xc3\xdf\xbe\xee"
	  "C", 1828    },
	{ "\xbe\xc6\xb8\xb6\xc3\xdf\xbe\xee"
	  "B", 1914    },
	{ "\xbe\xc6\xb8\xb6\xc3\xdf\xbe\xee"
	  "A", 2346    },
	{ "\xbc\xbc\xb9\xcc\xc7\xc1\xb7\xce"
	  "E", 2871    },
	{ "\xbc\xbc\xb9\xcc\xc7\xc1\xb7\xce"
	  "D", 2994    },
	{ "\xbc\xbc\xb9\xcc\xc7\xc1\xb7\xce"
	  "C", 3117    },
	{ "\xbc\xbc\xb9\xcc\xc7\xc1\xb7\xce"
	  "B", 3240    },
	{ "\xbc\xbc\xb9\xcc\xc7\xc1\xb7\xce"
	  "A", 6480    },
	{ "\xc7\xc1\xb7\xce"
	  "E", 4536    },
	{ "\xc7\xc1\xb7\xce"
	  "D", 4684    },
	{ "\xc7\xc1\xb7\xce"
	  "C", 4832    },
	{ "\xc7\xc1\xb7\xce"
	  "B", 4980    },
	{ "\xc7\xc1\xb7\xce"
	  "A", 14940   },
	{ "\xb3\xbb\xbc\xc5\xb3\xaf\xc7\xc1\xb7\xce"
	  "E", 6972    },
	{ "\xb3\xbb\xbc\xc5\xb3\xaf\xc7\xc1\xb7\xce"
	  "D", 7168    },
	{ "\xb3\xbb\xbc\xc5\xb3\xaf\xc7\xc1\xb7\xce"
	  "C", 7364    },
	{ "\xb3\xbb\xbc\xc5\xb3\xaf\xc7\xc1\xb7\xce"
	  "B", 7560    },
	{ "\xb3\xbb\xbc\xc5\xb3\xaf\xc7\xc1\xb7\xce"
	  "A", 15120   },
	{ "\xbf\xf9\xb5\xe5\xc7\xc1\xb7\xce"
	  "E", 9072    },
	{ "\xbf\xf9\xb5\xe5\xc7\xc1\xb7\xce"
	  "D", 9322    },
	{ "\xbf\xf9\xb5\xe5\xc7\xc1\xb7\xce"
	  "C", 9572    },
	{ "\xbf\xf9\xb5\xe5\xc7\xc1\xb7\xce"
	  "B", 9822    },
	{ "\xbf\xf9\xb5\xe5\xc7\xc1\xb7\xce"
	  "A", 19644   },
	{ "\xb8\xb6\xbd\xba\xc5\xcd"
	  "E", 9822    },
	{ "\xb8\xb6\xbd\xba\xc5\xcd"
	  "D", 10122   },
	{ "\xb8\xb6\xbd\xba\xc5\xcd"
	  "C", 10422   },
	{ "\xb8\xb6\xbd\xba\xc5\xcd"
	  "B", 10722   },
	{ "\xb8\xb6\xbd\xba\xc5\xcd"
	  "A", 21444   },
	{ "\xc5\xbe\xb8\xb6\xbd\xba\xc5\xcd"
	  "E", 10722   },
	{ "\xc5\xbe\xb8\xb6\xbd\xba\xc5\xcd"
	  "D", 11122   },
	{ "\xc5\xbe\xb8\xb6\xbd\xba\xc5\xcd"
	  "C", 11522   },
	{ "\xc5\xbe\xb8\xb6\xbd\xba\xc5\xcd"
	  "B", 11922   },
	{ "\xc5\xbe\xb8\xb6\xbd\xba\xc5\xcd"
	  "A", 23844   },
	{ "\xbf\xf9\xb5\xe5\xb8\xb6\xbd\xba\xc5\xcd"
	  "E", 23844   },
	{ "\xbf\xf9\xb5\xe5\xb8\xb6\xbd\xba\xc5\xcd"
	  "D", 24394   },
	{ "\xbf\xf9\xb5\xe5\xb8\xb6\xbd\xba\xc5\xcd"
	  "C", 24944   },
	{ "\xbf\xf9\xb5\xe5\xb8\xb6\xbd\xba\xc5\xcd"
	  "B", 25494   },
	{ "\xbf\xf9\xb5\xe5\xb8\xb6\xbd\xba\xc5\xcd"
	  "A", 50988   },
	{ "\xb7\xb9\xc0\xfc\xb5\xe5"
	  "E", 101978  },
	{ "\xb7\xb9\xc0\xfc\xb5\xe5"
	  "D", 203952  },
	{ "\xb7\xb9\xc0\xfc\xb5\xe5"
	  "C", 407904  },
	{ "\xb7\xb9\xc0\xfc\xb5\xe5"
	  "B", 815808  },
	{ "\xb7\xb9\xc0\xfc\xb5\xe5"
	  "A", 1631616 },
	{ "\xc0\xce\xc7\xc7\xb4\xcf\xc6\xbc\xb7\xb9\xc0\xfc\xb5\xe5"
	  "E", 1631616 },
	{ "\xc0\xce\xc7\xc7\xb4\xcf\xc6\xbc\xb7\xb9\xc0\xfc\xb5\xe5"
	  "D", 1631616 },
	{ "\xc0\xce\xc7\xc7\xb4\xcf\xc6\xbc\xb7\xb9\xc0\xfc\xb5\xe5"
	  "C", 1631616 },
	{ "\xc0\xce\xc7\xc7\xb4\xcf\xc6\xbc\xb7\xb9\xc0\xfc\xb5\xe5"
	  "B", 1631616 },
	{ "\xc0\xce\xc7\xc7\xb4\xcf\xc6\xbc\xb7\xb9\xc0\xfc\xb5\xe5"
	  "A", 1631616 },
};

#ifdef REBANG_GOLFRULE_PCH
#ifndef RB_HOLEINBONUS_LINKAGE
#define RB_HOLEINBONUS_LINKAGE static
#endif
// HACK: golfrule.cpp exports it (extern "C"): voiceitem.obj still references the unit's data blob by this name
RB_HOLEINBONUS_LINKAGE sHoleInBonus g_HoleInBonusTable[20] = {
#else
static sHoleInBonus g_HoleInBonusTable[20] = {
#endif
	{ 50,  50,  30,  12,  3,  0 },
	{ 100, 100, 60,  30,  11, 0 },
	{ 110, 110, 65,  32,  12, 0 },
	{ 180, 180, 98,  59,  20, 0 },
	{ 150, 150, 85,  43,  16, 0 },
	{ 55,  55,  36,  17,  5,  0 },
	{ 100, 100, 60,  30,  11, 0 },
	{ 150, 150, 85,  43,  16, 0 },
	{ 80,  80,  52,  26,  9,  0 },
	{ 110, 110, 65,  32,  12, 0 },
	{ 80,  80,  52,  26,  9,  0 },
	{ 50,  50,  30,  12,  3,  0 },
	{ 0,   0,   0,   0,   0,  0 },
	{ 180, 180, 98,  59,  20, 0 },
	{ 50,  50,  30,  12,  3,  0 },
	{ 50,  50,  30,  12,  3,  0 },
	{ 80,  80,  52,  26,  9,  0 },
	{ 800, 800, 520, 260, 90, 0 },
	{ 0,   0,   0,   0,   0,  0 },
	{ 80,  80,  52,  26,  9,  0 },
};

inline bool IsLicenseLimitedItem(unsigned long tid)
{
	const int LICENSEITEMSIZE = 1;

	unsigned long aLicenseLimitedItem[LICENSEITEMSIZE] = { 0x14000004 };

	for (int i = 0; i < LICENSEITEMSIZE; i++)
	{
		if (aLicenseLimitedItem[i] == tid)
			return true;
	}

	return false;
}
