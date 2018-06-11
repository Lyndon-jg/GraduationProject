from socket import *
import pyaudio
import struct
import pickle
import time
import random
from PyQt5.QtCore import QThread
from myProtocol import *
# https://blog.csdn.net/lu_embedded/article/details/50784355

# 每次读取和播放的帧数
CHUNK = 1024
# 采样大小（精度）
FORMAT = pyaudio.paInt16
# 通道数
CHANNELS = 1
# 采样频率：每秒采集数据的次数
RATE = 44100
# 每次记录的时间 即间隔0.5s发送一次
RECORD_SECONDS = 0.5

class AudioServer(QThread):

    def __init__(self) :
        QThread.__init__(self)
        # 关闭线程标志
        self.closeThreadFlag = 0
        # 自己的用户名和好友的用户名
        self.my_count = ''
        self.friend_count = ''
        # 端口号和地址
        self.port = 0
        self.ADDR = ()
        # 语音数据对象
        self.audio_data = AudioStruct()
        # server  tcp  socket
        self.audio_server_tcp_socket = socket(AF_INET, SOCK_STREAM)
        # server  udp  socket
        self.audio_server_udp_socket = socket(AF_INET, SOCK_DGRAM)
        # 定义PyAudio对象
        self.p = pyaudio.PyAudio()
        # 数据流
        self.stream = None

    def __del__(self):
        # 关闭socket
        self.audio_server_tcp_socket.close()
        self.audio_server_udp_socket.close()
        # 如果stream不为空，停止并关闭
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        # 中断PyAudio对象
        self.p.terminate()

    # 关闭audio server
    def closeAudioServer(self):
        # 设置关闭线程标志为1
        self.closeThreadFlag = 1
    # 设置账户名函数
    def setCount(self, my_count, friend_count):
        self.my_count = my_count
        self.friend_count = friend_count

    # 启动线程
    def run(self):
        print("AUDIO server starts...")
        while True:
            # 随机生成一个端口并绑定，直到成功
            try:
                # 随机生成port
                self.port = random.randint(1025,65535)
                self.ADDR = ('', self.port)
                # 绑定
                self.audio_server_tcp_socket.bind(self.ADDR)
                # 监听
                self.audio_server_tcp_socket.listen(1)
                print('audio server port:%d'%self.port)
                #--------告知服务器更新tcp socket端口---------
                self.audio_data.set_my_count(self.my_count)
                self.audio_data.set_audio_server_port(self.port)
                self.audio_data.set_audio_status(AUDIO_STATUS_UPDATE_SERVER_PORT)
                self.audio_server_udp_socket.sendto(self.audio_data.audio_struct_pack(),(AUDIO_SERVER_IP, AUDIO_SERVER_PORT))
                break
            except:
                print('bind error, trying...')
                time.sleep(1)
        # 接受客户端的连接
        connect, addr = self.audio_server_tcp_socket.accept()
        print("remote AUDIO client success connected...")
        data = "".encode("utf-8")
        # 有效载荷大小（8）
        payloadSize = struct.calcsize("L")
        # 创建新的音频流
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  output=True,
                                  frames_per_buffer = CHUNK
                                  )
        while self.closeThreadFlag == 0:
            while len(data) < payloadSize:
                data += connect.recv(81920)
            # 收到数据大小（bytes类型）
            recvSize = data[:payloadSize]
            # 有效数据
            data = data[payloadSize:]
            # 收到的数据大小（返回元组（xxx，））
            unpackedDataSize = struct.unpack("L", recvSize)[0]
            print(unpackedDataSize)
#            while len(data) < unpackedDataSize:
#                data += connect.recv(81920)
            # 帧数据
            frameData = data[:unpackedDataSize]
            # 剩余数据
#            data = data[unpackedDataSize:]
            data = "".encode("utf-8")
#            print(len(data))
            # 反序列化帧数据
            frames = pickle.loads(frameData)
            # 输出每一帧的数据
            for frame in frames:
                self.stream.write(frame, CHUNK)

class AudioClient(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.closeThreadFlag = 0

        self.my_count = ''
        self.friend_count = ''

        self.audio_server_ip = ''
        self.audio_server_port = 0
        self.ADDR = ()

        self.audio_data = AudioStruct()

        self.audio_server_tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.audio_server_udp_socket = socket(AF_INET, SOCK_DGRAM)

        self.p = pyaudio.PyAudio()
        self.stream = None

    def __del__(self) :
        self.audio_server_tcp_socket.close()
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

    def closeAudioClient(self):
        self.closeThreadFlag = 1

    def setCount(self,my_count ,friend_count):
        self.my_count = my_count
        self.friend_count = friend_count

    def setIpPort(self, ip, port):
        self.ip = ip
        self.port = port
        self.ADDR = (self.ip, self.port)

    def run(self):
        print("AUDIO client starts...")

        while True:
            # 更新自己端口
            # 向服务器要对方的ip, 端口，并联接
            self.audio_data.set_my_count(self.my_count)
            self.audio_data.set_friend_count(self.friend_count)
            self.audio_data.set_audio_status(AUDIO_STATUS_UPDATE_CLIENT_PORT)
            self.audio_server_udp_socket.sendto(self.audio_data.audio_struct_pack(),(AUDIO_SERVER_IP, AUDIO_SERVER_PORT))
            recv_data, addr = self.audio_server_udp_socket.recvfrom(BUFFER_SIZE)
            self.audio_data.set_rcv_data(recv_data)
            self.audio_server_ip = self.audio_data.get_audio_server_ip()
            self.audio_server_port = self.audio_data.get_audio_server_port()
            self.ADDR = (self.audio_server_ip, self.audio_server_port)
            print('audio client :server addr is', self.ADDR)

            try:
                self.audio_server_tcp_socket.connect(self.ADDR)
                break
            except:
                print('connect faile, trying')
                time.sleep(1)
                continue

        print("AUDIO client connected...")
        # 创建新的数据流
        self.stream = self.p.open(format=FORMAT,
                             channels=CHANNELS,
                             rate=RATE,
                             input=True,
                             frames_per_buffer=CHUNK)
        while self.closeThreadFlag == 0 and self.stream.is_active() :
            frames = []
            # 每0.5s采集的帧
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = self.stream.read(CHUNK)
                frames.append(data)
            # 语音帧数据序列化(转换成可存储或传输的形式)
            senddata = pickle.dumps(frames)
            try:
                self.audio_server_tcp_socket.sendall(struct.pack("L", len(senddata)) + senddata)
            except:
                break
