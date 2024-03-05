from src.utils.motorcontrol import MotorController
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QTimer
import sys
from typing import Union

class PowerLineController(MotorController):
    """
    The PowerLineController class inherits from the MotorController class and is responsible for controlling
    power lines in the application.
    """

    def __init__(self) -> None:
        """
        Initializer for the PowerLineController class.
        Connects additional slots and resets input values to zero.
        """
        super().__init__()
        self.pwr_mnl: int = 0
        self.reset_input_to_zero()
        self.ui.le_pwr_mnl.editingFinished.connect(self._handle_line_edit)

    def _handle_line_edit(self) -> None:
        """
        Method that handles value changes in the power line input field.
        """
        ...

    @staticmethod
    def _is_input_empty(user_input: Union[str, int, float]) -> bool:
        """
        Returns True if user input is empty.
        """
        return user_input == ''

    def reset_input_to_zero(self) -> None:
        """
        Resets the power line's manual input field to zero.
        """
        self.pwr_mnl = 0
        self.ui.le_pwr_mnl.setText(str(self.pwr_mnl))

    @staticmethod
    def _check_valid_range(value: Union[int, float]) -> Union[int, float]:
        """
        Checks if the input value is within the valid range (0 to 100).
        If the value is out of bounds, it resets it to the nearest boundary.
        """
        if value > 100 or value < 0:
            # Reset out of bound values to maximum or minimum limit respectively.
            return 100 if value > 100 else 0
        return value

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PowerLineController()
    window.show()
    app.exec()