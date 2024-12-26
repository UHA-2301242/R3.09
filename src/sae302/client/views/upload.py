from __future__ import annotations

import logging
import pathlib
import typing

from PyQt6 import QtWidgets, QtCore

from sae302.commons import messages

if typing.TYPE_CHECKING:
    from sae302.client.__main__ import MainApplication

_log = logging.getLogger(__name__)


class Upload(QtWidgets.QWidget):
    def __init__(
        self,
        app: "MainApplication",
        *,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent=parent)
        self.app = app

        self.file: pathlib.Path | None = None

        layout = QtWidgets.QGridLayout()

        self.select_file_button = QtWidgets.QPushButton("Choisir le fichier à exécuter")
        self.select_file_button.clicked.connect(self.on_btn_select_file_clicked)  # type: ignore
        layout.addWidget(self.select_file_button, 1, 0)

        self.selected_file_text = QtWidgets.QLabel()
        self.selected_file_text.hide()
        layout.addWidget(self.selected_file_text, 2, 0, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.send_to_server_button = QtWidgets.QPushButton("Envoyer le fichier")
        self.send_to_server_button.setDisabled(True)
        self.send_to_server_button.clicked.connect(self.on_btn_send_to_server_clicked)  # type: ignore
        layout.addWidget(self.send_to_server_button, 3, 0)

        self.open_logs_button = QtWidgets.QPushButton("Ouvrir les logs d'exécution")
        self.open_logs_button.hide()
        layout.addWidget(self.open_logs_button, 4, 0)

        self.disconnect_button = QtWidgets.QPushButton("Déconnecter")
        self.disconnect_button.clicked.connect(self.on_btn_disconnect_clicked)  # type: ignore
        layout.addWidget(self.disconnect_button, 5, 0)

        self.setLayout(layout)
        self.app.resize(200, 100)

    def on_btn_select_file_clicked(self):
        """Method to call when the user want to pick which file to send to the server."""
        file = QtWidgets.QFileDialog().getOpenFileUrl(  # type: ignore
            self,
            "Choisir le fichier",
            filter="Allowed Files (*.py *.java *.c *.h *.cpp *.hpp)",
        )
        if file and file[0]:
            self.file = pathlib.Path(file[0].toLocalFile()).resolve()
            self.selected_file_text.setText(f"Fichier : {self.file.name}")
            self.selected_file_text.show()
            self.send_to_server_button.setDisabled(False)
        else:
            self.selected_file_text.hide()
            self.send_to_server_button.setDisabled(True)

    def on_btn_send_to_server_clicked(self):
        assert self.app.current_socket
        if self.file:
            self.app.current_socket.send(
                messages.FileMessage.create_message(self.file, "auto")
            )
        self.app.start_timer()

    def on_btn_disconnect_clicked(self):
        self.app.disconnect_socket()
        self.app.view.setup_login_view()
