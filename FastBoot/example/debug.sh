#!/bin/bash

set -x

fusermount -u mountdir

cd ..
make

cd ./example/
../src/bbfs rootdir/ mountdir/

cd mountdir
cat open.c 

cd ..
cat bbfs.log | grep -B 10 $1
cd ..




