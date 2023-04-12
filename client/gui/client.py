import sys
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from client.gui.ui_client import Ui_MainWindow


class MainClientGui(Ui_MainWindow):
    def __init__(self, db, client):
        super().__init__()
        self.db = db
        self.client = client
        self.setupUi()
        self.update_users_list()

    def update_users_list(self):
        users = self.db.get_users()
        self.users_model = QStandardItemModel()
        for user in users:
            active = "❤️" if user.is_active else "💀"
            contact = "👤" if user.is_contact else ""
            username = QStandardItem(f"{active} {user.username}{contact}")
            username.setEditable(False)
            self.users_model.appendRow(username)
        self.listView.setModel(self.users_model)
