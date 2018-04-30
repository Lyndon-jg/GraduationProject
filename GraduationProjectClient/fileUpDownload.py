import socket
import os
from myProtocol import *


class fileClient():
    def __init__(self, addr):
        self.addr = addr
        self.file_data = FileStruct()
        self.file_name = ''

    def sendFile(self, clientfile, serverfile):
        print('sendFile:',clientfile,serverfile)
        if not os.path.exists(clientfile):
            print("源文件不存在")
            return "No such file or directory"
        self.file_data.set_action('upload')
        self.file_data.set_size(os.stat(clientfile).st_size)
        self.file_data.set_server_file_path(serverfile)
        self.file_data.set_client_file_path(clientfile)

        datas = self.file_data.file_struct_pack()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(self.addr)
            s.send(datas)

            recv = s.recv(1024)

            if recv.decode() == 'dirNotExist':
                print("目标文件/文件夹不存在")
                return "No such file or directory"
            elif recv.decode() == 'ok':
                fo = open(clientfile, 'rb')
                while True:
                    filedata = fo.read(1024)
                    if not filedata:
                        break
                    s.send(filedata)
                fo.close()
                recv = s.recv(1024)

                if recv.decode() == 'ok':
                    print("文件传输成功")
                    s.close()
                    return 0
        except Exception as e:
            print(e)
            return "error:" + str(e)

    def recvFile(self, clientfile, serverfile):
        if not os.path.isdir(clientfile):
            filePath, fileName = os.path.split(clientfile)
        else:
            filePath = clientfile
        if not os.path.exists(filePath):
            print('本地目标文件/文件夹不存在')
            return "No such file or directory"

        self.file_data.set_action('download')
        self.file_data.set_client_file_path(clientfile)
        self.file_data.set_server_file_path(serverfile)
        print('recvFile:',clientfile,serverfile)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(self.addr)
            # ret = self.struct_pack()
            datas = self.file_data.file_struct_pack()
            s.send(datas)
            recv_data = s.recv(struct.calcsize(dataFormat))
            self.file_data.struct_unpack(recv_data)
            # self.struct_unpack(recv)
            if self.file_data.get_action().startswith("ok"):
                if os.path.isdir(clientfile):
                    fileName = (os.path.split(serverfile))[1]
                    clientfile = os.path.join(clientfile, fileName)
                self.recvd_size = 0
                file = open(clientfile, 'wb')
                while not self.recvd_size == self.file_data.get_size():
                    if self.file_data.get_size() - self.recvd_size > 1024:
                        rdata = s.recv(1024)
                        self.recvd_size += len(rdata)
                    else:
                        rdata = s.recv(self.file_data.get_size() - self.recvd_size)
                        self.recvd_size = self.file_data.get_size()
                    file.write(rdata)
                file.close()
                print("文件传输成功")
            elif self.file_data.get_action().startswith("nofile"):
                print('远程源文件/文件夹不存在')
                return "No such file or directory"
        except Exception as e:
            print(e)
            return "error:" + str(e)
