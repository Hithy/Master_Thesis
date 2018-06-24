#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <termios.h>
#include <signal.h>
#include <time.h>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>


time_t rawtime;
struct tm *timeinfo;

void write_log(char *str)
{
	FILE *fg = fopen("Connected.log", "a");
	if (fg == NULL)
	{
		return;
	}
	printf("[%d] Loging...\n%s\n", getpid(), str);
	fputs(str, fg);
	fclose(fg);
}

void split_crnl_to_space(char *str, int len)
{
	int i;
	if (str == NULL)
		return;
	for (i = 0; i < len; i++)
	{
		if (str[i] == '\x0a' || str[i] == '\x0d')
		{
			str[i] = ' ';
		}
	}
}

void deal_connect(int fd, struct in_addr ip)
{
	int nread = 0;
	char buf[256] = { 0 };
	char logbuf[1024] = { 0 };

	nread = read(fd, buf, 256);
	close(fd);
	split_crnl_to_space(buf, nread);

	time(&rawtime);
	timeinfo = localtime(&rawtime);
	memset(logbuf, 0, 1024);
	sprintf(logbuf, "[%d] Container %s connected from %s -- %s", getpid(), buf, inet_ntoa(ip), asctime(timeinfo));
	write_log(logbuf);
}

int main(int argc, char *argv[])
{

	int spid;
	char logbuf[1024] = { 0 };
	char container[256] = { 0 };


	struct sockaddr_in srv_addr;
	struct sockaddr_in client_addr;
	int sfd;
	int cfd;
	int client_addrlen = sizeof(client_addr);


	if (argc < 2)
	{
		printf("You should enter the port number\n");
		return -1;
	}

	signal(SIGCHLD, SIG_IGN);

	sfd = socket(AF_INET, SOCK_STREAM, 0);
	memset(&srv_addr, 0, sizeof(srv_addr));
	srv_addr.sin_family = AF_INET;
	srv_addr.sin_port = htons(atoi(argv[1]));
	srv_addr.sin_addr.s_addr = inet_addr("0.0.0.0");


	if (bind(sfd, (const struct sockaddr *) &srv_addr, sizeof srv_addr) ==
			0) {
		printf("Binding socket is OK\n");
	}
	else {
		fprintf(stderr, "Fail to bind the socket: %s\n", strerror(errno));
		exit(-1);
	}

	if (listen(sfd, 100) == 0) {
		printf("[%d] Start listening\n", getpid());
	}
	else {
		fprintf(stderr, "[%d] Fail to start listening: %s\n", getpid(), strerror(errno));
		exit(-1);
	}

	while (1)
	{
		cfd = accept(sfd, (struct sockaddr *) &client_addr, &client_addrlen);

		if (cfd != -1)
		{
			spid = fork();
			if (spid == 0)
			{
				deal_connect(cfd, client_addr.sin_addr);
				exit(0);
			}

			close(cfd);
		}
	}
}
