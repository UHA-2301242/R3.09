import sys

from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class AppDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Je répète du texte")
        self.setGeometry(0, 0, 350, 200)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Temp")

        self.ok_button = QPushButton("Ok", self)
        self.ok_button.clicked.connect(self.display_greeting)

        self.greeting_label = QLabel("", self)

        self.close_button = QPushButton("Quitter", self)
        self.close_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        layout.addWidget(self.name_input)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.greeting_label)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def display_greeting(self):
        name = self.name_input.text()
        self.greeting_label.setText(f"Bonjour {name}.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = AppDialog()
    dialog.show()
    sys.exit(app.exec())
