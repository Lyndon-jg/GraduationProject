import struct
DEFAULT_SERVER_IP = "127,0.0.1"
BUFFER_SIZE = 1024

# 注册
REGISTER_SERVER_IP = DEFAULT_SERVER_IP
REGISTER_SERVER_PORT = 1111
REGISTER_STATUS_OK = 0
REGISTER_STATUS_FAIL = 1

class RegisterStruct:
    def __init__(self):
        # 私有变量
        self.__count = None
        self.__passwd = None
        self.__status = 0
        self.rcv_data = None

    def rgs_struct_pack(self):
        self.__count = str(struct.pack("i", len(self.__count)), "utf-8") + self.__count
        self.__passwd = str(struct.pack("i", len(self.__passwd)), "utf-8") + self.__passwd
        send_data = struct.pack("64s64si", self.__count.encode(), self.__passwd.encode(), self.__status)
        return send_data


    def rgs_struct_unpack(self):
        self.__count, self.__passwd, self.__status = struct.unpack("64s64si", self.rcv_data)
        # 解压帐号
        length = struct.unpack('i', self.__count[0:4])[0]
        # print(length)
        str_content = struct.unpack('{length}s'.format(length=length), self.__count[4:4 + length])[0]
        self.__count = str(str_content, "utf-8")
        # 解压密码
        length = struct.unpack('i', self.__passwd[0:4])[0]
        str_content = struct.unpack('{length}s'.format(length=length), self.__passwd[4:4 + length])[0]
        self.__passwd = str(str_content, "utf-8")
        # print(str_content)
        '''
        length = struct.unpack('i', data[0:4])[0]
        # print(length)
        str_content = struct.unpack('{length}s'.format(length=length), data[4:4 + length])[0]
        str_content = str(str_content, "utf-8")
        # print(str_content)
        return str_content
        '''

    def set_count(self, count):
        self.__count = count

    def get_count(self):
        return self.__count

    def set_passwd(self, passed):
        self.__passwd = passed

    def get_passwd(self):
        return self.__passwd

    def set_status(self, status):
        self.__status = status

    def get_status(self):
        return self.__status

    def set_rcv_data(self, rcv_data):
        self.rcv_data = rcv_data
        self.rgs_struct_unpack()

# 登录
LOGIN_SERVER_IP = DEFAULT_SERVER_IP
LOGIN_SERVER_PORT = 2222
LOGIN_STATUS_OK = 0
LOGIN_STATUS_FAIL = 1
# LOGIN_STATUS_FAILC = 1
# LOGIN_STATUS_FAILP = 2

class LoginStruct:
    def __init__(self):
        # 私有变量
        self.__count = None
        self.__passwd = None
        self.__status = 0
        self.rcv_data = None

    def login_struct_pack(self):
        self.__count = str(struct.pack("i", len(self.__count)), "utf-8") + self.__count
        self.__passwd = str(struct.pack("i", len(self.__passwd)), "utf-8") + self.__passwd
        send_data = struct.pack("64s64si", self.__count.encode(), self.__passwd.encode(), self.__status)
        return send_data

    def login_struct_unpack(self):
        self.__count, self.__passwd, self.__status = struct.unpack("64s64si", self.rcv_data)
        # 解压帐号
        length = struct.unpack('i', self.__count[0:4])[0]
        # print(length)
        str_content = struct.unpack('{length}s'.format(length=length), self.__count[4:4 + length])[0]
        self.__count = str(str_content, "utf-8")
        # 解压密码
        length = struct.unpack('i', self.__passwd[0:4])[0]
        str_content = struct.unpack('{length}s'.format(length=length), self.__passwd[4:4 + length])[0]
        self.__passwd = str(str_content, "utf-8")

    def set_count(self, count):
        self.__count = count

    def get_count(self):
        return self.__count

    def set_passwd(self, passed):
        self.__passwd = passed

    def get_passwd(self):
        return self.__passwd

    def set_status(self, status):
        self.__status = status

    def get_status(self):
        return self.__status

    def set_rcv_data(self, rcv_data):
        self.rcv_data = rcv_data
        self.login_struct_unpack()

# 聊天
CHAT_SERVER_IP = DEFAULT_SERVER_IP
CHAT_SERVER_PORT = 3333
CHAT_STATUS_LIST = 0
CHAT_STATUS_MSG = 1
CHAT_STATUS_UPDATE = 2
CHAT_STATUS_HEART = 3
MSGSIZE = 1024

class ChatStruct:
    def __init__(self):
        self.__my_count = None
        self.__friend_count = None
        self.__message = None
        # 好友列表 / 消息  / 更新 ip and port
        self.__chat_status = None
        # 是否为心脏包
        # self._is_heart = None
        self.rcv_data = None

    def chat_struct_pack(self):
        self.__my_count = str(struct.pack("i", len(self.__my_count)), "utf-8") + self.__my_count
        self.__friend_count = str(struct.pack("i", len(self.__friend_count)), "utf-8") + self.__friend_count
        self.__message = str(struct.pack("i", len(self.__message)), "utf-8") + self.__message
        send_data = struct.pack("64s64s892si",
                                self.__my_count.encode(),
                                self.__friend_count.encode(),
                                self.__message.encode(),
                                self.__chat_status
                                )
        return send_data

    def chat_struct_unpack(self):
        self.__my_count, self.__friend_count, self.__message, self.__chat_status = struct.unpack("64s64s892si", self.rcv_data)
        length = struct.unpack('i', self.__my_count[0:4])[0]
        str_content = struct.unpack('{length}s'.format(length=length), self.__my_count[4:4 + length])[0]
        self.__my_count = str(str_content, "utf-8")

        length = struct.unpack('i', self.__friend_count[0:4])[0]
        str_content = struct.unpack('{length}s'.format(length=length), self.__friend_count[4:4 + length])[0]
        self.__friend_count = str(str_content, "utf-8")

        length = struct.unpack('i', self.__message[0:4])[0]
        str_content = struct.unpack('{length}s'.format(length=length), self.__message[4:4 + length])[0]
        self.__message = str(str_content, "utf-8")

    def change_name(self):
        name = self.__my_count
        self.__my_count = self.__friend_count
        self.__friend_count = name


    def set_my_count(self, my_count):
        self.__my_count = my_count

    def get_my_count(self):
        return self.__my_count

    def set_friend_count(self, friend_count):
        self.__friend_count = friend_count

    def get_friend_count(self):
        return self.__friend_count

    def set_message(self, message):
        self.__message = message

    def get_message(self):
        return self.__message

    def set_chat_status(self, chat_status):
        self.__chat_status = chat_status

    def get_chat_status(self):
        return self.__chat_status

    def set_rcv_data(self, rcv_data):
        self.rcv_data = rcv_data
        self.chat_struct_unpack()