from src.utils.base import Base
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
import sys


class TelemetryGetter(Base):
    """
    Class TelemetryGetter is a GUI for getting telemetry data automatically and manually.
    """
    def __init__(self):
        """
        Initializes the GUI and the connections for the TelemetryGetter GUI.

        The GUI has two checkboxes for enabling or disabling automatic requests.
        There are also two buttons for making manual requests.
        """
        super().__init__()
        self._auto_state = {'gps': 0, 'imu': 0}
        self.ui.btn_gps.clicked.connect(lambda _: self.request_telemetry('gps'))
        self.ui.btn_imu.clicked.connect(lambda _: self.request_telemetry('imu'))
        self.ui.cb_auto_gps.stateChanged.connect(lambda _: self.update_auto_state('gps'))
        self.ui.cb_auto_imu.stateChanged.connect(lambda _: self.update_auto_state('imu'))
        self.auto_request_timer = QTimer()
        self.auto_request_timer.timeout.connect(self.auto_request_telemetry)
        self.auto_request_timer.start(300)

    def update_auto_state(self, telemetrytype):
        """
        Update the state of automatic requests when a checkbox's state is changed.

        @param telemetrytype: String representing the type of telemetry ('gps' or 'imu') where the method
                                is going to update the checkbox state.
        """
        if self.ui.__dict__[f'cb_auto_{telemetrytype}'].checkState() == Qt.CheckState.Unchecked:
            self._auto_state[telemetrytype] -= 1
        elif self.ui.__dict__[f'cb_auto_{telemetrytype}'].checkState() == Qt.CheckState.Checked:
            self._auto_state[telemetrytype] += 1

    def auto_request_telemetry(self):
        """
        Request telemetry data automatically.

        If the connection is established and the checkbox for a telemetry type is checked,
        disables the respective button and makes an automatic request, else enables the button.
        """
        try:
            if self.server.conn is not None:
                for telemetrytype in ['gps', 'imu']:
                    if self._auto_state[telemetrytype] == 1:
                        self.ui.__dict__[f'btn_{telemetrytype}'].setEnabled(False)
                        self.request_telemetry(telemetrytype)
                    elif self._auto_state[telemetrytype] == 0:
                        self.ui.__dict__[f'btn_{telemetrytype}'].setEnabled(True)
        except AttributeError as _:
            pass

    def request_telemetry(self, telemetrytype):
        """
        Emit a signal to request telemetry data of a specific type.

        @param telemetrytype: String representing the type of telemetry ('gps' or 'imu') where the method
                                is going to request the data.
        """
        self.server.signals.__dict__[f'get_{telemetrytype}'].emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TelemetryGetter()
    window.show()
    app.exec()