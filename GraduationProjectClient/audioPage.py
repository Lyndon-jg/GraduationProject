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

    # 点击x按钮
    def closeEvent(self, QCloseEvent):
        self.pressCloseBtn()

    # 点击接受按钮
    def pressAcceptBtn(self):
        # 发消息给服务器我接受对方的请求
        self.audio_data.set_my_count(self.my_count)
        self.audio_data.set_friend_count(self.friend_count)
        self.audio_data.set_audio_status(AUDIO_STATUS_ACCEPT)
        self.audio_socket.writeDatagram(self.audio_data.audio_struct_pack(), QHostAddress(AUDIO_SERVER_IP),AUDIO_SERVER_PORT)
        # 发送信号给线程
        self.set_count_server.emit(self.my_count, self.friend_count)
        # 设置界面显示xxx
        self.label.setText('正在和%s通话'%self.friend_count)
        # 隐藏接受 拒绝按钮  显示 关闭按钮
        self.recvBtn.hide()
        self.rejectBtn.hide()
        self.closeBtn.show()
        # 接收语音线程开始
        self.audio_server.start()

    # 点击拒绝按钮
    def pressRejectBtn(self):
        # 发消息给服务器我拒绝对方的请求
        self.audio_data.set_my_count(self.my_count)
        self.audio_data.set_friend_count(self.friend_count)
        self.audio_data.set_audio_status(AUDIO_STATUS_REJECT)
        self.audio_socket.writeDatagram(self.audio_data.audio_struct_pack(), QHostAddress(AUDIO_SERVER_IP),AUDIO_SERVER_PORT)
        # 关闭本界面
        self.close()

    # 点击关闭按钮
    def pressCloseBtn(self):
        # 若线程打开，关闭线程
        self.audio_client.closeAudioClient()
        self.audio_server.closeAudioServer()
        # 发消息给服务器我已经断开语音连接
        self.audio_data.set_my_count(self.my_count)
        self.audio_data.set_friend_count(self.friend_count)
        self.audio_data.set_audio_status(AUDIO_STATU_CLOSE)
        self.audio_socket.writeDatagram(self.audio_data.audio_struct_pack(), QHostAddress(AUDIO_SERVER_IP),AUDIO_SERVER_PORT)
        # 关闭本界面
        self.close()
    # 取消请求
    def cancleRequest(self):
        '''请求方如果取消语音请求则本地只能显示关闭按钮'''
        self.label.setText('对方以关闭语音通信连接')
        # 隐藏接受 拒绝按钮  显示 关闭按钮
        self.recvBtn.hide()
        self.rejectBtn.hide()
        self.closeBtn.show()

    # 接收服务器发来的消息
    def receiveMessage(self):
        '''接收服务器转发回来的消息'''
        rcv_data, audio_server_ip, audio_server_port = self.audio_socket.readDatagram(BUFFER_SIZE)
        self.audio_data.set_rcv_data(rcv_data)
        # 判断接收到的消息的类型
        if self.audio_data.get_audio_status() == AUDIO_STATUS_ACCEPT:
            print('recv accept')
            # 发送信号给线程
            self.set_count_client.emit(self.my_count, self.friend_count)
            self.label.setText('正在和%s通话' % self.friend_count)
            # 发送语音线程开始
            self.audio_client.start()
        elif self.audio_data.get_audio_status() == AUDIO_STATUS_REJECT:
            print('recv reject111')
            self.label.setText('对方拒绝了你的请求')
        elif self.audio_data.get_audio_status() == AUDIO_STATU_CLOSE:
            print('recv close')
            self.cancleRequest()

    # 有人发来请求，槽函数
    def recvAudioText(self,my_count, friend_count):
        self.my_count = my_count
        self.friend_count = friend_count
        self.recvBtn.show()
        self.rejectBtn.show()
        self.closeBtn.hide()
        self.label.setText("%s发来语音请求"%friend_count)
    # 点击语音请求按钮,槽函数
    def clickAudioText(self, text, my_count, friend_count):
        self.my_count = my_count
        self.friend_count = friend_count
        self.recvBtn.hide()
        self.rejectBtn.hide()
        self.closeBtn.show()
        self.label.setText(text)
    # 更新port
    def updateAudioPort(self):
        '''更新我的端口和ip'''
        self.audio_data.set_my_count(self.my_count)
        self.audio_data.set_audio_status(AUDIO_STATUS_UPDATE)
        self.audio_socket.writeDatagram(self.audio_data.audio_struct_pack(), QHostAddress(AUDIO_SERVER_IP), AUDIO_SERVER_PORT)


