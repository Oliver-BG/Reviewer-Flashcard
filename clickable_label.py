from PyQt5 import QtCore as qtc, QtWidgets as qtw

class ClickableLabel(qtw.QLabel):
    clicked = qtc.pyqtSignal()
    def __init__(self, parent=None):
        qtw.QLabel.__init__(self, parent=parent)

    def mousePressEvent(self, event):
        self.clicked.emit()