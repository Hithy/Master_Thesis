#!/bin/bash
fusermount -u mountdir
cd .. && make CFLAG=-DDEBUG 
