# Required python packages
from PySide6.QtCore import QThreadPool, Slot, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from typing import List, Any

# User-defined packages
from src.server.server import ServerThread
from mainwindow import Ui_MainWindow


# System package
import sys

# Constants
ZERO = '0'
ERROR_TITLE = "Внимание"
ERROR_MESSAGE = "Сервер не запущен"
WARNING_BUTTON = QMessageBox.StandardButton


class Base(QMainWindow):
    """
    Base class that represents main GUI window.
    """
    msg_to_terminal: Signal = Signal(dict, str)
    telemetry_to_operator: Signal = Signal(str)

    def __init__(self) -> None:
        """
        Initialize the Base class.
        """
        super().__init__()

        self.ui: Ui_MainWindow = Ui_MainWindow()
        self.ui.setupUi(self)

        # Setting Button Stats
        self.ui.btn_server_start.setDisabled(False)
        self.ui.btn_server_stop.setDisabled(True)

        # Signals on Button Click
        self.ui.btn_server_start.clicked.connect(self.start_server)
        self.ui.btn_server_stop.clicked.connect(self.stop_server)

        self.pool: QThreadPool = QThreadPool.globalInstance()
        self.set_zero_values()

    def set_zero_values(self) -> None:
        """
        Sets initial values for on screen elements.
        """
        zero_labels: List[QLabel] = [self.ui.lb_latitude_val, self.ui.lb_NS_val, self.ui.lb_longitude_val,
                                     self.ui.lb_EW_val, self.ui.lb_altitude_val, self.ui.lb_grndspeed_val,
                                     self.ui.lb_axl_x_val, self.ui.lb_axl_y_val, self.ui.lb_axl_z_val, ]

        for label in zero_labels:
            label.setText(ZERO)  # Introduced Constant 'ZERO'

    def start_server(self) -> None:
        """
        Starts the server thread and connects signals.
        """
        self.server: ServerThread = ServerThread()
        self.pool.start(self.server)

        # signals from the thread
        self.server.signals.started.connect(self.server_started_actions)
        self.server.signals.connection_timeout.connect(self.timeout_actions)
        self.server.signals.data_received.connect(self._process_rcv_data)
        self.server.signals.data_sent.connect(self._process_snd_data)

    def stop_server(self) -> None:
        """
        Stops the server and resets connection data.
        """
        try:
            self.server.conn.shutdown(0)
            self.set_zero_values()
            self.server.conn = None
            self.server.addr = None
            self.ui.btn_motor_start.setEnabled(True)
            self.ui.btn_motor_stop.setEnabled(False)
        except AttributeError as _:
            self.display_error()
        except OSError as e:
            self.display_error()
        finally:
            self.server_stopped_actions()

    def server_started_actions(self) -> None:
        """
        Actions to perform after server starts.
        """
        self.ui.btn_server_start.setDisabled(True)
        self.ui.btn_server_stop.setDisabled(False)

    def server_stopped_actions(self) -> None:
        """
        Actions to perform after server stops.
        """
        self.ui.btn_server_start.setDisabled(False)
        self.ui.btn_server_stop.setDisabled(True)

    @staticmethod
    def timeout_actions(self) -> None:
        """
        Actions to perform on connection timeout.
        """
        QMessageBox.critical(None, "Ошибка", "Таймаут подключения",
                             QMessageBox.StandardButton.Ok)

    @staticmethod
    def display_error(self) -> None:
        """
        Displays error message when server is not started.
        """
        print('Сервер не запущен, чтобы его останавливать')
        QMessageBox.warning(None, ERROR_TITLE, ERROR_MESSAGE, WARNING_BUTTON)

    @Slot(object)
    def _process_snd_data(self, data: dict) -> None:
        """
        Process and emit sent data.

        :param data: Data that was sent.
        """
        self.msg_to_terminal.emit(data, "SEND")

    @Slot(object)
    def _process_rcv_data(self, data: dict) -> None:
        """
        Process and emit received data.

        :param data: Data that was received.
        """
        self.msg_to_terminal.emit(data, "RCVD")
        if "status" in data and data["status"] == "RESPONSE":
            if "GPSRESPONSE" in data["msg_data"]:
                self.telemetry_to_operator.emit(data["msg_data"]["GPSRESPONSE"])
            if "IMURESPONSE" in data["msg_data"]:
                self.telemetry_to_operator.emit(data["msg_data"]["IMURESPONSE"])


if __name__ == '__main__':
    app: QApplication = QApplication(sys.argv)
    window: Base = Base()
    window.show()
    app.exec()