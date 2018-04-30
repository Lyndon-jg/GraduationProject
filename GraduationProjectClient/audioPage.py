from PyQt5.QtWidgets import (QMessageBox,QWidget)
from PyQt5.QtNetwork import (QUdpSocket, QHostAddress)
from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import loadUi
from audioChat import AudioServer, AudioClient
from myProtocol import *

class AudioWindow(QWidget):
    set_count_server = pyqtSignal(str,str)
    set_count_client = pyqtSignal(str, str)
    def __init__(self):
        super(AudioWindow, self).__init__()
        # 加载ui文件
        loadUi('audioPage.ui', self)

        self.my_count = ''
        self.friend_count = ''

        # 创建socket对象
        self.audio_socket = QUdpSocket()
        # 收到服务器消息链接到 receive_message槽函数
        self.audio_socket.readyRead.connect(self.receiveMessage)

        # 创建audio_data对象
        self.audio_data = AudioStruct()

        # 创建两个线程对象
        self.audio_client = AudioClient()
        self.audio_server = AudioServer()

        # 接受语音消息
        self.recvBtn.clicked.connect(self.pressAcceptBtn)
        # 拒绝语音消息
        self.rejectBtn.clicked.connect(self.pressRejectBtn)
        # 关闭
        self.closeBtn.clicked.connect(self.pressCloseBtn)

        self.set_count_server.connect(self.audio_server.setCount)
        self.set_count_client.connect(self.audio_client.setCount)

    def pressAcceptBtn(self):
        self.audio_data.set_my_count(self.my_count)
        self.audio_data.set_friend_count(self.friend_count)
        self.audio_data.set_audio_status(AUDIO_STATUS_ACCEPT)
        self.audio_socket.writeDatagram(self.audio_data.audio_struct_pack(), QHostAddress(AUDIO_SERVER_IP),AUDIO_SERVER_PORT)
        self.set_count_server.emit(self.my_count, self.friend_count)
        self.label.setText('正在和%s通话'%self.friend_count)
        self.recvBtn.hide()
        self.rejectBtn.hide()
        self.closeBtn.show()
        self.audio_server.start()

    def pressRejectBtn(self):
        self.audio_data.set_my_count(self.my_count)
        self.audio_data.set_friend_count(self.friend_count)
        self.audio_data.set_audio_status(AUDIO_STATUS_REJECT)
        self.audio_socket.writeDatagram(self.audio_data.audio_struct_pack(), QHostAddress(AUDIO_SERVER_IP),AUDIO_SERVER_PORT)
        self.close()

    def pressCloseBtn(self):
        self.audio_client.closeAudioClient()
        self.audio_server.closeAudioServer()
        self.close()
        '''gao su dui fang yi gua duan 还没有实现'''

    def receiveMessage(self):
        '''接收服务器转发回来的消息'''
        rcv_data, audio_server_ip, audio_server_port = self.audio_socket.readDatagram(BUFFER_SIZE)
        self.audio_data.set_rcv_data(rcv_data)
        # 判断接收到的消息的类型
        if self.audio_data.get_audio_status() == AUDIO_STATUS_ACCEPT:
            print('recv accept')
            self.set_count_client.emit(self.my_count, self.friend_count)
            self.label.setText('正在和%s通话' % self.friend_count)
            self.audio_client.start()
        elif self.audio_data.get_audio_status() == AUDIO_STATUS_REJECT:
            print('recv reject')
            self.label.setText('对方拒绝了你的请求')


    def setFirstText(self,my_count, friend_count):
        self.my_count = my_count
        self.friend_count = friend_count
        self.recvBtn.show()
        self.rejectBtn.show()
        self.closeBtn.hide()
        self.label.setText("%s发来语音请求"%friend_count)

    def setSecondText(self, text, my_count, friend_count):
        self.my_count = my_count
        self.friend_count = friend_count
        self.recvBtn.hide()
        self.rejectBtn.hide()
        self.closeBtn.show()
        self.label.setText(text)

    def updateAudioPort(self):
        '''更新我的端口和ip'''
        self.audio_data.set_my_count(self.my_count)
        self.audio_data.set_audio_status(AUDIO_STATUS_UPDATE)
        self.audio_socket.writeDatagram(self.audio_data.audio_struct_pack(), QHostAddress(AUDIO_SERVER_IP), AUDIO_SERVER_PORT)


