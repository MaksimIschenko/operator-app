from src.utils.telemetrygetter import TelemetryGetter
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QTimer
from enum import Enum
import sys
from typing import Union, Any


class ControlMode(Enum):
    """Enumeration used to define the control modes."""
    MANUAL = 'Manual'
    REMOTE = 'Remote'
    UNDEFINED = 'Undefined'

class ModeController(TelemetryGetter):
    """
    ModeController is a subclass of TelemetryGetter.

    This controller can set the mode of the appliance in terms of who controls it.
    The UI for the client side is handled here.
    A Timer (mode_timer) is used to check the state of the connection to the server.
    """
    def __init__(self) -> None:
        """Initializes the ModeController."""
        super().__init__()

        self.mode: ControlMode = ControlMode.UNDEFINED

        self.mode_timer: QTimer = QTimer()
        self.mode_timer.timeout.connect(self._rmode)
        self.mode_timer.start(500)

        self.ui.btn_mnl_mode.clicked.connect(self.set_manual_mode)
        self.ui.btn_auto_mode.clicked.connect(self.set_auto_mode)
        self.ui.btn_rmt_mode.clicked.connect(self.set_remote_mode)

    def _rmode(self) -> None:
        """
        Check the connection status to the server and display it on the UI.
        Display the current mode on the UI.
        """
        try:
            if self.server.conn == None:
                self.ui.lb_status_val.setText('Не подключен')
            else:
                self.ui.lb_status_val.setText(str(self.server.addr[0]))
        except AttributeError as _:
            self.ui.lb_status_val.setText('Не подключен')

        self.ui.lb_rmode_val.setText(self.mode.value)

    def set_manual_mode(self) -> None:
        """Set the mode to a manual control by the client."""
        if self.mode == ControlMode.MANUAL:
            self.mode = ControlMode.UNDEFINED
        else:
            self.mode = ControlMode.MANUAL
            self.server.signals.set_mode.emit('MAN')

    def set_remote_mode(self) -> None:
        """Set the mode to remote control by the client."""
        if self.mode == ControlMode.REMOTE:
            self.mode = ControlMode.UNDEFINED
        else:
            self.mode = ControlMode.REMOTE
            self.server.signals.set_mode.emit('RMT')

    def set_auto_mode(self) -> None:
        """
        Try to set the mode to an automatic control.

        Since the mode is not yet implemented, it informs the client and sets the mode to 'undefined'.
        """
        QMessageBox.warning(None,
                            "Упсссс....",
                            "Этот режим ещё не готов. Принесите программисту сгущёнки",
                            QMessageBox.StandardButton.Ok)
        self.mode = ControlMode.UNDEFINED


if __name__ == "__main__":
    """Define the entry point of the application."""
    app: QApplication = QApplication(sys.argv)
    window: ModeController = ModeController()
    window.show()
    app.exec()