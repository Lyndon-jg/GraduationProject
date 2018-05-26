import pymysql
from socket import *
from myProtocol import *

# 初始化套接字
ADDR = ("",AUDIO_SERVER_PORT)
udpSerSock = socket(AF_INET,SOCK_DGRAM)
udpSerSock.bind(ADDR)

def audio_handler(data, audio_client_addr):
    '''消息处理函数,并返回一个值'''
    # 打开数据库
    db_connect = pymysql.connect(host = "localhost", user = "root", passwd = "ljgubuntu", db = "graduationPorject", charset='utf8')
    connect_cursor = db_connect.cursor()
    # 判断语音消息的状态
    # 拒绝语音请求
    if data.get_audio_status() == AUDIO_STATUS_REJECT:
        print("AUDIO_STATUS_REJECT")
        sql = "SELECT ip,audioPagePort FROM userTable where count = '%s'" % (data.get_friend_count())
        connect_cursor.execute(sql)
        result = connect_cursor.fetchall()
        print("result:", result)
        if len(result) == 1:
            for row in result:
                destination_addr = (row[0], int(row[1]))
            data.change_name()
            udpSerSock.sendto(data.audio_struct_pack(), destination_addr)
        elif len(result) == 0:
            connect_cursor.close()
            db_connect.close()
            return -1
    # 接受语音请求
    elif data.get_audio_status() == AUDIO_STATUS_ACCEPT:
        print("AUDIO_STATUS_ACCEPT")
        sql = "SELECT ip,audioPagePort FROM userTable where count = '%s'" % (data.get_friend_count())
        connect_cursor.execute(sql)
        result = connect_cursor.fetchall()
        print("result:", result)
        if len(result) == 1:
            for row in result:
                destination_addr = (row[0], int(row[1]))
            data.change_name()
            udpSerSock.sendto(data.audio_struct_pack(), destination_addr)
        elif len(result) == 0:
            connect_cursor.close()
            db_connect.close()
            return -1
    # 更新语音server端口
    elif data.get_audio_status() == AUDIO_STATUS_UPDATE_SERVER_PORT:
        print("AUDIO_STATUS_UPDATE_SERVER_PORT")
        sql = "UPDATE userTable SET audioServerPort = %d WHERE count = '%s'" % (data.get_audio_server_port(), data.get_my_count())
        connect_cursor.execute(sql)
        db_connect.commit()
    # 更新语音client端口
    elif data.get_audio_status() == AUDIO_STATUS_UPDATE_CLIENT_PORT:
        print("AUDIO_STATUS_UPDATE_CLIENT_PORT")                                # udp port
        sql = "UPDATE userTable SET audioClientPort = %d WHERE count = '%s'" % (audio_client_addr[1], data.get_my_count())
        connect_cursor.execute(sql)
        db_connect.commit()

        sql = "SELECT ip,audioServerPort FROM userTable where count = '%s'" % (data.get_friend_count())
        connect_cursor.execute(sql)
        result = connect_cursor.fetchall()
        print("result:", result)
        if len(result) == 1:
            for row in result:
                data.set_audio_server_ip(row[0])
                data.set_audio_server_port(int(row[1]))

            udpSerSock.sendto(data.audio_struct_pack(), audio_client_addr)
        elif len(result) == 0:
            connect_cursor.close()
            db_connect.close()
            return -1
    # 更新语音界面Port
    elif data.get_audio_status() == AUDIO_STATUS_UPDATE:
        print("AUDIO_STATUS_UPDATE")
        sql = "UPDATE userTable SET audioPagePort = %d WHERE count = '%s'" % (audio_client_addr[1], data.get_my_count())
        connect_cursor.execute(sql)
        db_connect.commit()

    connect_cursor.close()
    db_connect.close()


def main():
    # 接收消息对象
    data = AudioStruct()
    while True:
        print("waitting for audio message...")
        # 接收客户端发来的消息和客户端地址
        rcv_data, audio_client_addr = udpSerSock.recvfrom(BUFFER_SIZE)
        data.set_rcv_data(rcv_data)

        #把data接受到的数据交给voice_handler函数进行处理
        ret = audio_handler(data, audio_client_addr)
        if ret == -1:
            print("voice_server:voice_handler error")
            break

    udpSerSock.close()


if __name__=="__main__":
    main()
