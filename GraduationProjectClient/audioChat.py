from socket import *
import pyaudio
import struct
import pickle
import time
import random
from PyQt5.QtCore import QThread
from myProtocol import *

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 0.5

class AudioServer(QThread):

    def __init__(self) :
        QThread.__init__(self)
        self.closeThreadFlag = 0

        self.my_count = ''
        self.friend_count = ''

        self.port = 0
        self.ADDR = ()

        self.audio_data = AudioStruct()

        self.audio_server_tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.audio_server_udp_socket = socket(AF_INET, SOCK_DGRAM)

        self.p = pyaudio.PyAudio()
        self.stream = None

    def __del__(self):
        self.audio_server_tcp_socket.close()
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

    def closeAudioServer(self):
        self.closeThreadFlag = 1

    def setCount(self, my_count, friend_count):
        self.my_count = my_count
        self.friend_count = friend_count

    def run(self):
        print("AUDIO server starts...")
        while True:
            try:
                # 设置tcp绑定 监听
                self.port = random.randint(1025,65535)
                self.ADDR = ('', self.port)
                self.audio_server_tcp_socket.bind(self.ADDR)
                self.audio_server_tcp_socket.listen(1)
                print('audio server port:%d'%self.port)
                #--------更新端口
                self.audio_data.set_my_count(self.my_count)
                self.audio_data.set_audio_server_port(self.port)
                self.audio_data.set_audio_status(AUDIO_STATUS_UPDATE_SERVER_PORT)
                self.audio_server_udp_socket.sendto(self.audio_data.audio_struct_pack(),(AUDIO_SERVER_IP, AUDIO_SERVER_PORT))
                break
            except:
                print('bind error, trying...')
                time.sleep(1)
        connect, addr = self.audio_server_tcp_socket.accept()
        print("remote AUDIO client success connected...")
        data = "".encode("utf-8")
        payloadSize = struct.calcsize("L")
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  output=True,
                                  frames_per_buffer = CHUNK
                                  )
        while self.closeThreadFlag == 0:
            while len(data) < payloadSize:
                data += connect.recv(81920)
            recvSize = data[:payloadSize]
            data = data[payloadSize:]
            unpackedDataSize = struct.unpack("L", recvSize)[0]
            while len(data) < unpackedDataSize:
                data += connect.recv(81920)
            frameData = data[:unpackedDataSize]
            data = data[unpackedDataSize:]
            frames = pickle.loads(frameData)
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
            # 想服务器要对方的ip, 端口，并联接
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
        self.stream = self.p.open(format=FORMAT,
                             channels=CHANNELS,
                             rate=RATE,
                             input=True,
                             frames_per_buffer=CHUNK)
        while self.closeThreadFlag == 0 and self.stream.is_active() :
            frames = []
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = self.stream.read(CHUNK)
                frames.append(data)
            senddata = pickle.dumps(frames)
            try:
                self.audio_server_tcp_socket.sendall(struct.pack("L", len(senddata)) + senddata)
            except:
                break

