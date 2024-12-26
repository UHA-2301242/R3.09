from PyQt6 import QtCore

from sae302.commons import messages


class Events(QtCore.QObject):
    """Class listing the events to be emitted in the app.
    It MUST be initialized.
    """

    on_message = QtCore.pyqtSignal(messages.Message)
    """Emitted upon a received message."""
    on_file = QtCore.pyqtSignal(messages.FileMessage)
    """Emitted upon a file was received."""
    on_logs = QtCore.pyqtSignal(messages.LogsMessage)
    """Emitted upon logs were received."""
    on_capabilities = QtCore.pyqtSignal(messages.CapabilitiesMessage)
    """Emitted upon capabilities were received."""
    on_error = QtCore.pyqtSignal(messages.ErrorMessage)
    """Emitted upon an error was received."""
