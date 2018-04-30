# -*- coding:utf-8 -*-
from myProtocol import *
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QMessageBox, QTableWidgetItem)
# 加载ui文件
from PyQt5.uic import loadUi
from PyQt5.QtCore import (QTimer, pyqtSignal, Qt)
from PyQt5.QtNetwork import (QUdpSocket, QHostAddress)
import fileUpDownload


class FileWindow(QtWidgets.QWidget):
    '''文件窗口'''
    upload = pyqtSignal(str)
    download = pyqtSignal(str)
    def __init__(self):
        super(FileWindow, self).__init__()
        # 加载ui文件
        loadUi('filepage.ui', self)
        # 关闭页面 就销毁对象
        self.setAttribute(Qt.WA_DeleteOnClose)
        # 定义显示在TableWidget中的空对象
        self.newItem0 = None
        self.newItem1 = None

        # 创建定时器对象
        self.timer = QTimer()
        # 创建udp客户端socket
        self.udp_client_socket = QUdpSocket()
        # 上传路径+文件名
        self.file_path_name = ''
        # 下载文件名
        self.file_name = ''

        # 收到服务器消息链接到 receive_message槽函数
        self.udp_client_socket.readyRead.connect(self.receiveMessage)
        # 上传文件按钮点击信号，连接到槽函数
        self.up_btn.clicked.connect(self.pressUpLoadBtn)
        # 下载文件按钮点击信号，连接到槽函数
        self.down_btn.clicked.connect(self.pressDownloadBtn)
        # 定时器超时信号，连接到槽函数
        self.timer.timeout.connect(self.timeout)
        # 初始化TableWidget
        self.initTableWidget()
        # 启动定时器
        self.timer.start(2000)

    def initTableWidget(self):
        '''初始化对象时 设置表格参数'''
        header = ["fileName", "fileSize"]
        # 设置两列
        self.tableWidget.setColumnCount(2)
        # 设置列名
        self.tableWidget.setHorizontalHeaderLabels(header)
        # 向服务器发送数据（要求服务器传回所有文件名）
        self.udp_client_socket.writeDatagram(str(FILE_STATUS_UPDATE).encode('utf-8'), QHostAddress(FILE_SERVER_IP),FILE_SERVER_PORT_2)


    def timeout(self):
        '''定时器超时，槽函数，定期给服务器发送消息，获取服务器上所有的文件'''
        self.udp_client_socket.writeDatagram(str(FILE_STATUS_UPDATE).encode('utf-8'), QHostAddress(FILE_SERVER_IP),FILE_SERVER_PORT_2)

    def loadData(self,file_names):
        '''加载数据，显示出所有的文件名'''
        # 行归0
        self.tableWidget.setRowCount(0)
        self.tableWidget.clearContents()
        for file_name in file_names:
            # 创建QTableWidgetItem对象，显示到表中
            self.newItem0 = QTableWidgetItem(file_name)
            # 当前行数
            row_count = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_count)
            self.tableWidget.setItem(row_count, 0, self.newItem0)

    def receiveMessage(self):
        '''接受服务器发来的数据，将所有的文件名显示出来'''
        rcv_data, chat_server_ip, chat_server_port = self.udp_client_socket.readDatagram(BUFFER_SIZE)
        self.loadData(eval(rcv_data.decode('utf-8')))

    def pressUpLoadBtn(self):
        '''上传文件按钮槽函数，输入文件路径，发送文件到服务器'''
        # 获取输入框中的文件路径
        self.file_path_name = self.up_lineEdit.text()
        # 上传文件
        fileclient = fileUpDownload.fileClient((FILE_SERVER_IP, FILE_SERVER_PORT))
        fileclient.sendFile(self.file_path_name, 'file')

    def pressDownloadBtn(self):
        '''下载文件按钮槽函数，从服务器下载文件到本地file文件夹'''
        # 获取输入框中文件名
        self.file_name = self.down_lineEdit.text()
        # 下载文件
        file_path = 'file/' + self.file_name
        fileclient = fileUpDownload.fileClient((FILE_SERVER_IP, FILE_SERVER_PORT))
        fileclient.recvFile('file', file_path)

