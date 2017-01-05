#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <ctype.h>
#include <stdio.h>              // Standard input/output definitions
#include <string.h>             // String function definitions
#include <fcntl.h>              // File control definitions
#include <unistd.h>             // UNIX standard function definitions
#include <errno.h>              // Error number definitions
#include <termios.h>            // POSIX terminal control definitions
#include <stdint.h>
#include <stdlib.h>
#include <dirent.h>
#include <math.h>
#include <pthread.h>
#include <wiringPi.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include "server.h"
#include "gps.h"

void error(char *msg)
{
    perror(msg);
    exit(1);
}

int SendJSON(int connfd, struct TGPS *GPS)
{
	int OK;
    char sendBuff[1025];
	
	OK = 1;
	
    memset(sendBuff, '0', sizeof(sendBuff ));
	
	sprintf(sendBuff, "{\"time\":\"%02d:%02d:%02d\",\"lat\":%.5lf,\"lon\":%.5lf,\"alt\":%d,\"sats\":%d,\"fix\":%d}\r\n",
						GPS->Hours, GPS->Minutes, GPS->Seconds,
						GPS->Latitude, GPS->Longitude,
						GPS->Altitude,
						GPS->Satellites,
						GPS->FixType);
	
	if (send(connfd, sendBuff, strlen(sendBuff), MSG_NOSIGNAL ) <= 0)
	{
		printf( "Disconnected from client\n" );
		OK = 0;
	}
	
	return OK;
}

void ProcessSocket(int sock, struct TGPS *GPS)
{
	int OK=1;
	
	while (OK)
	{
		OK = SendJSON(sock, GPS);
		delay(1000);
	}	
}

/*
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	memset(&serv_addr, '0', sizeof(serv_addr));

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr = htonl( INADDR_ANY );
	serv_addr.sin_port = htons(Port);

	printf("Listening on JSON port %d\n", Port);

	if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &(int){1}, sizeof(int)) < 0)
	{
		printf("setsockopt(SO_REUSEADDR) failed" );
	}

	if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0)
	{
		printf("Server failed errno %d\n", errno );
		exit( -1 );
	}

	listen(sockfd, 10);
	
	fcntl(sockfd, F_SETFL, fcntl(sockfd, F_GETFL) & ~O_NONBLOCK);	// Blocking mode so we wait for a connection

	connfd = accept(sockfd, ( struct sockaddr * ) NULL, NULL);	// Wait for connection

	printf("Connected to client\n");
	Connected = 1;

	// fcntl(connfd, F_SETFL, fcntl(sockfd, F_GETFL) | O_NONBLOCK);	// Non-blocking, so we don't block on receiving any commands from client

	while (Connected)
	{
		if (SendJSON(connfd, GPS))
		{
			Connected = 0;
		}
		else
		{
			delay(1000);
		}
	}

	printf("Close connection\n");
	close(connfd);
*/

void *ServerLoop(void *some_void_ptr)
{
	struct TGPS *GPS;
	int portno;
	int sockfd, newsockfd;
    struct sockaddr_in serv_addr, cli_addr;
	
	GPS = (struct TGPS *)some_void_ptr;
	
    while (1)
    {
		// int pid;
		unsigned int clilen;
		
		sockfd = socket(AF_INET, SOCK_STREAM, 0);
		if (sockfd < 0) 
			error("ERROR opening socket");
		
		bzero((char *) &serv_addr, sizeof(serv_addr));
     
		portno = 6005;
		serv_addr.sin_family = AF_INET;
		serv_addr.sin_addr.s_addr = INADDR_ANY;
		serv_addr.sin_port = htons(portno);
		
		if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) 
		{
			error("ERROR on binding");
		}
		  
		listen(sockfd, 10);
		printf("Listening on JSON port %d\n", portno);
		
		clilen = sizeof(cli_addr);
		
		// while (1)
		{
			newsockfd = accept(sockfd, (struct sockaddr *)&cli_addr, &clilen);
			
			if (newsockfd < 0) 
				error("ERROR on accept");
			// pid = fork();
			// if (pid < 0)
				// error("ERROR on fork");
			// if (pid == 0)
			// {
				printf("sockfd=%d, newsockfd=%d\n", sockfd, newsockfd);
				close(sockfd);
				ProcessSocket(newsockfd, GPS);
				// exit(0);
			// }
			// else
			// {
				// close(newsockfd);
			// }
		}
    }

    return NULL;
}
