"""Module used for the process and the preparation of messages in the communication
between the client and the server.
"""

import abc
import enum
import hashlib
import json
import logging
import os
import pathlib
import socket
import typing
from io import BytesIO

if typing.TYPE_CHECKING:
    from sae302.commons import events
    from sae302.server.executor import BaseExecutor

_log = logging.getLogger(__name__)


type ERROR_GRAVITY = typing.Literal["ERROR", "WARNING", "INFO"]


class KnownMetadata(enum.StrEnum):
    """A class listing known metadata."""

    LENGTH = "DATA_LENGTH"
    CHECKSUM = "DATA_CHECKSUM"
    FILENAME = "DATA_FILENAME"
    """The name of the file that is sent."""
    EXEC_TYPE = "EXEC_TYPE"
    """The type of execution the user wishes to run. Can either be ``auto``, ``python``, ``java``,
    ``cpp`` or ``c``"""
    DATA = "DATA"
    """The data that has been sent, and received."""


class BaseMetadata(typing.TypedDict):
    DATA_CHECKSUM: str
    """Checksum of the data we are supposedly receiving."""
    DATA_LENGTH: str
    """The length of the message. Used to know when the message is fully received."""
    DATA_TYPE: typing.Literal["MSG", "FILE", "LOGS", "ERROR", "CAPABILITIES"]
    """The type of the message we are sending/receiving."""
    DATA: str
    """The data sent in the message."""


class MessageMetadata(BaseMetadata): ...


class LogsMetadata(BaseMetadata):
    STATUS: str
    """The exit code that was returned by the executor."""


class CapabilitiesMetadata(BaseMetadata): ...


class FileMetadata(BaseMetadata):
    DATA_FILENAME: str
    """The name of the file that is sent."""
    CHOSEN_EXECUTOR: typing.NotRequired[str]


class ErrorMetadata(BaseMetadata):
    GRAVITY: ERROR_GRAVITY
    """The gravity of the error."""


def pack_message(metadata: BaseMetadata) -> str:
    """Prepares the message to be sent.
    The message must be set as a metadata.

    Parameters
    ----------
    metadata : dict[str, str]
        The metadata that will be inserted in the message.

    Returns
    -------
    str
        The message as a form of string in the socket.
    """
    msg = "".join(f"{key}: {value}\n" for key, value in metadata.items())
    if not msg.endswith("DATA_END: True\n"):
        msg += "DATA_END: True"
    _log.debug("Packed message: %s", msg)
    return msg


def unpack_message(message: str) -> dict[str, str]:
    """Read the message that has been received, and returns all of its metadata,
    including the message.

    Parameters
    ----------
    message : str
        The received message.

    Returns
    -------
    dict[str, str]
        Each metadata of the message.
    """
    metadata: dict[str, str] = {}
    for line in message.split("\n"):
        if "DATA_END" in line:
            metadata["DATA_END"] = "True"
        if ": " not in line:
            continue
        key, value = line.split(": ", maxsplit=1)
        metadata[key] = value
    return metadata


def calculate_checksum(message: str) -> str:
    return hashlib.md5(message.encode()).hexdigest()


class MessageBuffer:
    """The MessageBuffer class is used to receive message parts, while allowing the
    ability to instantly read metadata contained into the message.

    It also allow to store message parts into a buffer, so that it can be transformed
    later on as a Message.
    """

    def __init__(self):
        self.buffer = BytesIO()

    def push(self, data: bytes) -> None:
        """Append data to the end of the buffer."""
        self.buffer.write(data)

    def read(self) -> str:
        """Read the whole buffer and return it as a string."""
        self.buffer.seek(os.SEEK_SET)
        return self.buffer.read().decode()

    @property
    def is_complete(self) -> bool:
        """Ensure all data has been received.

        Returns
        -------
        bool
            True if the length matches the length of the data, otherwise False.
        """
        current_data = self.read()
        metadata = unpack_message(current_data)
        return metadata[KnownMetadata.LENGTH.value] == str(len(metadata["DATA"]))

    def get_raw(self, socket: socket.socket) -> "RawMessage":
        """Transform the current buffer into a Message object.

        Returns
        -------
        Message
            Transformed content into a Message object.
        """
        return RawMessage(socket, unpack_message(self.read()))

    def get_message(self, socket: socket.socket):
        return self.get_raw(socket).get_class_type()


