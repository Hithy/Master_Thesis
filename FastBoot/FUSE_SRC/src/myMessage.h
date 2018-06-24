#ifndef my_MESSAGE_H
#define my_MESSAGE_H

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <sys/socket.h>
#include <netinet/ip.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include "crc.h"

#define SERVERPORT 2333
#define REQUEST_LENGTH 200
#define MESSAGE_SIZE 16

#define LOG(format,args...) printf("LINE%d: " format "\n", __LINE__, ##args)   

struct myMessage{

    off_t offset;
    size_t size;
};

#endif