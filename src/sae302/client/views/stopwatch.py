from PyQt6 import QtCore, QtWidgets


class Stopwatch(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 80)

        self.label = QtWidgets.QLabel("Temps d'exécution")
        self.label.setMaximumHeight(25)
        self.label.setMinimumHeight(25)

        self.timer = QtWidgets.QLCDNumber()
        self.timer.setDigitCount(4)

        self._true_timer = QtCore.QTimer(self)
        self._true_timer.timeout.connect(self.up_by_1)  # type: ignore
        self._true_timer.start(1000)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.timer)

        self.setLayout(layout)

    def up_by_1(self):
        self.timer.display(self.timer.intValue() + 1)

    def stop(self):
        self._true_timer.stop()
