#!/usr/bin/python

import time
import socket
import subprocess
import multiprocessing
import sys
from struct import *
from thread import *
from docker import *


def print_usage():
	print "USAGE:"
	print "\t./proc list {node | task}"
	print "\t./proc start {IMAGE_NAME} {\"NODE_INDEX_ARRAY\"} {\"COUNT_ARRAY\"} \"[ARGV...]\""
	print "\t./proc stop {TASK_ID}"

	
def get_list(input):
	return [ int(x) for x in input.split(' ')]
	
def start_task(sock, img_name, param, node_list, count_list):
	img_name_len = len(img_name)
	param_len = len(param)
	
	list_len = len(node_list)

	sock.send("FDS\x02")
	sock.send(pack("b",img_name_len))
	sock.send(img_name)
	sock.send(pack("b",param_len))
	if (param_len != 0):
		sock.send(param)
	sock.send(pack("<I",list_len))
	for i in range(list_len):
		sock.send(pack("<I",node_list[i]))
		sock.send(pack("<I",count_list[i]))
	if (sock.recv(2) != "OK"):
		print "Fail to start task"
		exit()
	
	task_id = unpack("<I",sock.recv(4))[0]
	print "Task " + str(task_id) +" has been started"
	
def stop_task(sock, task_id):
	sock.send("FDS\x03")
	sock.send(pack("<I",task_id))
	if (sock.recv(2) != "OK"):
		print "Fail to stop task"
		exit()
	print "Task " + str(task_id) +" has been killed"

def list_node(sock):
	sock.send("FDS\x01")
	list_len = unpack("<I",sock.recv(4))[0]
	if(list_len == 0):
		print "Node list is empty"
		exit()
		
	for i in range(list_len):
		ip = sock.recv(4)
		port = unpack("<H",sock.recv(2))[0]
		print str(i)+". "+socket.inet_ntoa(ip)+":"+str(port)
		
def list_task(sock):
	sock.send("FDS\x04")
	list_len = unpack("<I",sock.recv(4))[0]
	if(list_len == 0):
		print "Task list is empty"
		exit()
	
	for i in range(list_len):
		task_id = unpack("<I",sock.recv(4))[0]
		img_len = unpack("b",sock.recv(1))[0]
		img_name = sock.recv(img_len)
		
		client_list_len = unpack("<I",sock.recv(4))[0]
		client_list = []
		for i in range(client_list_len):
			client_list.append(unpack("<I",sock.recv(4))[0])
			
		count_list_len = unpack("<I",sock.recv(4))[0]
		count_list = []
		for i in range(count_list_len):
			count_list.append(unpack("<I",sock.recv(4))[0])
		
		print "Task "+str(task_id)+" with image \"" + img_name +"\":"
		for i in range(client_list_len):
			print "\tNode: "+str(client_list[i])+"\tCount: "+str(count_list[i])
		
		
	
	
if __name__ == "__main__":
	param_len = len(sys.argv)
	if (param_len == 1):
		print_usage()
		exit()
		
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect(("localhost", 65522))
		
	if (sys.argv[1] == "list"):
		if (sys.argv[2] == "node"):
			list_node(s)
		elif (sys.argv[2] == "task"):
			list_task(s)
	elif (sys.argv[1] == "start"):
		image_name = sys.argv[2]
		node_list = get_list(sys.argv[3])
		count_list = get_list(sys.argv[4])
		param = ""
		if (param_len == 6):
			param = sys.argv[5]
			
		start_task(s, image_name, param, node_list, count_list)
		#print "IMG: "+image_name
		#print "Param: "+param
		#print "NODE: "
		#for i in node_list:
		#	print "\t"+str(i)
		#print "COUNT: "
		#for i in count_list:
		#	print "\t"+str(i)
	elif (sys.argv[1] == "stop"):
		task_id = int(sys.argv[2])
		stop_task(s, task_id)
		
		
	
	s.close()
