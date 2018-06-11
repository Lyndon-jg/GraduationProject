# -*- coding:utf-8 -*-

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QMessageBox, QTableWidgetItem)
import sys
# 加载ui文件
from PyQt5.uic import loadUi
from PyQt5.QtCore import (QTimer, QDateTime)
import pymysql


class HouTaiWindow(QtWidgets.QWidget):
    def __init__(self):
        super(HouTaiWindow, self).__init__()
        self.openDB = True
        try:
            # 打开数据库
            self.db_connect = pymysql.connect(host="localhost", user="root", passwd="ljgubuntu", db="graduationPorject",
                                         charset='utf8')
            self.connect_cursor = self.db_connect.cursor()
            print("connect db ok")
        except:
            print('open db file')
            self.openDB = False

        self.timer = QTimer()
        self.newItem0 = None
        self.newItem1 = None
        self.newItem2 = None
        self.newItem3 = None
        self.newItem4 = None
        # 加载ui文件
        loadUi('backStage.ui', self)
        self.init_tableWidget()

        # 定时器初始化每一秒产生一个信号
        self.timer.start(1000)
        self.timer.timeout.connect(self.timeout)
        #按钮定时器
        self.add_Btn.clicked.connect(self.addBtnClicked)
        self.del_Btn.clicked.connect(self.delBtnClicked)

    def __del__(self):
        self.connect_cursor.close()
        self.db_connect.close()
        print("close db ok")


    def init_tableWidget(self):
        '''初始化对象时 设置表格参数'''
        header = ["count", "passwd", "status", "ip", "port"]
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(header)
        self.loadData()

    def loadData(self):
        '''加载数据'''
        if self.openDB == False:
            QMessageBox.warning(self, ("Warning"), ("连接数据库失败"), QMessageBox.Yes)
        else:
            # 行归0
            self.tableWidget.setRowCount(0)
            self.tableWidget.clearContents()
            #  取出所有的数据
            sql = "SELECT * FROM userTable"
            self.connect_cursor.execute(sql)
            result = self.connect_cursor.fetchall()
            # print(result)
            # 在线 非在线人数计数
            all_count_num = 0
            online_count_num = 0
            for row in result:
                all_count_num += 1
                if row[2] == 1:
                    online_count_num += 1
                # 创建QTableWidgetItem对象，显示到表中
                self.newItem0 = QTableWidgetItem(row[0])
                self.newItem1 = QTableWidgetItem(row[1])
                self.newItem2 = QTableWidgetItem(str(row[2]))
                self.newItem3 = QTableWidgetItem(row[3])
                self.newItem4 = QTableWidgetItem(str(row[4]))
                # 当前行数
                row_count = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row_count)
                self.tableWidget.setItem(row_count, 0, self.newItem0)
                self.tableWidget.setItem(row_count, 1, self.newItem1)
                self.tableWidget.setItem(row_count, 2, self.newItem2)
                self.tableWidget.setItem(row_count, 3, self.newItem3)
                self.tableWidget.setItem(row_count, 4, self.newItem4)


            self.all_num_label.setText('总人数: %d'%all_count_num)
            self.online_label.setText('在线: %d'%online_count_num)


    def addBtnClicked(self):
        '''添加帐号按钮槽函数'''
        # 若edit内容非空
        if self.count_lineEdit.text() != '' and self.passwd_lineEdit.text() != '':
            # 查找count是否已经被注册
            sql = "SELECT count FROM userTable WHERE count='%s'"%(self.count_lineEdit.text())
            self.connect_cursor.execute(sql)
            result = self.connect_cursor.fetchall()
            # 如果没有被注册
            if len(result) == 0:
                # 插入帐号
                sql = "INSERT INTO userTable VALUES('%s','%s',0,'0',0,'0','0','0','0')"%(self.count_lineEdit.text(),self.passwd_lineEdit.text())
                self.connect_cursor.execute(sql)
                self.db_connect.commit()
                QMessageBox.warning(self, ("Warning"), ("帐号已插入"), QMessageBox.Yes)
                # 清空内容
                self.count_lineEdit.clear()
                self.passwd_lineEdit.clear()
                # 更新表
                self.loadData()
            # 如果已被注册
            elif len(result) == 1:
                QMessageBox.warning(self, ("Warning"), ("帐号已经被注册，不可插入"), QMessageBox.Yes)
        else:
            QMessageBox.warning(self, ("Warning"), ("帐号或密码不能为空"), QMessageBox.Yes)

    def delBtnClicked(self):
        '''删除帐号按钮槽函数'''
        if self.count_lineEdit_2.text() != '':
            print("connect db ok")
            # 查找count是否已经被注册
            sql = "SELECT count FROM userTable WHERE count='%s'" % (self.count_lineEdit_2.text())
            self.connect_cursor.execute(sql)
            result = self.connect_cursor.fetchall()
            # 如果没有被注册
            if len(result) == 0:
                QMessageBox.warning(self, ("Warning"), ("无此帐号"), QMessageBox.Yes)
            # 如果已被注册
            elif len(result) == 1:
                # 删除帐号
                sql = "DELETE FROM  userTable WHERE count='%s'"%(self.count_lineEdit_2.text())
                self.connect_cursor.execute(sql)
                self.db_connect.commit()
                QMessageBox.warning(self, ("Warning"), ("帐号删除成功"), QMessageBox.Yes)
                # 清空内容
                self.count_lineEdit_2.clear()
                # 更新表
                self.loadData()
        else:
            QMessageBox.warning(self, ("Warning"), ("帐号不能为空"), QMessageBox.Yes)

    def timeout(self):
        # 更新表
        self.loadData()
        # 获取当前系统时间
        time = QDateTime.currentDateTime()
        # 时间显示格式
        time_str = time.toString("yyyy-MM-dd hh:mm:ss")
        self.lcdNumber.display(time_str)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = HouTaiWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()