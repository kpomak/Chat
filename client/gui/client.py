import sys
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QFont
from client.gui.ui_client import Ui_MainWindow


class MainClientGui(Ui_MainWindow):
    def __init__(self, db, client):
        super().__init__()
        self.db = db
        self.client = client
        self.setupUi()
        self.listView.doubleClicked.connect(self.select_chat)
        self.update_users()

    def update_users(self):
        users = self.db.get_users()
        self.users_model = QStandardItemModel()
        for user in users:
            active = "🍉" if user.is_active else "💀"
            contact = "👤" if user.is_contact else " "
            username = QStandardItem(f"{active} {user.username} {contact}")
            username.setEditable(False)
            self.users_model.appendRow(username)
        self.listView.setModel(self.users_model)

    def select_chat(self):
        self.chat = self.listView.currentIndex().data()[2:-2]
        self.label_2.setText(f"{self.chat}")
        self.update_messages()

    def update_messages(self):
        contact = self.label_2.text()
        messages = self.db.get_messages(contact)
        self.messages.clear()
        for message in messages:
            text = QStandardItem(f"{message.message}")
            date = QStandardItem(f"{message.date.replace(microsecond=0)}")
            font = QFont("Helvetica [Cronyx]", 6)
            date.setFont(QFont(font))
            for row in (text, date):
                row.setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignLeft
                    if message.recieved == True
                    else QtCore.Qt.AlignmentFlag.AlignRight
                )
                self.messages.appendRow(row)
