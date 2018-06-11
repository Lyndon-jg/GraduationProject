import socket
import os
from myProtocol import *


class fileClient():
    def __init__(self):
        self.addr = (FILE_SERVER_IP, FILE_SERVER_PORT)
        self.file_data = FileStruct()
        self.file_name = ''

    def sendFile(self, clientfile):
        print('sendFile:',clientfile)
        # 判断源文件是否存在
        if not os.path.exists(clientfile):
            return "fileNotExist"
        # 设置文件传输动作：上传
        self.file_data.set_action('upload')
        # 设置文件大小
        self.file_data.set_size(os.stat(clientfile).st_size)
        # 源文件路径
        self.file_data.set_client_file_path(clientfile)
        # 将数据打包发
        datas = self.file_data.file_struct_pack()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # 链接到服务器负责文件传输的socket
            s.connect(self.addr)
            # 将打包数据发送给服务器
            s.send(datas)
            # 接收服务器返回的消息，判断是否可以进行文件传输
            recv = s.recv(1024)
            # 不可以传输文件
            if recv.decode() == 'dirNotExist':
                return "upLoadFaile"
            # 可以传输文件
            elif recv.decode() == 'ok':
                fo = open(clientfile, 'rb')
                while True:
                    # 从文件读取数据
                    filedata = fo.read(1024)
                    # 文件读不到数据（读取完毕）
                    if not filedata:
                        break
                    # 发送数据
                    s.send(filedata)
                # 关闭文件
                fo.close()
                recv = s.recv(1024)

                if recv.decode() == 'ok':
                    s.close()
                    return 'upLoadSuccess'
        except Exception as e:
            print(e)
            return "error:" + str(e)

    def recvFile(self,serverfile):
        '''接受文件
        serverfile：从服务器上下载的文件
        '''
        # 若本地file文件夹不存在则创建
        if not os.path.exists('file'):
            try:
                os.mkdir('file')
            except Exception as e:
                print(e)
                return 'file dir not exist'
        # 设置文件传输行为：下载
        self.file_data.set_action('download')
        self.file_data.set_server_file_path(serverfile)
        print('recvFile:',serverfile)
        # 创建tcp socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # 链接到服务器负责文件传输的socket
            s.connect(self.addr)
            # 将数据打包
            datas = self.file_data.file_struct_pack()
            # 发送到服务器
            s.send(datas)
            # 接受服务器传回来的消息
            recv_data = s.recv(struct.calcsize(dataFormat))
            self.file_data.struct_unpack(recv_data)
            # 判断是否可以下载文件
            if self.file_data.get_action() == "ok":
                # 以收到的数据大小
                self.recvd_size = 0
                # 在file文件夹下创建新文件
                fileName = os.path.join('file/', (os.path.split(serverfile))[1])
                file = open(fileName, 'wb')
                # 传输文件
                while not self.recvd_size == self.file_data.get_size():
                    if self.file_data.get_size() - self.recvd_size > 1024:
                        rdata = s.recv(1024)
                        self.recvd_size += len(rdata)
                    else:
                        rdata = s.recv(self.file_data.get_size() - self.recvd_size)
                        self.recvd_size = self.file_data.get_size()
                    file.write(rdata)
                file.close()
                return 'downLoadSuccess'
            elif self.file_data.get_action() == "nofile":
                return "downLoadFaile"
        except Exception as e:
            print(e)
            return "error:" + str(e)
