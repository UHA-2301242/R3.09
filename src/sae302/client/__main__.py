from __future__ import annotations

import logging
import sys

from PyQt6 import QtCore, QtWidgets

from sae302.client.socket_client import SocketClient
from sae302.client.views.connection import Connect
from sae302.client.views.enter_chat import ChatWithServer
from sae302.client.views.stopwatch import Stopwatch
from sae302.client.views.upload import Upload
from sae302.client.views.windows.logs import LogsWindow
from sae302.commons import messages
from sae302.commons.events import Events

_log = logging.getLogger(__name__)


class MessageWorker(QtCore.QThread):
    """Worker thread used to receive message and send them to the main thread."""

    on_broken = QtCore.pyqtSignal()

    def __init__(self, app: "MainApplication", socket: SocketClient):
        super().__init__()
        self.app = app
        self.socket = socket

    def run(self):
        _log.debug("Starting message worker.")
        while True:
            message = self.socket.receive()
            if not message:
                self.on_broken.emit()
                break
            message.emit(self.app.events)


class ViewManager:
    """The View Manager is in charge of changing the application's current widget, when requested,
    and make public methods to easily change widgets programmatically.
    """

    def __init__(self, app: "MainApplication"):
        self.app = app

    def on_message_worker_broken(self):
        self.setup_login_view()
        self.app.status_bar.showMessage("Déconnecté par le serveur de force", 10000)

    def setup_login_view(self) -> None:
        self.app.status_bar.showMessage("Non connecté", 0)
        self.app.setCentralWidget(Connect(self.app))

    def setup_chat_view(self) -> None:
        self.app.status_bar.showMessage("Connecté", 0)
        self.app.setCentralWidget(ChatWithServer(self.app))
        self.start_message_worker()

    def setup_upload_view(self) -> None:
        self.app.status_bar.showMessage("Connecté", 0)
        self.app.setCentralWidget(Upload(self.app))
        self.start_message_worker()

    def start_message_worker(self):
        assert self.app.current_socket
        self.message_worker = MessageWorker(self.app, self.app.current_socket)
        self.message_worker.on_broken.connect(self.on_message_worker_broken)  # type: ignore
        self.message_worker.start()
        # Do NOT remove this! For some reason, view will crash if this isn't here.
        # I just won't question it and accept the faith.
        # Apparently not impactful for both the socket and the UI... So......? Super good I guess?
        self.message_worker.usleep(1)


class MainApplication(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.events = Events()
        self.events.on_message.connect(self.on_message)  # type: ignore
        self.events.on_capabilities.connect(self.on_capabilities)  # type: ignore
        self.events.on_logs.connect(self.on_logs)  # type: ignore
        self.events.on_error.connect(self.on_error)  # type: ignore

        self.current_socket: SocketClient | None = None
        self.message_worker: MessageWorker | None = None
        self.server_is_capable_of: dict[str, bool] | None = None
        self.timer_window: Stopwatch | None = None

        self.setWindowTitle("Send Files to Server")

        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)

        self.view = ViewManager(self)
        self.view.setup_login_view()

    def on_message(self, message: messages.Message):
        match message.message:
            case "CAPABILITIES":
                self.view.setup_chat_view()
            case _:
                _log.info("Received message did not match any known possibilities.")

    def on_logs(self, message: messages.LogsMessage):
        _log.debug("Logs received.")
        self.stop_timer()
        LogsWindow(message.logs).exec()

    def on_capabilities(self, message: messages.CapabilitiesMessage):
        self.server_is_capable_of = message.capabilities

    def on_error(self, message: messages.ErrorMessage):
        self.stop_timer()
        if message.gravity == "ERROR":
            method = QtWidgets.QMessageBox.critical
        elif message.gravity == "WARNING":
            method = QtWidgets.QMessageBox.warning
        else:
            method = QtWidgets.QMessageBox.information
        method(None, "Error received from server", message.message)

    def start_timer(self):
        self.timer_window = Stopwatch()
        self.timer_window.show()

    def stop_timer(self):
        if self.timer_window:
            self.timer_window.close()
            self.timer_window.stop()

    def connect_socket(self, host: str, port: int):
        sock = SocketClient(host, port)
        self.status_bar.showMessage("Connecté", 0)
        self.current_socket = sock

    def disconnect_socket(self):
        """Public method to call whenever we would like to close the socket.
        This will attempt best to close the socket as best as possible. No window will be closed,
        simply the socket connection.

        Parameters
        ----------
        return_to_connection_view : bool, default to :py:obj:`False`
            If True, the current view of the main window will be replaced
            by the connection view.
        """
        if self.message_worker:
            self.message_worker.terminate()
        if self.current_socket:
            self.current_socket.close()
            self.current_socket = None


def launch():
    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="[%(levelname)s] %(name)s -> %(funcName)s: %(message)s",
        level=0,
    )

    app = QtWidgets.QApplication(sys.argv)
    client_app = MainApplication()

    try:
        client_app.show()
    except Exception as e:
        _log.exception("Fatal exception: %s", e)
    finally:
        client_app.disconnect_socket()
        sys.exit(app.exec())


if __name__ == "__main__":
    launch()
