from src.utils.modecontrol import ModeController
from PySide6.QtWidgets import QApplication
from typing import Optional, Union
import sys


class MotorController(ModeController):
    """
    MotorController class extends the ModeController class and is responsible for controlling motor operations.
    """

    def __init__(self):
        """
        Initializes the MotorController class.
        """
        super().__init__()

        self.set_button_states(True, False)

    def mtr_start_action(self):
        """
        If server connection is established, sends a 'START' signal to the motor and updates button states.
        """
        if self.is_server_connected():
            self.server.signals.mtr_cmd.emit('START')
            self.set_button_states(False, True)

    def mtr_stop_action(self):
        """
        If server connection is established, sends a 'STOP' signal to the motor and updates button states.
        """
        if self.is_server_connected():
            self.server.signals.mtr_cmd.emit('STOP')
            self.set_button_states(True, False)

    def is_server_connected(self) -> bool:
        """
        Checks if the server connection is established.

        :return: Boolean indicating if server connection is present.
        """
        try:
            return self.server.conn is not None
        except AttributeError:
            return False

    def set_button_states(self, start: bool, stop: bool) -> None:
        """
        Enables or disables the start and stop buttons for the motor.

        :param start: Boolean indicating if the start button should be enabled.
        :param stop: Boolean indicating if the stop button should be enabled.
        """
        self.ui.btn_motor_start.setEnabled(start)
        self.ui.btn_motor_stop.setEnabled(stop)


if __name__ == "__main__":
    """
    Main entry point of the application.
    """
    app = QApplication(sys.argv)
    # Create an instance of the MotorController
    window = MotorController()
    window.show()
    # Enter the application main loop
    app.exec()