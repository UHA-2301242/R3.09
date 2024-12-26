from __future__ import annotations

import contextlib
import logging
import socket

from sae302.commons.messages import Message, MessageBuffer

_log = logging.getLogger(__name__)


class SocketClient:
    def __init__(self, host: str, port: int):
        self.socket: socket.socket = socket.create_connection((host, port))

    def send(self, message: str):
        _log.debug("Sending message: %s", message)
        self.socket.send(Message.create_message(message).encode())

    def receive(self):
        message_buffer = MessageBuffer()

        while True:
            try:
                message = self.socket.recv(1024)
            except OSError:
                message = None
            if not message:
                # When no message has been received, this generally mean that the client has
                # willingly disconnected. We can break the loop and end the thread.
                break
            message_buffer.push(message)

            if message_buffer.is_complete:
                message = message_buffer.get_message(self.socket)
                # New buffer
                message_buffer = MessageBuffer()
                return message

    def close(self):
        with contextlib.suppress(OSError):
            self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        _log.debug("Socket has been closed.")
