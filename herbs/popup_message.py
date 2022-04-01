import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class PopupMessage(QMessageBox):

    def __init__(self, parent=None):
        QMessageBox.__init__(self)

        self.setWindowTitle("Caution!")
        self.setText('Histological image: is oversized.')
        button = self.exec()
        if button == QMessageBox.Ok:
            print('222')