class RawMessage:
    metadata: dict[str, str]

    def __init__(self, socket: socket.socket, metadata: dict[str, str]):
        self.socket = socket
        self.metadata = metadata

    def get_class_type(self):
        """Attempt to return the correct type of message to process this message.

        Returns
        -------
        Any subclasses of :py:class:`BaseMessage`
            The type of message to process.

        Raises
        ------
        KeyError
            In case the DATA_TYPE was not included in the metadata, or an unknown key was provided.
        """
        msg_type = self.metadata["DATA_TYPE"]

        match msg_type:
            case "MSG":
                return Message(self.socket, typing.cast(MessageMetadata, self.metadata))
            case "FILE":
                return FileMessage(
                    self.socket, typing.cast(FileMetadata, self.metadata)
                )
            case "LOGS":
                return LogsMessage(
                    self.socket, typing.cast(LogsMetadata, self.metadata)
                )
            case "CAPABILITIES":
                return CapabilitiesMessage(
                    self.socket, typing.cast(CapabilitiesMetadata, self.metadata)
                )
            case "ERROR":
                return ErrorMessage(
                    self.socket, typing.cast(ErrorMetadata, self.metadata)
                )
            case _:
                raise KeyError("Unknown message type.")

    def list_metadata(self) -> list[str]:
        """List all metadata contained into this message.

        Returns
        -------
        list[str]
            The list of metadata.
        """
        return list(self.metadata.keys())


class BaseMessage[TypeMetadata: BaseMetadata](abc.ABC):
    checksum: str
    __metadata: TypeMetadata

    @abc.abstractmethod
    def __init__(self, socket: socket.socket, metadata: TypeMetadata):
        self.checksum = metadata["DATA_CHECKSUM"]
        self.__socket = socket
        self.__metadata = metadata

    @property
    def __metadata__(self) -> TypeMetadata:
        return self.__metadata

    def __repr__(self) -> str:
        return f"<Message checksum={self.checksum}>"

    def validate_checksum(self) -> bool:
        """Calculate the MD5 checksum for the message we have received, compared to the
        checksum that has been shared by the sender.

        Returns
        -------
        bool
            True if checksums are matching, False otherwise.
        """
        current_msg_checksum = calculate_checksum(self.__metadata__["DATA"])
        return current_msg_checksum == self.__metadata__["DATA_CHECKSUM"]

    @staticmethod
    @abc.abstractmethod
    def create_message(*args: typing.Any, **kwargs: typing.Any) -> str:
        """This method will create a message ready to be sent in the socket.

        Parameters
        ----------
        message : str
            Data that must be sent into the socket
        additional_metadata : dict[str, str]
            Any additional metadata that might be sent.
        """
        raise NotImplementedError("Not implemented")

    @abc.abstractmethod
    def emit(self, events: "events.Events") -> None:
        """This method will emit the message in its assigned signal.
        Refer to :py:mod:`sae302.commons.events` for list of available signals.
        """
        raise NotImplementedError("Not implemented")

    def reply(self, message: str) -> None:
        self.__socket.send(message.encode())


class Message(BaseMessage[MessageMetadata]):
    message: str

    def __init__(self, socket: socket.socket, metadata: MessageMetadata):
        super().__init__(socket, metadata)
        self.message = metadata["DATA"]

    @staticmethod
    def create_message(message: str):
        metadata = MessageMetadata(
            DATA_CHECKSUM=calculate_checksum(message),
            DATA_LENGTH=str(len(message)),
            DATA_TYPE="MSG",
            DATA=message,
        )

        return pack_message(metadata)

    def emit(self, events: "events.Events"):
        _log.debug("Emitting message: %s", self.message)
        events.on_message.emit(self)


