from __future__ import annotations

import argparse
import contextlib
import logging
import queue
import socket
import sys
import threading

from sae302.commons import messages
from sae302.server.executor import BaseExecutor, ExecutorFactory

_log = logging.getLogger(__name__)
clients: list[socket.socket] = []
clients_lock = threading.Lock()
messages_queue: queue.Queue[messages.ALL_MESSAGES] = queue.Queue()


def get_socket_port(sock: socket.socket) -> int:
    return sock.getpeername()[1]


def _disconnect_client(client: socket.socket):
    with clients_lock:
        if client in clients:
            _log.debug("Disconnecting port %s", get_socket_port(client))
            with contextlib.suppress(OSError):
                client.shutdown(socket.SHUT_RDWR)
            client.close()
            clients.remove(client)


class MessageHandler(threading.Thread):
    """The MessageHandler class is used to handle messages that have been put into the queue, and
    require to be processed.
    """

    def __init__(self) -> None:
        super().__init__(daemon=True)

        self.queue = messages_queue
        self.currently_running_file = False
        self.factory = ExecutorFactory()
        self.current_executor: BaseExecutor | None = None

    def handle_file(self, message: messages.FileMessage) -> None:
        executor = self.factory.find_executor(
            friendly_name=(
                message.chosen_executor if message.chosen_executor != "auto" else None
            ),
            supported_suffixes=[message.file_name.split(".")[-1]],
        )
        if not executor:
            message.reply(
                messages.ErrorMessage.create_message(
                    "ERROR",
                    "No executor found for this file type.",
                )
            )
            return

        self.current_executor = executor()

        if not self.current_executor.is_available:
            message.reply(
                messages.ErrorMessage.create_message(
                    "ERROR",
                    f"Executor not available. Missing required tool(s) on server.",
                )
            )
            return

        try:
            logs = self.current_executor.execute(message.file_name, message.file_content)
            message.reply(messages.LogsMessage.create_message(str(logs.code), logs.output))
        except Exception as e:
            message.reply(messages.ErrorMessage.create_message("ERROR", f"Could not execute the file: {e}"))

    def run(self) -> None:
        while True:
            try:
                message = self.queue.get()
                if isinstance(message, messages.FileMessage):
                    if self.currently_running_file:
                        message.reply(
                            messages.ErrorMessage.create_message(
                                "ERROR",
                                "File cannot be processed at this time. Use another server.",
                            )
                        )
                        return
                    try:
                        self.currently_running_file = True
                        self.handle_file(message)
                    finally:
                        self.currently_running_file = True
            except queue.ShutDown:
                break
            except queue.Empty:
                # Weird?
                pass


class ClientHandler(threading.Thread):
    def __init__(self, socket: socket.socket) -> None:
        super().__init__(daemon=True)
        self.socket = socket
        self.queue = messages_queue

    def run(self) -> None:
        message_buffer = messages.MessageBuffer()

        while True:
            try:
                message = self.socket.recv(1024)
                if not message:
                    _disconnect_client(self.socket)
                    break

                message_buffer.push(message)

                if message_buffer.is_complete:
                    message = message_buffer.get_message(self.socket)
                    messages_queue.put(message)
                    # New buffer
                    message_buffer = messages.MessageBuffer()

            except Exception as e:
                _log.exception(e)
                _disconnect_client(self.socket)
                break


class Server:
    def __init__(self, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("127.0.0.1", port))
        self.socket.listen(10)
        _log.info("Server started at port %s, waiting for connections...", port)

        self.handler = MessageHandler()
        self.handler.start()

    def accept_connections(self):
        while True:
            try:
                client_socket, _ = self.socket.accept()
                _log.debug("Connection from port %s", get_socket_port(client_socket))
                clients.append(client_socket)
                client_thread = ClientHandler(client_socket)
                client_thread.start()
            except KeyboardInterrupt:
                _log.debug("Received KeyboardInterrupted!")
                if clients:
                    _log.info("There are still a few clients connected.")
                self.handler.queue.shutdown()
                break


def launch():
    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="[%(levelname)s] %(name)s -> %(funcName)s: %(message)s",
        level=0,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "port",
        nargs="?",
        default=25587,
        type=int,
        help="Le port sur lequel le serveur va démarrer.",
    )
    args = parser.parse_args()

    try:
        server = Server(args.port)
    except OSError:
        _log.critical("Impossible de démarrer le serveur sur ce port.")
        sys.exit(1)

    try:
        server.accept_connections()
    finally:
        for client in clients:
            _disconnect_client(client)
        with contextlib.suppress(Exception):
            server.socket.shutdown(socket.SHUT_RDWR)
        server.socket.close()
        _log.info("Server socket closed.")
    sys.exit(0)


if __name__ == "__main__":
    launch()
