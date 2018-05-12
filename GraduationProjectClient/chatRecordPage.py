# -*- coding:utf-8 -*-
from myProtocol import *
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QMessageBox, QTableWidgetItem)
# 加载ui文件
from PyQt5.uic import loadUi
from PyQt5.QtCore import (QTimer, pyqtSignal, Qt)
from PyQt5.QtNetwork import (QUdpSocket, QHostAddress)

class ChatRecordWindow(QtWidgets.QWidget):
    def __init__(self, my_count, friend_count):
        super(ChatRecordWindow, self).__init__()
        # 加载界面文件
        loadUi('chatrecordpage.ui', self)
        # 设置只读
        self.textEdit.setReadOnly(True)
        # 设置属性，关闭页面 就销毁对象
        self.setAttribute(Qt.WA_DeleteOnClose)

        # # 创建udp客户端socket
        self.udp_client_socket = QUdpSocket()
        # 收发数据对象
        self.data = ChatStruct()
        # 接受聊天界面的两个用户名
        self.my_count = my_count
        self.friend_count = friend_count

        self.udp_client_socket.readyRead.connect(self.receiveMessage)
        # 更新端口
        self.updatePort()
        # 获取聊天记录
        self.giveMyChatRecord()

    def receiveMessage(self):
        '''接收服务器发来的聊天记录'''
        rcv_data, chat_server_ip, chat_server_port = self.udp_client_socket.readDatagram(BUFFER_SIZE)
        self.data.set_rcv_data(rcv_data)
        # 将消息显示到Edit中
        # if self.data.get_message() != 'xxx':
        self.textEdit.append(self.data.get_time() + "     " + self.data.get_my_count() + ":")
        self.textEdit.append(self.data.get_message())
        # else:
            # self.textEdit.append('无消息')

    def updatePort(self):
        '''告知服务器，更新我的聊天记录界面端口'''
        self.data.set_my_count(self.my_count)
        self.data.set_chat_status(CHAT_STATUS_UPDATE_RECORD_PAGE)
        self.udp_client_socket.writeDatagram(self.data.chat_struct_pack(), QHostAddress(CHAT_SERVER_IP), CHAT_SERVER_PORT)

    def giveMyChatRecord(self):
        '''告知服务器，返回我的聊天记录'''
        self.data.set_my_count(self.my_count)
        self.data.set_friend_count(self.friend_count)
        self.data.set_chat_status(CHAT_STATUS_CHAT_RECORE)
        self.udp_client_socket.writeDatagram(self.data.chat_struct_pack(), QHostAddress(CHAT_SERVER_IP),CHAT_SERVER_PORT)

