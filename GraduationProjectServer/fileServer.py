from socket import *
import os
import socketserver
import threading
import time
from myProtocol import *
dataFormat = '8s100s100sl'
file_dir = 'file'

# 初始化套接字
ADDR = ("",FILE_SERVER_PORT_2)
udpSerSock = socket(AF_INET,SOCK_DGRAM)
udpSerSock.bind(ADDR)

class fileServer(socketserver.StreamRequestHandler):
    def handle(self):
        self.file_data = FileStruct()
        print('connected from:', self.client_address)
        fileinfo_size = struct.calcsize(dataFormat)
        recv_data = self.request.recv(fileinfo_size)
        if recv_data:
            self.file_data.struct_unpack(recv_data)
            print("get action:" + self.file_data.get_action())
            if self.file_data.get_action().startswith("upload"):
                try:
                    # 服务器端 文件夹/文件名 是否为文件夹
                    if os.path.isdir(self.file_data.get_server_file_path()):
                        # 分割pathName,[1]：找到文件名clientfilePath
                        fileName = (os.path.split(self.file_data.get_client_file_path()))[1]
                        # 将存储路径和文件名链接起来
                        self.file_data.set_server_file_path(os.path.join(self.file_data.get_server_file_path(), fileName))
                    # 将文件路径分为 文件夹和文件名
                    filePath, fileName = os.path.split(self.file_data.get_server_file_path())
                    # 判断文件夹是否存在
                    if not os.path.exists(filePath):
                        self.request.send(str.encode('dirNotExist'))
                    else:
                        self.request.send(str.encode('ok'))

                        recvd_size = 0
                        file = open(self.file_data.get_server_file_path(), 'wb')
                        while not recvd_size == self.file_data.get_size():
                            if self.file_data.get_size() - recvd_size > 1024:
                                rdata = self.request.recv(1024)
                                recvd_size += len(rdata)
                            else:
                                rdata = self.request.recv(self.file_data.get_size() - recvd_size)
                                recvd_size = self.file_data.get_size()
                            file.write(rdata)
                        file.close()
                        self.request.send(str.encode('ok'))
                except Exception as e:
                    print(e)
                finally:
                    self.request.close()
            elif self.file_data.get_action().startswith("download"):
                try:
                    if os.path.exists(self.file_data.get_server_file_path()):
                        self.file_data.set_action('ok')
                        self.file_data.set_size(os.stat(self.file_data.get_server_file_path()).st_size)
                        ret = self.file_data.file_struct_pack()
                        self.request.send(ret)
                        fo = open(self.file_data.get_server_file_path(), 'rb')
                        while True:
                            filedata = fo.read(1024)
                            if not filedata:
                                break
                            self.request.send(filedata)
                        fo.close()
                    else:
                        self.file_data.set_action('nofile')
                        ret = self.file_data.file_struct_pack()
                        self.request.send(ret)
                except Exception as e:
                    print(e)
                finally:
                    self.request.close()


class fileServerth(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.create_time = time.time()
        self.local = threading.local()

    def run(self):
        print("fileServer is running...")
        fileserver.serve_forever()


def main():
    while True:
        rcv_data, file_client_addr = udpSerSock.recvfrom(BUFFER_SIZE)
        if int(rcv_data.decode('utf-8')) == FILE_STATUS_UPDATE:
            for root, dirs, files in os.walk(file_dir):
                # print('=================================')
                # print(root)  # 当前目录路径
                # print(dirs)  # 当前路径下所有子目录
                # print(files)  # 当前路径下所有非目录子文件
                # print('=================================')
                udpSerSock.sendto(str(files).encode('utf-8'), file_client_addr)
                break
        else:
            print('file:not update')
            break


if __name__ == '__main__':
    fileserver = socketserver.ThreadingTCPServer((FILE_SERVER_IP,FILE_SERVER_PORT), fileServer)
    fileserverth = fileServerth()
    fileserverth.start()
    main()
