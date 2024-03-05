from src.utils.powerlinecontrol import PowerLineController
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QTimer
import sys
from typing import Optional


class ManualCommandLine(PowerLineController):
    """
    A class to manually handle powerline commands.

    Attributes
    ----------
    None

    Methods
    -------
    send_mnl_cmd():
        Sends a manual command if the server connection is established and the command is not empty.
    """

    def __init__(self):
        """
        Initializes the ManualCommandLine class, hooks up widgets to their respective slots.
        """

        super().__init__()

        # отправка мануальной команды по нажатию клавиши "ENTER"
        self.ui.le_mnl_cmd.returnPressed.connect(self.send_mnl_cmd)
        # кнопка отправки мануальной команды
        self.ui.btn_mnl_cmd.clicked.connect(self.send_mnl_cmd)
    def send_mnl_cmd(self) -> Optional[None]:
        """
        Checks if the server connection is established and the command is not empty,
        then sends the entered manual command.

        Returns
        -------
        None
        """

        try:
            if self.server.conn is None:
                return
        except:
            return

        msg: str = str(self.ui.le_mnl_cmd.text())

        if msg == "":
            return

        # добавляем к строке 
        full_str: str = msg + '\r\n'

        self.server.signals.man_commandline.emit(full_str)


if __name__ == "__main__":
    """
    Entry point for the application.
    """

    app: QApplication = QApplication(sys.argv)
    window: ManualCommandLine = ManualCommandLine()
    window.show()
    app.exec()