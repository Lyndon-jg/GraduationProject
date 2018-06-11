from PyQt5 import QtWidgets
from PyQt5.QtGui import (QPixmap, QBrush, QColor)
from PyQt5.QtCore import (QTimer, QDateTime, pyqtSignal, Qt)
from PyQt5.QtWidgets import (QMessageBox, QTreeWidgetItem)
# 加载ui文件 
from PyQt5.uic import loadUi
from PyQt5.QtNetwork import (QUdpSocket, QHostAddress)
from myProtocol import *
import audioPage
import filePage, chatRecordPage


class ChatWindow(QtWidgets.QWidget):
    # 接收到语音请求信号
    receive_audio_signal = pyqtSignal(str, str)
    # 点击语音按钮信号
    click_audio_btn_signal = pyqtSignal(str, str, str)

    def __init__(self, my_count):
        super(ChatWindow, self).__init__()
        # 关闭页面 就销毁对象
        self.setAttribute(Qt.WA_DeleteOnClose)
        # 加载界面文件
        loadUi("chatPage.ui", self)
        self.my_count = my_count
        self.myname_label.setText(self.my_count)
        # 定时器对象
        self.timer = QTimer()
        # 创建udp客户端socket
        self.udp_client_socket = QUdpSocket()
        # 收发数据对象
        self.data = ChatStruct()
        # 用户列表
        self.user_list = []

        # 聊天记录界面空对象
        self.chat_record_page = None
        # 文件传输界面空对象
        self.file_window = None

        # 设置背景图片
        background = QPixmap("img/chat_background.jpg")
        background = background.scaled(self.back_label.width(), self.back_label.width())
        self.back_label.setPixmap(background)

        # 设置只读
        self.show_msg_textEdit.setReadOnly(True)

        # 定时器初始化
        self.timer.start(1000)
        # 定时器超时信号，连接到槽函数
        self.timer.timeout.connect(self.timeout)

        # 双击好友treeWidget
        self.friends_treeWidget.doubleClicked.connect(self.on_treeWidget_doubleClicked)
        # 发送消息按钮，连接到槽函数
        self.send_Btn.clicked.connect(self.pressSendBtn)
        # 查看聊天记录按钮，连接到槽函数
        self.msg_log_Btn.clicked.connect(self.pressMsgBtn)
        # 文件按钮信号，连接到槽函数
        self.file_up_Btn.clicked.connect(self.pressFileBtn)
        # 收到服务器消息链接到 receiveMessage槽函数
        self.udp_client_socket.readyRead.connect(self.receiveMessage)

        # 语音界面
        self.audio_window = None
        # 语音消息按钮
        self.audio_Btn.clicked.connect(self.pressAudioBtn)

        # 更新ip 和 端口
        self.update_ip_port()
        # 获取好友列表
        self.updateUserList()

    def closeEvent(self, QCloseEvent):
        '''关闭按钮'''
        # 设置消息内容
        self.data.set_my_count(self.myname_label.text())
        self.data.set_chat_status(CHAT_STATUS_EXIT)
        # 告诉服务器，更新此人登录状态为0
        self.udp_client_socket.writeDatagram(self.data.chat_struct_pack(), QHostAddress(CHAT_SERVER_IP),
                                             CHAT_SERVER_PORT)


    def timeout(self):
        '''定时器超时槽函数'''
        # 获取当前系统时间
        time = QDateTime.currentDateTime()
        # 时间显示格式
        time_str = time.toString("yyyy-MM-dd hh:mm:ss")
        # 更新时间
        self.lcdNumber.display(time_str)
        # 更新用户列表
        self.updateUserList()

    def pressAudioBtn(self):
        '''语音按钮,自己显示一个语音界面，并通知对方有语音连接消息到达'''
        print("press_audio_btn")
        # 判断是否已经选择好友
        if self.friendname_label.text() == "":
            QMessageBox.warning(self, ("Waring"), ("请选择相应的好友"), QMessageBox.Yes)
            return
        # 语音界面
        self.audio_window = audioPage.AudioWindow()
        # 将两个信号 绑定槽函数
        self.receive_audio_signal.connect(self.audio_window.recvAudioText)
        self.click_audio_btn_signal.connect(self.audio_window.clickAudioText)
        # 将语音请求消息发送给服务器
        self.data.set_my_count(self.myname_label.text())
        self.data.set_friend_count(self.friendname_label.text())
        self.data.set_chat_status(CHAT_STATUS_AUDIO_REQUEST)
        self.udp_client_socket.writeDatagram(self.data.chat_struct_pack(), QHostAddress(CHAT_SERVER_IP),
                                             CHAT_SERVER_PORT)
        # 发送 点击语音按钮 信号
        self.click_audio_btn_signal.emit("等待对方接听...", self.myname_label.text(), self.friendname_label.text())
        # 显示语音界面
        self.audio_window.show()
        # 更新语音界面端口
        self.audio_window.updateAudioPort()
