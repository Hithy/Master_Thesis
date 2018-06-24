import matplotlib.pyplot as plt
import math
import sys

## return: [offset, len, w/r, ret, time]
def raw_format(filename):
    with open(filename, "rb") as f:
        raw = f.read()
    raw_lines = raw.split('\n')[1:-1]
    data_lines = [ [int(j,16) for j in  x.split()] for x in raw_lines]
    return data_lines

def raw_format_without_write(filename):
    tmp = raw_format(filename)
    for i in tmp:
        if i[2] == 1:
            tmp.remove(i)
    return tmp

def data_spwan(data, size):
    bitmap = [0] * (max([i[1] >> 12 for i in data]) + 1)
    for i in data:
        length = i[1] >> 12
        bitmap[length] += 1
    return bitmap

def make_pie(data):
    labels = [ str(4*(x)) + "KB" for x in range(len(data))]
    for i in range(8,len(labels)-1):
        labels[i] = ""
    print data
    print labels
    ## plt.pie(x=data, labels=labels, pctdistance = 0.6)
    ## plt.show()

def make_offset(data):
    size = max([i[0] >> 12 for i in data])
    m = 1000
    print m
    xa = []
    ya = []
    for i in data:
	off = i[0] >> 12
	x = off / m
	y = off % m
	xa.append(x)
	ya.append(y)
    return xa,ya

def get_size(data):
    res = 0
    for i in data:
	res += i[1]
    return res

path = sys.argv[1]
data = raw_format_without_write(path)
#a,b = make_offset(data)
#print a
#print b

## make_pie(data_spwan(data,0))

## make_pie(data_spwan(data,0))
## print data_spwan(data, 0)
print get_size(data)/1024/1024
