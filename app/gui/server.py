from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QStandardItem, QStandardItemModel


class UiMainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(625, 400)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 20, 601, 351))
        self.tabWidget.setObjectName("tabWidget")
        self.widget = QtWidgets.QWidget()
        self.widget.setAccessibleName("")
        self.widget.setObjectName("widget")
        self.users = QtWidgets.QTableView(parent=self.widget)
        self.users.setGeometry(QtCore.QRect(0, 0, 601, 321))
        self.users.setObjectName("users")
        self.tabWidget.addTab(self.widget, "")
        self.widget1 = QtWidgets.QWidget()
        self.widget1.setObjectName("widget1")
        self.history = QtWidgets.QTableView(parent=self.widget1)
        self.history.setGeometry(QtCore.QRect(0, 0, 601, 321))
        self.history.setObjectName("history")
        self.tabWidget.addTab(self.widget1, "")
        self.widget2 = QtWidgets.QWidget()
        self.widget2.setObjectName("widget2")
        self.lineEdit = QtWidgets.QLineEdit(parent=self.widget2)
        self.lineEdit.setGeometry(QtCore.QRect(50, 50, 251, 25))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(parent=self.widget2)
        self.lineEdit_2.setGeometry(QtCore.QRect(50, 120, 251, 25))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(parent=self.widget2)
        self.lineEdit_3.setGeometry(QtCore.QRect(50, 190, 251, 25))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.label = QtWidgets.QLabel(parent=self.widget2)
        self.label.setGeometry(QtCore.QRect(50, 20, 461, 31))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(parent=self.widget2)
        self.label_2.setGeometry(QtCore.QRect(50, 90, 461, 31))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(parent=self.widget2)
        self.label_3.setGeometry(QtCore.QRect(50, 160, 461, 31))
        self.label_3.setObjectName("label_3")
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.widget2)
        self.pushButton_2.setGeometry(QtCore.QRect(380, 110, 131, 51))
        self.pushButton_2.setObjectName("pushButton_2")
        self.tabWidget.addTab(self.widget2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.widget.setWhatsThis(
            _translate(
                "MainWindow", "<html><head/><body><p>all clients</p></body></html>"
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.widget), _translate("MainWindow", "All users")
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.widget1),
            _translate("MainWindow", "Users History"),
        )
        self.label.setText(_translate("MainWindow", "database path"))
        self.label_2.setText(_translate("MainWindow", "ip address"))
        self.label_3.setText(_translate("MainWindow", "port"))
        self.pushButton_2.setText(_translate("MainWindow", "Start"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.widget2), _translate("MainWindow", "Settings")
        )

    def get_all_users(self, db):
        users = db.get_all_clients()
        table = QStandardItemModel()
        table.setHorizontalHeaderLabels(["User ID", "Username", "On-line"])
        for user in users:
            user_id, username, is_active = user.id, user.username, user.is_active
            username = QStandardItem(username)
            username.setEditable(False)
            user_id = QStandardItem(str(user_id))
            user_id.setEditable(False)
            is_active = QStandardItem(str(is_active))
            is_active.setEditable(False)
            table.appendRow([user_id, username, is_active])
        return table

    def get_all_history(self, db):
        history = db.get_all_history()
        table = QStandardItemModel()
        table.setHorizontalHeaderLabels(["User ID", "Entry date", "IP", "Port"])
        for mem in history:
            user_id, entry_date, ip_address, port = (
                mem.id,
                mem.entry_date,
                mem.ip_address,
                mem.port,
            )
            entry_date = QStandardItem(str(entry_date))
            entry_date.setEditable(False)
            user_id = QStandardItem(str(user_id))
            user_id.setEditable(False)
            port = QStandardItem(str(port))
            port.setEditable(False)
            ip_address = QStandardItem(ip_address)
            ip_address.setEditable(False)
            table.appendRow([user_id, entry_date, ip_address, port])
        return table


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UiMainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
