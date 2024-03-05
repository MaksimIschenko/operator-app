from src.utils.manualcommandline import ManualCommandLine
from src.utils.modecontrol import ControlMode
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
import sys


class ManualKeysControl(ManualCommandLine):
    """Class for manually controlling keys using keyboard"""
    def __init__(self):
        """Initialize ManualKeysControl class by inheriting from ManualCommandLine class"""
        super().__init__()

    def emit_server_signal(self, cmds_character: str) -> None:
        """
        Emit server signal by appending power_signal to command character

        :param cmds_character: Command character representing direction
        """
        cmds = cmds_character + str(self.pwr_mnl)
        self.server.signals.man_key_control.emit(cmds)

    def keyPressEvent(self, event) -> None:
        """
        Handle key press event. If a key corresponding to a certain direction is
        pressed, emit server signal. For server connection or control mode not set to
        MANUAL or key not matched, it returns nothing.

        :param event: Key event to handle.
        """
        try:
            if self.server.conn is None:
                return
        except:
            return
        if self.mode != ControlMode.MANUAL:
            return
        key_press = event.key()
        if key_press == Qt.Key.Key_W:
            self.emit_server_signal('F')
        elif key_press == Qt.Key.Key_S:
            self.emit_server_signal('B')
        elif key_press == Qt.Key.Key_A:
            self.emit_server_signal('L')
        elif key_press == Qt.Key.Key_D:
            self.emit_server_signal('R')


if __name__ == "__main__":
    """Run the ManualKeysControl class"""
    app = QApplication(sys.argv)
    window = ManualKeysControl()
    window.show()
    app.exec()