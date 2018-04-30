from socket import *
import threading
import pyaudio
import time
import sys
from myProtocol import *

CHUNK = 1024
# 取样值的量化格式
FORMAT = pyaudio.paInt16
# 声道数
CHANNELS = 2
# 取样频率
RATE = 44100

RECORD_SECONDS = 0.5

class AudioClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.my_count = None
        self.data = ChatStruct()
        self.destnation_addr = None
        self.my_udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.voice = pyaudio.PyAudio()
        self.stream = None

    def __del__(self) :
        self.my_udp_socket.close()
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        # pyaudio 资源
        self.voice.terminate()
        print("thread over client")

    def setIpPortName(self, destnation_ip, destnation_port,my_count):
        self.destnation_addr = (destnation_ip,destnation_port)
        print(self.destnation_addr)
        self.my_count = my_count


    def run(self):
        print("AUDIO client starts...")
        self.stream = self.voice.open(format=FORMAT,
                             channels=CHANNELS,
                             rate=RATE,
                             input=True,
                             frames_per_buffer=CHUNK)

        self.data.set_my_count(self.my_count)
        self.data.set_friend_count("")
        self.data.set_message("")
        self.data.set_chat_status(CHAT_STATUS_UPDATE_VOICE_CLIENT_PORT)
        self.my_udp_socket.sendto(self.data.chat_struct_pack(), (CHAT_SERVER_IP, CHAT_SERVER_PORT))

        while self.stream.is_active():
            # self.my_udp_socket.sendto(self.stream.read(CHUNK), (DEFAULT_SERVER_IP,4000))
#            try:
            self.my_udp_socket.sendto(self.stream.read(CHUNK), self.destnation_addr)
#            except:
#                print("find error fuck... ")
 #               break
        print('run voice_client game over')


if __name__ == '__main__':
    aclient = AudioClient()
    aclient.start()
    while True:
        time.sleep(1)
        if not aclient.isAlive():
            print("aclient game over...")
            sys.exit(0)