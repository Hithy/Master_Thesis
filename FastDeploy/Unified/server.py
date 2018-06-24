import os
import configparser
import mysql.connector



class DB_helper:
    def __init__(self, ip, user, pw, db):
        self.conn = mysql.connector.connect(user=user,database=db,host=ip,password=pw)
        self.conn.autocommit = True

    def __del__(self):
        self.conn.close()

    def select(self, sql):
        curs = self.conn.cursor(dictionary=True)
        curs.execute(sql)
        res = curs.fetchall()
        curs.close()
        return res

    def insert(self, sql):
        curs = self.conn.cursor(dictionary=True)
        curs.execute(sql)
        res = curs.lastrowid
        curs.close()
        return res

    def delete(self, sql):
        curs = self.conn.cursor(dictionary=True)
        curs.execute(sql)
        curs.close()

    def update(self, sql):
        curs = self.conn.cursor(dictionary=True)
        curs.execute(sql)
        curs.close()


class node_server:
    def __init__(self, db):
        self.db = db

    def get_ip_by_address(self, ip_address):
        res = self.db.select("select ip_id from ip where ip_address = \"" + ip_address +"\"")
        if len(res) == 0:
            return None
        else:
            return res[0]['ip_id']

    def create_host(self):
        return self.db.insert("insert into host value()")

    def create_ip(self, ip_type, ip_address):
        return self.db.insert("insert into ip (ip_type, ip_address) value(" + str(ip_type) + ",\"" + str(ip_address) + "\")")

    def create_ipv4(self, ip_address):
        return self.create_ip(4,ip_address)

    def bind_ip(self, ip_address, mac_address, host_id):
        ip_id = self.get_ip_by_address(ip_address)
        if ip_id == None:
            ip_id = self.create_ipv4(ip_address)
        bind_exist = self.db.select("select ip_id from host_ip where ip_id = " + str(ip_id))
        if len(bind_exist) != 0:
            self.db.delete("delete from host_ip where ip_id = " + str(ip_id))
        self.db.insert("insert into host_ip value("+str(ip_id) + "," + str(host_id) + ",\"" + mac_address + "\")")

    def regist(self, ip_address, mac_address):
        new_host = self.create_host()
        self.bind_ip(ip_address, mac_address, new_host)

    def update_status(self, host_id, cpu = 0, mem = 0, disk = 0, status = 0):
        self.db.update("update host set cpu_usage=%3.2f, mem_usage=%3.2f, disk_usage=%3.2f, status=%d where host_id=%d" % (cpu % 100.0001,mem % 100.0001,disk % 100.0001,status % 10,host_id))

    def img_declare(self, img_id, host_id, img_name, img_sys, img_size, bc_size):
        img_exist = []
        new_id = -1
        if img_id != -1:
            img_exist = self.db.select("select img_id from image where img_id = %d" % (img_id,))
        if len(img_exist) == 0:
            new_id = self.db.insert("insert into image (img_name, img_sys, img_size, bc_size) value(\"%s\", \"%s\", %d, %d)" % (img_name, img_sys, img_size, bc_size))
        else:
            new_id = img_id

        host_has_img = self.db.select("select * from host_img where host_id = %d and img_id = %d" % (host_id, new_id))
        if len(host_has_img) == 0:
            self.db.insert("insert into host_img value(%d, %d)" % (host_id, new_id))
        return new_id


class Server:
    def __init__(self):
        config = configparser.ConfigParser()
        with open('config.cnf','r') as configfile:
            config.read_file(configfile)
        db_config = config['Database']
        self.db = DB_helper(db_config['host'], db_config['username'],db_config['password'],db_config['db'])
        self.node = node_server(self.db)

    def test(self):
        self.node.img_declare(-1, 52, "apache", "linux", 3123, 123)
        #self.node.create_host()



test = Server()
test.test();
