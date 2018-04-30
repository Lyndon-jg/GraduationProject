
from socket import *
import threading
from myProtocol import *
import sys
import time
import pyaudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 0.5


class AudioServer(threading.Thread):
    def __init__(self) :
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.my_udp_socket = socket(AF_INET ,SOCK_DGRAM)
        self.data = ChatStruct()
        self.voice = pyaudio.PyAudio()
        self.my_count = None
        self.stream = None

        # self.ADDR = ('',4000)

    def __del__(self):
        self.my_udp_socket.close()
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.voice.terminate()
        print("thread over server")

    def setCount(self,my_count):
        self.my_count = my_count

    def run(self):
        print("AUDIO server starts...")
        # self.my_udp_socket.bind(self.ADDR)
        self.stream = self.voice.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  output=True,
                                  frames_per_buffer = CHUNK
                                  )

        self.data.set_my_count(self.my_count)
        self.data.set_friend_count("")
        self.data.set_message("")
        self.data.set_chat_status(CHAT_STATUS_UPDATE_VOICE_SERVER_PORT)
        self.my_udp_socket.sendto(self.data.chat_struct_pack(),(CHAT_SERVER_IP,CHAT_SERVER_PORT))

        while True:
            audio_data, addr = self.my_udp_socket.recvfrom(1024)
            self.stream.write(audio_data, CHUNK)

        print('run voice_server game over')



if __name__ == '__main__':
    aserver = AudioServer()
    aserver.start()
    while True:
        time.sleep(1)
        if not aserver.isAlive():
            print("aserver game over...")
            sys.exit(0)