#        self.audio_window.exec_()


    def pressFileBtn(self):
        '''文件按钮槽函数'''
        # 创建文件界面对象
        self.file_window = filePage.FileWindow()
        # 显示文件界面
        self.file_window.show()
#        self.file_window.exec_()


    def pressSendBtn(self):
        '''发送消息按钮槽函数，将消息发送出去'''
        # 判断是否已经选择好友
        if self.friendname_label.text() == "":
            QMessageBox.warning(self, ("Waring"), ("请选择相应的好友"), QMessageBox.Yes)
            return
        # 获取输入内容，并判断是否为空
        message = self.chat_textEdit.toPlainText()
        if message == "":
            QMessageBox.warning(self, ("Waring"), ("发送内容不能为空"), QMessageBox.Yes)
            return
        # 获取当前系统时间
        time = QDateTime.currentDateTime()
        # 时间显示格式
        time_str = time.toString("yyyy-MM-dd hh:mm:ss")
        # 将消息显示到聊天Edit中
        self.show_msg_textEdit.append(time_str + "    " + self.myname_label.text() + ":")
        self.show_msg_textEdit.append(message)
        self.chat_textEdit.clear()
        # 将消息发送给服务器
        self.data.set_my_count(self.myname_label.text())
        self.data.set_friend_count(self.friendname_label.text())
        self.data.set_time(time_str)
        self.data.set_message(message)
        self.data.set_chat_status(CHAT_STATUS_MSG)
        self.udp_client_socket.writeDatagram(self.data.chat_struct_pack(), QHostAddress(CHAT_SERVER_IP), CHAT_SERVER_PORT)

    def pressMsgBtn(self):
        '''聊天记录按钮槽函数，点击消息记录按钮，显示和好友的聊天记录'''
        # 判断是否已经选择好友
        if self.friendname_label.text() == "":
            QMessageBox.warning(self, ("Waring"), ("请选择相应的好友"), QMessageBox.Yes)
            return
        # 创建聊天记录界面对象
        self.chat_record_page = chatRecordPage.ChatRecordWindow(self.myname_label.text(), self.friendname_label.text())
        # 显示聊天记录界面
        self.chat_record_page.show()
