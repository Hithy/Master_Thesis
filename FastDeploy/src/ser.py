#!/usr/bin/python

import time
import socket
import subprocess
import multiprocessing
import sys
from struct import *
from threading import Thread
from threading import Lock
from thread import *
from docker import *


c_list = []
t_list = []
img_mutex = Lock()
img_data_list = {}
task_id = 0

def add_client(ip, port):
	try:
		c_list.index((ip,port))
		print "client has been added already"
	except:
		c_list.append((ip,port))

def img_data(img_name):
	return dkcli.get_image(img_name).data

def add_task(sock):
	global task_id
	task_id += 1;
	cur_task_id = task_id - 1;
	client_list = []
	count_list = []

	img_name_len = unpack("b",sock.recv(1))[0]
	img_name = sock.recv(img_name_len)
	print "Add Image: "+img_name

	param_len = unpack("b",sock.recv(1))[0]
	param = ""
	if param_len != 0:
		param = sock.recv(param_len)
		
	print "Add Param: "+param

	list_len = unpack("<I",sock.recv(4))[0]
	for i in range(list_len):
		c_index = unpack("<I",sock.recv(4))[0]
		c_count = unpack("<I",sock.recv(4))[0]
		print "ADD C_INDEX: "+str(c_index) +" C_COUNT: "+str(c_count)
		client_list.append(c_index)
		count_list.append(c_count)

	t_list.append([cur_task_id, img_name, client_list, count_list, param])
	print "Task "+str(cur_task_id)+" has been added"
	return cur_task_id
	

	
def send_img(sock, img_name):
	print "Sending img..."
	if img_mutex.acquire():
		if img_name in img_data_list:
			data = img_data_list[img_name]
		else:
			data = img_data(img_name)
			img_data_list[img_name] = data
		img_mutex.release()
		
	
	sock.send(pack("<I",len(data)))
	sock.send(data)
	sock.close()
	print "Done!"
	

def deploy_task(task):
	tid = pack("<I",task[0])
	img_name = task[1]
	img_name_len = pack("b",len(img_name))
	param = task[4]
	param_len = pack("b",len(param))
	client_list = task[2]
	count_list = task[3]
	host_len = len(client_list)
	for i in range(host_len):
		ip, port = c_list[client_list[i]]
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		try:
			s.connect((socket.inet_ntoa(ip), port))
		except:
			print "Fail to connect to node"
			t_list.remove(task)
			c_list.remove(c_list[client_list[i]])
			return False
		action = "FD"+pack("b",0)
		count = pack("<I",count_list[i])
		s.send(action+tid+img_name_len+img_name+param_len+param+count)
		ret = s.recv(4)
		threads = []
		if ret == "IMG\x01":
			t = Thread(target=send_img, args=(s,img_name, ))
			t.start()
			threads.append(t)
		else:
			s.close()
	
	for t in threads:
		t.join()
			
	print "Task " + str(task[0]) + " has been deployed"
	return True

def deploy_task_by_id(tid):
	flag = 0
	for i in t_list:
		if i[0] == tid:
			target_task = i
			flag = 1
			break
	if flag == 0:
		print "Cannot find target task"
		return False

	return deploy_task(target_task)
	
def delete_task(task):
	tid = pack("<I",task[0])
	
	client_list = task[2]
	host_len = len(client_list)
	for i in range(host_len):
		ip, port = c_list[client_list[i]]
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		try:
			s.connect((socket.inet_ntoa(ip), port))
		except:
			print "Fail to connect to node"
			return False
		
		action = "FD"+pack("b",1)
		s.send(action+tid)
		s.close()
		
	return True
	
def delete_task_by_id(tid):
	print "Removing task "+str(tid)
	flag = 0
	for i in t_list:
		if i[0] == tid:
			target_task = i
			flag = 1
			break
	if flag == 0:
		print "Cannot find target task"
		return False

	if (delete_task(target_task) == False):
		return False
	t_list.remove(target_task)
	
	print "Task "+str(tid)+" has been removed"
	return True
	
def list_task(sock ):
	sock.send(pack("<I",len(t_list)))
	for cur_task_id, img_name, client_list, count_list, param in t_list:
		sock.send(pack("<I",cur_task_id))
		sock.send(pack("b",len(img_name)))
		sock.send(img_name)
		
		sock.send(pack("<I",len(client_list)))
		for i in client_list:
			sock.send(pack("<I",i))
			
		sock.send(pack("<I",len(count_list)))
		for i in count_list:
			sock.send(pack("<I",i))
		
def action(sock):
	while True:
		try:
			act = unpack("4s",sock.recv(4))[0]
			if act[0:3] != "FDS":
				print "Invalid action"
				return
			act = ord(act[3])
		except:
			#print "Invalid action or lose connection"
			return
		
		if (act == 0):#add client
			ip_addr = sock.getpeername()[0]
			ip = socket.inet_aton(ip_addr)
			port = unpack("<H",sock.recv(2))[0]
			add_client(ip,port)
			print ip_addr+":"+str(port)+" has been added"
			sock.send("OK")
			
		elif (act == 1):#list client
			sock.send(pack("<I",len(c_list)))
			for (ip, port) in c_list:
				sock.send(ip)
				sock.send(pack("<H",port))
		elif (act == 2):#add task
			tid = add_task(sock)
			if (deploy_task_by_id(tid) == True):
				sock.send("OK")
				sock.send(pack("<I",tid))
			else:
				sock.send("ER")
		elif (act == 3):#delete task
			tid = unpack("<I",sock.recv(4))[0]
			if (delete_task_by_id(tid) == True):
				sock.send("OK")
			else:
				sock.send("ER")
		elif (act == 4):#list task
			list_task(sock)
		else:
			sock.close()
			break


if __name__ == "__main__":
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	dkcli = Client(base_url='unix://var/run/docker.sock',version='auto')

	port = 65522
	s.bind(("",port))
	s.listen(5)
	while True:
		con,addr = s.accept()
		print "connect from ",addr
		start_new_thread(action,(con,))

