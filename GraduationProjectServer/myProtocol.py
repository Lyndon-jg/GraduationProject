# -*- coding:UTF-8 -*-
import struct

DEFAULT_SERVER_IP = "127.0.0.1"
BUFFER_SIZE = 2048

# -------------------------------注册----------------------------------
REGISTER_SERVER_IP = DEFAULT_SERVER_IP
REGISTER_SERVER_PORT = 1111
REGISTER_STATUS_OK = 0
REGISTER_STATUS_FAIL = 1


class RegisterStruct:
    def __init__(self):
        # 私有变量
        # 存放 账户 密码 状态的字典
        self.register_data = {}
        self.__count = None
        self.__passwd = None
        self.__status = 0
        # 接收服务器返回来的消息
        self.rcv_data = None

    def rgs_struct_pack(self):
        '''将账户 密码 状态放入字典，返回要发送的字节流数据'''
        self.register_data["count"] = self.__count
        self.register_data["passwd"] = self.__passwd
        self.register_data["status"] = self.__status
        # 先将字典转换成字符串然后编码
        return str(self.register_data).encode("utf-8")

    def rgs_struct_unpack(self):
        '''对接受到的数据进行解码成字符串在转换成字典'''
        self.register_data = eval(self.rcv_data.decode())
        self.__count = self.register_data["count"]
        self.__passwd = self.register_data["passwd"]
        self.__status = self.register_data["status"]

    def set_count(self, count):
        self.__count = count

    def get_count(self):
        return self.__count

    def set_passwd(self, passwd):
        self.__passwd = passwd

    def get_passwd(self):
        return self.__passwd

    def set_status(self, status):
        self.__status = status

    def get_status(self):
        return self.__status

    def set_rcv_data(self, rcv_data):
        self.rcv_data = rcv_data
        self.rgs_struct_unpack()


# -------------------------------注册----------------------------------

# -------------------------------登录----------------------------------
LOGIN_SERVER_IP = DEFAULT_SERVER_IP
LOGIN_SERVER_PORT = 2222
LOGIN_STATUS_OK = 0
LOGIN_STATUS_FAIL = 1


class LoginStruct:
    def __init__(self):
        # 私有变量
        # 存放 账户 密码 状态的字典
        self.login_data = {}
        self.__count = None
        self.__passwd = None
        self.__status = 0
        # 接收返回的消息
        self.rcv_data = None

    def login_struct_pack(self):
        '''将账户 密码 状态放入字典，返回要发送的字节流数据'''
        self.login_data["count"] = self.__count
        self.login_data["passwd"] = self.__passwd
        self.login_data["status"] = self.__status
        # 先将字典转换成字符串然后编码
        return str(self.login_data).encode("utf-8")

    def login_struct_unpack(self):
        '''对接受到的数据进行解码成字符串在转换成字典'''
        self.login_data = eval(self.rcv_data.decode())
        self.__count = self.login_data["count"]
        self.__passwd = self.login_data["passwd"]
        self.__status = self.login_data["status"]

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


# -------------------------------登录----------------------------------


# 聊天
CHAT_SERVER_IP = DEFAULT_SERVER_IP
CHAT_SERVER_PORT = 3333

CHAT_STATUS_LIST = 0
CHAT_STATUS_MSG = 1
CHAT_STATUS_UPDATE_CHAT_PAGE = 2
CHAT_STATUS_AUDIO_REQUEST = 3
CHAT_STATUS_CHAT_RECORE = 4
CHAT_STATUS_UPDATE_RECORD_PAGE = 5
CHAT_STATUS_ONEDAY_MESSAGE = 6
CHAT_STATUS_EXIT = 7
CHAT_STATUS_CHECK_STATUS = 8


class ChatStruct:
    def __init__(self):
        self.chat_data = {}
        self.rcv_data = None

        self.__my_count = None
        self.__friend_count = None
        self.__time = None
        self.__message = None
        # 好友列表 / 消息  / 更新 ip and port
        self.__chat_status = None

        self.__destnation_ip = None
        self.__destnation_port = None

    def chat_struct_pack(self):
        '''将自己用户名，朋友用户名，以及要发送的消息，和消息类型，打包成字节流'''
        self.chat_data["my_count"] = self.__my_count
        self.chat_data["friend_count"] = self.__friend_count
        self.chat_data["chat_status"] = self.__chat_status
        self.chat_data["time"] = self.__time
        self.chat_data["message"] = self.__message
        # 先将字典转换成字符串然后编码
        return str(self.chat_data).encode("utf-8")

    def chat_struct_unpack(self):
        '''对接受到的数据进行解码成字符串在转换成字典'''
        self.chat_data = eval(self.rcv_data.decode())
        self.__my_count = self.chat_data["my_count"]
        self.__friend_count = self.chat_data["friend_count"]
        self.__chat_status = self.chat_data["chat_status"]
        self.__time = self.chat_data["time"]
        self.__message = self.chat_data["message"]

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

    def set_time(self, time):
        self.__time = time

    def get_time(self):
        return self.__time

    def set_message(self, message):
        self.__message = message

    def get_message(self):
        return self.__message

    def set_chat_status(self, chat_status):
        self.__chat_status = chat_status

    def get_chat_status(self):
        return self.__chat_status

    def set_destnation_ip(self, destnation_ip):
        self.__destnation_ip = destnation_ip

    def get_destnation_ip(self):
        return self.__destnation_ip

    def set_destnation_port(self, destnation_port):
        self.__destnation_port = destnation_port

    def get_destnation_port(self):
        return self.__destnation_port

    def set_rcv_data(self, rcv_data):
        self.rcv_data = rcv_data
        self.chat_struct_unpack()