#        self.chat_record_page._exec()


    def receiveMessage(self):
        '''接收服务器转发回来的消息，判断消息状态，进行相应的处理'''
        # print("chat_client：收到消息")
        rcv_data, chat_server_ip, chat_server_port = self.udp_client_socket.readDatagram(BUFFER_SIZE)
        self.data.set_rcv_data(rcv_data)
        # 判断接收到的消息的类型
        if self.data.get_chat_status() == CHAT_STATUS_MSG:
            print("receive_message:CHAT_STATUS_MSG")
            if self.friendname_label.text() == self.data.get_friend_count():
                # 获取当前系统时间
                time = QDateTime.currentDateTime()
                # 时间显示格式
                time_str = time.toString("yyyy-mm-dd hh:mm:ss")
                self.show_msg_textEdit.append(time_str + "    " + self.data.get_friend_count() + ":")
                self.show_msg_textEdit.append(self.data.get_message())
                # print("chat_client：好友发送的消息显示完毕")
            else:
                items = self.friends_treeWidget.findItems(self.data.get_friend_count(), Qt.MatchRecursive, 0)
                # items[0].setText(1, "消息")
                items[0].setBackground(0, QBrush(QColor("#00FF00")))
        elif self.data.get_chat_status() == CHAT_STATUS_ONEDAY_MESSAGE:
            print("receive_message:CHAT_STATUS_ONEDAY_MESSAGE")
            self.data.set_rcv_data(rcv_data)
            # 将消息显示到Edit中
            self.show_msg_textEdit.append(self.data.get_time() + "    " + self.data.get_my_count() + ":")
            self.show_msg_textEdit.append(self.data.get_message())
        elif self.data.get_chat_status() == CHAT_STATUS_LIST:
            # print("receive_message:CHAT_STATUS_LIST")
            message = self.data.get_message().split("+")
            # print(type(message))
            # print(message)
            if message[0] not in self.user_list:
                item = QTreeWidgetItem(self.friends_treeWidget)
                item.setText(0, message[0])
                if message[1] == '0':
                    item.setText(1, "离线")
                if message[1] == '1':
                    item.setText(1, "在线")
                self.user_list.append(message[0])
            else:
                items = self.friends_treeWidget.findItems(message[0], Qt.MatchRecursive, 0)
                if message[1] == '0':
                    items[0].setText(1, "离线")
                if message[1] == '1':
                    items[0].setText(1, "在线")
        # 客户端发来语音消息
        elif self.data.get_chat_status() == CHAT_STATUS_AUDIO_REQUEST:
            print("receive_message:CHAT_STATUS_VOICE_REQUEST")
            # 创建语音界面对象
            self.audio_window = audioPage.AudioWindow()
            # 两个信号绑定槽函数
            self.receive_audio_signal.connect(self.audio_window.recvAudioText)
            self.click_audio_btn_signal.connect(self.audio_window.clickAudioText)
            # 发送接收到语音请求信号
            self.receive_audio_signal.emit(self.data.get_my_count(),self.data.get_friend_count())
            # 显示语音界面
            self.audio_window.show()
            # 更新语音界面端口
            self.audio_window.updateAudioPort()
            self.audio_window.exec_()


    def on_treeWidget_doubleClicked(self):
        '''双击好友列表'''
        item = self.friends_treeWidget.currentItem()
        item.setBackground(0, QBrush(QColor("#FFFFFF")))
        self.friendname_label.setText(item.text(0))
        self.chat_textEdit.clear()
        self.show_msg_textEdit.clear()
        # 获取当前系统时间
        time = QDateTime.currentDateTime()
        # 时间显示格式
        time_str = time.toString("yyyy-MM-dd hh:mm:ss")
        # 将消息发送给服务器,让其返回今天和好友的聊天记录
        self.data.set_my_count(self.myname_label.text())
        self.data.set_friend_count(self.friendname_label.text())
        self.data.set_time(time_str)
        self.data.set_chat_status(CHAT_STATUS_ONEDAY_MESSAGE)
        self.udp_client_socket.writeDatagram(self.data.chat_struct_pack(), QHostAddress(CHAT_SERVER_IP),
                                             CHAT_SERVER_PORT)

    def updateUserList(self):
        '''更新好友列表'''
        self.data.set_my_count(self.myname_label.text())
        self.data.set_chat_status(CHAT_STATUS_LIST)
        self.udp_client_socket.writeDatagram(self.data.chat_struct_pack(), QHostAddress(CHAT_SERVER_IP), CHAT_SERVER_PORT)

    def update_ip_port(self):
        '''更新我的端口和ip'''
        self.data.set_my_count(self.myname_label.text())
        self.data.set_friend_count("")
        self.data.set_message("")
        self.data.set_chat_status(CHAT_STATUS_UPDATE_CHAT_PAGE)
        self.udp_client_socket.writeDatagram(self.data.chat_struct_pack(), QHostAddress(CHAT_SERVER_IP), CHAT_SERVER_PORT)



'''
def chatpage(count):
    chat_window = ChatWindow()
    # 设置自己账户名
    chat_window.myname_label.setText(count)
    chat_window.show()
    chat_window.update_ip_port()
    chat_window.give_my_friends()
    chat_window.exec_()
'''