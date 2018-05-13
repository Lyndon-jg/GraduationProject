from socket import *
import os
import socketserver
import threading
import time
from myProtocol import *
# 数据格式：
# dataFormat = '8s100s100sl'
file_dir = 'file'
# https://www.cnblogs.com/renpingsheng/p/7260974.html
# 初始化套接字
ADDR = ("",FILE_SERVER_PORT_2)
udpSerSock = socket(AF_INET,SOCK_DGRAM)
udpSerSock.bind(ADDR)

# StreamRequestHandler         TCP请求处理类的一个实现
class fileServer(socketserver.StreamRequestHandler):
    def handle(self):
        self.file_data = FileStruct()
        print('connected from:', self.client_address)
        fileinfo_size = struct.calcsize(dataFormat)
        # 接受fileinfo_size 大小的数据
        recv_data = self.request.recv(fileinfo_size)
        # 接收到数据
        if recv_data:
            # 将数据解析出来
            self.file_data.struct_unpack(recv_data)
            print("get action:" + self.file_data.get_action())
            # 判断是要上传文件，还是下载文件
            # 上传
            if self.file_data.get_action().startswith("upload"):
                try:
                    if not os.path.exists(self.file_data.get_server_file_path()):
                        try:
                            os.mkdir('file')
                        except Exception as e:
                            print(e)
                            self.request.send(str.encode('dirNotExist'))
                            self.request.close()
                            return 'file dir not exist'
                    # else:
                    self.request.send(str.encode('ok'))
                    # 以收到数据的大小
                    recvd_size = 0
                    # 分割客户端文件为路径（0） 和 文件名（1）：找到文件名[1]
                    fileName = (os.path.split(self.file_data.get_client_file_path()))[1]
                    #           将要存储的文件路径和文件名结合起来，并创建新的文件
                    file = open(os.path.join(self.file_data.get_server_file_path(), fileName), 'wb')
                    # 以收到数据的大小   和  文件的大小
                    while not recvd_size == self.file_data.get_size():
                        if self.file_data.get_size() - recvd_size > 1024:
                            rdata = self.request.recv(1024)
                            recvd_size += len(rdata)
                        else:
                            rdata = self.request.recv(self.file_data.get_size() - recvd_size)
                            recvd_size = self.file_data.get_size()
                        # 将收到的数据写入文件
                        file.write(rdata)
                    # 关闭文件
                    file.close()
                    # 告诉客户端接收完毕
                    self.request.send(str.encode('ok'))
                except Exception as e:
                    print(e)
                finally:
                    self.request.close()
            # 下载
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
