import pymysql
from socket import *
from myProtocol import *

# 初始化套接字
ADDR = ("",LOGIN_SERVER_PORT)
udp_login_server_socket = socket(AF_INET,SOCK_DGRAM)
udp_login_server_socket.bind(ADDR)

def login_handler(data, db_connect, connect_cursor):

    # 用户登录
    if data.get_status() == 0:
        # 查找账户是否已经存在
        print("count = '%s' AND passwd = '%s'"%(data.get_count(), data.get_passwd()))
        sql = "SELECT count,passwd FROM userTable WHERE count = '%s' AND passwd = '%s'"%(data.get_count(), data.get_passwd())
        connect_cursor.execute(sql)
        result = connect_cursor.fetchall()
        # print(result)
        if len(result) == 0:
            print("帐号或密码不正确")
            return LOGIN_STATUS_FAIL
        if len(result) == 1:
            print("帐号和密码正确,可以登录")
            sql = "UPDATE userTable SET status = 1 WHERE count = '%s' AND passwd = '%s'"%(data.get_count(), data.get_passwd())
            connect_cursor.execute(sql)
            db_connect.commit()
            return LOGIN_STATUS_OK
    # 管理员登录
    elif data.get_status() == 1:
        print("count = '%s' AND passwd = '%s'"%(data.get_count(), data.get_passwd()))
        # 查找账户是否已经存在
        sql = "SELECT count,passwd FROM manager WHERE count = '%s' AND passwd = '%s'" % (
        data.get_count(), data.get_passwd())
        connect_cursor.execute(sql)
        result = connect_cursor.fetchall()
        if len(result) == 0:
            print("帐号或密码不正确")
            return LOGIN_STATUS_FAIL
        if len(result) == 1:
            print("帐号和密码正确,可以登录")
            return LOGIN_STATUS_OK

    return -1


def main():
    try:
        # 打开数据库
        db_connect = pymysql.connect(host = "localhost", user = "root", passwd = "ljgubuntu", db = "graduationPorject", charset='utf8')
        connect_cursor = db_connect.cursor()
    except:
        print('open db file')
        return -1
    # 接受数据对象
    data = LoginStruct()
    while True:
        print("login_server waitting for login message...")
        # 接收客户端发过来的消息和客户端地址
        rcv_data, login_client_addr = udp_login_server_socket.recvfrom(BUFFER_SIZE)
        data.set_rcv_data(rcv_data)
        # 将消息传给login_handler函数
        status = login_handler(data, db_connect, connect_cursor)
        # 判断函数返回状态
        if status == -1:
            print("login_handler error")
            break

        data.set_status(status)
        udp_login_server_socket.sendto(data.login_struct_pack(), login_client_addr)

    connect_cursor.close()
    db_connect.close()
    udp_login_server_socket.close()
    print('close')

if __name__ == "__main__":
    main()
