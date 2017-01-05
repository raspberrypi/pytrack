struct TGPS
{
	// long Time;						// Time as read from GPS, as an integer but 12:13:14 is 121314
	long SecondsInDay;					// Time in seconds since midnight
	int Hours, Minutes, Seconds;
	float Longitude, Latitude;
	int32_t Altitude, MaximumAltitude;
	unsigned int Satellites;
	int FixType;
	// int Speed;
	// int Direction;
	// int FlightMode;
	// int PowerMode;
	// int Lock;
};
