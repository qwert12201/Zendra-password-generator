import base64
import random
import sys
import os
import time
import shutil
import threading
import queue

try:
    from pyperclip import copy as password_copy
    from PyQt6 import QtWidgets, QtCore
    from design import Ui_MainWindow
    from multiply_generator import Ui_Dialog
    from functools import partial
    from modules import *
except (ImportError, ModuleNotFoundError):
    print("You haven't install all modules from requirements.txt, I can try to do it")
    choice = input("yes / no ").strip().lower()
    while choice not in ("yes", "no"):
        choice = input("yes / no ").strip().lower()
    if choice == "yes":
        os.system("pip install -r requirements.txt")
        print("Please restart the program")
        sys.exit()
    else:
        raise ImportError("Modules haven't installed")

def future():
    # ---------------------------
    # Debug
    # os.system("pyuic6 design.ui -o design.py")
    # os.system("pyuic6 module_multiply_generator.ui -o multiply_generator.py")
    # os.system("lupdate main.py multiply_generator.py design.ui module_multiply_generator.ui -ts translations/ru.ts translations/en.ts")
    # os.system("lrelease translations/*.ts")
    for file in os.listdir("test"):
        if os.lstat(f"test/{file}")[6] != 0:
            try:
                os.replace(f"test/{file}", f"past/{file}")
            except FileExistsError:
                os.replace(f"test/{file}", f"past/{str(random.choice([0, 10000]))}{file}")
    shutil.rmtree("test")
    os.mkdir("test")
    for i in range(6):
        with open(f"test/file_{i}.txt", "w", encoding="utf-8"): pass
    print("Папки созданы и интерфейсы обновлены!")


# Constants
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
big_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
special_symbols = [
    "~", "`", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "=", "+",
    "[", "]", "{", "}", "|", ";", ":", "'", "\"", ",", ".", "<", ">", "/", "?",
    "№", "€", "£", "₽"
]
numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

WORKERS = 1
BUFFER_LINES = 100_000
threads_queue = queue.Queue()

class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def __init__(self, file: str, length: int, to_generate: int, boxes: dict[str, bool]):
        super().__init__()
        self.file = file
        self.length = length
        self.to_generate = to_generate
        self.file_lock = threading.Lock()
        self._iswork = True
        for param, value in boxes.items():
            if value:
                setattr(self, param, value)

    @staticmethod
    def one_char(array: list[str | int]) -> str:
        return str(random.choice(array))

    def generatePassword(self) -> str:
        lists = []
        result = ""
        length = self.length
        if getattr(self, "nums", False):
            lists.append(numbers)
        if getattr(self, "letters", False):
            lists.append(letters)
        if getattr(self, "specialSymbols", False):
            lists.append(special_symbols)
        if getattr(self, "randLength", False):
            length = random.randint(5, 20)
        if getattr(self, "caps", False):
            lists.append(big_letters)
        for _ in range(length):
            choice = random.choice(lists)
            result += self.one_char(choice)
        if getattr(self, "base64", False):
            result = base64.b64encode(result.encode("utf-8")).decode()
        return result

    def writeLines(self, buffer: list[str]):
        with self.file_lock:
            with open(self.file, "a", encoding="utf-8") as f:
                f.writelines(buffer)

    def sendLogs(self, passwords_generated: int, result: str):
        # label_7, label_9
        threads_queue.put((passwords_generated, result))

    @QtCore.pyqtSlot()
    def run(self):
        buffer = []
        generated = 0
        for _ in range(self.to_generate):
            if not self._iswork:
                return False
            result = self.generatePassword()
            generated += 1
            buffer.append(result + "\n")
            if len(buffer) >= BUFFER_LINES:
                self.writeLines(buffer)
                buffer.clear()
            if generated % 500 == 0:
                self.sendLogs(generated, result)
                generated = 0
        if buffer:
            self.writeLines(buffer)
        self.sendLogs(generated, result)
        buffer.clear()
        self._iswork = False
        self.finished.emit()

