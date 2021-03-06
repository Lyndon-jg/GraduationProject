# -*- coding:utf-8 -*-
from myProtocol import *
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QMessageBox, QTableWidgetItem)
# 加载ui文件
from PyQt5.uic import loadUi
from PyQt5.QtCore import (QTimer, pyqtSignal, Qt)
from PyQt5.QtNetwork import (QUdpSocket, QHostAddress)
# 正则，匹配文件路径
import re
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
        header = ["fileName"]
        # 设置1列
        self.tableWidget.setColumnCount(1)
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
        # 现将文件列表字符串解码，在转换成字符串
        self.loadData(eval(rcv_data.decode('utf-8')))

    def pressUpLoadBtn(self):
        '''上传文件按钮槽函数，输入文件路径，发送文件到服务器'''
        # 获取输入框中的文件路径
        # 先获取文本
        self.file_path_name = self.up_lineEdit.text()
        # 如果是拖动文件，则对文件路径进行处理
        if self.file_path_name[:4] == 'file':
            # 将%20 替换为 空格
            self.file_path_name = self.file_path_name.replace('%20', ' ')
            self.file_path_name = self.file_path_name[7:-2]
        # 上传文件
        fileclient = fileUpDownload.fileClient()
        ret = fileclient.sendFile(self.file_path_name)
        if ret == 'fileNotExist':
            QMessageBox.warning(self, ("Warning"), ("文件不存在"), QMessageBox.Yes)
        elif ret == 'upLoadFaile':
            QMessageBox.warning(self, ("Warning"), ("上传失败"), QMessageBox.Yes)
        elif ret == 'upLoadSuccess':
            QMessageBox.warning(self, ("Warning"), ("上传成功"), QMessageBox.Yes)

    def pressDownloadBtn(self):
        '''下载文件按钮槽函数，从服务器下载文件到本地file文件夹'''
        # 获取输入框中文件名
        self.file_name = self.down_lineEdit.text()
        fileclient = fileUpDownload.fileClient()
        ret = fileclient.recvFile(self.file_name)
        if ret == 'downLoadSuccess':
            QMessageBox.warning(self, ("Warning"), ("下载成功"), QMessageBox.Yes)
        elif ret == 'downLoadFaile':
            QMessageBox.warning(self, ("Warning"), ("下载失败"), QMessageBox.Yes)

    def closeEvent(self, QCloseEvent):
        '''点击x号,关闭自己界面'''
        # 关闭自己界面
        self.close()
