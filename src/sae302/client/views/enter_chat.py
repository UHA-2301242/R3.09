from __future__ import annotations

import logging
import typing

from PyQt6 import QtWidgets

from sae302.commons.messages import RawMessage

if typing.TYPE_CHECKING:
    from sae302.client.__main__ import MainApplication

_log = logging.getLogger(__name__)


class ChatWithServer(QtWidgets.QWidget):
    def __init__(
        self,
        app: "MainApplication",
        *,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent=parent)
        self.app = app

        layout = QtWidgets.QGridLayout()

        self.text_box_ui = QtWidgets.QTextEdit()
        self.text_box_ui.setReadOnly(True)
        layout.addWidget(self.text_box_ui, 0, 0)

        self.send_msg_ui = QtWidgets.QLineEdit()
        self.send_msg_ui.setPlaceholderText("Message")
        layout.addWidget(self.send_msg_ui, 1, 0)

        button = QtWidgets.QPushButton("Envoyer")
        button.clicked.connect(self.on_btn_send_clicked)  # type: ignore
        layout.addWidget(button, 1, 2)

        self.status_text_ui = QtWidgets.QLabel()
        self.status_text_ui.hide()
        layout.addWidget(self.status_text_ui, 3, 0)

        self.setLayout(layout)

    def on_btn_send_clicked(self):
        assert self.app.current_socket

        if message := self.send_msg_ui.text():
            self.app.current_socket.send(message)

        self.send_msg_ui.setText(None)

    def on_message_receiver(self, message: RawMessage):
        """This method should be called whenever a new message has been received.
        This will cause the text box to update with the new message.

        Parameters
        ----------
        message : str
            The message that has been received by the client.
        """
        current_content = self.text_box_ui.toPlainText()
        self.text_box_ui.setText(f"{current_content}\n{str(message)}")
