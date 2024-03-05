import os
from typing import Dict, Any, Union
from PySide6.QtCore import QRunnable, Signal, QObject, Slot
import socket
import select
import json
from dotenv import load_dotenv

load_dotenv()

class ServerSignals(QObject):
    """
    Defines signals for different actions or events that occur in the server.
    """
    started = Signal()
    stoped = Signal()
    connection_timeout = Signal()
    data_received = Signal(dict)
    data_sent = Signal(dict)

    get_gps = Signal()  # Request GPS
    get_imu = Signal()  # Request IMU

    set_mode = Signal(str)  # Set Mode
    mtr_cmd = Signal(str)  # Control Motor Command
    man_commandline = Signal(str)  # Manual Command
    man_key_control = Signal(str)  # Manual Key Control

class ServerThread(QRunnable):
    """
    Separate thread class for the server.
    """
    def __init__(self):
        """
        Initialize the server thread with default values.
        """
        super().__init__()
        self.snd_msg: Dict[str, Union[list, Dict[str, Any]]] = {'cmd': [], 'msg_data': {}}

        self.HOST: str = os.getenv("SERVER_HOST")
        self.PORT: int = 12345
        self.conn = None
        self.addr = None
        self.no_ro_resp_counts: int = 0

        self.signals = ServerSignals()
        self.signals.get_gps.connect(self.get_gps)
        self.signals.get_imu.connect(self.get_imu)
        self.signals.set_mode.connect(self.set_mode)
        self.signals.mtr_cmd.connect(self.mtr_cmd)
        self.signals.man_commandline.connect(self.man_commandline)
        self.signals.man_key_control.connect(self.man_key_control)

    @staticmethod
    def exception_handler(func):
        """
        Decorator function for handling exceptions in other methods.
        """
        def wrapper(*args, **kwargs):
            self = args[0]
            try:
                func(*args, **kwargs)
            except TimeoutError as e:
                self.signals.connection_timeout.emit()
            except ConnectionAbortedError as e:
                pass
            except OSError as e:
                pass
            except TypeError as e:
                print(e)
            except RuntimeError as e:
                print(e)
            finally:
                self.signals.stoped.emit()

        return wrapper

    def get_gps(self):
        """
        Append GPS to command.
        """
        self.snd_msg["cmd"].append("GPS")

    def get_imu(self):
        """
        Append IMU to command.
        """
        self.snd_msg["cmd"].append("IMU")

    @Slot(object)
    def set_mode(self, mode: str):
        """
        Set mode command with the provided mode.
        """
        self.snd_msg["cmd"].append("SETMODE")
        self.snd_msg['msg_data']['SETMODE'] = mode

    @Slot(object)
    def mtr_cmd(self, cmd: str):
        """
        Handle motor command.
        """
        self.snd_msg["cmd"].append("MTRCMD")
        self.snd_msg['msg_data']['MTRCMD'] = cmd

    @Slot(object)
    def man_commandline(self, cmd: str):
        """
        Assign manual command line.
        """
        if "MANLINECMD" not in self.snd_msg["cmd"]:
            self.snd_msg["cmd"].append("MANLINECMD")
            self.snd_msg['msg_data']['MANLINECMD'] = cmd

    @Slot(object)
    def man_key_control(self, cmds: str):
        """
        Handle manual key control.
        """
        if "MANKEYCMD" not in self.snd_msg["cmd"]:
            self.snd_msg["cmd"].append("MANKEYCMD")
            self.snd_msg['msg_data']['MANKEYCMD'] = cmds

    @exception_handler
    def run(self):
        """
        Create a new server socket and listen to incoming connections.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.bind((self.HOST, self.PORT))
            s.listen()

            self.conn, self.addr = s.accept()

            with self.conn:
                self.signals.started.emit()
                while True:
                    raw_data = self._get_data(self.conn)
                    data = self._parse_data(raw_data)
                    self.signals.data_received.emit(data)

                    self._send_data(self.conn)
                    self.signals.data_sent.emit(self.snd_msg)
                    self.snd_msg = {'cmd': [], 'msg_data': {}}

    def _get_data(self, conn: socket.socket) -> str:
        _TIMEOUT = 5
        _CTIMEOUT = 3
        if conn:
            ready = select.select([conn], [], [], _TIMEOUT)
            if ready[0]:
                self.no_ro_resp_counts = 0
                raw_data = conn.recv(1024).decode()
                return raw_data

            else:
                self.no_ro_resp_counts += 1
                if self.no_ro_resp_counts >= _CTIMEOUT:
                    raise ConnectionError(
                        f" [ERROR] - Нет ответа от клиента в течение {self.no_ro_resp_counts * _TIMEOUT} секунд!\n")

    def _parse_data(self, raw_data: str) -> Dict[str, Any]:
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError as e:
            print(f'[ERROR] - Unable to parse the raw data: {e}')
            data = {}
        return data

    def _send_data(self, conn: socket.socket):
        self.data_to_resp = json.dumps(self.snd_msg).encode()
        if conn is not None:
            conn.sendall(self.data_to_resp)
