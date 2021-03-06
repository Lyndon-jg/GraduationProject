import pymysql
from socket import *
from myProtocol import *

# 初始化套接字
ADDR = ("",REGISTER_SERVER_PORT)
udp_register_server_socket = socket(AF_INET,SOCK_DGRAM)
udp_register_server_socket.bind(ADDR)


def rgs_handler(data, register_client_addr, db_connect, connect_cursor):
    '''遍历注册表----》查看是否已经注册'''

    sql = "SELECT count FROM userTable"
    connect_cursor.execute(sql)
    result = connect_cursor.fetchall()
    for row in result:
        # print(row) ('xxx',)
        if data.get_count() == row[0]:
            # 若发现帐号存在，不可注册
            return REGISTER_STATUS_FAIL
    # 将注册帐号插入注册表
    sql = "INSERT INTO userTable (count, passwd, status, ip, chatPagePort, audioPagePort, audioClientPort, audioServerPort,chatRecordPagePort)" \
          " VALUES ('%s','%s',0,'%s',%d,0,0,0,0)"%(data.get_count(),data.get_passwd(),register_client_addr[0],register_client_addr[1])
    connect_cursor.execute(sql)
    # 给新注册的用户聊天记录创建表
    try:
        sql = """CREATE TABLE IF NOT EXISTS %s
    			(time CHAR(20) NOT NULL,
                first_count CHAR(64) NOT NULL,
                second_count CHAR(64) NOT NULL,
                message VARCHAR(1024) NOT NULL)"""%(data.get_count()+'_chatRecord')
        connect_cursor.execute(sql)
    except:
        print("Create chatRecord table for user failed")
    db_connect.commit()
    return REGISTER_STATUS_OK


def main():
    # 打开数据库
    db_connect = pymysql.connect(host = "localhost", user = "root", passwd = "ljgubuntu", db = "graduationPorject", charset='utf8')
    connect_cursor = db_connect.cursor()
    # 创建注册表（若不存在）
    try:
        sql = """CREATE TABLE IF NOT EXISTS userTable
    			(count CHAR(64) NOT NULL,
    			passwd CHAR(64) NOT NULL,
    			status INT NOT NULL,
    			ip CHAR(16) NOT NULL,
    			chatPagePort INT NOT NULL,
    			audioPagePort INT NOT NULL,
    			audioClientPort INT NOT NULL,
    			audioServerPort INT NOT NULL,
    			chatRecordPagePort INT NOT NULL)"""
        connect_cursor.execute(sql)
    except:
        print("Create table failed")

#    connect_cursor.close()
#    db_connect.close()
    data = RegisterStruct()
    while True:
        print("waiting for register_client message...")
        # 接收客户端发过来的消息和客户端地址
        rcv_data, register_client_addr = udp_register_server_socket.recvfrom(BUFFER_SIZE)
        data.set_rcv_data(rcv_data)
        # 将消息传给rgs_handler函数
        status = rgs_handler(data, register_client_addr, db_connect, connect_cursor)
        # 判断函数返回状态
        if status == REGISTER_STATUS_OK:
            print("rgs_server:注册成功")
        elif status == REGISTER_STATUS_FAIL:
            print("res_server:注册失败")

        data.set_status(status)
        udp_register_server_socket.sendto(data.rgs_struct_pack(), register_client_addr)

    connect_cursor.close()
    db_connect.close()
    udp_register_server_socket.close()

if __name__ == "__main__":
	main()