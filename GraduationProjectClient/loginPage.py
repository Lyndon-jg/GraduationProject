from PyQt5.QtWidgets import (QMessageBox, QLineEdit)
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
# 加载ui文件
from PyQt5.uic import loadUi
from PyQt5.QtNetwork import (QUdpSocket, QHostAddress)
from PyQt5.QtCore import Qt
from myProtocol import *
import chatPage, backStage, registerPage
import sys

class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super(LoginWindow, self).__init__()

        # 加载ui文件
        loadUi('loginPage.ui', self)

        # 关闭页面 就销毁对象
        self.setAttribute(Qt.WA_DeleteOnClose)
        # 创建udp客户端socket
        self.udp_client_socket = QUdpSocket()
        # 收发数据对象
        self.data = LoginStruct()
        # 注册界面空对象
        self.register_window = None
        # 聊天界面空对象
        self.chat_window = None

        # 设置背景图片
        background = QPixmap("img/login_background.jpeg")
        background = background.scaled(self.background_label.width(),self.background_label.width())
        self.background_label.setPixmap(background)
        # 设置输入密码框
        self.passwd_lineEdit.setEchoMode(QLineEdit.Password)

        # 登录按钮接到press_login_btn槽函数
        self.login_Btn.clicked.connect(self.pressLoginBtn)
        # 注册按钮接到press_rgs_btn槽函数
        self.rgs_Btn.clicked.connect(self.pressRgsBtn)
        # 收到服务器消息链接到 receive_message槽函数
        self.udp_client_socket.readyRead.connect(self.receiveMessage)


    def pressLoginBtn(self):
        '''登录按钮槽函数,将账户 密码 状态(在这里设置为0：用户，1：管理员) 发送到服务器'''
        # 判断是否获取信息成功
        if self.count_lineEdit.text() == "" or self.passwd_lineEdit.text() == "":
            QMessageBox.warning(self, ("Warning"), ("未输入帐号或密码，请重新输入"), QMessageBox.Yes)
        else:
            # 获取帐号密码帐号
            self.data.set_count(self.count_lineEdit.text())
            self.data.set_passwd(self.passwd_lineEdit.text())
            #用户登录
            if self.userRadioButton.isChecked():
                self.data.set_status(0)
                self.udp_client_socket.writeDatagram(self.data.login_struct_pack(), QHostAddress(LOGIN_SERVER_IP), LOGIN_SERVER_PORT)
                print("login_client send message ok")
            # 管理员登录
            elif self.managerRadioButton.isChecked():
                self.data.set_status(1)
                self.udp_client_socket.writeDatagram(self.data.login_struct_pack(), QHostAddress(LOGIN_SERVER_IP), LOGIN_SERVER_PORT)
                print("login_client send message ok")

    def pressRgsBtn(self):
        '''注册按钮槽函数'''
        # 创建注册界面对象
        self.register_window = registerPage.RgsWindow()
        # 关闭（销毁）本界面
        self.close()
        # 显示注册界面
        self.register_window.show()
        self.register_window.exec_()


    def receiveMessage(self):
        '''收到信息槽函数'''
        # 接受服务器发过来的消息和服务器地址
        rcv_data, login_server_ip, login_server_port = self.udp_client_socket.readDatagram(BUFFER_SIZE)
        self.data.set_rcv_data(rcv_data)
        # 判断是否可以登录
        if self.data.get_status() == LOGIN_STATUS_OK and self.userRadioButton.isChecked():
            self.close()
            self.chat_window = chatPage.ChatWindow(self.count_lineEdit.text())
            self.chat_window.show()
            self.chat_window._exec()
        elif self.data.get_status() == LOGIN_STATUS_OK and self.managerRadioButton.isChecked():
            self.close()
            backStage.houTaiPage()
        elif self.data.get_status() == LOGIN_STATUS_FAIL:
            QMessageBox.information(self, ("information"), ("""帐号或密码错误"""), QMessageBox.Yes)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
