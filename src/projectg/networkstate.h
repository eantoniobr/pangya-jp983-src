#pragma once

class NetworkState
{
public:
	NetworkState();
	virtual ~NetworkState();

	// TODO: this is an incomplete guess - vtable isn't recovered
	virtual void Process() = 0;
};
