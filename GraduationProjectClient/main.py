import sys
from PyQt5 import QtWidgets
from loginPage import LoginWindow

# 主函数
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = LoginWindow()
    w.show()
    sys.exit(app.exec_())