import base64
import random
import sys

from pyperclip import copy as password_copy
from PyQt6 import QtWidgets, QtCore
from design import Ui_MainWindow
from functools import partial

from hashes import *

# Constants
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
big_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
special_symbols = [
    "~", "`", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "=", "+",
    "[", "]", "{", "}", "|", ";", ":", "'", "\"", ",", ".", "<", ">", "/", "?",
    "№", "€", "£", "₽"
]
numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowTitle("Password Generator")
        self.display = "Добро пожаловать!"
        self.ui.lineEdit.setText(self.display)
        self.boxes = [self.ui.BaseBox, self.ui.CapsBox, self.ui.RandBox, self.ui.LetterBox, self.ui.NumBox, self.ui.SpecialBox]
        self.version = "1.0"
        self._rippers = ("Вы не выбрали ни одного параметра!", "Добро пожаловать!", "")
        self.ui.label_3.setText("Version: " + self.version)
        self.hashes = [self.ui.actionsha512, self.ui.actionMD5, self.ui.actionsha256, self.ui.actionsha_1]

        # MenuBar
        self.file = None
        self.hash = None

        # PushButtons
        self.ui.GeneratePush.clicked.connect(self.generator)
        self.ui.CopyPush.clicked.connect(self.copy_password)
        self.ui.ClearPush.clicked.connect(self.clear)
        self.ui.RandomPush.clicked.connect(self.randomize)

        # QActions (MenuBar)
        self.ui.menuFileSaver.triggered.connect(self.call_file_manager)
        for _hash, _hash2 in zip(self.hashes, algorithms):
            _hash.triggered.connect(partial(self.crypto_handler, _hash2))

    def update_display(self):
        self.ui.lineEdit.setText(self.display)

    def info_label(self, text: str):
        timer = QtCore.QTimer(self)
        self.ui.label_4.setText(text)
        timer.setInterval(2000)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self.ui.label_4.setText(""))
        timer.start()

    def call_file_manager(self):
        file, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Select a file", filter="*.txt")
        if file:
            with open(file, "+a", encoding="utf-8"):
                pass
            self.file = file
            self.info_label("Файл сохранения указан.")

    def copy_password(self):
        if self.display not in self._rippers:
            password_copy(self.display)
            self.info_label("Скопировано!")

    @staticmethod
    def one_char(array: list[str | int]) -> str:
        return str(random.choice(array))

    def generator(self):
        lists = []
        length = 8
        result = ""
        if not any(box.isChecked() for box in self.boxes):  # not - инвертирует -> если все = False
            self.display = ""
            self.ui.lineEdit.setText("Вы не выбрали ни одного параметра!")
            return
        if self.ui.NumBox.isChecked():
            lists.append(numbers)
        if self.ui.LetterBox.isChecked():
            lists.append(letters)
        if self.ui.SpecialBox.isChecked():
            lists.append(special_symbols)
        if self.ui.RandBox.isChecked():
            length = random.randint(5, 20)
        if self.ui.CapsBox.isChecked():
            lists.append(big_letters)
        for _ in range(length):
            choice = random.choice(lists)
            result += self.one_char(choice)
        if self.ui.BaseBox.isChecked():
            result = base64.b64encode(result.encode("utf-8")).decode()
        self.display = result
        self.update_display()
        self.info_label("Пароль сгенерирован!")

    def crypto_handler(self, algorithm):
        if self.display not in self._rippers:
            self.display = hashlib_user(self.display, algorithm)
            self.update_display()

    def randomize(self):
        if self.display not in self._rippers:
            result = list(self.display)
            random.shuffle(result)
            self.display = "".join(result)
            self.update_display()

    def clear(self):
        self.display = ""
        self.update_display()
        self.info_label("Очищено!")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
