from PyQt5.Qt import QGridLayout, QSplitter, QFrame, pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QTextEdit
import json

from emselector_widget import EMSelector

class DemoWidget(QWidget):
    signalClose = pyqtSignal()

    def __init__(self):
        super(DemoWidget, self).__init__()

        self.btnApplyColors = QPushButton('Применить')
        self.btnApplyColors.clicked.connect(self.btnApplyColorsClicked)
        self.teColorsLeft = QTextEdit()
        self.teColorsRight = QTextEdit()

        self.lytControl = QGridLayout()
        self.lytControl.addWidget(self.teColorsLeft, 0, 0)
        self.lytControl.addWidget(self.teColorsRight, 0, 1)
        self.lytControl.addWidget(self.btnApplyColors, 1, 0, 1, 2)

        self.frameControl = QFrame()
        self.frameControl.setLayout(self.lytControl)

        self.emLeft = EMSelector(False)
        self.emRight = EMSelector(True)

        self.lytEMs = QGridLayout()
        self.lytEMs.addWidget(self.emLeft, 0, 0)
        self.lytEMs.addWidget(self.emRight, 0, 1)

        self.frameEMs = QFrame()
        self.frameEMs.setLayout(self.lytEMs)

        self.slVertical = QSplitter()
        self.slVertical.setOrientation(Qt.Vertical)
        self.slVertical.addWidget(self.frameEMs)
        self.slVertical.addWidget(self.frameControl)

        self.lytMain = QGridLayout()
        self.lytMain.addWidget(self.slVertical)

        self.setLayout(self.lytMain)
        self.setFocusPolicy(Qt.StrongFocus)

        self.setTestData()

    def setTestData(self):
        self.emLeft.setSigns(['fjkdkte', 'ekktnt', 'ehtkdkwtd'])
        self.emLeft.setQuantity({'fjkdkte': 20, 'ekktnt': 32})

        self.emRight.setSigns(['fjkdkte', 'ekktnt', 'ehtkdkwtd'])
        self.emRight.setQuantity({'fjkdkte': 20, 'ehtkdkwtd': 32})

        self.teColorsLeft.setText('''{ 
          "fjkdkte": { "backcolor": "#BD67FF",
          "textcolor": "#000000",
          "textcolor_0": "#808080"}
        }''')

    def btnApplyColorsClicked(self):
        jsonLeft = json.loads(self.teColorsLeft.toPlainText())
        colorsLeft = {}

        for key, value in jsonLeft.items():
            colorsLeft[str(key)] = value

        # colorsRight = json.loads(self.teColorsRight.toPlainText())

        self.emLeft.setSignsColors(colorsLeft)
        # self.emRight.setSignsColors(colorsRight)


    def closeEvent(self, event):
        self.signalClose.emit()
        super(DemoWidget, self).closeEvent(event)

    def keyPressEvent(self, event):
        # Check Ctrl pressed
        if event.key() == 0x01000021:
            self.emLeft.multi(True)
            self.emRight.multi(True)

    def keyReleaseEvent(self, event):
        # Check Ctrl released
        if event.key() == 0x01000021:
            self.emLeft.multi(False)
            self.emRight.multi(False)


