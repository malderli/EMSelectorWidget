import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout
from PyQt5.Qt import QEventLoop

from demo import DemoWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)

    demowgt = DemoWidget()
    loop = QEventLoop()

    demowgt.signalClose.connect(loop.quit)

    demowgt.show()
    loop.exec()