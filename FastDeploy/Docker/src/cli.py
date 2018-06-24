#!/usr/bin/python

import time
import socket
import subprocess
import multiprocessing
import sys
from struct import *
from thread import *
from docker import *

socksize = 1024

def get_img(flag, sock):
	if flag == 1:
		sock.send('IMG\x00');
		return

	print "Get image file from remote repo..."
	
	sock.send('IMG\x01')
	img_size = unpack("<I",sock.recv(4))[0]
	print "File size: " + str(img_size)
	received = 0
	buf = ''
	while received < img_size:
		data = sock.recv(socksize)
		if not data:
			break
		buf += data
		received += len(data)
	
	if received != img_size:
		print "fail to recv img"
		return

	print "Data recv completed!"
	dkcli.load_image(buf)

def start_a_ins(task_id, image, param):
	ins_name = str(task_id)+"_"
	random_date = "%.20f" % time.time()
	ins_name += random_date.translate(None,'.')
	dk_container = dkcli.create_container(name=ins_name, image=image, command=param)
	print "create container: " + dk_container['Id']
	dkcli.start(dk_container)


def new_ins(task_id, image, count, param):
	print "New task ["+str(task_id)+"] to start "+str(count)+" "+image+"......"
		
	pool = multiprocessing.Pool(processes = 200)
	if count > 600:
		print "Too large count"
		return
	for i in range(count):
		pool.apply_async(start_a_ins, [task_id, image, param])
	pool.close()
	pool.join()
	print "Create successfully!"
		
	

def del_ins(task_id):
	target = dkcli.containers(all=True,filters={'name':str(task_id)+"_"})
	target = [x['Id'] for x in target]
	for i in target:
		dkcli.kill(i)
		dkcli.remove_container(i)
		print i+" has been removed"
	
	print "Delete task ["+str(task_id)+"]"

def action(sock):
	while True:
		try:
			act = unpack("3s",sock.recv(3))[0]
			if act[0:2] != "FD":
				print "Invalid action"
				return
			act = ord(act[2])
		except:
			#print "Invalid action or lose connection"
			return
		
		if (act == 0):
			task_id = unpack("<I",sock.recv(4))[0]
			
			img_len = unpack("b",sock.recv(1))[0]
			name = sock.recv(img_len)
			
			param_len = unpack("b",sock.recv(1))[0]
			param = ""
			if (param_len != 0):
				param = sock.recv(param_len)
			
			count = unpack("<I",sock.recv(4))[0] 

			img_list = dkcli.images()
			print "Task_id: "+str(task_id)
			print "Img_name: "+name
			print "Count: "+str(count)
			print "Param: "+param
			flag = 0
			for i in img_list:
				if i['RepoTags'][0].encode('ascii') == name+":latest":
					flag = 1
					break
			get_img(flag, sock)
			new_ins(task_id, name, count, param)
		elif (act == 1):
			task_id = unpack("<I",sock.recv(4))[0]
			del_ins(task_id)
		else:
			sock.close()
			break

if __name__ == "__main__":
	port = 65523
	dkcli = Client(base_url='unix://var/run/docker.sock',version='auto')
	
	cen_ip = sys.argv[1]
	cen_port = sys.argv[2]
	cen = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	cen.connect((cen_ip, int(cen_port)))
	cen.send("FDS\x00")
	cen.send(pack("<H",port))
	ret = cen.recv(2)
	cen.close()
	if (ret != "OK"):
		print "Fail to reg node"
		exit()
	print "Success to reg node"

	
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.bind(("",port))
	s.listen(5)
	while True:
		con,addr = s.accept()
		print "connect from ",addr
		start_new_thread(action,(con,))
