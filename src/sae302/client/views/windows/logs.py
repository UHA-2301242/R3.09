from PyQt6 import QtWidgets


class LogsWindow(QtWidgets.QDialog):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self, logs: str):
        super().__init__()

        self.setWindowTitle("Received Logs")

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(QtWidgets.QLabel("Logs d'exécution du programme"))

        self.logs_box = QtWidgets.QTextEdit(self)
        self.logs_box.setReadOnly(True)
        self.logs_box.setText(logs)
        self.logs_box.resize(300, 600)
        layout.addWidget(self.logs_box)

        self.setLayout(layout)
