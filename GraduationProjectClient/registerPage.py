from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
# 加载ui文件
from PyQt5.uic import loadUi
from PyQt5.QtNetwork import (QUdpSocket, QHostAddress)
import loginPage
import sys
from myProtocol import *

class RgsWindow(QtWidgets.QWidget):
    def __init__(self):
        super(RgsWindow, self).__init__()
        # 加载ui文件
        loadUi('registerPage.ui', self)

        # 关闭页面 就销毁对象
        self.setAttribute(Qt.WA_DeleteOnClose)

        #创建udp socket
        self.udp_client_socket = QUdpSocket()
        #收发数据对象
        self.data = RegisterStruct()

        #  登录界面空对象
        self.login_window = None

        # 确定按钮链接到 sure_btn_press槽函数
        self.sure_Btn.clicked.connect(self.pressSureBtn)
        # 取消按钮链接到 cancel_btn_press槽函数
        self.cancel_Btn.clicked.connect(self.PressCancelBtn)
        # 收到服务器消息链接到 receive_message槽函数
        self.udp_client_socket.readyRead.connect(self.receiveMessage)


    def pressSureBtn(self):
        '''确定按钮槽函数,将账户 密码 发送到服务器'''
        # 获取帐号密码帐号
        self.data.set_count(self.count_lineEdit.text())
        self.data.set_passwd(self.passwd_lineEdit.text())

        if self.data.get_count() == "" or self.data.get_passwd() == "":
            QMessageBox.warning(self, ("Warning"), ("未输入帐号或密码，请重新输入"), QMessageBox.Yes)
        else:
            self.udp_client_socket.writeDatagram(self.data.rgs_struct_pack(), QHostAddress(REGISTER_SERVER_IP), REGISTER_SERVER_PORT)



    def PressCancelBtn(self):
        '''取消按钮槽函数,关闭自己界面，显示登录界面'''
        # 创建登录界面对象
        self.login_window = loginPage.LoginWindow()
        # 关闭自己界面
        self.close()
        # 调出登录界面
        self.login_window.show()
#        self.login_window._exec()

    def closeEvent(self, QCloseEvent):
        '''点击x号,关闭自己界面，显示登录界面'''
        # 创建登录界面对象
        self.login_window = loginPage.LoginWindow()
        # 关闭自己界面
        self.close()
        # 调出登录界面
        self.login_window.show()
#        self.login_window._exec()


    def receiveMessage(self):
        '''收到信息槽函数，判断收到的信息状态，提示用户是否注册成功'''
        # 接收收到的消息和地址
        rcv_data, register_server_ip, register_server_port = self.udp_client_socket.readDatagram(BUFFER_SIZE)
        self.data.set_rcv_data(rcv_data)
        # 判断是否注册成功
        if self.data.get_status() == REGISTER_STATUS_OK:
            QMessageBox.information(self, ("information"), ("""注册成功"""), QMessageBox.Yes)
        else:
            QMessageBox.information(self, ("information"), ("""注册失败"""), QMessageBox.Yes)
        # 输入框清空
        self.count_lineEdit.clear()
        self.passwd_lineEdit.clear()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    rgs_window = RgsWindow()
    rgs_window.show()
    sys.exit(app.exec_())