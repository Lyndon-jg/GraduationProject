import pymysql
from socket import *
from myProtocol import *

# 初始化套接字
ADDR = ("",CHAT_SERVER_PORT)
udpSerSock = socket(AF_INET,SOCK_DGRAM)
udpSerSock.bind(ADDR)

def send_count_to_user(data, row):
    data.set_message(row[0]+"+"+str(row[1]))
    return data.chat_struct_pack()

def storeMessage(db_connect, connect_cursor, data):
    # 将消息插入到表中,然后返回
    try:
        sql = "INSERT INTO %s (time, first_count, second_count, message) VALUES ('%s', '%s','%s', '%s')" % (
            data.get_my_count() + '_chatRecord', data.get_time(), data.get_my_count(), data.get_friend_count(), data.get_message())
        connect_cursor.execute(sql)
        db_connect.commit()
    # 若插入失败
    except:
        print('消息插入失败1')
    try:
        sql = "INSERT INTO %s (time, first_count, second_count, message) VALUES ('%s', '%s','%s', '%s')" % (
            data.get_friend_count() + '_chatRecord', data.get_time(), data.get_my_count(), data.get_friend_count(), data.get_message())
        connect_cursor.execute(sql)
        db_connect.commit()
    # 若插入失败
    except:
        print('消息插入失败2')


