from src.utils.terminalwindow import TerminalWindow
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Slot
import sys
from typing import List


class DataShower(TerminalWindow):
    """
    This class is responsible for handling data and displaying it.
    It inherits TerminalWindow class to use its features.
    """

    def __init__(self):
        """
        Constructor, initialize the class DataShower.
        Connect the telemetry_to_operator signal with parse slot.
        """

        super().__init__()
        self.telemetry_to_operator.connect(self.parse)

    @Slot(object)
    def parse(self, raw_data: str) -> None:
        """
        A slot function which prints and parses raw telemetry data.
        """
        print(raw_data)
        self.parse_msg(raw_data)

    def parse_msg(self, raw_data: str) -> None:
        """
        Method to parse message. Handles the message based on identifiers.
        """

        splitted = raw_data.split(',')
        data = splitted[4:-1]
        raw_crc = splitted[-1:]
        crc = int(raw_crc[0].split("*")[1])

        parsers = {"D,s,1,1": self.parse_msg_gps, "D,s,1,3": self.parse_msg_imu}

        for identifier, parser in parsers.items():
            if raw_data.startswith(identifier):
                parser(data)

    def parse_msg_gps(self, data: List[str]) -> None:
        """
        Method to parse GPS data.
        """

        # "D,s,1,1,5520.0459,N,2047.5840,E,15.2,123752,38.000,48.000,*73"
        Latitude, NS, Longitude, EW, Altitude = map(float, data[:5])
        _, _, GrndSpeed = map(float, data[5:])

        ## Updating attributes
        for attr, value in [('latitude', Latitude), ('NS', NS), ('longitude', Longitude), ('EW', EW), ('altitude', Altitude), ('grndspeed', GrndSpeed)]:
            getattr(self.ui, f'lb_{attr}_val').setText(str(value))

    def parse_msg_imu(self, data: List[str]) -> None:
        """
        Method to parse IMU data.
        """

        AXL_x, AXL_y, AXL_z = data[0:3]

        ## Updating attributes
        for attr, value in [('axl_x', AXL_x), ('axl_y', AXL_y), ('axl_z', AXL_z)]:
            getattr(self.ui, f'lb_{attr}_val').setText(str(value))


if __name__ == "__main__":
    ## Main function to run the application
    app = QApplication(sys.argv)
    window = DataShower()
    window.show()
    app.exec()