# ----------------------------文件

FILE_SERVER_IP = DEFAULT_SERVER_IP
# 文件传输
FILE_SERVER_PORT = 19812
# 文件名传输
FILE_SERVER_PORT_2 = 19813

FILE_STATUS_UPLOAD = 1
FILE_STATUS_DOWNLOAD = 2
# 更新文件列表
FILE_STATUS_UPDATE = 3
dataFormat = '8s100s100sl'


class FileStruct:
    def __init__(self):
        self.file_data = {}
        self.rcv_data = None

        # 文件传输动作
        self.action = ''
        # 文件路径
        self.client_file_path = ''
        self.server_file_path = ''
        # 文件大小
        self.size = 0

    def file_struct_pack(self):
        ret = struct.pack(dataFormat, self.action.encode(), self.client_file_path.encode(),
                          self.server_file_path.encode(), self.size)
        return ret

    def struct_unpack(self, package):
        self.action, self.client_file_path, self.server_file_path, self.size = struct.unpack(dataFormat, package)
        self.action = self.action.decode().strip('\x00')
        self.client_file_path = self.client_file_path.decode().strip('\x00')
        self.server_file_path = self.server_file_path.decode().strip('\x00')

    def set_action(self, action):
        self.action = action

    def get_action(self):
        return self.action

    def set_file_name(self, file_name):
        self.file_name = file_name

    def get_file_name(self):
        return self.file_name

    def set_client_file_path(self, client_file_path):
        self.client_file_path = client_file_path

    def get_client_file_path(self):
        return self.client_file_path

    def set_server_file_path(self, server_file_path):
        self.server_file_path = server_file_path

    def get_server_file_path(self):
        return self.server_file_path

    def set_size(self, size):
        self.size = size

    def get_size(self):
        return self.size


# --------------------------------------语音
AUDIO_SERVER_IP = DEFAULT_SERVER_IP
AUDIO_SERVER_PORT = 55555
# 更新端口号
AUDIO_STATUS_UPDATE_CLIENT_PORT = 1
AUDIO_STATUS_UPDATE_SERVER_PORT = 2

AUDIO_STATUS_UPDATE = 3
# 接受 拒绝语音通信
AUDIO_STATUS_REJECT = 4
AUDIO_STATUS_ACCEPT = 5
# 关闭语音通信
AUDIO_STATU_CLOSE = 6


class AudioStruct:
    def __init__(self):
        self.audio_data = {}
        self.rcv_data = None

        self.__audio_status = 0
        self.__my_count = ''
        self.__friend_count = ''
        self.__audio_server_ip = ''
        self.__audio_server_port = 0

    def audio_struct_pack(self):
        '''将自己用户名,语音recrive端口和消息状态，打包成字节流'''
        self.audio_data["my_count"] = self.__my_count
        self.audio_data["friend_count"] = self.__friend_count
        self.audio_data["audio_status"] = self.__audio_status
        self.audio_data['server_ip'] = self.__audio_server_ip
        self.audio_data['server_port'] = self.__audio_server_port
        # 先将字典转换成字符串然后编码
        return str(self.audio_data).encode("utf-8")

    def audio_struct_unpack(self):
        '''对接受到的数据进行解码成字符串在转换成字典'''
        self.audio_data = eval(self.rcv_data.decode("utf-8"))
        self.__my_count = self.audio_data["my_count"]
        self.__friend_count = self.audio_data["friend_count"]
        self.__audio_status = self.audio_data["audio_status"]
        self.__audio_server_ip = self.audio_data['server_ip']
        self.__audio_server_port = self.audio_data["server_port"]

    def change_name(self):
        name = self.__my_count
        self.__my_count = self.__friend_count
        self.__friend_count = name

    def set_rcv_data(self, rcv_data):
        self.rcv_data = rcv_data
        self.audio_struct_unpack()

    def set_my_count(self, my_count):
        self.__my_count = my_count

    def get_my_count(self):
        return self.__my_count

    def set_friend_count(self, friend_count):
        self.__friend_count = friend_count

    def get_friend_count(self):
        return self.__friend_count

    def set_audio_server_ip(self, server_ip):
        self.__audio_server_ip = server_ip

    def get_audio_server_ip(self):
        return self.__audio_server_ip

    def set_audio_server_port(self, server_port):
        self.__audio_server_port = server_port

    def get_audio_server_port(self):
        return self.__audio_server_port

    def set_audio_status(self, status):
        self.__audio_status = status

    def get_audio_status(self):
        return self.__audio_status