class FileMessage(BaseMessage[FileMetadata]):
    file_name: str
    file_content: str
    chosen_executor: str | typing.Literal["auto"]

    def __init__(self, socket: socket.socket, metadata: FileMetadata):
        super().__init__(socket, metadata)
        self.file_name = metadata["DATA_FILENAME"]
        self.file_content = json.loads(metadata["DATA"])["data"]
        self.chosen_executor = metadata.get("CHOSEN_EXECUTOR") or "auto"

    @staticmethod
    def create_message(
        file: pathlib.Path, executor: str | typing.Literal["auto"]
    ) -> str:
        content = json.dumps({"data": file.read_text()})
        metadata = FileMetadata(
            DATA_CHECKSUM=calculate_checksum(content),
            DATA_LENGTH=str(len(content)),
            DATA_TYPE="FILE",
            DATA_FILENAME=file.name,
            CHOSEN_EXECUTOR=executor,
            DATA=content,
        )
        return pack_message(metadata)

    def emit(self, events: "events.Events"):
        events.on_file.emit(self)


class LogsMessage(BaseMessage[LogsMetadata]):
    logs: str
    status: int

    def __init__(self, socket: socket.socket, metadata: LogsMetadata):
        super().__init__(socket, metadata)
        self.logs = json.loads(metadata["DATA"])["data"]
        self.status = int(metadata["STATUS"])

    @staticmethod
    def create_message(status: str, logs: str) -> str:
        data = json.dumps({"data": logs})
        metadata = LogsMetadata(
            DATA_CHECKSUM=calculate_checksum(data),
            DATA_LENGTH=str(len(data)),
            DATA_TYPE="LOGS",
            DATA=data,
            STATUS=status,
        )
        return pack_message(metadata)

    def emit(self, events: "events.Events"):
        events.on_logs.emit(self)


class CapabilitiesMessage(BaseMessage[CapabilitiesMetadata]):
    capabilities: dict[str, bool]

    def __init__(self, socket: socket.socket, metadata: CapabilitiesMetadata):
        super().__init__(socket, metadata)
        self.capabilities = json.loads(metadata["DATA"])

    @staticmethod
    def create_message(available_executors: dict["BaseExecutor", bool]) -> str:
        data = json.dumps(
            {
                executor[0].friendly_name: executor[1]
                for executor in available_executors.items()
            }
        )
        metadata = CapabilitiesMetadata(
            DATA_CHECKSUM=calculate_checksum(data),
            DATA_LENGTH=str(len(data)),
            DATA_TYPE="CAPABILITIES",
            DATA=data,
        )
        return pack_message(metadata)

    def emit(self, events: "events.Events"):
        events.on_capabilities.emit(self)


class ErrorMessage(BaseMessage[ErrorMetadata]):
    gravity: ERROR_GRAVITY
    message: str

    def __init__(self, socket: socket.socket, metadata: ErrorMetadata):
        super().__init__(socket, metadata)
        self.message = metadata["DATA"]
        self.gravity = metadata["GRAVITY"]

    @staticmethod
    def create_message(gravity: ERROR_GRAVITY, message: str) -> str:
        metadata = ErrorMetadata(
            DATA_CHECKSUM=calculate_checksum(message),
            DATA_LENGTH=str(len(message)),
            DATA_TYPE="ERROR",
            GRAVITY=gravity,
            DATA=message,
        )
        return pack_message(metadata)

    def emit(self, events: "events.Events"):
        events.on_error.emit(self)


type ALL_MESSAGES = Message | FileMessage | LogsMessage | CapabilitiesMessage | ErrorMessage