class ModuleWindow_1(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowTitle("Multiply Generator")
        self.boxes = [self.ui.BaseBox2, self.ui.RandBox2, self.ui.CapsBox2, self.ui.LetterBox2, self.ui.NumBox2, self.ui.SpecialBox2]
        self.labels = [self.ui.label_5, self.ui.label_6, self.ui.label_7, self.ui.label_8, self.ui.label_9]
        self.ui.Nativelabel.setText("")
        self.file = None
        self._worker = None
        self._thread = None
        self.reset_settings()

        self.ui.GenerateMultiply.clicked.connect(self.procces_generation)
        self.ui.SelectFile.clicked.connect(self.selectFile)
        self.ui.CancelButton.clicked.connect(self.CancelGeneration)

    def update_native_display(self, text: str):
        timer = QtCore.QTimer(self)
        self.ui.Nativelabel.setText(text)
        timer.setInterval(2000)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self.ui.Nativelabel.setText(""))
        timer.start()

    def closeEvent(self, a0):
        self._iswork = False
        return super().closeEvent(a0)

    def reset_settings(self):
        self.ui.progressBar.setValue(0)
        self._iswork = False
        self.ui.lineEdit.setReadOnly(False)
        for label in self.labels:
            label.hide()

    def CancelGeneration(self):
        if self._iswork and self.ui.lineEdit.isReadOnly():
            choice = QtWidgets.QMessageBox.warning(self, self.tr("Warning"), self.tr("Do you want to stop generation?"), QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if choice == QtWidgets.QMessageBox.StandardButton.Yes:
                if self._thread:
                    self._worker._iswork = False
                self.update_native_display(self.tr("Interrupted."))
                self._iswork = False
        elif self.ui.CancelButton.text() == self.tr("Clear"):
            self.reset_settings()
            self.update_native_display(self.tr("Cleaned!"))
            self.ui.CancelButton.setText("Cancel")

    def type_of_bit(self, bits: int | float) -> str:
        bytess = bits / 8
        if bits == 0:
            return self.tr("0 bits")
        data = {self.tr("bits"): bits, self.tr("bytes"): bytess, self.tr("KB"): bytess / 1024, self.tr("MB"): bytess / 1048576, self.tr("GB"): bytess / 1048576 / 1024, self.tr("TB"): bytess / 1099511627776}
        for key, value in data.items():
            if value >= 1:
                result = str(round(value, 2)) + " " + key
        return result

    @staticmethod
    def one_char(array: list[str | int]) -> str:
        return str(random.choice(array))

    def selectFile(self):
        file, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.tr("Select a file"), filter="*.txt")
        if file:
            with open(file, "+a", encoding="utf-8"):
                pass
            self.file = file
            self.update_native_display(self.tr("File has selected succesfully!"))
        else:
            self.update_native_display(self.tr("File selection was interrupted"))

    def check_options(self):
        length = self.ui.lineEdit_2.text()
        value = self.ui.lineEdit.text()
        box_check = [box.isChecked() for box in self.boxes]
        if not length.isdigit() or int(length) < 1:
            QtWidgets.QMessageBox.critical(self, self.tr("Length"), self.tr("Incorrect length"))
            return
        if not value.isdigit() or int(value) < 1:
            QtWidgets.QMessageBox.critical(self, self.tr("Value"), self.tr("Please type correct value in the count field"))
            self.ui.lineEdit.setText("")
            return
        if (not any(box_check)) or (box_check[0] and not any(box_check[1:])) or (box_check[1] and not any(box_check[2:])):
            QtWidgets.QMessageBox.critical(self, self.tr("Options"), self.tr("You haven't selected any option"))
            return
        if not self.file:
            QtWidgets.QMessageBox.critical(self, self.tr("File"), self.tr("You have to select a file to save passwords"))
            return
        return True

    def updateLabels(self, size: float, generated_passwords: int, remaining: int, password: str, progressResult: int):
        self.ui.label_6.setText(self.tr("File size: ") + size)
        self.ui.label_7.setText(self.tr("Passwords generated: ") + str(generated_passwords))
        self.ui.label_8.setText(self.tr("Seconds remaining: ") + str(remaining))
        self.ui.label_9.setText(self.tr('Current password: ') + password)
        self.ui.progressBar.setValue(progressResult)

    def thread_init(self, length: int, value: int, boxes: dict[str, bool]):
        self._thread = QtCore.QThread()
        self._worker = Worker(self.file, length, value, boxes)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    def generate_password(self, length: int) -> str:
        lists = []
        result = ""
        if self.ui.NumBox2.isChecked():
            lists.append(numbers)
        if self.ui.LetterBox2.isChecked():
            lists.append(letters)
        if self.ui.SpecialBox2.isChecked():
            lists.append(special_symbols)
        if self.ui.RandBox2.isChecked():
            length = random.randint(5, 20)
        if self.ui.CapsBox2.isChecked():
            lists.append(big_letters)
        for _ in range(length):
            choice = random.choice(lists)
            result += self.one_char(choice)
        if self.ui.BaseBox2.isChecked():
            result = base64.b64encode(result.encode("utf-8")).decode()
        return result

    def syncroneGenerator(self, length: int, value: int, mode: str, start=None):  # mode in ("generate", "generate_last")
        # Synchrone Generator procces
        self._iswork = True
        with open(self.file, "a", encoding="utf-8") as f:
            for i in range(value):
                if not self._iswork:
                    self.ui.CancelButton.setText(self.tr("Clear"))
                    return
                result = self.generate_password(length)
                if mode == "generate":
                    progressResult = int((i / value) * 100)
                    size = self.type_of_bit(os.lstat(self.file)[6] * 8)
                    remaining = int(((time.perf_counter() - start) / (i + 1)) * (value - i - 1)) if i != 0 else 0
                    self.updateLabels(size, i, remaining, result, progressResult)
                f.write(result + "\n") if i + 1 != value else f.write(result)

    def generateMultiply(self, start: float, length: int, value: int, boxes: dict[str, bool]):
        # Procces generation
        self.thread_init(length, value, boxes)
        total_generated = 0
        while not threads_queue.empty() or self._worker._iswork:
            try:
                result = threads_queue.get(timeout=0.2)  # result[0] = passwords_generated, result[1] = password
                print(result)
                size = self.type_of_bit(os.lstat(self.file)[6] * 8)
                total_generated += result[0]
                password = result[1]
                print(total_generated)
                remaining = int(((time.perf_counter() - start) / (total_generated)) * (value - total_generated)) if total_generated != 0 else 0
                remaining = str(remaining)
                progress = int((total_generated / value) * 100)
                self.updateLabels(size, total_generated, remaining, password, progress)
            except queue.Empty:
                pass

    def procces_generation(self):
        self.reset_settings()
        if not self.check_options():
            return
        length = int(self.ui.lineEdit_2.text())
        value = int(self.ui.lineEdit.text())
        self.ui.CancelButton.setText("Cancel")
        for label in self.labels:
            label.show()
        self.update_native_display(self.tr("Generation has started..."))
        self.ui.lineEdit.setReadOnly(True)
        self.ui.label_5.setText(self.tr("File: ") + self.file.split("/")[-1])
        start = time.perf_counter()
        boxes = {
            "nums": self.ui.NumBox2.isChecked(),
            "letters": self.ui.LetterBox2.isChecked(),
            "specialSymbols": self.ui.SpecialBox2.isChecked(),
            "randLength": self.ui.RandBox2.isChecked(),
            "caps": self.ui.CapsBox2.isChecked(),
            "base64": self.ui.BaseBox2.isChecked()
        }
        if value > 100_000:
            remaining = value // WORKERS
            left = value % WORKERS
            self.generateMultiply(start, length, remaining, boxes)
            if left:
                self.syncroneGenerator(length, left, "generate_last")
        else:
            self.syncroneGenerator(length, value, "generate", start)
        self.ui.CancelButton.setText(self.tr("Clear"))
        self.ui.progressBar.setValue(100)
        self._iswork = False
        self.ui.lineEdit.setReadOnly(False)
        self.update_native_display(self.tr("Finished!"))
        self.ui.label_6.setText(self.tr("File size: ") + self.type_of_bit(int(os.lstat(self.file)[6]) * 8))
        self.ui.label_7.setText(self.tr("Passwords generated: ") + str(value))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowTitle("Password Generator")
        self.display = self.tr("Welcome!")
        self.ui.lineEdit.setText(self.display)
        self.boxes = [self.ui.BaseBox, self.ui.RandBox, self.ui.CapsBox, self.ui.LetterBox, self.ui.NumBox, self.ui.SpecialBox]
        self.version = "1.09"
        self._rippers = (self.tr("You haven't selected any option!"), self.tr("Welcome!"), "")
        self.ui.label_3.setText(self.tr("Version: ") + self.version)
        self.hashes = [self.ui.actionsha512, self.ui.actionMD5, self.ui.actionsha256, self.ui.actionsha_1]
        self.ui.label_4.setText("")
        self.show()
        self.app_translator = QtCore.QTranslator(app)

        # PushButtons
        self.ui.GeneratePush.clicked.connect(self.generator)
        self.ui.CopyPush.clicked.connect(self.copy_password)
        self.ui.ClearPush.clicked.connect(self.clear)
        self.ui.RandomPush.clicked.connect(self.randomize)

        # QActions (MenuBar)
        for _hash, _hash2 in zip(self.hashes, algorithms):
            _hash.triggered.connect(partial(self.crypto_handler, _hash2))
        self.ui.actionGenerate_Multiply_Times.triggered.connect(self.multiply_handler)
        self.ui.actionEnglish.triggered.connect(lambda: self.translate("en"))
        self.ui.actionRussian.triggered.connect(lambda: self.translate("ru"))

    def update_display(self):
        self.ui.lineEdit.setText(self.display)

    def multiply_handler(self):
        dialog = ModuleWindow_1()
        dialog.exec()

    def translate(self, lang: str):
        app.removeTranslator(self.app_translator)
        path = resource_path("translations/" + lang + ".qm")
        if self.app_translator.load(path):
            app.installTranslator(self.app_translator)
            self.ui.retranslateUi(self)
            self.ui.lineEdit.setText("")

    def info_label(self, text: str):
        timer = QtCore.QTimer(self)
        self.ui.label_4.setText(text)
        timer.setInterval(2000)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self.ui.label_4.setText(""))
        timer.start()

    def copy_password(self):
        if self.display not in self._rippers:
            password_copy(self.display)
            self.info_label(self.tr("Copied!"))

    def generator(self):
        lists = []
        length = self.ui.lineEdit_2.text()
        result = ""
        box_check = [box.isChecked() for box in self.boxes]
        if not length.isdigit() or int(length) < 1:
            QtWidgets.QMessageBox.critical(self, self.tr("Length"), self.tr("Incorrect length"))
            self.ui.lineEdit.setText("")
            return
        if (not any(box_check)) or (box_check[0] and not any(box_check[1:])) or (box_check[1] and not any(box_check[2:])):
            QtWidgets.QMessageBox.critical(self, self.tr("Options"), self.tr("You haven't selected any option!"))
            return
        length = int(length)
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
        self.info_label(self.tr("Password has generated!"))

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
            self.info_label(self.tr("Randomized!"))

    def clear(self):
        self.display = ""
        self.update_display()
        self.info_label(self.tr("Cleaned!"))


if __name__ == '__main__':
    future()
    app = QtWidgets.QApplication(sys.argv)
    translator = QtCore.QTranslator(app)
    translator.load("translations/en.qm")
    app.installTranslator(translator)
    w = MainWindow()
    sys.exit(app.exec())
