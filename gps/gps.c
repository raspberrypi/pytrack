/* ========================================================================== */
/*   gps.c                                                                    */
/*                                                                            */
/*   GPS program using software i2c for ublox                                 */
/*                                                                            */
/* ========================================================================== */

#define _GNU_SOURCE 1

#include <stdio.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <time.h>
#include <math.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/mman.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <wiringPi.h>
#include "gps.h"
#include "ublox.h"
#include "server.h"


int main(void)
{
	pthread_t GPSThread, ServerThread;
	struct TGPS GPS;

	memset((void *)&GPS, 0, sizeof(GPS));
	
	if (pthread_create(&GPSThread, NULL, GPSLoop, &GPS))
	{
		fprintf(stderr, "Error creating GPS thread\n");
		return 1;
	}

	if (pthread_create(&ServerThread, NULL, ServerLoop, &GPS))
	{
		fprintf(stderr, "Error creating Server thread\n");
		return 1;
	}
	
    while (1)
    {
		sleep(1);
	}
}