def chat_handler(data, chat_client_addr, db_connect, connect_cursor):
    '''消息处理函数,并返回一个值'''
    # 判断聊天消息的状态
    # 好友聊天消息
    if data.get_chat_status() == CHAT_STATUS_MSG:
        print("CHAT_STATUS_MSG")
        # 查找好友的ip 和 port
        sql = "SELECT ip,chatPagePort FROM userTable where count = '%s'"%(data.get_friend_count())
        connect_cursor.execute(sql)
        result = connect_cursor.fetchall()
        # 找到好友ip 和 port
        if len(result) == 1:
            # 存储消息
            ret = storeMessage(db_connect, connect_cursor, data)
            if ret == -1:
                return ret
            else:
                # 将消息转发
                for row in result:
                    destination_addr = (row[0], int(row[1]))
                data.change_name()
                udpSerSock.sendto(data.chat_struct_pack(), destination_addr)
        # 未找到
        elif len(result) == 0:
            print('未找到好友')
            return -1
    # 查看当天聊天记录
    elif data.get_chat_status() == CHAT_STATUS_ONEDAY_MESSAGE:
        print('CHAT_STATUS_ONEDAY_MESSAGE')
        table_name = data.get_my_count()+'_chatRecord'
        sql = "SELECT time, first_count, second_count, message FROM %s WHERE (first_count='%s' and second_count='%s') or (first_count='%s' and second_count='%s')" % (
        table_name, data.get_my_count(), data.get_friend_count(), data.get_friend_count(), data.get_my_count())
        connect_cursor.execute(sql)
        result = connect_cursor.fetchall()
        if len(result) != 0:
            for row in result:
                # print(row[0][0:10], data.get_time()[0:10]) 匹配日期
                if row[0][0:10] == data.get_time()[0:10]:
                    data.set_time(row[0])
                    data.set_my_count(row[1])
                    data.set_friend_count(row[2])
                    data.set_message(row[3])
                    udpSerSock.sendto(data.chat_struct_pack(), chat_client_addr)

    # 获得自己的好友列表
    elif data.get_chat_status() == CHAT_STATUS_LIST:
        print("CHAT_STATUS_LIST")
        # 查找userTable 将所有用户名称发给登录用户
        sql = "SELECT count,status FROM userTable"
        connect_cursor.execute(sql)
        result = connect_cursor.fetchall()
        for row in result:
            udpSerSock.sendto(send_count_to_user(data, row), chat_client_addr)
    # 更新聊天界面的ip 和 port
    elif data.get_chat_status() == CHAT_STATUS_UPDATE_CHAT_PAGE:
        print("CHAT_STATUS_UPDATE_CHAT_PAGE")
        sql = "UPDATE userTable SET ip = '%s', chatPagePort = '%s' WHERE count = '%s'" % (chat_client_addr[0], chat_client_addr[1], data.get_my_count())
        connect_cursor.execute(sql)
        db_connect.commit()
    # 更新消息记录界面的port
    elif data.get_chat_status() == CHAT_STATUS_UPDATE_RECORD_PAGE:
        print("CHAT_STATUS_UPDATE_RECORD_PAGE")
        sql = "UPDATE userTable SET chatRecordPagePort = '%s' WHERE count = '%s'" % (chat_client_addr[1], data.get_my_count())
        # print(sql)
        connect_cursor.execute(sql)
        db_connect.commit()
    # 语音请求消息
    elif data.get_chat_status() == CHAT_STATUS_AUDIO_REQUEST:
        print("VOICE_STATUS_REQUEST")
        sql = "SELECT ip,chatPagePort FROM userTable where count = '%s'" % (data.get_friend_count())
        connect_cursor.execute(sql)
        result = connect_cursor.fetchall()
        if len(result) == 1:
            for row in result:
                destination_addr = (row[0], int(row[1]))
            data.change_name()
            udpSerSock.sendto(data.chat_struct_pack(), destination_addr)
        elif len(result) == 0:
            print('未找到好友')
            return -1
    # 查看聊天记录
    elif data.get_chat_status() == CHAT_STATUS_CHAT_RECORE:
        print("CHAT_STATUS_CHAT_RECORE")

        sql = "SELECT ip,chatRecordPagePort FROM userTable where count = '%s'" % (data.get_my_count())
        connect_cursor.execute(sql)
        result = connect_cursor.fetchall()
        if len(result) == 1:
            for row in result:
                chat_record_addr = (row[0], int(row[1]))
            table_name = data.get_my_count()+'_chatRecord'
            # 查找聊天记录
            sql = "SELECT time, first_count, second_count, message FROM %s WHERE (first_count='%s' and second_count='%s') or (first_count='%s' and second_count='%s')" % (table_name, data.get_my_count(), data.get_friend_count(),data.get_friend_count(),data.get_my_count())
            connect_cursor.execute(sql)
            result = connect_cursor.fetchall()
            if len(result) != 0:
                # 将聊天记录发送到客户端
                for row in result:
                    data.set_time(row[0])
                    data.set_my_count(row[1])
                    data.set_friend_count(row[2])
                    data.set_message(row[3])
                    udpSerSock.sendto(data.chat_struct_pack(), chat_record_addr)
        elif len(result) == 0:
            print('未找到好友')
            return -1
    # 退出，更新在线状态为0
    elif data.get_chat_status() == CHAT_STATUS_EXIT:
        sql = "UPDATE userTable SET status = 0 WHERE count = '%s'" % (data.get_my_count())
        connect_cursor.execute(sql)
        db_connect.commit()


def main():
    try:
        # 打开数据库
        db_connect = pymysql.connect(host = "localhost", user = "root", passwd = "ljgubuntu", db = "graduationPorject", charset='utf8')
        connect_cursor = db_connect.cursor()
    except:
        print('open db file')
        return -1
    # 接收消息对象
    data = ChatStruct()
    while True:
        print("waitting for chat message...")
        # 接收客户端发来的消息和客户端地址
        rcv_data, chat_client_addr = udpSerSock.recvfrom(BUFFER_SIZE)
        data.set_rcv_data(rcv_data)

        #把data接受到的数据交给chat_handler函数进行处理
        ret = chat_handler(data, chat_client_addr, db_connect, connect_cursor)
        if ret == -1:
            print("chat_server:chat_handler error")
            break

    connect_cursor.close()
    db_connect.close()
    udpSerSock.close()
    print('close')


if __name__=="__main__":
    main()
