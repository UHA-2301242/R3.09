from __future__ import annotations

import ipaddress
import typing

from PyQt6 import QtWidgets

if typing.TYPE_CHECKING:
    from sae302.client.__main__ import MainApplication


class Connect(QtWidgets.QWidget):

    def __init__(self, app: "MainApplication"):
        super().__init__()
        self.app = app

        layout = QtWidgets.QGridLayout()

        self.server_ip_ui = QtWidgets.QLineEdit("127.0.0.1")
        self.server_ip_ui.setPlaceholderText("Adresse IP du serveur")
        self.server_ip_ui.textChanged.connect(self._hide_status_text)  # type: ignore
        layout.addWidget(QtWidgets.QLabel("Adresse IP"), 0, 0)
        layout.addWidget(self.server_ip_ui, 0, 1)

        self.server_port_ui = QtWidgets.QLineEdit("25587")
        self.server_port_ui.setPlaceholderText("Port du serveur")
        self.server_ip_ui.textChanged.connect(self._hide_status_text)  # type: ignore
        layout.addWidget(QtWidgets.QLabel("Port"), 1, 0)
        layout.addWidget(self.server_port_ui, 1, 1)

        button = QtWidgets.QPushButton("Se connecter")
        button.clicked.connect(self.on_btn_connect_clicked)  # type: ignore
        layout.addWidget(button, 2, 0, 1, 0)

        self.status_text_ui = QtWidgets.QLabel()
        self.status_text_ui.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
        )
        self.status_text_ui.setHidden(True)
        layout.addWidget(self.status_text_ui, 3, 0)

        self.setLayout(layout)
        self.app.resize(300, 200)

    def _hide_status_text(self):
        self.status_text_ui.setHidden(True)

    def update_status_text(
        self, text: str, style: typing.Literal["black", "red"] = "black"
    ):
        self.status_text_ui.setHidden(False)
        self.status_text_ui.setText(text)
        self.status_text_ui.setStyleSheet(f"color: {style}")

    def on_btn_connect_clicked(self):
        try:
            host = self.server_ip()
        except ValueError:
            return self.app.status_bar.showMessage("Invalid IP address", 0)

        try:
            port = self.server_port()
        except ValueError:
            return self.app.status_bar.showMessage("Invalid port", 0)

        try:
            self.app.connect_socket(str(host), port)
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                None,
                "Could not establish connection",
                f"Impossible de se connecter au serveur : {e}",
            )
            self.app.status_bar.showMessage(
                f"Impossible de se connecter au serveur : {e}", 0
            )
        else:
            assert self.app.current_socket
            self.app.view.setup_upload_view()

    def server_ip(self) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
        """Obtains the server IP currently indicated by the user in the UI.

        Returns
        -------
        ipaddress.IPv4Address
            The given address IP

        Raises
        ------
        ValueError
            Not a valid IP to connect to.
        """
        return ipaddress.ip_address(self.server_ip_ui.text())

    def server_port(self) -> int:
        """Obtains the server port currently indicated by the user in the UI.

        Returns
        -------
        int
            The given port

        Raises
        ------
        ValueError
            Not a valid port to connect to.
        """
        return int(self.server_port_ui.text())
