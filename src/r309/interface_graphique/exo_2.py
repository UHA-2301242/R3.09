import sys
import typing

from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)


class Temperature:
    value: float

    def __init__(self, value: float) -> None:
        self.value: float = value  # En Celsius

    @classmethod
    def from_fahrenheit(cls, value: float) -> typing.Self:
        return cls((value - 32) * 5 / 9)

    @classmethod
    def from_kelvin(cls, value: float) -> typing.Self:
        return cls(value - 273.15)

    def to_celsius(self) -> float:
        return self.value

    def to_fahrenheit(self) -> float:
        return (self.value * 9 / 5) + 32

    def to_kelvin(self) -> float:
        return self.value + 273.15


class TemperatureConverter(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conversion de température")
        self.setGeometry(100, 100, 300, 200)

        self.temp_input = QLineEdit(self)
        self.temp_input.setPlaceholderText("Enter temperature")

        self.unit_from_box = QHBoxLayout()
        self.unit_from = QComboBox(self)
        self.unit_from.addItems(["Celsius", "Fahrenheit", "Kelvin"])
        self.unit_from_box.addWidget(QLabel("Unité d'origine :"))
        self.unit_from_box.addWidget(self.unit_from)

        self.unit_to_box = QHBoxLayout()
        self.unit_to = QComboBox(self)
        self.unit_to.addItems(["Celsius", "Fahrenheit", "Kelvin"])
        self.unit_to_box.addWidget(QLabel("Unité vers :"))
        self.unit_to_box.addWidget(self.unit_to)

        self.convert_button = QPushButton("Convert", self)
        self.convert_button.clicked.connect(self.convert_temperature)

        self.result_label = QLabel("", self)

        layout = QVBoxLayout()
        layout.addWidget(self.temp_input)
        layout.addLayout(self.unit_from_box)
        layout.addLayout(self.unit_to_box)
        layout.addWidget(self.convert_button)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

        self.help_button = QPushButton("?", self)
        self.help_button.clicked.connect(self.show_help)
        # The help button must not take a full width, and only take as much space as needed. PyQt6 valid code
        self.help_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )

        layout.addWidget(self.help_button)

    def show_help(self):
        QMessageBox.information(
            self, "Help", "Permet la conversion de valeurs de température."
        )

    def convert_temperature(self):
        try:
            value = float(self.temp_input.text())
            from_unit = self.unit_from.currentText()
            to_unit = self.unit_to.currentText()

            match from_unit:
                case "Celsius":
                    temp = Temperature(value)
                case "Fahrenheit":
                    temp = Temperature.from_fahrenheit(value)
                case "Kelvin":
                    temp = Temperature.from_kelvin(value)
                case _:
                    temp = Temperature(0)

            match to_unit:
                case "Celsius":
                    result = temp.to_celsius()
                case "Fahrenheit":
                    result = temp.to_fahrenheit()
                case "Kelvin":
                    result = temp.to_kelvin()
                case _:
                    result = "weird error??!?"

            self.result_label.setText(f"Result: {result:.2f} {to_unit}")

        except ValueError as e:
            QMessageBox.critical(self, "Conversion Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = TemperatureConverter()
    dialog.show()
    sys.exit(app.exec())
