from src.utils.manualkeyscontrol import ManualKeysControl
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QTimer, Slot
from typing import Dict,List
import sys
import datetime


class TerminalWindow(ManualKeysControl):
    """
    A class used to represent a Terminal Window
    Displays a message based on the given data and message type
    """

    def __init__(self) -> None:
        """
        Constructs necessary attributes for the TerminalWindow object.
        """
        super().__init__()
        self.current_text: str = ""
        self.msg_to_terminal.connect(self.show_msg)

        self.terminal_cleaner = QTimer()
        self.terminal_cleaner.timeout.connect(self._clean_by_timer)
        self.terminal_cleaner.start(300)

        self.ui.btn_clean_textBrw.clicked.connect(self._clean_by_button)

    def _clean_by_timer(self) -> None:
        """
        If the current text exceeds 2000 characters, it is cleared.
        """
        if len(self.current_text) > 2000:
            self.current_text = ''

    def _clean_by_button(self) -> None:
        """
        Clears the current display text in the terminal.

        """
        self.current_text = ''

    def _add_to_terminal(self, message: str) -> None:
        """
        Adds a given message to the terminal.

        Parameters:
            message (str): The message to be added.
        """
        self.current_text = f'{message}' + self.current_text
        self.ui.terminal_window.setText(self.current_text)

    @Slot(object)
    def show_msg(self, data: Dict, msg_type: str) -> None:
        """
        Displays a given message based on the provided data and message type.

        Parameters:
            data (Dict): The data based on which the message is created.
            msg_type (str): The type of the message.
        """
        try:
            if data['msg_data'] == {} and data['cmd'] == []:
                return
        except KeyError:
            return

        if list(data['msg_data'].keys()) == ['INFO']:
            return

        message = self._create_message(data, msg_type)
        self._add_to_terminal(message)

    def _create_message(self, data: Dict, msg_type: str) -> str:
        """
        Creates a formatted message from given data and message type.

        Parameters:
            data (Dict): The data based on which the message is created.
            msg_type (str): The type of the message.

        Returns:
            str: The constructed message.
        """
        message = self._current_time() + f' - {msg_type}' + '\n'
        try:
            if len(data['cmd']) != 0:
                message += 'CMD: '
                for command in data['cmd']:
                    message += f'{command} '
                message += '\n'
        except Exception as _:
            pass

        for key in data['msg_data']:
            value_string = f'{str(data["msg_data"][key])[:-4]}\n'
            if key in ['INFO', 'SETMODE', 'MANKEYCMD', 'MANLINECM']:
                value_string = f'{str(data["msg_data"][key])}\n'
            message += f'{key}: {value_string}'

        return message + '\n'

    @staticmethod
    def _current_time() -> str:
        """
        Returns the current date and time as a string.

        Returns:
            str: The current time as a string in HH:MM:SS.fff format
        """
        return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TerminalWindow()
    window.show()
    app.exec()